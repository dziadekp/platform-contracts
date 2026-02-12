"""Tests for accounting domain schemas.

These tests validate that all accounting and common schemas work correctly
with their ACTUAL field names, types, and validation rules.
"""

from datetime import date, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from platform_contracts.accounting.account import Account
from platform_contracts.accounting.classification import (
    AlternativeSuggestion,
    AvailableAccount,
    BatchClassificationResponse,
    ClassificationResponseMeta,
    ClientContext,
    ExistingRule,
    HistoricalPattern,
    RiskFlag,
    SuggestedRule,
    TransactionClassificationRequest,
    TransactionClassificationResult,
    TransactionForClassification,
)
from platform_contracts.accounting.journal_entry import JournalEntry, JournalEntryLine
from platform_contracts.accounting.risk import KNOWN_RISK_CODES
from platform_contracts.accounting.risk import RiskFlag as RiskFlagRisk
from platform_contracts.accounting.suspense import SuspenseItem
from platform_contracts.accounting.transaction import BankTransaction
from platform_contracts.accounting.vendor import Vendor
from platform_contracts.common.identifiers import ExternalRef, TenantRef
from platform_contracts.common.money import Money
from platform_contracts.enums import (
    AccountType,
    BankAccountType,
    ClassificationSource,
    ConfidenceBand,
    EntityType,
    RiskSeverity,
    ReviewStatus,
    SuspenseReason,
    TransactionType,
)
from platform_contracts.versioning import VersionedSchema


class TestVersionedSchema:
    """Test schema versioning."""

    def test_default_version(self):
        schema = VersionedSchema()
        assert schema.schema_version == "1.0"

    def test_valid_version_formats(self):
        """Test valid version formats."""
        valid_versions = ["1.0", "2.0", "1.5", "10.99"]
        for version in valid_versions:
            schema = VersionedSchema(schema_version=version)
            assert schema.schema_version == version

    def test_invalid_version_formats(self):
        """Test invalid version formats raise ValidationError."""
        invalid_versions = ["abc", "1", "1.2.3", "v1.0", "1.x"]
        for version in invalid_versions:
            with pytest.raises(ValidationError) as exc_info:
                VersionedSchema(schema_version=version)
            assert "Invalid schema version format" in str(exc_info.value)

    def test_is_compatible_same_major(self):
        """Test compatibility with same major version."""
        schema_v1_0 = VersionedSchema(schema_version="1.0")
        assert schema_v1_0.is_compatible("1.0") is True
        assert schema_v1_0.is_compatible("1.5") is True
        assert schema_v1_0.is_compatible("1.99") is True

    def test_is_compatible_different_major(self):
        """Test incompatibility with different major version."""
        schema_v1_0 = VersionedSchema(schema_version="1.0")
        assert schema_v1_0.is_compatible("2.0") is False
        assert schema_v1_0.is_compatible("0.9") is False


