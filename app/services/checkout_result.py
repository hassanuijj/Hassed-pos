from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class CheckoutResult:
    invoice_id: int
    invoice_number: str
    total: Decimal
    paid: Decimal
    remaining: Decimal
    journal_entry_id: int
