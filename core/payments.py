from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from core.exceptions import ValidationError, NotFoundError


CENT = Decimal("0.01")


def amount(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class PaymentAllocation:
    amount: Decimal
    method: str
    reference: str | None = None


class PaymentService:
    ALLOWED_METHODS = {"CASH", "CARD", "BANK", "TRANSFER", "CREDIT"}

    def __init__(self, session: Session):
        self.session = session

    def validate(self, total, allocations) -> list[PaymentAllocation]:
        total = amount(total)
        rows = [
            PaymentAllocation(amount(x.amount), x.method.upper(), x.reference)
            for x in allocations
        ]
        if total < 0:
            raise ValidationError("إجمالي الفاتورة لا يمكن أن يكون سالبًا.")
        if any(x.amount <= 0 for x in rows):
            raise ValidationError("مبلغ الدفع يجب أن يكون أكبر من صفر.")
        if any(x.method not in self.ALLOWED_METHODS for x in rows):
            raise ValidationError("طريقة الدفع غير مدعومة.")
        allocated = amount(sum((x.amount for x in rows), Decimal("0")))
        if allocated > total:
            raise ValidationError("إجمالي المدفوع أكبر من إجمالي الفاتورة.")
        return rows

    def remaining(self, total, allocations) -> Decimal:
        total = amount(total)
        allocated = amount(sum((amount(x.amount) for x in allocations), Decimal("0")))
        return amount(total - allocated)
