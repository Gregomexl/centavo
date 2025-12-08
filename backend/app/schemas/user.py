"""User Pydantic schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr | None = None
    display_name: str = Field(..., min_length=1, max_length=100)
    default_currency: str = Field(default="MXN", min_length=3, max_length=3)


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserRead(UserBase):
    """Schema for reading a user."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    telegram_id: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: EmailStr | None = None
    display_name: str | None = Field(None, min_length=1, max_length=100)
    default_currency: str | None = Field(None, min_length=3, max_length=3)


class Token(BaseModel):
    """Token schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token payload schema."""

    sub: str | None = None  # subject (user_id)
    exp: int | None = None  # expiration time
    type: str | None = None  # token type (access/refresh)
