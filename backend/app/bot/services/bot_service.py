"""Bot service for backend API integration."""

import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.transaction import Transaction, TransactionType
from app.models.user import User
from app.repositories.category_repo import CategoryRepository
from app.repositories.transaction_repo import TransactionRepository
from app.repositories.user_repo import UserRepository


class BotService:
    """Service for bot operations with backend."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.transaction_repo = TransactionRepository(db)
        self.category_repo = CategoryRepository(db)

    async def get_or_create_user(
        self, telegram_id: int, username: str | None, first_name: str | None
    ) -> User:
        """Get or create user by Telegram ID."""
        # Try to get existing user
        user = await self.user_repo.get_by_telegram_id(telegram_id)
        
        if user:
            return user
        
        # Create new user
        display_name = first_name or username or f"User{telegram_id}"
        user = await self.user_repo.create_user(
            email=None,
            hashed_password=None,
            display_name=display_name,
            telegram_id=telegram_id,
        )
        
        await self.db.commit()
        return user

    async def create_transaction(
        self,
        user_id: uuid.UUID,
        transaction_type: TransactionType,
        amount: Decimal,
        description: str,
        category_id: uuid.UUID | None = None,
        raw_message: str | None = None,
    ) -> Transaction:
        """Create a transaction."""
        transaction = await self.transaction_repo.create_transaction(
            user_id=user_id,
            transaction_type=transaction_type,
            amount=float(amount),
            currency="MXN",
            description=description,
            category_id=category_id,
            transaction_date=date.today(),
            raw_message=raw_message,
        )
        
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction

    async def get_categories(
        self, user_id: uuid.UUID, transaction_type: TransactionType | None = None
    ) -> list[Category]:
        """Get categories for user."""
        return await self.category_repo.get_user_categories(user_id, transaction_type)

    async def get_month_summary(self, user_id: uuid.UUID) -> dict:
        """Get current month summary."""
        # Get start of current month
        now = datetime.now()
        start_of_month = date(now.year, now.month, 1)
        
        # Get transactions for this month
        transactions = await self.transaction_repo.get_by_user(
            user_id=user_id,
            start_date=start_of_month,
            skip=0,
            limit=1000,
        )
        
        # Calculate totals
        total_expenses = Decimal(0)
        total_income = Decimal(0)
        
        for t in transactions:
            if t.type == TransactionType.EXPENSE:
                total_expenses += Decimal(str(t.amount))
            elif t.type == TransactionType.INCOME:
                total_income += Decimal(str(t.amount))
        
        # Get category breakdown for expenses
        expense_by_category = {}
        for t in transactions:
            if t.type == TransactionType.EXPENSE and t.category:
                cat_name = t.category.name
                expense_by_category[cat_name] = (
                    expense_by_category.get(cat_name, Decimal(0)) + Decimal(str(t.amount))
                )
        
        # Sort by amount
        top_categories = sorted(
            expense_by_category.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:5]
        
        return {
            "total_expenses": float(total_expenses),
            "total_income": float(total_income),
            "balance": float(total_income - total_expenses),
            "transaction_count": len(transactions),
            "top_categories": [(name, float(amt)) for name, amt in top_categories],
            "period": f"{now.strftime('%B %Y')}",
        }

    async def get_recent_transactions(
        self, user_id: uuid.UUID, limit: int = 5
    ) -> list[Transaction]:
        """Get recent transactions."""
        return await self.transaction_repo.get_by_user(
            user_id=user_id,
            skip=0,
            limit=limit,
        )

    async def find_category_by_keyword(
        self, user_id: uuid.UUID, keyword: str, transaction_type: TransactionType
    ) -> Category | None:
        """Find category by keyword match."""
        categories = await self.category_repo.get_user_categories(
            user_id, transaction_type
        )
        
        keyword_lower = keyword.lower()
        
        # First try exact name match
        for cat in categories:
            if cat.name.lower() == keyword_lower:
                return cat
        
        # Then try partial match
        for cat in categories:
            if keyword_lower in cat.name.lower():
                return cat
        
        return None
