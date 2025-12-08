"""Authentication endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.core.exceptions import BadRequestException, ConflictException, UnauthorizedException
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.db.session import get_db
from app.repositories.user_repo import UserRepository
from app.schemas.common import MessageResponse
from app.schemas.user import Token, UserCreate, UserLogin, UserRead

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    """Register a new user."""
    user_repo = UserRepository(db)
    
    # Check if user already exists
    if user_data.email:
        existing_user = await user_repo.get_by_email(user_data.email)
        if existing_user:
            raise ConflictException("Email already registered")
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user
    user = await user_repo.create_user(
        email=user_data.email,
        hashed_password=hashed_password,
        display_name=user_data.display_name,
    )
    
    return UserRead.model_validate(user)


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """Login with email and password."""
    user_repo = UserRepository(db)
    
    # Get user by email
    user = await user_repo.get_by_email(credentials.email)
    if not user or not user.hashed_password:
        raise UnauthorizedException("Invalid email or password")
    
    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise UnauthorizedException("Invalid email or password")
    
    if not user.is_active:
        raise UnauthorizedException("User account is inactive")
    
    # Create tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=UserRead)
async def get_current_user_info(current_user: CurrentUser) -> UserRead:
    """Get current user information."""
    return UserRead.model_validate(current_user)


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: CurrentUser) -> MessageResponse:
    """Logout (client should discard tokens)."""
    return MessageResponse(message="Successfully logged out")
