from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from core.exceptions import ValidationError

CENT = Decimal("0.01")


def money(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class POSLine:
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    discount: Decimal = Decimal("0")

    @property
    def total(self) -> Decimal:
        quantity = Decimal(str(self.quantity))
        if quantity <= 0:
            raise ValidationError("كمية الصنف يجب أن تكون أكبر من صفر.")
        price = money(self.unit_price)
        discount = money(self.discount)
        gross = money(quantity * price)
        if discount < 0 or discount > gross:
            raise ValidationError("خصم السطر غير صالح.")
        return money(gross - discount)


@dataclass(frozen=True)
class CheckoutRequest:
    customer_id: int | None
    warehouse_id: int
    payment_method: str
    paid_amount: Decimal
    lines: tuple[POSLine, ...]
    company_id: int = 0


@dataclass(frozen=True)
class CheckoutTotals:
    subtotal: Decimal
    discount: Decimal
    total: Decimal
    paid: Decimal
    remaining: Decimal


class POSCheckoutService:
    def calculate(self, request: CheckoutRequest) -> CheckoutTotals:
        if not request.lines:
            raise ValidationError("الفاتورة يجب أن تحتوي على صنف واحد على الأقل.")
        if request.company_id <= 0:
            raise ValidationError("الشركة غير صالحة.")
        if request.warehouse_id <= 0:
            raise ValidationError("المخزن غير صالح.")
        if request.payment_method not in {"CASH", "CARD", "BANK", "CREDIT"}:
            raise ValidationError("طريقة الدفع غير مدعومة.")
        subtotal = money(sum((money(x.quantity * x.unit_price) for x in request.lines), Decimal("0")))
        discount = money(sum((money(x.discount) for x in request.lines), Decimal("0")))
        total = money(sum((x.total for x in request.lines), Decimal("0")))
        paid = money(request.paid_amount)
        if request.payment_method == "CREDIT" and paid != 0:
            raise ValidationError("فاتورة الآجل يجب أن تكون بدون دفعة في عملية الإنشاء.")
        if paid < 0 or paid > total:
            raise ValidationError("قيمة المدفوع غير صالحة.")
        return CheckoutTotals(subtotal, discount, total, paid, money(total - paid))
