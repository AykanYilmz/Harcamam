"""Report calculations.

Rules shared by every report, based on each category's kind:
- Transfer categories are left out entirely (moving money is neither income nor spending).
- Income is the net of the income categories.
- Spending in an expense category is its expenses minus its income, so a refund lowers the
  spending of the category it belongs to instead of counting as income.

"Month" means the user's reporting period (see app.services.periods): the calendar month, or
the month that ends on their statement closing day. Months are named by their first day.
"""

import datetime as dt
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from decimal import Decimal

from sqlalchemy import ColumnElement, case, func, select
from sqlalchemy.orm import Session

from app.models import Category, CategoryKind, Transaction, TransactionType, User
from app.services.categories import build_categorizer
from app.services.parsing.formats import normalize_text
from app.services.periods import Period, PeriodCalendar, add_months

ZERO = Decimal("0.00")

# +amount for income, -amount for expenses.
_signed_amount = case(
    (Transaction.type == TransactionType.INCOME, Transaction.amount), else_=-Transaction.amount
)


def period_calendar(user: User) -> PeriodCalendar:
    return PeriodCalendar(user.period_end_day)


def _within(first: Period, last: Period) -> tuple[ColumnElement[bool], ColumnElement[bool]]:
    """Filter for transactions from the start of `first` to the end of `last`."""
    return Transaction.date >= first.start, Transaction.date < last.end_exclusive


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
    return period_calendar(user).month_of(latest or dt.date.today())


@dataclass(frozen=True)
class MonthTotals:
    period: Period
    income: Decimal
    expense: Decimal

    @property
    def month(self) -> dt.date:
        return self.period.month

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


def month_range(user: User, first: dt.date, last: dt.date) -> list[Period]:
    """The user's periods for every month from `first` to `last`."""
    return period_calendar(user).periods(first, last)


def monthly_totals(db: Session, user: User, first: dt.date, last: dt.date) -> list[MonthTotals]:
    """Income and expense for every month from `first` to `last`, months without data as 0."""
    periods = period_calendar(user)
    months = periods.periods(first, last)
    is_income = Category.kind == CategoryKind.INCOME
    # Summed per day in SQL, then per period here: a period need not start on the 1st.
    rows = db.execute(
        select(
            Transaction.date,
            func.sum(case((is_income, _signed_amount), else_=0)),
            func.sum(case((is_income, 0), else_=-_signed_amount)),
        )
        .join(Category, Transaction.category_id == Category.id)
        .where(
            Transaction.user_id == user.id,
            Category.kind != CategoryKind.TRANSFER,
            *_within(months[0], months[-1]),
        )
        .group_by(Transaction.date)
    )
    income: defaultdict[dt.date, Decimal] = defaultdict(lambda: ZERO)
    expense: defaultdict[dt.date, Decimal] = defaultdict(lambda: ZERO)
    for day, day_income, day_expense in rows:
        month = periods.month_of(day)
        income[month] += day_income
        expense[month] += day_expense

    return [MonthTotals(period, income[period.month], expense[period.month]) for period in months]


@dataclass(frozen=True)
class CategoryTrend:
    category: Category
    # One amount per month, in the same order as the months asked for.
    amounts: list[Decimal]

    @property
    def total(self) -> Decimal:
        return sum(self.amounts, ZERO)


def category_trend(db: Session, user: User, first: dt.date, last: dt.date) -> list[CategoryTrend]:
    """Spending per expense category for every month from `first` to `last`, largest total
    first. Categories without spending in the period are left out."""
    periods = period_calendar(user)
    months = periods.periods(first, last)
    rows = db.execute(
        select(Category, Transaction.date, func.sum(-_signed_amount))
        .join(Transaction, Transaction.category_id == Category.id)
        .where(
            Transaction.user_id == user.id,
            Category.kind == CategoryKind.EXPENSE,
            *_within(months[0], months[-1]),
        )
        .group_by(Category.id, Transaction.date)
    )
    by_category: defaultdict[Category, defaultdict[dt.date, Decimal]] = defaultdict(
        lambda: defaultdict(lambda: ZERO)
    )
    for category, day, amount in rows:
        by_category[category][periods.month_of(day)] += amount

    trends = [
        CategoryTrend(category, [amounts[period.month] for period in months])
        for category, amounts in by_category.items()
    ]
    trends.sort(key=lambda trend: (-trend.total, trend.category.name))
    return trends


