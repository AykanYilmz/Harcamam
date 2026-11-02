import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.transaction import Transaction


class Statement(Base):
    __tablename__ = "statements"
    __table_args__ = (UniqueConstraint("user_id", "file_hash"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    file_name: Mapped[str] = mapped_column(String(255))
    bank_name: Mapped[str | None] = mapped_column(String(100))
    # SHA-256 of the uploaded file; the file itself is never stored.
    file_hash: Mapped[str] = mapped_column(String(64))
    period_start: Mapped[date]
    period_end: Mapped[date]
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="statement", cascade="all, delete-orphan", passive_deletes=True
    )
