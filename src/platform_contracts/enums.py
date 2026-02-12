"""Shared enums used across platform schemas."""

from enum import StrEnum


class SourceSystem(StrEnum):
    HUB = "hub"
    QBO_LEG = "qbo_leg"
    GL_LEG = "gl_leg"
    AI_TRANSLATOR = "ai_translator"
    MESSAGING = "messaging"
    TAX_ENGINE = "tax_engine"


class AccountType(StrEnum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"
    COST_OF_GOODS_SOLD = "cost_of_goods_sold"
    OTHER_INCOME = "other_income"
    OTHER_EXPENSE = "other_expense"


class TransactionType(StrEnum):
    DEBIT = "debit"
    CREDIT = "credit"


class BankAccountType(StrEnum):
    CHECKING = "checking"
    SAVINGS = "savings"
    CREDIT_CARD = "credit_card"
    LINE_OF_CREDIT = "line_of_credit"
    LOAN = "loan"
    OTHER = "other"


class ConfidenceBand(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"


class ClassificationSource(StrEnum):
    RULE = "rule"
    AI = "ai"
    HISTORICAL = "historical"
    CLIENT = "client"
    ACCOUNTANT = "accountant"


class ReviewStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    AUTO_APPLIED = "auto_applied"


class SuspenseReason(StrEnum):
    LOW_CONFIDENCE = "low_confidence"
    NEEDS_CLIENT_INPUT = "needs_client_input"
    MONTHLY_CALL = "monthly_call"
    DECLINED = "declined"
    ESCALATED_MAX_CLARIFICATION = "escalated_max_clarification"


class RiskSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MessageDirection(StrEnum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class MessageStatus(StrEnum):
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class ConsentType(StrEnum):
    OPT_IN = "opt_in"
    OPT_OUT = "opt_out"
    REVOKED = "revoked"


class ConversationStatus(StrEnum):
    ACTIVE = "active"
    WAITING_REPLY = "waiting_reply"
    TIMED_OUT = "timed_out"
    COMPLETED = "completed"


class EntityType(StrEnum):
    SOLE_PROPRIETOR = "sole_proprietor"
    LLC = "llc"
    S_CORP = "s_corp"
    C_CORP = "c_corp"
    PARTNERSHIP = "partnership"


class TaxFilingType(StrEnum):
    SCHEDULE_C = "schedule_c"
    FORM_1120S = "form_1120s"
    FORM_1120 = "form_1120"
    FORM_1065 = "form_1065"
