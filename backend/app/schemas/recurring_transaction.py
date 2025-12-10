"""Recurring Transaction schemas."""

import uuid
from datetime import datetime

import pydantic

from app.models.recurring_transaction import RecurringFrequency
from app.models.transaction import TransactionType


class RecurringTransactionBase(pydantic.BaseModel):
    """Base schema for recurring transaction."""

    name: str = pydantic.Field(..., min_length=1, max_length=100)
    amount: float = pydantic.Field(..., gt=0)
    currency: str = pydantic.Field(default="MXN", min_length=3, max_length=3)
    category_id: uuid.UUID | None = None
    type: TransactionType
    frequency: RecurringFrequency = RecurringFrequency.MONTHLY
    day_of_month: int = pydantic.Field(..., ge=1, le=31)
    is_active: bool = True


class RecurringTransactionCreate(RecurringTransactionBase):
    """Schema for creating a recurring transaction."""

    pass


class RecurringTransactionUpdate(pydantic.BaseModel):
    """Schema for updating a recurring transaction."""

    name: str | None = pydantic.Field(default=None, min_length=1, max_length=100)
    amount: float | None = pydantic.Field(default=None, gt=0)
    category_id: uuid.UUID | None = None
    day_of_month: int | None = pydantic.Field(default=None, ge=1, le=31)
    is_active: bool | None = None


class RecurringTransactionRead(RecurringTransactionBase):
    """Schema for reading a recurring transaction."""

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = pydantic.ConfigDict(from_attributes=True)