class TestEnums:
    """Test all platform enums."""

    def test_account_type_enum(self):
        """Test AccountType enum values."""
        assert AccountType.ASSET == "asset"
        assert AccountType.LIABILITY == "liability"
        assert AccountType.EQUITY == "equity"
        assert AccountType.REVENUE == "revenue"
        assert AccountType.EXPENSE == "expense"
        assert AccountType.COST_OF_GOODS_SOLD == "cost_of_goods_sold"
        assert AccountType.OTHER_INCOME == "other_income"
        assert AccountType.OTHER_EXPENSE == "other_expense"

    def test_transaction_type_enum(self):
        """Test TransactionType enum values."""
        assert TransactionType.DEBIT == "debit"
        assert TransactionType.CREDIT == "credit"

    def test_bank_account_type_enum(self):
        """Test BankAccountType enum values."""
        assert BankAccountType.CHECKING == "checking"
        assert BankAccountType.SAVINGS == "savings"
        assert BankAccountType.CREDIT_CARD == "credit_card"
        assert BankAccountType.LINE_OF_CREDIT == "line_of_credit"
        assert BankAccountType.LOAN == "loan"
        assert BankAccountType.OTHER == "other"

    def test_confidence_band_enum(self):
        """Test ConfidenceBand enum values."""
        assert ConfidenceBand.HIGH == "high"
        assert ConfidenceBand.MEDIUM == "medium"
        assert ConfidenceBand.LOW == "low"
        assert ConfidenceBand.UNCERTAIN == "uncertain"

    def test_classification_source_enum(self):
        """Test ClassificationSource enum values."""
        assert ClassificationSource.RULE == "rule"
        assert ClassificationSource.AI == "ai"
        assert ClassificationSource.HISTORICAL == "historical"
        assert ClassificationSource.CLIENT == "client"
        assert ClassificationSource.ACCOUNTANT == "accountant"

    def test_review_status_enum(self):
        """Test ReviewStatus enum values."""
        assert ReviewStatus.PENDING == "pending"
        assert ReviewStatus.APPROVED == "approved"
        assert ReviewStatus.REJECTED == "rejected"
        assert ReviewStatus.MODIFIED == "modified"
        assert ReviewStatus.AUTO_APPLIED == "auto_applied"

    def test_suspense_reason_enum(self):
        """Test SuspenseReason enum values."""
        assert SuspenseReason.LOW_CONFIDENCE == "low_confidence"
        assert SuspenseReason.NEEDS_CLIENT_INPUT == "needs_client_input"
        assert SuspenseReason.MONTHLY_CALL == "monthly_call"
        assert SuspenseReason.DECLINED == "declined"
        assert SuspenseReason.ESCALATED_MAX_CLARIFICATION == "escalated_max_clarification"

    def test_risk_severity_enum(self):
        """Test RiskSeverity enum values."""
        assert RiskSeverity.LOW == "low"
        assert RiskSeverity.MEDIUM == "medium"
        assert RiskSeverity.HIGH == "high"
        assert RiskSeverity.CRITICAL == "critical"

    def test_entity_type_enum(self):
        """Test EntityType enum values."""
        assert EntityType.SOLE_PROPRIETOR == "sole_proprietor"
        assert EntityType.LLC == "llc"
        assert EntityType.S_CORP == "s_corp"
        assert EntityType.C_CORP == "c_corp"
        assert EntityType.PARTNERSHIP == "partnership"


class TestTenantRef:
    """Test TenantRef schema."""

    def test_required_fields(self):
        """Test TenantRef with required fields."""
        tenant_ref = TenantRef(tenant_id="team_123")
        assert tenant_ref.tenant_id == "team_123"
        assert tenant_ref.source_system == ""

    def test_with_source_system(self):
        """Test TenantRef with source system."""
        tenant_ref = TenantRef(tenant_id="team_456", source_system="hub")
        assert tenant_ref.tenant_id == "team_456"
        assert tenant_ref.source_system == "hub"

    def test_missing_tenant_id_fails(self):
        """Test that missing tenant_id raises ValidationError."""
        with pytest.raises(ValidationError):
            TenantRef()


class TestExternalRef:
    """Test ExternalRef schema."""

    def test_required_fields(self):
        """Test ExternalRef with required fields."""
        ext_ref = ExternalRef(system="qbo", external_id="12345")
        assert ext_ref.system == "qbo"
        assert ext_ref.external_id == "12345"
        assert ext_ref.external_type == ""
        assert ext_ref.metadata == {}

    def test_with_optional_fields(self):
        """Test ExternalRef with all fields."""
        ext_ref = ExternalRef(
            system="plaid",
            external_id="txn_abc",
            external_type="transaction",
            metadata={"account_id": "acc_123"},
        )
        assert ext_ref.system == "plaid"
        assert ext_ref.external_id == "txn_abc"
        assert ext_ref.external_type == "transaction"
        assert ext_ref.metadata == {"account_id": "acc_123"}

    def test_missing_required_fields_fails(self):
        """Test that missing required fields raise ValidationError."""
        with pytest.raises(ValidationError):
            ExternalRef(system="qbo")
        with pytest.raises(ValidationError):
            ExternalRef(external_id="123")


