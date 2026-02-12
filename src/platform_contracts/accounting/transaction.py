"""Transaction schemas."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from ..versioning import VersionedSchema


class BankTransaction(VersionedSchema):
    """Canonical bank transaction for classification."""

    transaction_id: str
    description: str
    amount: Decimal
    transaction_date: date
    transaction_type: str = ""
    bank_account_type: str = ""
    vendor_name: str = ""
    memo: str = ""
    check_number: str = ""
    plaid_category: list[str] = Field(default_factory=list)
    plaid_merchant_name: str = ""
    plaid_transaction_id: str = ""
    metadata: dict = Field(default_factory=dict)
