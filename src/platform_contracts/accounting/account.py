"""Account schemas."""

from pydantic import BaseModel, Field


class Account(BaseModel):
    """Chart of accounts entry."""

    id: str = Field(..., description="Account ID in source system")
    name: str
    account_type: str = ""
    sub_type: str = ""
    account_number: str = ""
    schedule_c_line: str = ""
    is_active: bool = True
    parent_id: str | None = None
