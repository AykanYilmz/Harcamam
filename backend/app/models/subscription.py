import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DismissedSubscription(Base):
    """A repeating payment the user said is not a subscription; it is no longer suggested."""

    __tablename__ = "dismissed_subscriptions"
    __table_args__ = (UniqueConstraint("user_id", "merchant_key"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    # The merchant as app.services.merchants names it, normalized: "netflix com".
    merchant_key: Mapped[str] = mapped_column(String(200))
    # As shown when it was dismissed, so the list of hidden payments can name it.
    name: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
