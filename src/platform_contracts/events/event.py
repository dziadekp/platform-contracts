"""Platform event envelope."""

from datetime import datetime

from pydantic import BaseModel, Field

from ..common.timestamps import utc_now
from ..versioning import VersionedSchema


class PlatformEvent(VersionedSchema):
    """Standard event envelope for cross-service communication."""

    event_id: str = ""
    event_type: str = Field(..., description="Dotted event type, e.g. 'transaction.classified'")
    source_system: str = ""
    tenant_id: str = ""
    timestamp: datetime = Field(default_factory=utc_now)
    payload: dict = Field(default_factory=dict)
    correlation_id: str = ""


KNOWN_EVENT_TYPES = [
    "transaction.classified",
    "transaction.posted",
    "clarification.requested",
    "clarification.completed",
    "clarification.timed_out",
    "suspense.created",
    "suspense.cleared",
    "digest.generated",
    "digest.approved",
    "message.sent",
    "message.delivered",
    "message.read",
    "message.failed",
    "conversation.started",
    "conversation.completed",
    "conversation.timed_out",
]
