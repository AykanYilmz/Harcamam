import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, SmallInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # Copied into every token; bumping it (e.g. on a password change) invalidates all of them.
    token_version: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # A requested new address; it replaces `email` once its verification link is opened.
    pending_email: Mapped[str | None] = mapped_column(String(320))
    verification_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # Statement closing day that reports split months on; None means calendar months.
    period_end_day: Mapped[int | None] = mapped_column(SmallInteger)

    __table_args__ = (
        CheckConstraint("period_end_day BETWEEN 1 AND 31", name="users_period_end_day_check"),
    )

    @property
    def email_verified(self) -> bool:
        return self.email_verified_at is not None