class TestMoney:
    """Test Money schema."""

    def test_money_creation(self):
        """Test Money creation with amount and currency."""
        money = Money(amount=Decimal("100.50"), currency="USD")
        assert money.amount == Decimal("100.50")
        assert money.currency == "USD"

    def test_default_currency(self):
        """Test default currency is USD."""
        money = Money(amount=Decimal("50.00"))
        assert money.currency == "USD"

    def test_is_positive(self):
        """Test is_positive method."""
        assert Money(amount=Decimal("10.00")).is_positive() is True
        assert Money(amount=Decimal("0.01")).is_positive() is True
        assert Money(amount=Decimal("0")).is_positive() is False
        assert Money(amount=Decimal("-10.00")).is_positive() is False

    def test_is_negative(self):
        """Test is_negative method."""
        assert Money(amount=Decimal("-10.00")).is_negative() is True
        assert Money(amount=Decimal("-0.01")).is_negative() is True
        assert Money(amount=Decimal("0")).is_negative() is False
        assert Money(amount=Decimal("10.00")).is_negative() is False

    def test_is_zero(self):
        """Test is_zero method."""
        assert Money(amount=Decimal("0")).is_zero() is True
        assert Money(amount=Decimal("0.00")).is_zero() is True
        assert Money(amount=Decimal("0.01")).is_zero() is False
        assert Money(amount=Decimal("-0.01")).is_zero() is False


class TestAccount:
    """Test Account schema."""

    def test_required_fields(self):
        """Test Account with required fields only."""
        account = Account(id="acc_123", name="Cash")
        assert account.id == "acc_123"
        assert account.name == "Cash"
        assert account.account_type == ""
        assert account.sub_type == ""
        assert account.account_number == ""
        assert account.schedule_c_line == ""
        assert account.is_active is True
        assert account.parent_id is None

    def test_with_all_fields(self):
        """Test Account with all fields."""
        account = Account(
            id="acc_456",
            name="Office Supplies",
            account_type=AccountType.EXPENSE,
            sub_type="Operating Expense",
            account_number="5100",
            schedule_c_line="18",
            is_active=True,
            parent_id="acc_500",
        )
        assert account.id == "acc_456"
        assert account.name == "Office Supplies"
        assert account.account_type == "expense"
        assert account.sub_type == "Operating Expense"
        assert account.account_number == "5100"
        assert account.schedule_c_line == "18"
        assert account.is_active is True
        assert account.parent_id == "acc_500"


class TestVendor:
    """Test Vendor schema."""

    def test_required_fields(self):
        """Test Vendor with required fields only."""
        vendor = Vendor(id="vendor_123", name="ABC Corp")
        assert vendor.id == "vendor_123"
        assert vendor.name == "ABC Corp"
        assert vendor.display_name == ""
        assert vendor.is_1099_eligible is False
        assert vendor.is_active is True

    def test_with_all_fields(self):
        """Test Vendor with all fields."""
        vendor = Vendor(
            id="vendor_456",
            name="XYZ LLC",
            display_name="XYZ Services",
            is_1099_eligible=True,
            is_active=True,
        )
        assert vendor.id == "vendor_456"
        assert vendor.name == "XYZ LLC"
        assert vendor.display_name == "XYZ Services"
        assert vendor.is_1099_eligible is True
        assert vendor.is_active is True


