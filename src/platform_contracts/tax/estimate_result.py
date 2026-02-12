"""Tax computation result schema (mirrors es_tax API)."""

from decimal import Decimal

from pydantic import BaseModel, Field

from ..versioning import VersionedSchema


class QuarterlyPayment(BaseModel):
    """Single quarterly estimated payment."""

    quarter: int
    due_date: str = ""
    federal_amount: Decimal = Decimal("0")
    state_amount: Decimal = Decimal("0")
    total_amount: Decimal = Decimal("0")
    status: str = ""


class TaxComputeResponse(VersionedSchema):
    """Response from tax computation."""

    tenant_id: str = ""
    client_id: str = ""
    tax_year: int = 2025
    as_of_month: int = 0
    projected_annual_revenue: Decimal = Decimal("0")
    projected_annual_expenses: Decimal = Decimal("0")
    projected_net_income: Decimal = Decimal("0")
    total_federal_tax: Decimal = Decimal("0")
    total_state_tax: Decimal = Decimal("0")
    total_self_employment_tax: Decimal = Decimal("0")
    total_tax_liability: Decimal = Decimal("0")
    recommended_set_aside_pct: Decimal = Decimal("0")
    recommended_monthly_set_aside: Decimal = Decimal("0")
    quarterly_payments: list[QuarterlyPayment] = Field(default_factory=list)
    effective_tax_rate: Decimal = Decimal("0")
    marginal_tax_rate: Decimal = Decimal("0")
    qbi_deduction: Decimal = Decimal("0")
    engine_version: str = ""
