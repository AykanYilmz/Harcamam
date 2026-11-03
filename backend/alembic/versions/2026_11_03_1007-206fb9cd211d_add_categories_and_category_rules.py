"""add categories and category rules

Revision ID: 206fb9cd211d
Revises: d85457e65fd2
Create Date: 2026-11-03 10:07:38.095304

"""

import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "206fb9cd211d"
down_revision: str | Sequence[str] | None = "d85457e65fd2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Snapshot of the default categories at this revision. Migrations must not import app code,
# because the app will keep changing while this file has to keep producing the same result.
DEFAULT_CATEGORIES = [
    ("Market", "#22c55e", "shopping-cart"),
    ("Yemek", "#f97316", "utensils"),
    ("Ulaşım", "#3b82f6", "car"),
    ("Faturalar", "#eab308", "receipt"),
    ("Kira", "#a855f7", "home"),
    ("Eğlence", "#ec4899", "film"),
    ("Sağlık", "#ef4444", "heart-pulse"),
    ("Giyim", "#14b8a6", "shirt"),
    ("Alışveriş", "#f43f5e", "shopping-bag"),
    ("Abonelikler", "#6366f1", "repeat"),
    ("Nakit Çekim", "#84cc16", "banknote"),
    ("Transfer", "#64748b", "arrow-left-right"),
    ("Gelir", "#10b981", "wallet"),
    ("Diğer", "#94a3b8", "circle-ellipsis"),
]


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "categories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("color", sa.String(length=7), nullable=False),
        sa.Column("icon", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("categories_user_id_fkey"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("categories_pkey")),
        sa.UniqueConstraint(
            "user_id",
            "name",
            name=op.f("categories_user_id_name_key"),
            postgresql_nulls_not_distinct=True,
        ),
    )
    op.create_index(op.f("ix_categories_user_id"), "categories", ["user_id"], unique=False)
    op.create_table(
        "category_rules",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("keyword", sa.String(length=100), nullable=False),
        sa.Column("category_id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            name=op.f("category_rules_category_id_fkey"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("category_rules_user_id_fkey"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("category_rules_pkey")),
        sa.UniqueConstraint("user_id", "keyword", name=op.f("category_rules_user_id_keyword_key")),
    )
    op.create_index(op.f("ix_category_rules_user_id"), "category_rules", ["user_id"], unique=False)

    categories = sa.table(
        "categories",
        sa.column("id", sa.Uuid()),
        sa.column("name", sa.String()),
        sa.column("color", sa.String()),
        sa.column("icon", sa.String()),
    )
    op.bulk_insert(
        categories,
        [
            {"id": uuid.uuid4(), "name": name, "color": color, "icon": icon}
            for name, color, icon in DEFAULT_CATEGORIES
        ],
    )

    # Existing transactions go to "Diğer" so the column can be NOT NULL from the start.
    op.add_column("transactions", sa.Column("category_id", sa.Uuid(), nullable=True))
    op.execute(
        "UPDATE transactions SET category_id = "
        "(SELECT id FROM categories WHERE user_id IS NULL AND name = 'Diğer')"
    )
    op.alter_column("transactions", "category_id", nullable=False)
    op.add_column(
        "transactions",
        sa.Column(
            "is_manually_categorized", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
    )
    op.create_index(
        op.f("ix_transactions_category_id"), "transactions", ["category_id"], unique=False
    )
    op.create_foreign_key(
        op.f("transactions_category_id_fkey"),
        "transactions",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f("transactions_category_id_fkey"), "transactions", type_="foreignkey")
    op.drop_index(op.f("ix_transactions_category_id"), table_name="transactions")
    op.drop_column("transactions", "is_manually_categorized")
    op.drop_column("transactions", "category_id")
    op.drop_index(op.f("ix_category_rules_user_id"), table_name="category_rules")
    op.drop_table("category_rules")
    op.drop_index(op.f("ix_categories_user_id"), table_name="categories")
    op.drop_table("categories")
