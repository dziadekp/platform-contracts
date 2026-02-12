"""Timestamp helpers."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class TimestampMixin(BaseModel):
    """Mixin for created/updated timestamps."""

    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
