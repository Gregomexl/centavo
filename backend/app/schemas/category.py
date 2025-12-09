"""Category Pydantic schemas."""

import uuid
from datetime import datetime

import pydantic

from app.models.transaction import TransactionType


class CategoryBase(pydantic.BaseModel):
    """Base category schema."""

    name: str = pydantic.Field(..., min_length=1, max_length=50)
    icon: str = pydantic.Field(default="📦", max_length=50)
    color: str = pydantic.Field(default="#6366f1", pattern=r"^#[0-9A-Fa-f]{6}$")
    type: TransactionType


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""

    pass


class CategoryRead(CategoryBase):
    """Schema for reading a category."""

    model_config = pydantic.ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID | None
    is_system: bool
    created_at: datetime
    updated_at: datetime


class CategoryUpdate(pydantic.BaseModel):
    """Schema for updating a category."""

    name: str | None = pydantic.Field(None, min_length=1, max_length=50)
    icon: str | None = pydantic.Field(None, max_length=50)
    color: str | None = pydantic.Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
