"""Risk flag schemas."""

from pydantic import BaseModel


class RiskFlag(BaseModel):
    """Risk indicator for a transaction or classification."""

    code: str
    severity: str = "medium"
    message: str = ""
    category: str = ""


KNOWN_RISK_CODES = {
    "OWNER_TXN_POSSIBLE": "Transfer may be owner-related (draw, loan, contribution)",
    "LARGE_AMOUNT": "Transaction exceeds normal range for this category",
    "DUPLICATE_POSSIBLE": "Possible duplicate transaction detected",
    "TAX_SENSITIVE": "Classification affects tax-sensitive category",
    "PERSONAL_EXPENSE": "Possible personal expense in business account",
    "ROUND_AMOUNT": "Round dollar amount may indicate estimate or transfer",
    "NEW_VENDOR": "First transaction with this vendor/payee",
    "PATTERN_BREAK": "Transaction does not match historical patterns for this vendor",
}
