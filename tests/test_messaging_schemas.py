"""Tests for messaging, events, and tax schemas."""

from datetime import datetime, UTC
from decimal import Decimal

import pytest
from pydantic import ValidationError

from platform_contracts.messaging.message import SendMessageRequest, MessageDeliveryWebhook
from platform_contracts.messaging.conversation import (
    ConversationStep,
    StartConversationRequest,
    ConversationSession,
    ConversationReplyWebhook,
)
from platform_contracts.messaging.templates import (
    TemplateButton,
    WhatsAppTemplate,
    InteractiveMessage,
)
from platform_contracts.events.event import PlatformEvent
from platform_contracts.events.audit_event import AuditEvent
from platform_contracts.tax.estimate_request import TaxComputeRequest
from platform_contracts.tax.estimate_result import TaxComputeResponse, QuarterlyPayment


# ============================================================================
# MESSAGING - MESSAGE SCHEMAS
# ============================================================================


class TestSendMessageRequest:
    """Tests for SendMessageRequest schema."""

    def test_minimal_valid_message(self):
        """Test with only required fields."""
        msg = SendMessageRequest(
            tenant_id="tenant-123",
            client_id="client-456",
            contact_phone="+14155551234",
        )
        assert msg.tenant_id == "tenant-123"
        assert msg.client_id == "client-456"
        assert msg.contact_phone == "+14155551234"
        assert msg.contact_name == ""
        assert msg.channel == "whatsapp"
        assert msg.template_name == ""
        assert msg.template_params == {}
        assert msg.body == ""
        assert msg.context_type == ""
        assert msg.context_id == ""
        assert msg.context_data == {}

    def test_full_message_with_template(self):
        """Test message using template."""
        msg = SendMessageRequest(
            tenant_id="tenant-123",
            client_id="client-456",
            contact_phone="+14155551234",
            contact_name="John Doe",
            channel="whatsapp",
            template_name="payment_reminder",
            template_params={"amount": "500.00", "due_date": "2026-02-15"},
            context_type="invoice",
            context_id="inv-789",
            context_data={"invoice_number": "INV-2026-001"},
        )
        assert msg.template_name == "payment_reminder"
        assert msg.template_params["amount"] == "500.00"
        assert msg.context_type == "invoice"

    def test_full_message_with_body(self):
        """Test message with custom body text."""
        msg = SendMessageRequest(
            tenant_id="tenant-123",
            client_id="client-456",
            contact_phone="+14155551234",
            body="Your payment is due soon.",
            channel="sms",
        )
        assert msg.body == "Your payment is due soon."
        assert msg.channel == "sms"

    def test_missing_required_fields(self):
        """Test validation error when required fields missing."""
        with pytest.raises(ValidationError) as exc_info:
            SendMessageRequest()
        errors = exc_info.value.errors()
        field_names = {e["loc"][0] for e in errors}
        assert "tenant_id" in field_names
        assert "client_id" in field_names
        assert "contact_phone" in field_names


class TestMessageDeliveryWebhook:
    """Tests for MessageDeliveryWebhook schema."""

    def test_minimal_webhook(self):
        """Test with only required message_id."""
        webhook = MessageDeliveryWebhook(message_id="msg-123")
        assert webhook.message_id == "msg-123"
        assert webhook.conversation_id == ""
        assert webhook.channel_message_id == ""
        assert webhook.status == ""
        assert webhook.error_message == ""
        assert webhook.timestamp is None

    def test_full_webhook_success(self):
        """Test successful delivery webhook."""
        now = datetime.now(UTC)
        webhook = MessageDeliveryWebhook(
            message_id="msg-123",
            conversation_id="conv-456",
            channel_message_id="wa-msg-789",
            status="delivered",
            timestamp=now,
        )
        assert webhook.status == "delivered"
        assert webhook.timestamp == now
        assert webhook.error_message == ""

    def test_full_webhook_failure(self):
        """Test failed delivery webhook."""
        webhook = MessageDeliveryWebhook(
            message_id="msg-123",
            status="failed",
            error_message="Phone number not reachable",
        )
        assert webhook.status == "failed"
        assert webhook.error_message == "Phone number not reachable"


