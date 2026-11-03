import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

# Default categories the code refers to by name; all defaults are seeded by migration.
OTHER_CATEGORY = "Diğer"
INCOME_CATEGORY = "Gelir"
# Money moved between the user's own accounts; excluded from income and expense reports.
TRANSFER_CATEGORY = "Transfer"


class Category(Base):
    __tablename__ = "categories"
    # NULLS NOT DISTINCT: two default categories (user_id NULL) can't share a name either.
    __table_args__ = (UniqueConstraint("user_id", "name", postgresql_nulls_not_distinct=True),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    # NULL for default categories shared by every user.
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(50))
    color: Mapped[str] = mapped_column(String(7))
    icon: Mapped[str] = mapped_column(String(50))

    @property
    def is_default(self) -> bool:
        return self.user_id is None


class CategoryRule(Base):
    """A keyword the user taught: descriptions containing it go to `category_id`."""

    __tablename__ = "category_rules"
    __table_args__ = (UniqueConstraint("user_id", "keyword"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    keyword: Mapped[str] = mapped_column(String(100))
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