class TestBankTransaction:
    """Test BankTransaction schema."""

    def test_required_fields(self):
        """Test BankTransaction with required fields only."""
        txn = BankTransaction(
            transaction_id="txn_123",
            description="Purchase at Store",
            amount=Decimal("50.00"),
            transaction_date=date(2024, 1, 15),
        )
        assert txn.transaction_id == "txn_123"
        assert txn.description == "Purchase at Store"
        assert txn.amount == Decimal("50.00")
        assert txn.transaction_date == date(2024, 1, 15)
        assert txn.transaction_type == ""
        assert txn.bank_account_type == ""
        assert txn.vendor_name == ""
        assert txn.memo == ""
        assert txn.check_number == ""
        assert txn.plaid_category == []
        assert txn.plaid_merchant_name == ""
        assert txn.plaid_transaction_id == ""
        assert txn.metadata == {}
        assert txn.schema_version == "1.0"

    def test_with_all_fields(self):
        """Test BankTransaction with all fields."""
        txn = BankTransaction(
            transaction_id="txn_456",
            description="Office supplies from Amazon",
            amount=Decimal("-125.50"),
            transaction_date=date(2024, 2, 1),
            transaction_type=TransactionType.DEBIT,
            bank_account_type=BankAccountType.CHECKING,
            vendor_name="Amazon",
            memo="Printer paper",
            check_number="1234",
            plaid_category=["Shops", "Office Supplies"],
            plaid_merchant_name="Amazon.com",
            plaid_transaction_id="plaid_txn_abc",
            metadata={"imported_from": "plaid"},
            schema_version="1.0",
        )
        assert txn.transaction_id == "txn_456"
        assert txn.amount == Decimal("-125.50")
        assert txn.transaction_type == "debit"
        assert txn.bank_account_type == "checking"
        assert txn.plaid_category == ["Shops", "Office Supplies"]


