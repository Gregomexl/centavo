"""Recurring Transaction model."""

import uuid
from decimal import Decimal
from enum import Enum

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.transaction import TransactionType


class RecurringFrequency(str, Enum):
    """Recurring frequency enum."""

    MONTHLY = "monthly"


class RecurringTransaction(Base, TimestampMixin):
    """Recurring transaction model for bills and recurring expenses/income."""

    __tablename__ = "recurring_transactions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="MXN", nullable=False)
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    type: Mapped[TransactionType] = mapped_column(nullable=False)
    frequency: Mapped[RecurringFrequency] = mapped_column(
        default=RecurringFrequency.MONTHLY,
        nullable=False,
    )
    day_of_month: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="recurring_transactions")  # noqa: F821
    category: Mapped["Category | None"] = relationship()  # noqa: F821

    def __repr__(self) -> str:
        return (
            f"<RecurringTransaction(id={self.id}, name={self.name}, "
            f"amount={self.amount} {self.currency})>"
        )
