"""Category endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.db.session import get_db
from app.models.transaction import TransactionType
from app.repositories.category_repo import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryRead])
async def list_categories(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    type: TransactionType | None = None,
) -> list[CategoryRead]:
    """List all categories (system + user's custom)."""
    category_repo = CategoryRepository(db)
    
    categories = await category_repo.get_user_categories(
        user_id=current_user.id,
        transaction_type=type,
    )
    
    return [CategoryRead.model_validate(c) for c in categories]


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> CategoryRead:
    """Create a custom category."""
    category_repo = CategoryRepository(db)
    
    # Check if category name already exists for this user and type
    existing = await category_repo.get_by_name(
        name=category_data.name,
        user_id=current_user.id,
        transaction_type=category_data.type,
    )
    
    if existing:
        raise BadRequestException(
            f"Category '{category_data.name}' already exists for {category_data.type.value}"
        )
    
    category = await category_repo.create_category(
        user_id=current_user.id,
        name=category_data.name,
        icon=category_data.icon,
        color=category_data.color,
        transaction_type=category_data.type,
        is_system=False,
    )
    
    return CategoryRead.model_validate(category)


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(
    category_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> CategoryRead:
    """Get a single category."""
    category_repo = CategoryRepository(db)
    
    category = await category_repo.get_user_category(category_id, current_user.id)
    if not category:
        raise NotFoundException("Category not found")
    
    return CategoryRead.model_validate(category)


@router.put("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: uuid.UUID,
    category_data: CategoryUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> CategoryRead:
    """Update a custom category (system categories can only update monthly_limit)."""
    category_repo = CategoryRepository(db)
    
    # Get category
    category = await category_repo.get_user_category(category_id, current_user.id)
    if not category:
        raise NotFoundException("Category not found")
    
    # Parse update data
    update_data = category_data.model_dump(exclude_unset=True)
    
    # If system category, only allow monthly_limit updates
    if category.is_system:
        # Only monthly_limit can be updated for system categories
        if any(key != 'monthly_limit' for key in update_data.keys()):
            raise ForbiddenException("System categories can only update monthly_limit")
    else:
        # Cannot update if not owner (for custom categories)
        if category.user_id != current_user.id:
            raise ForbiddenException("Cannot modify other users' categories")
    
    # Update fields
    for field, value in update_data.items():
        setattr(category, field, value)
    
    # Save
    category = await category_repo.update(category)
    
    return CategoryRead.model_validate(category)


@router.delete("/{category_id}", response_model=MessageResponse)
async def delete_category(
    category_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Delete a custom category (system categories cannot be deleted)."""
    category_repo = CategoryRepository(db)
    
    deleted = await category_repo.delete_user_category(category_id, current_user.id)
    
    if not deleted:
        raise NotFoundException("Category not found or cannot be deleted")
    
    return MessageResponse(message="Category deleted successfully")
