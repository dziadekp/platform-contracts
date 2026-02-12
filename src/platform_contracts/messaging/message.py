"""Message schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from ..versioning import VersionedSchema


class SendMessageRequest(VersionedSchema):
    """Request to send a message via messaging service."""

    tenant_id: str
    client_id: str
    contact_phone: str = Field(..., description="E.164 format phone number")
    contact_name: str = ""
    channel: str = "whatsapp"
    template_name: str = ""
    template_params: dict = Field(default_factory=dict)
    body: str = ""
    context_type: str = ""
    context_id: str = ""
    context_data: dict = Field(default_factory=dict)


class MessageDeliveryWebhook(BaseModel):
    """Webhook payload for message delivery status update."""

    message_id: str
    conversation_id: str = ""
    channel_message_id: str = ""
    status: str = ""
    error_message: str = ""
    timestamp: datetime | None = None
