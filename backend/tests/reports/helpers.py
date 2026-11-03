import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Category, Statement, Transaction, TransactionType, User


def add_transactions(db: Session, user: User, rows: list[tuple[date, str, str, str]]) -> None:
    """Insert (date, description, signed amount, category name) rows for `user`."""
    statement = Statement(
        user_id=user.id,
        file_name="test.csv",
        file_hash=uuid.uuid4().hex,
        period_start=min(row[0] for row in rows),
        period_end=max(row[0] for row in rows),
    )
    db.add(statement)
    db.flush()
    for day, description, amount, category_name in rows:
        signed = Decimal(amount)
        db.add(
            Transaction(
                user_id=user.id,
                statement_id=statement.id,
                date=day,
                description=description,
                amount=abs(signed),
                type=TransactionType.INCOME if signed > 0 else TransactionType.EXPENSE,
                fingerprint=uuid.uuid4().hex,
                category_id=db.scalar(select(Category.id).where(Category.name == category_name)),
            )
        )
    db.flush()
