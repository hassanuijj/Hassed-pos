from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from core.exceptions import ValidationError

CENT = Decimal("0.01")


def money(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Transfer:
    amount: Decimal
    source_id: int
    destination_id: int
    reference: str | None = None


class TransferService:
    def validate(self, transfer: Transfer) -> Transfer:
        amount = money(transfer.amount)
        if amount <= 0:
            raise ValidationError("مبلغ التحويل يجب أن يكون أكبر من صفر.")
        if transfer.source_id == transfer.destination_id:
            raise ValidationError("لا يمكن التحويل إلى نفس الحساب.")
        if transfer.source_id <= 0 or transfer.destination_id <= 0:
            raise ValidationError("حسابات التحويل غير صالحة.")
        return Transfer(amount, transfer.source_id, transfer.destination_id, transfer.reference)
