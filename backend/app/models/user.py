"""User model."""

import uuid

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    """User model for authentication and ownership."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    telegram_id: Mapped[int | None] = mapped_column(BigInteger, unique=True, nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    hashed_password: Mapped[str | None] = mapped_column(String(512), nullable=True)
    display_name: Mapped[str] = mapped_column(String(100))
    default_currency: Mapped[str] = mapped_column(String(3), default="MXN")
    is_active: Mapped[bool] = mapped_column(default=True)

    # Relationships
    transactions: Mapped[list["Transaction"]] = relationship(  # noqa: F821
        back_populates="user",
        cascade="all, delete-orphan",
    )
    categories: Mapped[list["Category"]] = relationship(  # noqa: F821
        back_populates="user",
        cascade="all, delete-orphan",
    )
    recurring_transactions: Mapped[list["RecurringTransaction"]] = relationship(  # noqa: F821
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, display_name={self.display_name})>"