# ============================================================================
# MESSAGING - CONVERSATION SCHEMAS
# ============================================================================


class TestConversationStep:
    """Tests for ConversationStep schema."""

    def test_minimal_step(self):
        """Test step with only step_number."""
        step = ConversationStep(step_number=1)
        assert step.step_number == 1
        assert step.direction == ""
        assert step.body == ""
        assert step.buttons == []
        assert step.timestamp is None
        assert step.response == ""

    def test_full_outbound_step(self):
        """Test outbound step with buttons."""
        now = datetime.now(UTC)
        step = ConversationStep(
            step_number=1,
            direction="outbound",
            body="Would you like to proceed?",
            buttons=[{"id": "yes", "title": "Yes"}, {"id": "no", "title": "No"}],
            timestamp=now,
        )
        assert step.direction == "outbound"
        assert len(step.buttons) == 2
        assert step.buttons[0]["id"] == "yes"

    def test_full_inbound_step(self):
        """Test inbound step with response."""
        step = ConversationStep(
            step_number=2,
            direction="inbound",
            response="Yes",
        )
        assert step.direction == "inbound"
        assert step.response == "Yes"


class TestStartConversationRequest:
    """Tests for StartConversationRequest schema."""

    def test_minimal_conversation_start(self):
        """Test with only required fields."""
        req = StartConversationRequest(
            tenant_id="tenant-123",
            client_id="client-456",
            contact_phone="+14155551234",
        )
        assert req.tenant_id == "tenant-123"
        assert req.client_id == "client-456"
        assert req.contact_phone == "+14155551234"
        assert req.contact_name == ""
        assert req.channel == "whatsapp"
        assert req.flow_type == ""
        assert req.timeout_minutes == 1440

    def test_full_conversation_start(self):
        """Test with all fields."""
        req = StartConversationRequest(
            tenant_id="tenant-123",
            client_id="client-456",
            contact_phone="+14155551234",
            contact_name="Jane Doe",
            channel="whatsapp",
            flow_type="payment_confirmation",
            context_type="invoice",
            context_id="inv-789",
            context_data={"amount": "1000.00"},
            timeout_minutes=60,
        )
        assert req.flow_type == "payment_confirmation"
        assert req.context_type == "invoice"
        assert req.timeout_minutes == 60


class TestConversationSession:
    """Tests for ConversationSession schema."""

    def test_minimal_session(self):
        """Test with minimal fields."""
        session = ConversationSession(
            conversation_id="conv-123",
            contact_phone="+14155551234",
        )
        assert session.conversation_id == "conv-123"
        assert session.contact_phone == "+14155551234"
        assert session.channel == "whatsapp"
        assert session.status == "active"
        assert session.current_state == "initial"
        assert session.steps == []

    def test_full_session_with_steps(self):
        """Test session with conversation steps."""
        step1 = ConversationStep(
            step_number=1,
            direction="outbound",
            body="Hello! Would you like to confirm your payment?",
        )
        step2 = ConversationStep(
            step_number=2,
            direction="inbound",
            response="Yes",
        )
        now = datetime.now(UTC)

        session = ConversationSession(
            conversation_id="conv-123",
            contact_phone="+14155551234",
            channel="whatsapp",
            status="active",
            current_state="awaiting_confirmation",
            flow_type="payment_flow",
            context_type="invoice",
            context_id="inv-999",
            steps=[step1, step2],
            last_activity_at=now,
        )
        assert len(session.steps) == 2
        assert session.steps[0].step_number == 1
        assert session.steps[1].response == "Yes"
        assert session.current_state == "awaiting_confirmation"


