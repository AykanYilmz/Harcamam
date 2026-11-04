"""Finds payments that repeat every month: subscriptions, but also rent or a phone bill.

Nothing is stored: subscriptions are worked out from the transactions on every request, so
they are never out of date after an upload, a deletion or a correction. Only the user's
"this is not a subscription" choices are kept.
"""

import calendar
import datetime as dt
from dataclasses import dataclass
from decimal import Decimal
from itertools import pairwise

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import (
    Category,
    CategoryKind,
    DismissedSubscription,
    Transaction,
    TransactionType,
    User,
)
from app.services.merchants import merchant_name
from app.services.parsing.formats import normalize_text
from app.services.periods import add_months

MIN_CHARGES = 3
# Days between two charges: about a month, or two when a month's statement is missing.
MONTHLY_GAPS = (range(25, 36), range(55, 71))
# The highest charge may be at most this much above the lowest: enough for a price rise,
# not for a gas bill that is four times higher in winter.
MAX_AMOUNT_SPREAD = Decimal("1.35")
# A subscription not charged for longer than this is shown as stopped.
ACTIVE_WITHIN_DAYS = 45


@dataclass(frozen=True)
class Charge:
    date: dt.date
    amount: Decimal


@dataclass(frozen=True)
class Subscription:
    key: str
    name: str
    category: Category
    charges: list[Charge]
    active: bool

    @property
    def amount(self) -> Decimal:
        """What it costs now: the latest charge."""
        return self.charges[-1].amount

    @property
    def yearly_amount(self) -> Decimal:
        return self.amount * 12

    @property
    def previous_amount(self) -> Decimal | None:
        """The old price, if a price that had stayed the same changed with the latest charge.

        Bills that differ every month (water, food delivery) never count as a price rise.
        """
        before, previous = self.charges[-3].amount, self.charges[-2].amount
        if before == previous != self.amount:
            return previous
        return None

    @property
    def next_charge(self) -> dt.date | None:
        """The same day next month (or that month's last day): charges come on a fixed day."""
        if not self.active:
            return None
        last = self.charges[-1].date
        month = add_months(last.replace(day=1), 1)
        days_in_month = calendar.monthrange(month.year, month.month)[1]
        return month.replace(day=min(last.day, days_in_month))


def _is_monthly(charges: list[Charge]) -> bool:
    if len(charges) < MIN_CHARGES:
        return False
    gaps = [(b.date - a.date).days for a, b in pairwise(charges)]
    if not all(any(gap in window for window in MONTHLY_GAPS) for gap in gaps):
        return False
    amounts = [charge.amount for charge in charges]
    return max(amounts) <= min(amounts) * MAX_AMOUNT_SPREAD


def dismissed(db: Session, user: User) -> list[DismissedSubscription]:
    return list(
        db.scalars(
            select(DismissedSubscription)
            .where(DismissedSubscription.user_id == user.id)
            .order_by(DismissedSubscription.name)
        )
    )


def find_subscriptions(db: Session, user: User) -> list[Subscription]:
    """Monthly payments, most expensive first, with the ones the user dismissed left out."""
    rows = db.execute(
        select(Transaction, Category)
        .join(Category, Transaction.category_id == Category.id)
        .where(
            Transaction.user_id == user.id,
            Transaction.type == TransactionType.EXPENSE,
            Category.kind == CategoryKind.EXPENSE,
        )
        .order_by(Transaction.date)
    ).all()
    if not rows:
        return []
    # "Now" is the latest transaction rather than today: statements arrive a month late.
    latest = max(transaction.date for transaction, _ in rows)

    groups: dict[str, tuple[str, list[tuple[Transaction, Category]]]] = {}
    for transaction, category in rows:
        name = merchant_name(transaction.description)
        groups.setdefault(normalize_text(name), (name, []))[1].append((transaction, category))

    hidden = {item.merchant_key for item in dismissed(db, user)}
    subscriptions = []
    for key, (name, items) in groups.items():
        if key in hidden:
            continue
        charges = [Charge(transaction.date, transaction.amount) for transaction, _ in items]
        if not _is_monthly(charges):
            continue
        subscriptions.append(
            Subscription(
                key=key,
                name=name,
                category=items[-1][1],
                charges=charges,
                active=(latest - charges[-1].date).days <= ACTIVE_WITHIN_DAYS,
            )
        )
    subscriptions.sort(key=lambda s: (not s.active, -s.amount, s.name))
    return subscriptions


class SubscriptionNotFoundError(Exception):
    pass


def dismiss(db: Session, user: User, key: str) -> None:
    """Hide a detected subscription; `key` must be one currently detected."""
    subscription = next((s for s in find_subscriptions(db, user) if s.key == key), None)
    if subscription is None:
        raise SubscriptionNotFoundError
    db.add(DismissedSubscription(user_id=user.id, merchant_key=key, name=subscription.name))
    db.commit()


def restore(db: Session, user: User, key: str) -> None:
    db.execute(
        delete(DismissedSubscription).where(
            DismissedSubscription.user_id == user.id,
            DismissedSubscription.merchant_key == key,
        )
    )
    db.commit()
