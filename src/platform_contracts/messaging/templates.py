"""WhatsApp template schemas."""

from pydantic import BaseModel, Field


class TemplateButton(BaseModel):
    """Button in a WhatsApp interactive message."""

    id: str
    title: str = Field(..., max_length=20)


class TemplateParameter(BaseModel):
    """Parameter for a WhatsApp template."""

    type: str = "text"
    text: str = ""


class WhatsAppTemplate(BaseModel):
    """WhatsApp message template definition."""

    name: str
    language: str = "en_US"
    category: str = "UTILITY"
    components: list[dict] = Field(default_factory=list)


class InteractiveMessage(BaseModel):
    """WhatsApp interactive message with buttons."""

    body_text: str
    buttons: list[TemplateButton] = Field(default_factory=list)
    header_text: str = ""
    footer_text: str = ""
