"""Tax computation request schema (mirrors es_tax API)."""

from decimal import Decimal

from pydantic import BaseModel, Field

from ..versioning import VersionedSchema


class TaxComputeRequest(VersionedSchema):
    """Request to compute estimated taxes."""

    tenant_id: str = ""
    client_id: str = ""
    tax_year: int = 2025
    as_of_month: int = Field(ge=1, le=12)
    filing_status: str = ""
    entity_type: str = ""
    state: str = ""
    gross_receipts_ytd: Decimal = Decimal("0")
    cost_of_goods_sold_ytd: Decimal = Decimal("0")
    total_expenses_ytd: Decimal = Decimal("0")
    officer_compensation_ytd: Decimal = Decimal("0")
    other_income_ytd: Decimal = Decimal("0")
    w2_income: Decimal = Decimal("0")
    spouse_w2_income: Decimal = Decimal("0")
    capital_gains: Decimal = Decimal("0")
    other_taxable_income: Decimal = Decimal("0")
    itemized_deductions: Decimal = Decimal("0")
    prior_year_overpayment: Decimal = Decimal("0")
    estimated_payments_ytd: Decimal = Decimal("0")
    qbi_eligible: bool = True
    qbi_prior_year_loss: Decimal = Decimal("0")
