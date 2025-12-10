"""Add monthly_limit to categories

Revision ID: 002_category_budget
Revises: 001_initial
Create Date: 2025-12-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_category_budget'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add monthly_limit column to categories table
    op.add_column('categories',
        sa.Column('monthly_limit', sa.Numeric(precision=12, scale=2), nullable=True)
    )


def downgrade() -> None:
    # Remove monthly_limit column from categories table
    op.drop_column('categories', 'monthly_limit')
