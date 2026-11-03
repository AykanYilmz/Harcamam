import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CategoryRule, Transaction, User
from app.services.categories import (
    CategoryNotFoundError,
    get_accessible_category,
    save_rule,
    validate_keyword,
)


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
