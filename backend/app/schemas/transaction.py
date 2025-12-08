"""Transaction Pydantic schemas."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.transaction import TransactionType


class TransactionBase(BaseModel):
    """Base transaction schema."""

    type: TransactionType
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    currency: str = Field(default="MXN", min_length=3, max_length=3)
    description: str = Field(..., min_length=1, max_length=500)
    category_id: uuid.UUID | None = None
    transaction_date: date = Field(default_factory=date.today)


class TransactionCreate(TransactionBase):
    """Schema for creating a transaction."""

    raw_message: str | None = None


class TransactionRead(TransactionBase):
    """Schema for reading a transaction."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TransactionUpdate(BaseModel):
    """Schema for updating a transaction."""

    type: TransactionType | None = None
    amount: Decimal | None = Field(None, gt=0, decimal_places=2)
    currency: str | None = Field(None, min_length=3, max_length=3)
    description: str | None = Field(None, min_length=1, max_length=500)
    category_id: uuid.UUID | None = None
    transaction_date: date | None = None
