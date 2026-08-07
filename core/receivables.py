from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from core.exceptions import ValidationError

CENT = Decimal("0.01")


def money(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class BalanceSnapshot:
    invoice_total: Decimal
    paid: Decimal
    outstanding: Decimal


class ReceivableService:
    def __init__(self, session: Session):
        self.session = session

    def snapshot(self, invoice_total, paid) -> BalanceSnapshot:
        total = money(invoice_total)
        paid_amount = money(paid)
        if total < 0 or paid_amount < 0:
            raise ValidationError("إجمالي الفاتورة والمدفوع لا يمكن أن يكونا سالبين.")
        if paid_amount > total:
            raise ValidationError("المدفوع لا يمكن أن يتجاوز إجمالي الفاتورة.")
        return BalanceSnapshot(total, paid_amount, money(total - paid_amount))

    def credit_allowed(self, *, outstanding, credit_limit, current_balance=0) -> bool:
        return money(current_balance) + money(outstanding) <= money(credit_limit)
