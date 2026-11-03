"""add category kind

Revision ID: cec6882af8b1
Revises: 206fb9cd211d
Create Date: 2026-11-03 11:08:26.639682

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cec6882af8b1"
down_revision: str | Sequence[str] | None = "206fb9cd211d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "categories",
        sa.Column(
            "kind",
            sa.Enum(
                "income",
                "expense",
                "transfer",
                name="category_kind",
                native_enum=False,
                create_constraint=True,
                length=10,
            ),
            server_default="expense",
            nullable=False,
        ),
    )
    # Existing user categories keep behaving as spending, which is what reports assumed so far.
    op.execute("UPDATE categories SET kind = 'income' WHERE user_id IS NULL AND name = 'Gelir'")
    op.execute(
        "UPDATE categories SET kind = 'transfer' WHERE user_id IS NULL AND name = 'Transfer'"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("categories", "kind")
