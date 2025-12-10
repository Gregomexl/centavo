"""Add recurring_transactions table.

Revision ID: 003
Revises: 002
Create Date: 2025-12-10

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002_category_budget"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add recurring_transactions table."""
    op.create_table(
        "recurring_transactions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="MXN"),
        sa.Column("category_id", sa.UUID(), nullable=True),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("frequency", sa.String(), nullable=False, server_default="monthly"),
        sa.Column("day_of_month", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Create indexes
    op.create_index(
        "ix_recurring_transactions_user_id",
        "recurring_transactions",
        ["user_id"],
    )
    op.create_index(
        "ix_recurring_transactions_category_id",
        "recurring_transactions",
        ["category_id"],
    )


def downgrade() -> None:
    """Remove recurring_transactions table."""
    op.drop_index("ix_recurring_transactions_category_id", table_name="recurring_transactions")
    op.drop_index("ix_recurring_transactions_user_id", table_name="recurring_transactions")
    op.drop_table("recurring_transactions")
