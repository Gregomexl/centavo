"""User Pydantic schemas."""

import uuid
from datetime import datetime

import pydantic


class UserBase(pydantic.BaseModel):
    """Base user schema."""

    email: pydantic.EmailStr | None = None
    display_name: str = pydantic.Field(..., min_length=1, max_length=100)
    default_currency: str = pydantic.Field(default="MXN", min_length=3, max_length=3)


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = pydantic.Field(..., min_length=8, max_length=100)


class UserLogin(pydantic.BaseModel):
    """Schema for user login."""

    email: pydantic.EmailStr
    password: str


class UserRead(UserBase):
    """Schema for reading a user."""

    model_config = pydantic.ConfigDict(from_attributes=True)

    id: uuid.UUID
    telegram_id: int | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserUpdate(pydantic.BaseModel):
    """Schema for updating a user."""

    email: pydantic.EmailStr | None = None
    display_name: str | None = pydantic.Field(None, min_length=1, max_length=100)
    default_currency: str | None = pydantic.Field(None, min_length=3, max_length=3)


class Token(pydantic.BaseModel):
    """Token schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(pydantic.BaseModel):
    """Token payload schema."""

    sub: str | None = None  # subject (user_id)
    exp: int | None = None  # expiration time
    type: str | None = None  # token type (access/refresh)
