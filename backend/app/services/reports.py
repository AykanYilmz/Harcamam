"""Report calculations.

Rules shared by every report, based on each category's kind:
- Transfer categories are left out entirely (moving money is neither income nor spending).
- Income is the net of the income categories.
- Spending in an expense category is its expenses minus its income, so a refund lowers the
  spending of the category it belongs to instead of counting as income.
"""

import datetime as dt
from collections import Counter
from dataclasses import dataclass, field
from decimal import Decimal

from sqlalchemy import Date, case, func, select
from sqlalchemy.orm import Session

from app.models import Category, CategoryKind, Transaction, TransactionType, User
from app.services.categories import build_categorizer
from app.services.parsing.formats import normalize_text

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


def monthly_totals(db: Session, user: User, first: dt.date, last: dt.date) -> list[MonthTotals]:
    """Income and expense for every month from `first` to `last`, months without data as 0."""
    month = func.date_trunc("month", Transaction.date).cast(Date).label("month")
    is_income = Category.kind == CategoryKind.INCOME
    rows = db.execute(
        select(
            month,
            func.coalesce(func.sum(case((is_income, _signed_amount), else_=0)), 0),
            func.coalesce(func.sum(case((is_income, 0), else_=-_signed_amount)), 0),
        )
        .join(Category, Transaction.category_id == Category.id)
        .where(
            Transaction.user_id == user.id,
            Category.kind != CategoryKind.TRANSFER,
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


def _spending_by_category(db: Session, user: User, month: dt.date) -> dict[Category, Decimal]:
    rows = db.execute(
        select(Category, func.sum(-_signed_amount))
        .join(Transaction, Transaction.category_id == Category.id)
        .where(
            Transaction.user_id == user.id,
            Category.kind == CategoryKind.EXPENSE,
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

    spending = _spending_by_category(db, user, month)
    previous_spending = _spending_by_category(db, user, previous_month)
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
    month = month or latest_month(db, user)
    rows = db.execute(
        select(Transaction, Category)
        .join(Category, Transaction.category_id == Category.id)
        .where(
            Transaction.user_id == user.id,
            Category.kind == CategoryKind.EXPENSE,
            Transaction.date >= month,
            Transaction.date < add_months(month, 1),
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
    rows = db.execute(
        select(Transaction.date, func.sum(-_signed_amount))
        .join(Category, Transaction.category_id == Category.id)
        .where(
            Transaction.user_id == user.id,
            Category.kind == CategoryKind.EXPENSE,
            Transaction.date >= month,
            Transaction.date < add_months(month, 1),
        )
        .group_by(Transaction.date)
    )
    by_day = {day: Decimal(amount) for day, amount in rows}

    days = []
    day = month
    while day < add_months(month, 1):
        days.append((day, by_day.get(day, ZERO)))
        day += dt.timedelta(days=1)
    return days
