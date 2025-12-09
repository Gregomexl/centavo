"""Category repository."""

import uuid

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.transaction import TransactionType
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """Category-specific repository."""

    def __init__(self, db: AsyncSession):
        super().__init__(db, Category)

    async def get_user_categories(
        self,
        user_id: uuid.UUID,
        transaction_type: TransactionType | None = None,
    ) -> list[Category]:
        """Get all categories for a user (including system categories)."""
        query = select(Category).where(
            or_(
                Category.user_id == user_id,
                Category.is_system == True,  # noqa: E712
            )
        )
        
        if transaction_type:
            query = query.where(Category.type == transaction_type)
        
        query = query.order_by(Category.is_system.desc(), Category.name)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_user_category(
        self, category_id: uuid.UUID, user_id: uuid.UUID
    ) -> Category | None:
        """Get a category only if it's system or belongs to the user."""
        result = await self.db.execute(
            select(Category).where(
                and_(
                    Category.id == category_id,
                    or_(
                        Category.user_id == user_id,
                        Category.is_system == True,  # noqa: E712
                    ),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_name(
        self, name: str, user_id: uuid.UUID, transaction_type: TransactionType
    ) -> Category | None:
        """Get category by name for a user and type."""
        result = await self.db.execute(
            select(Category).where(
                and_(
                    Category.user_id == user_id,
                    Category.name == name,
                    Category.type == transaction_type,
                )
            )
        )
        return result.scalar_one_or_none()

    async def create_category(
        self,
        user_id: uuid.UUID | None,
        name: str,
        icon: str,
        color: str,
        transaction_type: TransactionType,
        is_system: bool = False,
    ) -> Category:
        """Create a new category."""
        category = Category(
            user_id=user_id,
            name=name,
            icon=icon,
            color=color,
            type=transaction_type,
            is_system=is_system,
        )
        return await self.create(category)

    async def delete_user_category(
        self, category_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        """Delete a user's category (not system categories)."""
        result = await self.db.execute(
            select(Category).where(
                and_(
                    Category.id == category_id,
                    Category.user_id == user_id,
                    Category.is_system == False,  # noqa: E712
                )
            )
        )
        category = result.scalar_one_or_none()
        
        if not category:
            return False
        
        await self.delete(category)
        return True