class TestTransactionClassification:
    """Test transaction classification schemas."""

    def test_client_context(self):
        """Test ClientContext schema."""
        context = ClientContext(
            business_type="LLC",
            industry="Software",
            tax_filing_type="schedule_c",
            state="CA",
        )
        assert context.business_type == "LLC"
        assert context.industry == "Software"
        assert context.tax_filing_type == "schedule_c"
        assert context.state == "CA"

    def test_available_account(self):
        """Test AvailableAccount schema."""
        account = AvailableAccount(
            id="acc_123",
            name="Office Expense",
            type=AccountType.EXPENSE,
            sub_type="Operating",
            schedule_c_line="18",
        )
        assert account.id == "acc_123"
        assert account.name == "Office Expense"
        assert account.type == "expense"
        assert account.schedule_c_line == "18"

    def test_existing_rule(self):
        """Test ExistingRule schema."""
        rule = ExistingRule(
            pattern="AMAZON",
            category_id="acc_456",
            category_name="Office Supplies",
        )
        assert rule.pattern == "AMAZON"
        assert rule.category_id == "acc_456"
        assert rule.category_name == "Office Supplies"

    def test_historical_pattern(self):
        """Test HistoricalPattern schema."""
        pattern = HistoricalPattern(
            description="Office Depot",
            account_id="acc_789",
            account_name="Office Supplies",
            count=15,
        )
        assert pattern.description == "Office Depot"
        assert pattern.account_id == "acc_789"
        assert pattern.count == 15

    def test_transaction_for_classification(self):
        """Test TransactionForClassification schema."""
        txn = TransactionForClassification(
            transaction_id="txn_001",
            description="Amazon purchase",
            amount=Decimal("50.00"),
            transaction_date=date(2024, 1, 15),
            transaction_type=TransactionType.DEBIT,
            bank_account_type=BankAccountType.CHECKING,
            vendor_name="Amazon",
            memo="Office supplies",
            plaid_category=["Shops", "Office"],
            plaid_merchant_name="Amazon.com",
        )
        assert txn.transaction_id == "txn_001"
        assert txn.description == "Amazon purchase"
        assert txn.amount == Decimal("50.00")

    def test_transaction_classification_request(self):
        """Test TransactionClassificationRequest schema."""
        request = TransactionClassificationRequest(
            tenant_id="team_123",
            client_id="client_456",
            transactions=[
                TransactionForClassification(
                    transaction_id="txn_001",
                    description="Test",
                    amount=Decimal("10.00"),
                    transaction_date=date(2024, 1, 1),
                )
            ],
            available_accounts=[AvailableAccount(id="acc_1", name="Cash")],
            existing_rules=[ExistingRule(pattern="TEST", category_id="acc_1")],
            historical_patterns=[
                HistoricalPattern(description="TEST", account_id="acc_1", count=5)
            ],
            client_context=ClientContext(business_type="LLC"),
        )
        assert request.tenant_id == "team_123"
        assert request.client_id == "client_456"
        assert len(request.transactions) == 1
        assert len(request.available_accounts) == 1
        assert request.schema_version == "1.0"

    def test_risk_flag(self):
        """Test RiskFlag schema."""
        risk = RiskFlag(
            code="LARGE_AMOUNT",
            severity=RiskSeverity.MEDIUM,
            message="Amount exceeds normal range",
        )
        assert risk.code == "LARGE_AMOUNT"
        assert risk.severity == "medium"
        assert risk.message == "Amount exceeds normal range"

    def test_alternative_suggestion(self):
        """Test AlternativeSuggestion schema."""
        suggestion = AlternativeSuggestion(
            account_id="acc_999",
            name="Travel Expense",
            confidence=0.65,
        )
        assert suggestion.account_id == "acc_999"
        assert suggestion.name == "Travel Expense"
        assert suggestion.confidence == 0.65

    def test_transaction_classification_result(self):
        """Test TransactionClassificationResult schema."""
        result = TransactionClassificationResult(
            transaction_id="txn_001",
            suggested_account_id="acc_123",
            suggested_account_name="Office Supplies",
            suggested_vendor_id="vendor_456",
            suggested_vendor_name="Amazon",
            confidence=0.85,
            confidence_band=ConfidenceBand.HIGH,
            source=ClassificationSource.AI,
            reasoning="Based on historical patterns",
            needs_review=False,
            needs_clarification=False,
            clarification_question="",
            risk_flags=[
                RiskFlag(code="NEW_VENDOR", severity="low", message="First transaction")
            ],
            alternative_suggestions=[
                AlternativeSuggestion(account_id="acc_789", confidence=0.60)
            ],
        )
        assert result.transaction_id == "txn_001"
        assert result.confidence == 0.85
        assert result.confidence_band == "high"
        assert result.source == "ai"
        assert len(result.risk_flags) == 1
        assert len(result.alternative_suggestions) == 1

    def test_confidence_validation(self):
        """Test confidence field validation (0.0 to 1.0)."""
        # Valid confidence values
        TransactionClassificationResult(
            transaction_id="txn_001",
            confidence=0.0,
        )
        TransactionClassificationResult(
            transaction_id="txn_002",
            confidence=1.0,
        )
        TransactionClassificationResult(
            transaction_id="txn_003",
            confidence=0.5,
        )

        # Invalid confidence values
        with pytest.raises(ValidationError):
            TransactionClassificationResult(
                transaction_id="txn_004",
                confidence=-0.1,
            )
        with pytest.raises(ValidationError):
            TransactionClassificationResult(
                transaction_id="txn_005",
                confidence=1.1,
            )

    def test_suggested_rule(self):
        """Test SuggestedRule schema."""
        rule = SuggestedRule(
            pattern="AMAZON",
            suggested_account_id="acc_123",
            suggested_account_name="Office Supplies",
            confidence=0.90,
        )
        assert rule.pattern == "AMAZON"
        assert rule.suggested_account_id == "acc_123"
        assert rule.confidence == 0.90

    def test_classification_response_meta(self):
        """Test ClassificationResponseMeta schema."""
        meta = ClassificationResponseMeta(
            request_id="req_abc123",
            duration_ms=250,
            model="gpt-4o",
            transactions_processed=10,
            rule_matches=3,
            historical_matches=4,
            ai_classifications=3,
        )
        assert meta.request_id == "req_abc123"
        assert meta.duration_ms == 250
        assert meta.model == "gpt-4o"
        assert meta.transactions_processed == 10

    def test_batch_classification_response(self):
        """Test BatchClassificationResponse schema."""
        response = BatchClassificationResponse(
            classifications=[
                TransactionClassificationResult(
                    transaction_id="txn_001",
                    confidence=0.75,
                )
            ],
            suggested_rules=[
                SuggestedRule(
                    pattern="TEST",
                    suggested_account_id="acc_1",
                    confidence=0.80,
                )
            ],
            meta=ClassificationResponseMeta(
                request_id="req_123",
                transactions_processed=1,
            ),
        )
        assert len(response.classifications) == 1
        assert len(response.suggested_rules) == 1
        assert response.meta.request_id == "req_123"
        assert response.schema_version == "1.0"

    def test_batch_classification_response_meta_alias(self):
        """Test that _meta alias works for ClassificationResponseMeta."""
        response = BatchClassificationResponse(
            classifications=[],
            _meta=ClassificationResponseMeta(request_id="req_456"),
        )
        assert response.meta.request_id == "req_456"


