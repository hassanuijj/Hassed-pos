from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from core.exceptions import ValidationError

CENT = Decimal("0.01")


def money(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class CashMovement:
    amount: Decimal
    movement_type: str
    reference: str | None = None


class CashAccountService:
    ALLOWED_TYPES = {"RECEIPT", "PAYMENT", "TRANSFER_IN", "TRANSFER_OUT", "OPENING", "ADJUSTMENT"}

    def validate(self, movement: CashMovement) -> CashMovement:
        normalized = CashMovement(money(movement.amount), movement.movement_type.upper(), movement.reference)
        if normalized.amount <= 0:
            raise ValidationError("مبلغ الحركة النقدية يجب أن يكون أكبر من صفر.")
        if normalized.movement_type not in self.ALLOWED_TYPES:
            raise ValidationError("نوع الحركة النقدية غير مدعوم.")
        return normalized

    def signed_amount(self, movement: CashMovement) -> Decimal:
        movement = self.validate(movement)
        if movement.movement_type in {"RECEIPT", "TRANSFER_IN", "OPENING"}:
            return movement.amount
        return -movement.amount
