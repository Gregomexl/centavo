"""Transaction model."""

import uuid
from datetime import date
from decimal import Decimal
from enum import Enum

from sqlalchemy import ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class TransactionType(str, Enum):
    """Transaction type enum."""

    EXPENSE = "expense"
    INCOME = "income"


class Transaction(Base, TimestampMixin):
    """Transaction model for expenses and incomes."""

    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    type: Mapped[TransactionType] = mapped_column(nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="MXN", nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    raw_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    transaction_date: Mapped[date] = mapped_column(default=func.current_date(), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="transactions")  # noqa: F821
    category: Mapped["Category | None"] = relationship(  # noqa: F821
        back_populates="transactions"
    )

    # Indexes for analytics queries
    __table_args__ = (
        Index("idx_user_date", "user_id", "transaction_date"),
        Index("idx_user_type_date", "user_id", "type", "transaction_date"),
    )

    def __repr__(self) -> str:
        return (
            f"<Transaction(id={self.id}, type={self.type}, "
            f"amount={self.amount} {self.currency})>"
        )
