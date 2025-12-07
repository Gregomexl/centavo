"""Initial schema with User, Transaction, and Category models

Revision ID: 001_initial
Revises: 
Create Date: 2024-12-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
       sa.Column('telegram_id', sa.BigInteger(), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('hashed_password', sa.String(length=512), nullable=True),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('default_currency', sa.String(length=3), server_default='MXN', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id'),
        sa.UniqueConstraint('email'),
    )
    
    # Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('icon', sa.String(length=50), server_default='📦', nullable=False),
        sa.Column('color', sa.String(length=7), server_default='#6366f1', nullable=False),
        sa.Column('type', sa.Enum('EXPENSE', 'INCOME', name='transactiontype'), nullable=False),
        sa.Column('is_system', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'name', 'type', name='uq_user_category_name_type'),
    )
    
    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('category_id', sa.UUID(), nullable=True),
        sa.Column('type', sa.Enum('EXPENSE', 'INCOME', name='transactiontype'), nullable=False),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), server_default='MXN', nullable=False),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('raw_message', sa.Text(), nullable=True),
        sa.Column('transaction_date', sa.Date(), server_default=sa.text('current_date'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create indexes for analytics queries
    op.create_index('idx_user_date', 'transactions', ['user_id', 'transaction_date'])
    op.create_index('idx_user_type_date', 'transactions', ['user_id', 'type', 'transaction_date'])


def downgrade() -> None:
    op.drop_index('idx_user_type_date', table_name='transactions')
    op.drop_index('idx_user_date', table_name='transactions')
    op.drop_table('transactions')
    op.drop_table('categories')
    op.drop_table('users')
    sa.Enum(name='transactiontype').drop(op.get_bind())
