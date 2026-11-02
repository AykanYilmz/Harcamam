import datetime as dt
import enum
import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.statement import Statement


class TransactionType(enum.StrEnum):
    INCOME = "income"
    EXPENSE = "expense"


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        # Re-importing an overlapping statement must not create the same transaction twice.
        UniqueConstraint("user_id", "fingerprint"),
        Index("ix_transactions_user_id_date", "user_id", "date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    statement_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("statements.id", ondelete="CASCADE"), index=True
    )
    date: Mapped[dt.date] = mapped_column(Date)
    description: Mapped[str] = mapped_column(String(500))
    # Always positive; the direction is stored in `type`.
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    type: Mapped[TransactionType] = mapped_column(
        Enum(
            TransactionType,
            name="transaction_type",
            native_enum=False,
            create_constraint=True,
            length=10,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        )
    )
    fingerprint: Mapped[str] = mapped_column(String(64))

    statement: Mapped["Statement"] = relationship(back_populates="transactions")
