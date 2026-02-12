"""Suspense item schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from ..versioning import VersionedSchema


class SuspenseItem(VersionedSchema):
    """Transaction parked in suspense."""

    suspense_id: str
    transaction_id: str
    client_id: str
    tenant_id: str
    reason: str = ""
    suspense_account_id: str = ""
    original_amount: str = ""
    description: str = ""
    parked_at: datetime | None = None
    resolved: bool = False
    resolved_at: datetime | None = None
    resolution_account_id: str = ""
    resolved_by: str = ""
    clarification_attempts: int = 0
