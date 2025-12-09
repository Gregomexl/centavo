"""User service for business logic."""
import random
import string
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.core.redis import get_redis_client
from app.repositories.user_repo import UserRepository
from app.repositories.transaction_repo import TransactionRepository

LINK_CODE_PREFIX = "link_code:"
LINK_CODE_EXPIRE_SECONDS = 300  # 5 minutes


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.transaction_repo = TransactionRepository(db)

    async def generate_link_code(self, user_id: uuid.UUID) -> str:
        """Generate a short-lived code to link Telegram account."""
        code = "".join(random.choices(string.digits, k=6))
        redis = await get_redis_client()
        
        # Store code -> user_id
        await redis.set(f"{LINK_CODE_PREFIX}{code}", str(user_id), ex=LINK_CODE_EXPIRE_SECONDS)
        
        return code

    async def link_telegram_account(self, code: str, telegram_id: int) -> bool:
        """Link a Telegram ID to a web user account using a code.
        
        If the telegram_id is already associated with 'bot-only' user (no email),
        we should migrate those transactions to the web user and delete the bot user.
        """
        redis = await get_redis_client()
        user_id_str = await redis.get(f"{LINK_CODE_PREFIX}{code}")
        
        if not user_id_str:
            return False
            
        user_id = uuid.UUID(user_id_str)
        web_user = await self.user_repo.get_by_id(user_id)
        
        if not web_user:
            return False
            
        # Check if there is an existing user with this telegram_id
        existing_bot_user = await self.user_repo.get_by_telegram_id(telegram_id)
        
        if existing_bot_user:
            if existing_bot_user.id == web_user.id:
                # Already linked to this user
                return True
                
            # If the bot user is different, we need to merge/migrate
            # Move all transactions to the web user
             # We need to manually update transactions since repo might not have bulk update for this specific case easily accessible
            from app.models.transaction import Transaction
            from sqlalchemy import update, delete
            
            # Move transactions
            await self.db.execute(
                update(Transaction)
                .where(Transaction.user_id == existing_bot_user.id)
                .values(user_id=web_user.id)
            )
            
            # Delete the old bot user
            # Note: We might need to handle other relations like Categories. 
            # For simplicity, let's assume we keep Web User categories. 
            # If Bot User had custom categories, we should probably migrate them too or they will be orphaned/deleted.
            # Let's delete the bot user. Cascade should handle orphans if configured, but let's be careful.
            
            # Update categories to new user
            from app.models.category import Category
            await self.db.execute(
                update(Category)
                .where(Category.user_id == existing_bot_user.id)
                .values(user_id=web_user.id)
            )
            
            await self.db.execute(
                delete(existing_bot_user.__class__)
                .where(existing_bot_user.__class__.id == existing_bot_user.id)
            )

        # Update the web user with the telegram_id
        web_user.telegram_id = telegram_id
        await self.db.commit()
        
        # Invalidate code
        await redis.delete(f"{LINK_CODE_PREFIX}{code}")
        
        return True
