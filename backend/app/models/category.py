"""Category model."""

import uuid

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.transaction import TransactionType


class Category(Base, TimestampMixin):
    """Category model for organizing transactions."""

    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,  # NULL = system default category
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    icon: Mapped[str] = mapped_column(String(50), default="📦", nullable=False)
    color: Mapped[str] = mapped_column(String(7), default="#6366f1", nullable=False)
    type: Mapped[TransactionType] = mapped_column(nullable=False)
    is_system: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships
    user: Mapped["User | None"] = relationship(back_populates="categories")  # noqa: F821
    transactions: Mapped[list["Transaction"]] = relationship(  # noqa: F821
        back_populates="category"
    )

    # Unique constraint: user can't have duplicate category names for the same type
    __table_args__ = (
        UniqueConstraint("user_id", "name", "type", name="uq_user_category_name_type"),
    )

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name}, type={self.type})>"