class TestConversationReplyWebhook:
    """Tests for ConversationReplyWebhook schema."""

    def test_minimal_reply(self):
        """Test with only conversation_id."""
        reply = ConversationReplyWebhook(conversation_id="conv-123")
        assert reply.conversation_id == "conv-123"
        assert reply.tenant_id == ""
        assert reply.client_id == ""
        assert reply.response_text == ""
        assert reply.button_id == ""

    def test_full_text_reply(self):
        """Test reply with text."""
        now = datetime.now(UTC)
        reply = ConversationReplyWebhook(
            conversation_id="conv-123",
            tenant_id="tenant-123",
            client_id="client-456",
            contact_phone="+14155551234",
            response_text="Yes, I confirm",
            context_type="invoice",
            context_id="inv-789",
            timestamp=now,
        )
        assert reply.response_text == "Yes, I confirm"
        assert reply.button_id == ""

    def test_full_button_reply(self):
        """Test reply via button click."""
        reply = ConversationReplyWebhook(
            conversation_id="conv-123",
            tenant_id="tenant-123",
            button_id="confirm_yes",
            response_text="",
        )
        assert reply.button_id == "confirm_yes"
        assert reply.response_text == ""


# ============================================================================
# MESSAGING - TEMPLATE SCHEMAS
# ============================================================================


class TestTemplateButton:
    """Tests for TemplateButton schema."""

    def test_valid_button(self):
        """Test valid button."""
        button = TemplateButton(id="btn_1", title="Confirm")
        assert button.id == "btn_1"
        assert button.title == "Confirm"

    def test_button_max_length(self):
        """Test button title max_length validation."""
        # 20 characters exactly should be valid
        button = TemplateButton(id="btn_1", title="12345678901234567890")
        assert len(button.title) == 20

        # 21 characters should fail
        with pytest.raises(ValidationError) as exc_info:
            TemplateButton(id="btn_1", title="123456789012345678901")
        errors = exc_info.value.errors()
        assert any("title" in str(e["loc"]) for e in errors)


class TestWhatsAppTemplate:
    """Tests for WhatsAppTemplate schema."""

    def test_minimal_template(self):
        """Test with only required name."""
        template = WhatsAppTemplate(name="payment_reminder")
        assert template.name == "payment_reminder"
        assert template.language == "en_US"
        assert template.category == "UTILITY"
        assert template.components == []

    def test_full_template(self):
        """Test with all fields."""
        template = WhatsAppTemplate(
            name="payment_reminder",
            language="es_MX",
            category="MARKETING",
            components=[
                {"type": "HEADER", "format": "TEXT", "text": "Payment Due"},
                {"type": "BODY", "text": "Your payment of {{1}} is due on {{2}}"},
            ],
        )
        assert template.language == "es_MX"
        assert template.category == "MARKETING"
        assert len(template.components) == 2


class TestInteractiveMessage:
    """Tests for InteractiveMessage schema."""

    def test_minimal_interactive_message(self):
        """Test with only body_text."""
        msg = InteractiveMessage(body_text="Please choose an option:")
        assert msg.body_text == "Please choose an option:"
        assert msg.buttons == []
        assert msg.header_text == ""
        assert msg.footer_text == ""

    def test_full_interactive_message(self):
        """Test with all fields."""
        buttons = [
            TemplateButton(id="option_1", title="Yes"),
            TemplateButton(id="option_2", title="No"),
        ]
        msg = InteractiveMessage(
            body_text="Would you like to proceed with payment?",
            buttons=buttons,
            header_text="Payment Confirmation",
            footer_text="Reply within 24 hours",
        )
        assert msg.header_text == "Payment Confirmation"
        assert msg.footer_text == "Reply within 24 hours"
        assert len(msg.buttons) == 2
        assert msg.buttons[0].title == "Yes"


# ============================================================================
# EVENTS SCHEMAS
# ============================================================================


class TestPlatformEvent:
    """Tests for PlatformEvent schema."""

    def test_minimal_event(self):
        """Test with only required event_type."""
        event = PlatformEvent(event_type="transaction.classified")
        assert event.event_type == "transaction.classified"
        assert event.event_id == ""
        assert event.source_system == ""
        assert event.tenant_id == ""
        assert event.payload == {}
        assert event.correlation_id == ""
        assert event.timestamp is not None

    def test_full_event(self):
        """Test with all fields."""
        now = datetime.now(UTC)
        event = PlatformEvent(
            event_id="evt-123",
            event_type="transaction.posted",
            source_system="transactionflow-qbo",
            tenant_id="tenant-456",
            timestamp=now,
            payload={
                "transaction_id": "txn-789",
                "amount": "500.00",
                "status": "posted",
            },
            correlation_id="corr-999",
        )
        assert event.event_id == "evt-123"
        assert event.source_system == "transactionflow-qbo"
        assert event.payload["transaction_id"] == "txn-789"
        assert event.correlation_id == "corr-999"

    def test_missing_required_event_type(self):
        """Test validation error when event_type missing."""
        with pytest.raises(ValidationError) as exc_info:
            PlatformEvent()
        errors = exc_info.value.errors()
        assert any(e["loc"][0] == "event_type" for e in errors)


