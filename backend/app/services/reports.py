"""Report calculations.

Rules shared by every report:
- Transactions in "Transfer" are left out entirely (moving money is neither income nor spending).
- Income is the net of the "Gelir" category.
- Spending in any other category is its expenses minus its income, so a refund lowers the
  spending of the category it belongs to instead of counting as income.
"""

import datetime as dt
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import Date, case, func, select
from sqlalchemy.orm import Session

from app.models import (
    INCOME_CATEGORY,
    TRANSFER_CATEGORY,
    Category,
    Transaction,
    TransactionType,
    User,
)
from app.services.categories import get_default_category

ZERO = Decimal("0.00")

# +amount for income, -amount for expenses.
_signed_amount = case(
    (Transaction.type == TransactionType.INCOME, Transaction.amount), else_=-Transaction.amount
)


def month_start(day: dt.date) -> dt.date:
    return day.replace(day=1)


def add_months(month: dt.date, count: int) -> dt.date:
    index = month.year * 12 + month.month - 1 + count
    return dt.date(index // 12, index % 12 + 1, 1)


def month_label(month: dt.date) -> str:
    return f"{month.year:04d}-{month.month:02d}"


def parse_month(value: str) -> dt.date:
    """`2026-10` -> date(2026, 10, 1); the format is validated by the API layer."""
    year, month = value.split("-")
    return dt.date(int(year), int(month), 1)


def change_pct(current: Decimal, previous: Decimal) -> float | None:
    """Percentage change; None when there is nothing to compare against."""
    if previous == 0:
        return None
    return round(float((current - previous) / abs(previous) * 100), 1)


def share_pct(amount: Decimal, total: Decimal) -> float | None:
    """`amount` as a percentage of `total`; None when the total is not positive."""
    if total <= 0:
        return None
    return round(float(amount / total * 100), 1)


def latest_month(db: Session, user: User) -> dt.date:
    """The most recent month with transactions, or the current month if there are none."""
    latest = db.scalar(select(func.max(Transaction.date)).where(Transaction.user_id == user.id))
    return month_start(latest or dt.date.today())


@dataclass(frozen=True)
class MonthTotals:
    month: dt.date
    income: Decimal
    expense: Decimal

    @property
    def net(self) -> Decimal:
        return self.income - self.expense


@dataclass(frozen=True)
class CategorySpending:
    category: Category
    amount: Decimal
    previous_amount: Decimal


@dataclass(frozen=True)
class MonthlyReport:
    current: MonthTotals
    previous: MonthTotals
    transaction_count: int
    categories: list[CategorySpending]


class _ReportCategories:
    """Ids of the default categories the rules above depend on."""

    def __init__(self, db: Session) -> None:
        self.income_id = get_default_category(db, INCOME_CATEGORY).id
        self.transfer_id = get_default_category(db, TRANSFER_CATEGORY).id


def monthly_totals(db: Session, user: User, first: dt.date, last: dt.date) -> list[MonthTotals]:
    """Income and expense for every month from `first` to `last`, months without data as 0."""
    categories = _ReportCategories(db)
    month = func.date_trunc("month", Transaction.date).cast(Date).label("month")
    is_income = Transaction.category_id == categories.income_id
    rows = db.execute(
        select(
            month,
            func.coalesce(func.sum(case((is_income, _signed_amount), else_=0)), 0),
            func.coalesce(func.sum(case((is_income, 0), else_=-_signed_amount)), 0),
        )
        .where(
            Transaction.user_id == user.id,
            Transaction.category_id != categories.transfer_id,
            Transaction.date >= first,
            Transaction.date < add_months(last, 1),
        )
        .group_by(month)
    )
    by_month = {row_month: (income, expense) for row_month, income, expense in rows}

    result = []
    current = first
    while current <= last:
        income, expense = by_month.get(current, (ZERO, ZERO))
        result.append(MonthTotals(current, Decimal(income), Decimal(expense)))
        current = add_months(current, 1)
    return result


def _spending_by_category(
    db: Session, user: User, month: dt.date, categories: _ReportCategories
) -> dict[Category, Decimal]:
    rows = db.execute(
        select(Category, func.sum(-_signed_amount))
        .join(Transaction, Transaction.category_id == Category.id)
        .where(
            Transaction.user_id == user.id,
            Transaction.category_id.not_in([categories.income_id, categories.transfer_id]),
            Transaction.date >= month,
            Transaction.date < add_months(month, 1),
        )
        .group_by(Category.id)
    )
    return {category: Decimal(amount) for category, amount in rows}


def monthly_report(db: Session, user: User, month: dt.date | None = None) -> MonthlyReport:
    month = month or latest_month(db, user)
    previous_month = add_months(month, -1)
    previous, current = monthly_totals(db, user, previous_month, month)

    categories = _ReportCategories(db)
    spending = _spending_by_category(db, user, month, categories)
    previous_spending = _spending_by_category(db, user, previous_month, categories)
    category_rows = [
        CategorySpending(
            category=category,
            amount=spending.get(category, ZERO),
            previous_amount=previous_spending.get(category, ZERO),
        )
        # Categories from either month, so a drop to zero is still visible.
        for category in spending.keys() | previous_spending.keys()
    ]
    category_rows.sort(key=lambda row: (-row.amount, row.category.name))

    transaction_count = db.scalar(
        select(func.count()).where(
            Transaction.user_id == user.id,
            Transaction.date >= month,
            Transaction.date < add_months(month, 1),
        )
    )
    return MonthlyReport(
        current=current,
        previous=previous,
        transaction_count=transaction_count or 0,
        categories=category_rows,
    )
