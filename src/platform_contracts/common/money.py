"""Money and currency schemas."""

from decimal import Decimal

from pydantic import BaseModel, Field


class Money(BaseModel):
    """Monetary amount with currency."""

    amount: Decimal = Field(..., description="Decimal amount")
    currency: str = Field(default="USD", max_length=3, description="ISO 4217 currency code")

    def is_positive(self) -> bool:
        return self.amount > 0

    def is_negative(self) -> bool:
        return self.amount < 0

    def is_zero(self) -> bool:
        return self.amount == Decimal("0")
