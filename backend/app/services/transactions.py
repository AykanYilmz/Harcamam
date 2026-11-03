import math
import uuid

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.orm import Session

from app.models import CategoryRule, Transaction, User
from app.schemas.transactions import TransactionFilters, TransactionSort
from app.services.categories import (
    CategoryNotFoundError,
    get_accessible_category,
    save_rule,
    validate_keyword,
)
from app.services.parsing.formats import ASCII_LETTERS, TURKISH_LETTERS, fold_turkish


class TransactionNotFoundError(Exception):
    pass


def _ensure_category_accessible(db: Session, user: User, category_id: uuid.UUID) -> None:
    if get_accessible_category(db, user, category_id) is None:
        raise CategoryNotFoundError


def correct_category(
    db: Session,
    user: User,
    transaction_id: uuid.UUID,
    category_id: uuid.UUID,
    rule_keyword: str | None = None,
) -> tuple[Transaction, CategoryRule | None, int]:
    """Set a transaction's category by hand, optionally teaching a rule from it.

    Returns the transaction, the saved rule (if any) and how many other transactions the
    rule re-categorized.
    """
    transaction = db.scalar(
        select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == user.id)
    )
    if transaction is None:
        raise TransactionNotFoundError
    _ensure_category_accessible(db, user, category_id)
    # Validate everything before changing anything.
    if rule_keyword:
        validate_keyword(rule_keyword)

    transaction.category_id = category_id
    transaction.is_manually_categorized = True
    # Flush before re-categorizing, which only selects rows still marked automatic in the DB.
    db.flush()

    rule, updated = None, 0
    if rule_keyword:
        rule, updated = save_rule(db, user, rule_keyword, category_id)
    db.commit()
    return transaction, rule, updated


def bulk_set_category(
    db: Session, user: User, transaction_ids: list[uuid.UUID], category_id: uuid.UUID
) -> int:
    """Set the category of several transactions; all or nothing."""
    _ensure_category_accessible(db, user, category_id)
    wanted = set(transaction_ids)
    transactions = db.scalars(
        select(Transaction).where(Transaction.id.in_(wanted), Transaction.user_id == user.id)
    ).all()
    # Any id that isn't the user's (or doesn't exist) fails the whole request.
    if len(transactions) != len(wanted):
        raise TransactionNotFoundError

    for transaction in transactions:
        transaction.category_id = category_id
        transaction.is_manually_categorized = True
    db.commit()
    return len(transactions)


_SORT_ORDER = {
    TransactionSort.DATE_DESC: (Transaction.date.desc(),),
    TransactionSort.DATE_ASC: (Transaction.date.asc(),),
    TransactionSort.AMOUNT_DESC: (Transaction.amount.desc(), Transaction.date.desc()),
    TransactionSort.AMOUNT_ASC: (Transaction.amount.asc(), Transaction.date.desc()),
}


def escape_like(value: str) -> str:
    """Make `%` and `_` typed by the user match literally instead of acting as wildcards."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _description_contains(text: str) -> ColumnElement[bool]:
    # Fold Turkish letters on both sides so "sok" finds "ŞOK"; ILIKE handles ASCII case.
    folded_description = func.translate(Transaction.description, TURKISH_LETTERS, ASCII_LETTERS)
    return folded_description.ilike(f"%{escape_like(fold_turkish(text))}%", escape="\\")


def list_transactions(
    db: Session, user: User, filters: TransactionFilters
) -> tuple[list[Transaction], int, int]:
    """One page of the user's transactions; returns (items, total, pages)."""
    conditions = [Transaction.user_id == user.id]
    if filters.date_from:
        conditions.append(Transaction.date >= filters.date_from)
    if filters.date_to:
        conditions.append(Transaction.date <= filters.date_to)
    if filters.category_id:
        conditions.append(Transaction.category_id.in_(filters.category_id))
    if filters.type:
        conditions.append(Transaction.type == filters.type)
    if filters.q and filters.q.strip():
        conditions.append(_description_contains(filters.q.strip()))

    total = db.scalar(select(func.count()).select_from(Transaction).where(*conditions)) or 0
    items = db.scalars(
        select(Transaction)
        .where(*conditions)
        # id last: rows with equal dates/amounts keep a stable order across pages.
        .order_by(*_SORT_ORDER[filters.sort], Transaction.id)
        .offset((filters.page - 1) * filters.page_size)
        .limit(filters.page_size)
    ).all()
    return list(items), total, math.ceil(total / filters.page_size)
