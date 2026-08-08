from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class StatementEntry:
    entry_date: date
    reference: str
    description: str
    debit: Decimal
    credit: Decimal

    @property
    def net(self) -> Decimal:
        return self.debit - self.credit


@dataclass(frozen=True)
class AccountStatement:
    customer_id: int
    opening_balance: Decimal
    entries: tuple[StatementEntry, ...]

    @property
    def closing_balance(self) -> Decimal:
        return self.opening_balance + sum((entry.net for entry in self.entries), Decimal("0"))
