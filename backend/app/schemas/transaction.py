"""Transaction Pydantic schemas."""

import uuid
from datetime import date, datetime
from decimal import Decimal

import pydantic

from app.models.transaction import TransactionType


class TransactionBase(pydantic.BaseModel):
    """Base transaction schema."""

    type: TransactionType
    amount: Decimal = pydantic.Field(..., gt=0, decimal_places=2)
    currency: str = pydantic.Field(default="MXN", min_length=3, max_length=3)
    description: str = pydantic.Field(..., min_length=1, max_length=500)
    category_id: uuid.UUID | None = None
    transaction_date: date = pydantic.Field(default_factory=date.today)


class TransactionCreate(TransactionBase):
    """Schema for creating a transaction."""

    raw_message: str | None = None


class TransactionRead(TransactionBase):
    """Schema for reading a transaction."""

    model_config = pydantic.ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TransactionUpdate(pydantic.BaseModel):
    """Schema for updating a transaction."""

    type: TransactionType | None = None
    amount: Decimal | None = pydantic.Field(None, gt=0, decimal_places=2)
    currency: str | None = pydantic.Field(None, min_length=3, max_length=3)
    description: str | None = pydantic.Field(None, min_length=1, max_length=500)
    category_id: uuid.UUID | None = None
    transaction_date: date | None = None
