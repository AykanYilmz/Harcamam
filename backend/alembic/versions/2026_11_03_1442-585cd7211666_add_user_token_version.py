"""add user token version

Revision ID: 585cd7211666
Revises: cec6882af8b1
Create Date: 2026-11-03 14:42:13.503000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "585cd7211666"
down_revision: str | Sequence[str] | None = "cec6882af8b1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users", sa.Column("token_version", sa.Integer(), server_default="0", nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "token_version")
