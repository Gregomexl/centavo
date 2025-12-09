"""Transaction repository."""

import uuid
from datetime import date

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.transaction import Transaction, TransactionType
from app.repositories.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    """Transaction-specific repository."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Transaction)

    async def get_by_user(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        transaction_type: TransactionType | None = None,
        category_id: uuid.UUID | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Transaction]:
        """Get transactions for a user with filters."""
        query = select(Transaction).where(Transaction.user_id == user_id)
        
        # Apply filters
        if transaction_type:
            query = query.where(Transaction.type == transaction_type)
        if category_id:
            query = query.where(Transaction.category_id == category_id)
        if start_date:
            query = query.where(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.where(Transaction.transaction_date <= end_date)
        
        # Eager load category relationship
        query = query.options(selectinload(Transaction.category))
        
        # Order by most recent first
        query = query.order_by(Transaction.transaction_date.desc())
        
        # Pagination
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_by_user(
        self,
        user_id: uuid.UUID,
        transaction_type: TransactionType | None = None,
        category_id: uuid.UUID | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> int:
        """Count transactions for a user with filters."""
        query = select(func.count(Transaction.id)).where(Transaction.user_id == user_id)
        
        # Apply same filters
        if transaction_type:
            query = query.where(Transaction.type == transaction_type)
        if category_id:
            query = query.where(Transaction.category_id == category_id)
        if start_date:
            query = query.where(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.where(Transaction.transaction_date <= end_date)
        
        result = await self.db.execute(query)
        return result.scalar_one()

    async def get_user_transaction(
        self, transaction_id: uuid.UUID, user_id: uuid.UUID
    ) -> Transaction | None:
        """Get a transaction only if it belongs to the user."""
        result = await self.db.execute(
            select(Transaction)
            .options(selectinload(Transaction.category))
            .where(
                and_(
                    Transaction.id == transaction_id,
                    Transaction.user_id == user_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def create_transaction(
        self,
        user_id: uuid.UUID,
        transaction_type: TransactionType,
        amount: float,
        currency: str,
        description: str,
        category_id: uuid.UUID | None = None,
        transaction_date: date | None = None,
        raw_message: str | None = None,
    ) -> Transaction:
        """Create a new transaction."""
        transaction = Transaction(
            user_id=user_id,
            type=transaction_type,
            amount=amount,
            currency=currency,
            description=description,
            category_id=category_id,
            transaction_date=transaction_date or date.today(),
            raw_message=raw_message,
        )
        return await self.create(transaction)