class TestJournalEntry:
    """Test JournalEntry schemas."""

    def test_journal_entry_line(self):
        """Test JournalEntryLine schema."""
        line = JournalEntryLine(
            account_id="acc_123",
            account_name="Cash",
            debit=Decimal("100.00"),
            credit=Decimal("0"),
            description="Payment received",
            entity_id="vendor_456",
            entity_type="vendor",
        )
        assert line.account_id == "acc_123"
        assert line.account_name == "Cash"
        assert line.debit == Decimal("100.00")
        assert line.credit == Decimal("0")
        assert line.description == "Payment received"

    def test_journal_entry_line_defaults(self):
        """Test JournalEntryLine default values."""
        line = JournalEntryLine(account_id="acc_789")
        assert line.account_name == ""
        assert line.debit == Decimal("0")
        assert line.credit == Decimal("0")
        assert line.description == ""
        assert line.entity_id == ""
        assert line.entity_type == ""

    def test_journal_entry_required_fields(self):
        """Test JournalEntry with required fields."""
        entry = JournalEntry(
            entry_date=date(2024, 1, 15),
        )
        assert entry.entry_id == ""
        assert entry.entry_date == date(2024, 1, 15)
        assert entry.memo == ""
        assert entry.lines == []
        assert entry.source == ""
        assert entry.reference_id == ""
        assert entry.is_adjusting is False
        assert entry.schema_version == "1.0"

    def test_journal_entry_with_lines(self):
        """Test JournalEntry with lines."""
        entry = JournalEntry(
            entry_id="je_001",
            entry_date=date(2024, 1, 15),
            memo="Monthly depreciation",
            lines=[
                JournalEntryLine(
                    account_id="acc_dep_exp",
                    account_name="Depreciation Expense",
                    debit=Decimal("500.00"),
                ),
                JournalEntryLine(
                    account_id="acc_accum_dep",
                    account_name="Accumulated Depreciation",
                    credit=Decimal("500.00"),
                ),
            ],
            source="system",
            reference_id="dep_jan_2024",
            is_adjusting=True,
        )
        assert entry.entry_id == "je_001"
        assert len(entry.lines) == 2
        assert entry.is_adjusting is True

    def test_is_balanced_true(self):
        """Test is_balanced returns True when debits equal credits."""
        entry = JournalEntry(
            entry_date=date(2024, 1, 1),
            lines=[
                JournalEntryLine(
                    account_id="acc_1",
                    debit=Decimal("100.00"),
                ),
                JournalEntryLine(
                    account_id="acc_2",
                    credit=Decimal("100.00"),
                ),
            ],
        )
        assert entry.is_balanced() is True

    def test_is_balanced_false(self):
        """Test is_balanced returns False when debits don't equal credits."""
        entry = JournalEntry(
            entry_date=date(2024, 1, 1),
            lines=[
                JournalEntryLine(
                    account_id="acc_1",
                    debit=Decimal("100.00"),
                ),
                JournalEntryLine(
                    account_id="acc_2",
                    credit=Decimal("50.00"),
                ),
            ],
        )
        assert entry.is_balanced() is False

    def test_is_balanced_multiple_lines(self):
        """Test is_balanced with multiple lines."""
        entry = JournalEntry(
            entry_date=date(2024, 1, 1),
            lines=[
                JournalEntryLine(account_id="acc_1", debit=Decimal("100.00")),
                JournalEntryLine(account_id="acc_2", debit=Decimal("50.00")),
                JournalEntryLine(account_id="acc_3", credit=Decimal("75.00")),
                JournalEntryLine(account_id="acc_4", credit=Decimal("75.00")),
            ],
        )
        assert entry.is_balanced() is True

    def test_is_balanced_empty_entry(self):
        """Test is_balanced with no lines."""
        entry = JournalEntry(entry_date=date(2024, 1, 1))
        assert entry.is_balanced() is True  # 0 == 0


