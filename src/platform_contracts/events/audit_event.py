"""Audit event schema for compliance logging."""

from datetime import datetime

from pydantic import BaseModel, Field

from ..common.timestamps import utc_now


class AuditEvent(BaseModel):
    """Immutable audit trail entry."""

    audit_id: str = ""
    event_type: str = ""
    actor_id: str = ""
    actor_type: str = ""
    tenant_id: str = ""
    resource_type: str = ""
    resource_id: str = ""
    action: str = ""
    before_state: dict = Field(default_factory=dict)
    after_state: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=utc_now)
    ip_address: str = ""
