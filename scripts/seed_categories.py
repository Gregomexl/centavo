#!/usr/bin/env python3
"""Seed default categories into the database."""

import asyncio
import uuid

from sqlalchemy import select

from app.core.constants import DEFAULT_EXPENSE_CATEGORIES, DEFAULT_INCOME_CATEGORIES
from app.db.session import async_session_maker
from app.models.category import Category
from app.models.transaction import TransactionType


async def seed_categories():
    """Seed default system categories."""
    async with async_session_maker() as session:
        # Check if system categories already exist
        result = await session.execute(
            select(Category).where(Category.is_system == True).limit(1)  # noqa: E712
        )
        if result.scalar_one_or_none():
            print("System categories already exist, skipping...")
            return
        
        print("Seeding default categories...")
        
        # Add expense categories
        for name, icon, color in DEFAULT_EXPENSE_CATEGORIES:
            category = Category(
                id=uuid.uuid4(),
                user_id=None,
                name=name,
                icon=icon,
                color=color,
                type=TransactionType.EXPENSE,
                is_system=True,
            )
            session.add(category)
            print(f"  ✅ Added expense category: {icon} {name}")
        
        # Add income categories
        for name, icon, color in DEFAULT_INCOME_CATEGORIES:
            category = Category(
                id=uuid.uuid4(),
                user_id=None,
                name=name,
                icon=icon,
                color=color,
                type=TransactionType.INCOME,
                is_system=True,
            )
            session.add(category)
            print(f"  ✅ Added income category: {icon} {name}")
        
        await session.commit()
        print(f"\n✅ Successfully seeded {len(DEFAULT_EXPENSE_CATEGORIES)} expense and {len(DEFAULT_INCOME_CATEGORIES)} income categories!")


if __name__ == "__main__":
    asyncio.run(seed_categories())