class TestSuspenseItem:
    """Test SuspenseItem schema."""

    def test_required_fields(self):
        """Test SuspenseItem with required fields."""
        suspense = SuspenseItem(
            suspense_id="susp_001",
            transaction_id="txn_123",
            client_id="client_456",
            tenant_id="team_789",
        )
        assert suspense.suspense_id == "susp_001"
        assert suspense.transaction_id == "txn_123"
        assert suspense.client_id == "client_456"
        assert suspense.tenant_id == "team_789"
        assert suspense.reason == ""
        assert suspense.suspense_account_id == ""
        assert suspense.original_amount == ""
        assert suspense.description == ""
        assert suspense.parked_at is None
        assert suspense.resolved is False
        assert suspense.resolved_at is None
        assert suspense.resolution_account_id == ""
        assert suspense.resolved_by == ""
        assert suspense.clarification_attempts == 0
        assert suspense.schema_version == "1.0"

    def test_with_all_fields(self):
        """Test SuspenseItem with all fields."""
        parked_time = datetime(2024, 1, 15, 10, 30, 0)
        resolved_time = datetime(2024, 1, 20, 14, 45, 0)

        suspense = SuspenseItem(
            suspense_id="susp_002",
            transaction_id="txn_456",
            client_id="client_789",
            tenant_id="team_abc",
            reason=SuspenseReason.NEEDS_CLIENT_INPUT,
            suspense_account_id="acc_suspense",
            original_amount="150.00",
            description="Unclear vendor",
            parked_at=parked_time,
            resolved=True,
            resolved_at=resolved_time,
            resolution_account_id="acc_office",
            resolved_by="user_123",
            clarification_attempts=2,
        )
        assert suspense.reason == "needs_client_input"
        assert suspense.suspense_account_id == "acc_suspense"
        assert suspense.resolved is True
        assert suspense.resolved_at == resolved_time
        assert suspense.clarification_attempts == 2


class TestRiskFlag:
    """Test RiskFlag schema and KNOWN_RISK_CODES."""

    def test_risk_flag_from_classification(self):
        """Test RiskFlag from classification module."""
        risk = RiskFlag(
            code="LARGE_AMOUNT",
            severity=RiskSeverity.HIGH,
            message="Transaction exceeds $5,000",
        )
        assert risk.code == "LARGE_AMOUNT"
        assert risk.severity == "high"
        assert risk.message == "Transaction exceeds $5,000"

    def test_risk_flag_from_risk_module(self):
        """Test RiskFlag from risk module (has category field)."""
        risk = RiskFlagRisk(
            code="TAX_SENSITIVE",
            severity=RiskSeverity.MEDIUM,
            message="Affects Schedule C calculation",
            category="tax",
        )
        assert risk.code == "TAX_SENSITIVE"
        assert risk.severity == "medium"
        assert risk.category == "tax"

    def test_known_risk_codes(self):
        """Test KNOWN_RISK_CODES constant."""
        assert "OWNER_TXN_POSSIBLE" in KNOWN_RISK_CODES
        assert "LARGE_AMOUNT" in KNOWN_RISK_CODES
        assert "DUPLICATE_POSSIBLE" in KNOWN_RISK_CODES
        assert "TAX_SENSITIVE" in KNOWN_RISK_CODES
        assert "PERSONAL_EXPENSE" in KNOWN_RISK_CODES
        assert "ROUND_AMOUNT" in KNOWN_RISK_CODES
        assert "NEW_VENDOR" in KNOWN_RISK_CODES
        assert "PATTERN_BREAK" in KNOWN_RISK_CODES

    def test_known_risk_codes_descriptions(self):
        """Test KNOWN_RISK_CODES descriptions."""
        assert (
            KNOWN_RISK_CODES["OWNER_TXN_POSSIBLE"]
            == "Transfer may be owner-related (draw, loan, contribution)"
        )
        assert (
            KNOWN_RISK_CODES["LARGE_AMOUNT"]
            == "Transaction exceeds normal range for this category"
        )
        assert KNOWN_RISK_CODES["NEW_VENDOR"] == "First transaction with this vendor/payee"
