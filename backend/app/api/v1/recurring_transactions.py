"""Recurring transactions API endpoints."""

import uuid
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db
from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.recurring_transaction import RecurringTransaction
from app.models.transaction import Transaction
from app.repositories.recurring_transaction_repo import RecurringTransactionRepository
from app.repositories.transaction_repo import TransactionRepository
from app.schemas.recurring_transaction import (
    RecurringTransactionCreate,
    RecurringTransactionRead,
    RecurringTransactionUpdate,
)
from app.schemas.transaction import TransactionRead

router = APIRouter(prefix="/recurring-transactions", tags=["recurring-transactions"])


@router.get("", response_model=list[RecurringTransactionRead])
async def list_recurring_transactions(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> list[RecurringTransactionRead]:
    """List all recurring transactions for the current user."""
    repo = RecurringTransactionRepository(db)
    recurring_transactions = await repo.get_by_user(current_user.id)
    return [RecurringTransactionRead.model_validate(rt) for rt in recurring_transactions]


@router.post("", response_model=RecurringTransactionRead, status_code=201)
async def create_recurring_transaction(
    data: RecurringTransactionCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> RecurringTransactionRead:
    """Create a new recurring transaction."""
    repo = RecurringTransactionRepository(db)
    
    recurring_transaction = RecurringTransaction(
        user_id=current_user.id,
        **data.model_dump(),
    )
    
    recurring_transaction = await repo.create(recurring_transaction)
    return RecurringTransactionRead.model_validate(recurring_transaction)


@router.get("/{recurring_transaction_id}", response_model=RecurringTransactionRead)
async def get_recurring_transaction(
    recurring_transaction_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> RecurringTransactionRead:
    """Get a specific recurring transaction."""
    repo = RecurringTransactionRepository(db)
    recurring_transaction = await repo.get_by_id(recurring_transaction_id, current_user.id)
    
    if not recurring_transaction:
        raise NotFoundException("Recurring transaction not found")
    
    return RecurringTransactionRead.model_validate(recurring_transaction)


@router.put("/{recurring_transaction_id}", response_model=RecurringTransactionRead)
async def update_recurring_transaction(
    recurring_transaction_id: uuid.UUID,
    data: RecurringTransactionUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> RecurringTransactionRead:
    """Update a recurring transaction."""
    repo = RecurringTransactionRepository(db)
    recurring_transaction = await repo.get_by_id(recurring_transaction_id, current_user.id)
    
    if not recurring_transaction:
        raise NotFoundException("Recurring transaction not found")
    
    if recurring_transaction.user_id != current_user.id:
        raise ForbiddenException("Cannot modify other users' recurring transactions")
    
    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(recurring_transaction, field, value)
    
    recurring_transaction = await repo.update(recurring_transaction)
    return RecurringTransactionRead.model_validate(recurring_transaction)


@router.delete("/{recurring_transaction_id}", status_code=204)
async def delete_recurring_transaction(
    recurring_transaction_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a recurring transaction."""
    repo = RecurringTransactionRepository(db)
    recurring_transaction = await repo.get_by_id(recurring_transaction_id, current_user.id)
    
    if not recurring_transaction:
        raise NotFoundException("Recurring transaction not found")
    
    if recurring_transaction.user_id != current_user.id:
        raise ForbiddenException("Cannot delete other users' recurring transactions")
    
    await repo.delete(recurring_transaction)


@router.post("/{recurring_transaction_id}/pay", response_model=TransactionRead, status_code=201)
async def pay_recurring_transaction(
    recurring_transaction_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TransactionRead:
    """Create a transaction from a recurring transaction (pay a bill)."""
    rt_repo = RecurringTransactionRepository(db)
    recurring_transaction = await rt_repo.get_by_id(recurring_transaction_id, current_user.id)
    
    if not recurring_transaction:
        raise NotFoundException("Recurring transaction not found")
    
    if not recurring_transaction.is_active:
        raise ForbiddenException("Cannot pay an inactive recurring transaction")
    
    # Create transaction from recurring transaction
    transaction = Transaction(
        user_id=current_user.id,
        category_id=recurring_transaction.category_id,
        type=recurring_transaction.type,
        amount=recurring_transaction.amount,
        currency=recurring_transaction.currency,
        description=recurring_transaction.name,
        transaction_date=date.today(),
    )
    
    transaction_repo = TransactionRepository(db)
    transaction = await transaction_repo.create_transaction(transaction)
    
    return TransactionRead.model_validate(transaction)
