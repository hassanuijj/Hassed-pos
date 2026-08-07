from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

MONEY_QUANTUM = Decimal("0.01")
QTY_QUANTUM = Decimal("0.000001")


def money(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)


def quantity(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(QTY_QUANTUM, rounding=ROUND_HALF_UP)
