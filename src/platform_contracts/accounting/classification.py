"""Classification request and result schemas."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from ..versioning import VersionedSchema


class ClientContext(BaseModel):
    """Business context for classification."""

    business_type: str = ""
    industry: str = ""
    tax_filing_type: str = ""
    state: str = ""


class AvailableAccount(BaseModel):
    """Account option for classification."""

    id: str
    name: str
    type: str = ""
    sub_type: str = ""
    schedule_c_line: str = ""


class ExistingRule(BaseModel):
    """Existing categorization rule."""

    pattern: str
    category_id: str
    category_name: str = ""


class HistoricalPattern(BaseModel):
    """Historical classification pattern."""

    description: str
    account_id: str
    account_name: str = ""
    count: int = 0


class TransactionForClassification(BaseModel):
    """Single transaction within a classification request."""

    transaction_id: str
    description: str
    amount: Decimal
    transaction_date: date
    transaction_type: str = ""
    bank_account_type: str = ""
    vendor_name: str = ""
    memo: str = ""
    plaid_category: list[str] = Field(default_factory=list)
    plaid_merchant_name: str = ""


class TransactionClassificationRequest(VersionedSchema):
    """Request to classify a batch of transactions."""

    tenant_id: str
    client_id: str
    transactions: list[TransactionForClassification]
    available_accounts: list[AvailableAccount] = Field(default_factory=list)
    existing_rules: list[ExistingRule] = Field(default_factory=list)
    historical_patterns: list[HistoricalPattern] = Field(default_factory=list)
    client_context: ClientContext = Field(default_factory=ClientContext)


class RiskFlag(BaseModel):
    """Risk indicator on a classification."""

    code: str
    severity: str = "medium"
    message: str = ""


class AlternativeSuggestion(BaseModel):
    """Alternative classification suggestion."""

    account_id: str
    name: str = ""
    confidence: float = 0.0


class TransactionClassificationResult(VersionedSchema):
    """Classification result for a single transaction."""

    transaction_id: str
    suggested_account_id: str | None = None
    suggested_account_name: str = ""
    suggested_vendor_id: str | None = None
    suggested_vendor_name: str = ""
    confidence: float = Field(ge=0.0, le=1.0)
    confidence_band: str = ""
    source: str = ""
    reasoning: str = ""
    needs_review: bool = False
    needs_clarification: bool = False
    clarification_question: str = ""
    risk_flags: list[RiskFlag] = Field(default_factory=list)
    alternative_suggestions: list[AlternativeSuggestion] = Field(default_factory=list)


class SuggestedRule(BaseModel):
    """Rule suggestion from classification results."""

    pattern: str
    suggested_account_id: str
    suggested_account_name: str = ""
    confidence: float = 0.0


class ClassificationResponseMeta(BaseModel):
    """Metadata about the classification request."""

    request_id: str = ""
    duration_ms: int = 0
    model: str = ""
    transactions_processed: int = 0
    rule_matches: int = 0
    historical_matches: int = 0
    ai_classifications: int = 0


class BatchClassificationResponse(VersionedSchema):
    """Response from batch classification."""

    classifications: list[TransactionClassificationResult]
    suggested_rules: list[SuggestedRule] = Field(default_factory=list)
    meta: ClassificationResponseMeta = Field(default_factory=ClassificationResponseMeta, alias="_meta")

    model_config = {"populate_by_name": True}
