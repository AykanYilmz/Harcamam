from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import OTHER_CATEGORY, Category, Statement, Transaction, TransactionType, User
from app.services.categories import get_default_category


def make_statement(user: User, file_hash: str = "a" * 64) -> Statement:
    return Statement(
        user_id=user.id,
        file_name="ekstre.csv",
        file_hash=file_hash,
        period_start=date(2026, 9, 1),
        period_end=date(2026, 9, 30),
    )


def make_transaction(db: Session, statement: Statement, fingerprint: str = "f" * 64) -> Transaction:
    return Transaction(
        category_id=get_default_category(db, OTHER_CATEGORY).id,
        user_id=statement.user_id,
        date=date(2026, 9, 5),
        description="MIGROS",
        amount=Decimal("123.45"),
        type=TransactionType.EXPENSE,
        fingerprint=fingerprint,
    )


def test_statement_with_transactions_is_saved(db: Session, user: User) -> None:
    statement = make_statement(user)
    statement.transactions.append(make_transaction(db, statement))
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
    first.transactions.append(make_transaction(db, first))
    second.transactions.append(make_transaction(db, second))
    db.add_all([first, second])

    with pytest.raises(IntegrityError):
        db.flush()


def test_deleting_statement_deletes_its_transactions(db: Session, user: User) -> None:
    statement = make_statement(user)
    statement.transactions.append(make_transaction(db, statement))
    db.add(statement)
    db.flush()

    db.delete(statement)
    db.flush()

    assert db.scalar(select(func.count()).select_from(Transaction)) == 0


def test_default_categories_are_seeded(db: Session) -> None:
    names = set(db.scalars(select(Category.name).where(Category.user_id.is_(None))))

    assert names == {
        "Market",
        "Yemek",
        "Ulaşım",
        "Faturalar",
        "Kira",
        "Eğlence",
        "Sağlık",
        "Giyim",
        "Alışveriş",
        "Abonelikler",
        "Nakit Çekim",
        "Transfer",
        "Gelir",
        "Diğer",
    }


def test_default_category_names_are_unique(db: Session) -> None:
    db.add(Category(name="Market", color="#000000", icon="x"))

    with pytest.raises(IntegrityError):
        db.flush()


def test_users_can_reuse_names_across_accounts(db: Session, user: User) -> None:
    other = User(email="baska@example.com", password_hash="x")
    db.add(other)
    db.flush()

    db.add_all(
        [
            Category(user_id=user.id, name="Hobi", color="#000000", icon="x"),
            Category(user_id=other.id, name="Hobi", color="#000000", icon="x"),
        ]
    )
    db.flush()
