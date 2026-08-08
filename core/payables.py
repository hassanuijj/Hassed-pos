from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from core.exceptions import ValidationError

CENT = Decimal("0.01")


def money(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(CENT, rounding=ROUND_HALF_UP)


class PayableService:
    def __init__(self, session: Session):
        self.session = session

    def outstanding(self, invoice_total, paid) -> Decimal:
        total = money(invoice_total)
        paid_amount = money(paid)
        if total < 0 or paid_amount < 0:
            raise ValidationError("إجمالي الفاتورة والمدفوع لا يمكن أن يكونا سالبين.")
        if paid_amount > total:
            raise ValidationError("المدفوع لا يمكن أن يتجاوز إجمالي الفاتورة.")
        return money(total - paid_amount)
