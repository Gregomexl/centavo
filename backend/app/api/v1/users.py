"""Users API router."""
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.services.user_service import UserService

router = APIRouter()


@router.post("/link/code")
async def generate_link_code(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Generate a code to link Telegram account."""
    user_service = UserService(db)
    code = await user_service.generate_link_code(current_user.id)
    return {"code": code}
