"""Vendor schemas."""

from pydantic import BaseModel, Field


class Vendor(BaseModel):
    """Vendor / payee reference."""

    id: str = Field(..., description="Vendor ID in source system")
    name: str
    display_name: str = ""
    is_1099_eligible: bool = False
    is_active: bool = True