class TestAuditEvent:
    """Tests for AuditEvent schema."""

    def test_minimal_audit_event(self):
        """Test with all defaults."""
        event = AuditEvent()
        assert event.audit_id == ""
        assert event.event_type == ""
        assert event.actor_id == ""
        assert event.before_state == {}
        assert event.after_state == {}
        assert event.timestamp is not None

    def test_full_audit_event(self):
        """Test with all fields."""
        now = datetime.now(UTC)
        event = AuditEvent(
            audit_id="audit-123",
            event_type="transaction.updated",
            actor_id="user-456",
            actor_type="user",
            tenant_id="tenant-789",
            resource_type="transaction",
            resource_id="txn-999",
            action="update",
            before_state={"status": "pending", "amount": "100.00"},
            after_state={"status": "approved", "amount": "100.00"},
            metadata={"reason": "Manual approval by admin"},
            timestamp=now,
            ip_address="192.168.1.100",
        )
        assert event.audit_id == "audit-123"
        assert event.actor_type == "user"
        assert event.resource_type == "transaction"
        assert event.before_state["status"] == "pending"
        assert event.after_state["status"] == "approved"
        assert event.ip_address == "192.168.1.100"


# ============================================================================
# TAX SCHEMAS
# ============================================================================


class TestTaxComputeRequest:
    """Tests for TaxComputeRequest schema."""

    def test_minimal_request(self):
        """Test with only required as_of_month."""
        req = TaxComputeRequest(as_of_month=6)
        assert req.as_of_month == 6
        assert req.tenant_id == ""
        assert req.client_id == ""
        assert req.tax_year == 2025
        assert req.gross_receipts_ytd == Decimal("0")
        assert req.qbi_eligible is True

    def test_full_request(self):
        """Test with all fields."""
        req = TaxComputeRequest(
            tenant_id="tenant-123",
            client_id="client-456",
            tax_year=2026,
            as_of_month=8,
            filing_status="married_filing_jointly",
            entity_type="sole_proprietor",
            state="CA",
            gross_receipts_ytd=Decimal("100000.00"),
            cost_of_goods_sold_ytd=Decimal("30000.00"),
            total_expenses_ytd=Decimal("20000.00"),
            officer_compensation_ytd=Decimal("0"),
            other_income_ytd=Decimal("5000.00"),
            w2_income=Decimal("50000.00"),
            spouse_w2_income=Decimal("60000.00"),
            capital_gains=Decimal("10000.00"),
            other_taxable_income=Decimal("2000.00"),
            itemized_deductions=Decimal("15000.00"),
            prior_year_overpayment=Decimal("1000.00"),
            estimated_payments_ytd=Decimal("5000.00"),
            qbi_eligible=True,
            qbi_prior_year_loss=Decimal("2000.00"),
        )
        assert req.tax_year == 2026
        assert req.as_of_month == 8
        assert req.filing_status == "married_filing_jointly"
        assert req.entity_type == "sole_proprietor"
        assert req.state == "CA"
        assert req.gross_receipts_ytd == Decimal("100000.00")
        assert req.qbi_prior_year_loss == Decimal("2000.00")

    def test_as_of_month_validation_min(self):
        """Test as_of_month must be >= 1."""
        with pytest.raises(ValidationError) as exc_info:
            TaxComputeRequest(as_of_month=0)
        errors = exc_info.value.errors()
        assert any("as_of_month" in str(e["loc"]) for e in errors)

    def test_as_of_month_validation_max(self):
        """Test as_of_month must be <= 12."""
        with pytest.raises(ValidationError) as exc_info:
            TaxComputeRequest(as_of_month=13)
        errors = exc_info.value.errors()
        assert any("as_of_month" in str(e["loc"]) for e in errors)

    def test_as_of_month_valid_range(self):
        """Test all valid as_of_month values."""
        for month in range(1, 13):
            req = TaxComputeRequest(as_of_month=month)
            assert req.as_of_month == month


