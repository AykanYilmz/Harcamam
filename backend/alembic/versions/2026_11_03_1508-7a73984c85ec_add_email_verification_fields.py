"""add email verification fields

Revision ID: 7a73984c85ec
Revises: 585cd7211666
Create Date: 2026-11-03 15:08:18.039365

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7a73984c85ec"
down_revision: str | Sequence[str] | None = "585cd7211666"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users", sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column("users", sa.Column("pending_email", sa.String(length=320), nullable=True))
    op.add_column(
        "users", sa.Column("verification_sent_at", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "verification_sent_at")
    op.drop_column("users", "pending_email")
    op.drop_column("users", "email_verified_at")
