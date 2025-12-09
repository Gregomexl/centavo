"""Common Pydantic schemas."""

from typing import Generic, TypeVar

import pydantic

T = TypeVar("T")


class PaginatedResponse(pydantic.BaseModel, Generic[T]):
    """Paginated response schema."""

    items: list[T]
    total: int
    page: int = pydantic.Field(..., ge=1)
    page_size: int = pydantic.Field(..., ge=1, le=100)
    total_pages: int


class MessageResponse(pydantic.BaseModel):
    """Simple message response."""

    message: str
