"""Recurring transaction repository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recurring_transaction import RecurringTransaction


class RecurringTransactionRepository:
    """Repository for recurring transaction operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user(self, user_id: uuid.UUID) -> list[RecurringTransaction]:
        """Get all recurring transactions for a user."""
        stmt = (
            select(RecurringTransaction)
            .where(RecurringTransaction.user_id == user_id)
            .order_by(RecurringTransaction.day_of_month.asc(), RecurringTransaction.name.asc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(
        self, recurring_transaction_id: uuid.UUID, user_id: uuid.UUID
    ) -> RecurringTransaction | None:
        """Get a recurring transaction by ID for a specific user."""
        stmt = select(RecurringTransaction).where(
            RecurringTransaction.id == recurring_transaction_id,
            RecurringTransaction.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, recurring_transaction: RecurringTransaction) -> RecurringTransaction:
        """Create a new recurring transaction."""
        self.db.add(recurring_transaction)
        await self.db.commit()
        await self.db.refresh(recurring_transaction)
        return recurring_transaction

    async def update(self, recurring_transaction: RecurringTransaction) -> RecurringTransaction:
        """Update an existing recurring transaction."""
        await self.db.commit()
        await self.db.refresh(recurring_transaction)
        return recurring_transaction

    async def delete(self, recurring_transaction: RecurringTransaction) -> None:
        """Delete a recurring transaction."""
        await self.db.delete(recurring_transaction)
        await self.db.commit()
