"""Monthly category budgets, measured with the same spending rules as the reports."""

import datetime as dt
import enum
import uuid
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Budget, Category, CategoryKind, User
from app.services.categories import CategoryNotFoundError, get_accessible_category
from app.services.periods import Period
from app.services.reports import ZERO, period_calendar, spending_by_category

# From this share of the limit on, a budget is "close to the limit".
WARNING_SHARE = Decimal("0.8")


class BudgetNotFoundError(Exception):
    pass


class BudgetExistsError(Exception):
    """The category already has a budget."""


class NotAnExpenseCategoryError(Exception):
    """Only spending can be budgeted; income and transfer categories can't."""


class BudgetStatus(enum.StrEnum):
    OK = "ok"
    WARNING = "warning"
    OVER = "over"


@dataclass(frozen=True)
class BudgetUsage:
    budget: Budget
    category: Category
    spent: Decimal

    @property
    def remaining(self) -> Decimal:
        return self.budget.monthly_limit - self.spent

    @property
    def used_pct(self) -> float:
        return round(float(self.spent / self.budget.monthly_limit * 100), 1)

    @property
    def status(self) -> BudgetStatus:
        if self.spent > self.budget.monthly_limit:
            return BudgetStatus.OVER
        if self.spent >= self.budget.monthly_limit * WARNING_SHARE:
            return BudgetStatus.WARNING
        return BudgetStatus.OK


@dataclass(frozen=True)
class BudgetReport:
    period: Period
    # How far into the month `today` is, for months in progress; None for past or future ones.
    days_elapsed: int | None
    usages: list[BudgetUsage]

    @property
    def days_in_period(self) -> int:
        return (self.period.end - self.period.start).days + 1

    def projected(self, usage: BudgetUsage) -> Decimal | None:
        """Where spending ends up if it goes on at this month's pace so far."""
        if not self.days_elapsed:
            return None
        pace = usage.spent / self.days_elapsed * self.days_in_period
        return pace.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def budget_report(
    db: Session, user: User, month: dt.date, today: dt.date | None = None
) -> BudgetReport:
    period = period_calendar(user).period(month)
    today = today or dt.date.today()
    in_progress = period.start <= today <= period.end
    spending = {
        category.id: amount for category, amount in spending_by_category(db, user, period).items()
    }

    rows = db.execute(
        select(Budget, Category)
        .join(Category, Budget.category_id == Category.id)
        .where(Budget.user_id == user.id)
    )
    usages = [
        BudgetUsage(budget, category, spending.get(category.id, ZERO)) for budget, category in rows
    ]
    # Closest to (or furthest over) the limit first: that is what needs attention.
    usages.sort(key=lambda usage: (-usage.used_pct, usage.category.name))
    return BudgetReport(
        period=period,
        days_elapsed=(today - period.start).days + 1 if in_progress else None,
        usages=usages,
    )


def _get_own_budget(db: Session, user: User, budget_id: uuid.UUID) -> Budget:
    budget = db.get(Budget, budget_id)
    if budget is None or budget.user_id != user.id:
        raise BudgetNotFoundError
    return budget


def create_budget(
    db: Session, user: User, category_id: uuid.UUID, monthly_limit: Decimal
) -> Budget:
    category = get_accessible_category(db, user, category_id)
    if category is None:
        raise CategoryNotFoundError
    if category.kind is not CategoryKind.EXPENSE:
        raise NotAnExpenseCategoryError
    exists = db.scalar(
        select(Budget.id).where(Budget.user_id == user.id, Budget.category_id == category_id)
    )
    if exists:
        raise BudgetExistsError

    budget = Budget(user_id=user.id, category_id=category_id, monthly_limit=monthly_limit)
    db.add(budget)
    try:
        db.commit()
    except IntegrityError as exc:
        # Another request added a budget for this category between the check and the insert.
        db.rollback()
        raise BudgetExistsError from exc
    return budget


def update_budget(db: Session, user: User, budget_id: uuid.UUID, monthly_limit: Decimal) -> Budget:
    budget = _get_own_budget(db, user, budget_id)
    budget.monthly_limit = monthly_limit
    db.commit()
    return budget


def delete_budget(db: Session, user: User, budget_id: uuid.UUID) -> None:
    db.delete(_get_own_budget(db, user, budget_id))
    db.commit()
