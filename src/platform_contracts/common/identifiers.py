"""Common identifier schemas."""

from pydantic import BaseModel, Field


class TenantRef(BaseModel):
    """Reference to a tenant (team) across services."""

    tenant_id: str = Field(..., description="Hub team UUID or slug")
    source_system: str = ""


class ExternalRef(BaseModel):
    """Reference to an external system entity."""

    system: str = Field(..., description="External system name (e.g., 'qbo', 'plaid', 'stripe')")
    external_id: str = Field(..., description="ID in the external system")
    external_type: str = ""
    metadata: dict = Field(default_factory=dict)
