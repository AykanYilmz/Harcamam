from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Statement, Transaction, TransactionType, User


def make_statement(user: User, file_hash: str = "a" * 64) -> Statement:
    return Statement(
        user_id=user.id,
        file_name="ekstre.csv",
        file_hash=file_hash,
        period_start=date(2026, 9, 1),
        period_end=date(2026, 9, 30),
    )


def make_transaction(statement: Statement, fingerprint: str = "f" * 64) -> Transaction:
    return Transaction(
        user_id=statement.user_id,
        date=date(2026, 9, 5),
        description="MIGROS",
        amount=Decimal("123.45"),
        type=TransactionType.EXPENSE,
        fingerprint=fingerprint,
    )


def test_statement_with_transactions_is_saved(db: Session, user: User) -> None:
    statement = make_statement(user)
    statement.transactions.append(make_transaction(statement))
    db.add(statement)
    db.flush()
    db.expire_all()

    saved = db.scalars(select(Transaction)).one()
    assert saved.amount == Decimal("123.45")
    assert saved.type is TransactionType.EXPENSE
    assert saved.statement.file_name == "ekstre.csv"


def test_same_file_hash_cannot_be_saved_twice_for_a_user(db: Session, user: User) -> None:
    db.add(make_statement(user))
    db.flush()

    db.add(make_statement(user))
    with pytest.raises(IntegrityError):
        db.flush()


def test_same_fingerprint_cannot_be_saved_twice_for_a_user(db: Session, user: User) -> None:
    first = make_statement(user, file_hash="a" * 64)
    second = make_statement(user, file_hash="b" * 64)
    first.transactions.append(make_transaction(first))
    second.transactions.append(make_transaction(second))
    db.add_all([first, second])

    with pytest.raises(IntegrityError):
        db.flush()


def test_deleting_statement_deletes_its_transactions(db: Session, user: User) -> None:
    statement = make_statement(user)
    statement.transactions.append(make_transaction(statement))
    db.add(statement)
    db.flush()

    db.delete(statement)
    db.flush()

    assert db.scalar(select(func.count()).select_from(Transaction)) == 0
