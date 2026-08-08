from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class AgingBucket:
    current: Decimal = Decimal("0")
    days_1_30: Decimal = Decimal("0")
    days_31_60: Decimal = Decimal("0")
    days_61_90: Decimal = Decimal("0")
    over_90: Decimal = Decimal("0")

    @property
    def total(self) -> Decimal:
        return self.current + self.days_1_30 + self.days_31_60 + self.days_61_90 + self.over_90


def classify_due(amount: Decimal, due_date: date, as_of: date) -> AgingBucket:
    amount = Decimal(amount)
    days = max((as_of - due_date).days, 0)
    if days == 0:
        return AgingBucket(current=amount)
    if days <= 30:
        return AgingBucket(days_1_30=amount)
    if days <= 60:
        return AgingBucket(days_31_60=amount)
    if days <= 90:
        return AgingBucket(days_61_90=amount)
    return AgingBucket(over_90=amount)
