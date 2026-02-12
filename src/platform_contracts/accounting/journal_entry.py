"""Journal entry schemas."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from ..versioning import VersionedSchema


class JournalEntryLine(BaseModel):
    """Single line of a journal entry."""

    account_id: str
    account_name: str = ""
    debit: Decimal = Decimal("0")
    credit: Decimal = Decimal("0")
    description: str = ""
    entity_id: str = ""
    entity_type: str = ""


class JournalEntry(VersionedSchema):
    """Canonical journal entry."""

    entry_id: str = ""
    entry_date: date
    memo: str = ""
    lines: list[JournalEntryLine] = Field(default_factory=list)
    source: str = ""
    reference_id: str = ""
    is_adjusting: bool = False

    def is_balanced(self) -> bool:
        """Check if debits equal credits."""
        total_debits = sum(line.debit for line in self.lines)
        total_credits = sum(line.credit for line in self.lines)
        return total_debits == total_credits