class TestQuarterlyPayment:
    """Tests for QuarterlyPayment schema."""

    def test_minimal_payment(self):
        """Test with only quarter."""
        payment = QuarterlyPayment(quarter=1)
        assert payment.quarter == 1
        assert payment.due_date == ""
        assert payment.federal_amount == Decimal("0")
        assert payment.state_amount == Decimal("0")
        assert payment.total_amount == Decimal("0")
        assert payment.status == ""

    def test_full_payment(self):
        """Test with all fields."""
        payment = QuarterlyPayment(
            quarter=2,
            due_date="2026-06-15",
            federal_amount=Decimal("3500.00"),
            state_amount=Decimal("1200.00"),
            total_amount=Decimal("4700.00"),
            status="upcoming",
        )
        assert payment.quarter == 2
        assert payment.due_date == "2026-06-15"
        assert payment.federal_amount == Decimal("3500.00")
        assert payment.state_amount == Decimal("1200.00")
        assert payment.total_amount == Decimal("4700.00")
        assert payment.status == "upcoming"


class TestTaxComputeResponse:
    """Tests for TaxComputeResponse schema."""

    def test_minimal_response(self):
        """Test with all defaults."""
        resp = TaxComputeResponse()
        assert resp.tenant_id == ""
        assert resp.client_id == ""
        assert resp.tax_year == 2025
        assert resp.as_of_month == 0
        assert resp.total_tax_liability == Decimal("0")
        assert resp.quarterly_payments == []

    def test_full_response_with_quarterly_payments(self):
        """Test with all fields and quarterly payments."""
        q1 = QuarterlyPayment(
            quarter=1,
            due_date="2026-04-15",
            federal_amount=Decimal("3000.00"),
            state_amount=Decimal("1000.00"),
            total_amount=Decimal("4000.00"),
            status="paid",
        )
        q2 = QuarterlyPayment(
            quarter=2,
            due_date="2026-06-15",
            federal_amount=Decimal("3000.00"),
            state_amount=Decimal("1000.00"),
            total_amount=Decimal("4000.00"),
            status="upcoming",
        )

        resp = TaxComputeResponse(
            tenant_id="tenant-123",
            client_id="client-456",
            tax_year=2026,
            as_of_month=8,
            projected_annual_revenue=Decimal("150000.00"),
            projected_annual_expenses=Decimal("50000.00"),
            projected_net_income=Decimal("100000.00"),
            total_federal_tax=Decimal("18000.00"),
            total_state_tax=Decimal("6000.00"),
            total_self_employment_tax=Decimal("14130.00"),
            total_tax_liability=Decimal("38130.00"),
            recommended_set_aside_pct=Decimal("25.42"),
            recommended_monthly_set_aside=Decimal("3177.50"),
            quarterly_payments=[q1, q2],
            effective_tax_rate=Decimal("24.00"),
            marginal_tax_rate=Decimal("32.00"),
            qbi_deduction=Decimal("20000.00"),
            engine_version="1.1.0",
        )
        assert resp.tenant_id == "tenant-123"
        assert resp.tax_year == 2026
        assert resp.as_of_month == 8
        assert resp.projected_annual_revenue == Decimal("150000.00")
        assert resp.total_tax_liability == Decimal("38130.00")
        assert resp.recommended_set_aside_pct == Decimal("25.42")
        assert resp.qbi_deduction == Decimal("20000.00")
        assert len(resp.quarterly_payments) == 2
        assert resp.quarterly_payments[0].status == "paid"
        assert resp.quarterly_payments[1].status == "upcoming"
        assert resp.engine_version == "1.1.0"

    def test_response_with_empty_quarterly_payments(self):
        """Test response can have empty quarterly_payments list."""
        resp = TaxComputeResponse(
            tenant_id="tenant-123",
            client_id="client-456",
            quarterly_payments=[],
        )
        assert resp.quarterly_payments == []