def _spending_by_category(db: Session, user: User, period: Period) -> dict[Category, Decimal]:
    rows = db.execute(
        select(Category, func.sum(-_signed_amount))
        .join(Transaction, Transaction.category_id == Category.id)
        .where(
            Transaction.user_id == user.id,
            Category.kind == CategoryKind.EXPENSE,
            *_within(period, period),
        )
        .group_by(Category.id)
    )
    return {category: Decimal(amount) for category, amount in rows}


def monthly_report(db: Session, user: User, month: dt.date | None = None) -> MonthlyReport:
    month = month or latest_month(db, user)
    previous, current = monthly_totals(db, user, add_months(month, -1), month)

    spending = _spending_by_category(db, user, current.period)
    previous_spending = _spending_by_category(db, user, previous.period)
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
            Transaction.user_id == user.id, *_within(current.period, current.period)
        )
    )
    return MonthlyReport(
        current=current,
        previous=previous,
        transaction_count=transaction_count or 0,
        categories=category_rows,
    )


@dataclass(frozen=True)
class MerchantSpending:
    name: str
    amount: Decimal
    transaction_count: int
    # The category most of this merchant's transactions are in.
    category: Category


@dataclass
class _MerchantGroup:
    name: str
    amount: Decimal = ZERO
    transaction_count: int = 0
    categories: Counter[Category] = field(default_factory=Counter)


def top_merchants(
    db: Session, user: User, month: dt.date | None = None, limit: int = 10
) -> list[MerchantSpending]:
    """Where the money went in `month`, grouped by the keyword that categorized each transaction.

    "MIGROS KADIKOY" and "MIGROS SANAL MARKET" both match the keyword MIGROS, so they form one
    merchant. Transactions no keyword matches are grouped by their own description. Refunds
    lower their merchant's total, the same way they lower category spending.
    """
    period = period_calendar(user).period(month or latest_month(db, user))
    rows = db.execute(
        select(Transaction, Category)
        .join(Category, Transaction.category_id == Category.id)
        .where(
            Transaction.user_id == user.id,
            Category.kind == CategoryKind.EXPENSE,
            *_within(period, period),
        )
    )

    categorizer = build_categorizer(db, user)
    groups: dict[str, _MerchantGroup] = {}
    for transaction, category in rows:
        rule = categorizer.match(transaction.description)
        name = rule.keyword if rule else transaction.description
        group = groups.setdefault(normalize_text(name), _MerchantGroup(name=name))
        is_expense = transaction.type is TransactionType.EXPENSE
        group.amount += transaction.amount if is_expense else -transaction.amount
        group.transaction_count += 1
        group.categories[category] += 1

    merchants = [
        MerchantSpending(
            name=group.name,
            amount=group.amount,
            transaction_count=group.transaction_count,
            category=group.categories.most_common(1)[0][0],
        )
        for group in groups.values()
        # A merchant with only refunds this month isn't somewhere money went.
        if group.amount > 0
    ]
    merchants.sort(key=lambda merchant: (-merchant.amount, merchant.name))
    return merchants[:limit]


def daily_spending(db: Session, user: User, month: dt.date) -> list[tuple[dt.date, Decimal]]:
    """Spending for every day of `month` (days without spending as 0), same rules as above."""
    period = period_calendar(user).period(month)
    rows = db.execute(
        select(Transaction.date, func.sum(-_signed_amount))
        .join(Category, Transaction.category_id == Category.id)
        .where(
            Transaction.user_id == user.id,
            Category.kind == CategoryKind.EXPENSE,
            *_within(period, period),
        )
        .group_by(Transaction.date)
    )
    by_day = {day: Decimal(amount) for day, amount in rows}
    return [(day, by_day.get(day, ZERO)) for day in period.days()]
