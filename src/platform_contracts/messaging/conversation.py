"""Conversation schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from ..versioning import VersionedSchema


class ConversationStep(BaseModel):
    """Single step in a conversation flow."""

    step_number: int
    direction: str = ""
    body: str = ""
    buttons: list[dict] = Field(default_factory=list)
    timestamp: datetime | None = None
    response: str = ""


class StartConversationRequest(VersionedSchema):
    """Request to start a stateful conversation."""

    tenant_id: str
    client_id: str
    contact_phone: str
    contact_name: str = ""
    channel: str = "whatsapp"
    flow_type: str = ""
    context_type: str = ""
    context_id: str = ""
    context_data: dict = Field(default_factory=dict)
    timeout_minutes: int = 1440


class ConversationSession(VersionedSchema):
    """Conversation session state."""

    conversation_id: str
    contact_phone: str
    channel: str = "whatsapp"
    status: str = "active"
    current_state: str = "initial"
    flow_type: str = ""
    context_type: str = ""
    context_id: str = ""
    steps: list[ConversationStep] = Field(default_factory=list)
    last_activity_at: datetime | None = None


class ConversationReplyWebhook(BaseModel):
    """Webhook payload when a client replies in a conversation."""

    conversation_id: str
    tenant_id: str = ""
    client_id: str = ""
    contact_phone: str = ""
    response_text: str = ""
    button_id: str = ""
    context_type: str = ""
    context_id: str = ""
    timestamp: datetime | None = None
