"""Transaction endpoints."""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.core.exceptions import ForbiddenException, NotFoundException
from app.db.session import get_db
from app.models.transaction import TransactionType
from app.repositories.transaction_repo import TransactionRepository
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TransactionRead:
    """Create a new transaction."""
    transaction_repo = TransactionRepository(db)
    
    transaction = await transaction_repo.create_transaction(
        user_id=current_user.id,
        transaction_type=transaction_data.type,
        amount=float(transaction_data.amount),
        currency=transaction_data.currency,
        description=transaction_data.description,
        category_id=transaction_data.category_id,
        transaction_date=transaction_data.transaction_date,
        raw_message=transaction_data.raw_message,
    )
    
    return TransactionRead.model_validate(transaction)


@router.get("", response_model=PaginatedResponse[TransactionRead])
async def list_transactions(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    type: TransactionType | None = None,
    category_id: uuid.UUID | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> PaginatedResponse[TransactionRead]:
    """List transactions with filters and pagination."""
    transaction_repo = TransactionRepository(db)
    
    # Calculate skip
    skip = (page - 1) * page_size
    
    # Get transactions
    transactions = await transaction_repo.get_by_user(
        user_id=current_user.id,
        skip=skip,
        limit=page_size,
        transaction_type=type,
        category_id=category_id,
        start_date=start_date,
        end_date=end_date,
    )
    
    # Get total count
    total = await transaction_repo.count_by_user(
        user_id=current_user.id,
        transaction_type=type,
        category_id=category_id,
        start_date=start_date,
        end_date=end_date,
    )
    
    # Calculate total pages
    total_pages = (total + page_size - 1) // page_size
    
    return PaginatedResponse(
        items=[TransactionRead.model_validate(t) for t in transactions],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{transaction_id}", response_model=TransactionRead)
async def get_transaction(
    transaction_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TransactionRead:
    """Get a single transaction by ID."""
    transaction_repo = TransactionRepository(db)
    
    transaction = await transaction_repo.get_user_transaction(transaction_id, current_user.id)
    if not transaction:
        raise NotFoundException("Transaction not found")
    
    return TransactionRead.model_validate(transaction)


@router.put("/{transaction_id}", response_model=TransactionRead)
async def update_transaction(
    transaction_id: uuid.UUID,
    transaction_data: TransactionUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TransactionRead:
    """Update a transaction."""
    transaction_repo = TransactionRepository(db)
    
    # Get transaction
    transaction = await transaction_repo.get_user_transaction(transaction_id, current_user.id)
    if not transaction:
        raise NotFoundException("Transaction not found")
    
    # Update fields
    update_data = transaction_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)
    
    # Save
    transaction = await transaction_repo.update(transaction)
    
    return TransactionRead.model_validate(transaction)


@router.delete("/{transaction_id}", response_model=MessageResponse)
async def delete_transaction(
    transaction_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Delete a transaction."""
    transaction_repo = TransactionRepository(db)
    
    # Get transaction
    transaction = await transaction_repo.get_user_transaction(transaction_id, current_user.id)
    if not transaction:
        raise NotFoundException("Transaction not found")
    
    # Delete
    await transaction_repo.delete(transaction)
    
    return MessageResponse(message="Transaction deleted successfully")
