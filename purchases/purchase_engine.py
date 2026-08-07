from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from core.exceptions import ValidationError
from inventory.stock_ledger import StockLedger

MONEY = Decimal("0.01")


def money(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(MONEY, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class PurchaseLine:
    product_id: int
    quantity: Decimal
    unit_cost: Decimal
    discount: Decimal = Decimal("0")

    @property
    def total(self) -> Decimal:
        quantity = Decimal(str(self.quantity))
        cost = money(self.unit_cost)
        discount = money(self.discount)
        if self.product_id <= 0:
            raise ValidationError("الصنف في سطر المشتريات غير صالح.")
        if quantity <= 0 or cost < 0 or discount < 0:
            raise ValidationError("بيانات سطر المشتريات غير صالحة.")
        gross = money(quantity * cost)
        if discount > gross:
            raise ValidationError("خصم المشتريات أكبر من قيمة السطر.")
        return money(gross - discount)


@dataclass(frozen=True)
class PurchaseTotals:
    subtotal: Decimal
    discount: Decimal
    total: Decimal


class PurchaseEngine:
    def calculate(self, lines: tuple[PurchaseLine, ...]) -> PurchaseTotals:
        if not lines:
            raise ValidationError("فاتورة المشتريات يجب أن تحتوي على صنف واحد على الأقل.")

        subtotal = Decimal("0")
        discount = Decimal("0")
        for line in lines:
            quantity = Decimal(str(line.quantity))
            unit_cost = money(line.unit_cost)
            line_discount = money(line.discount)

            # Evaluate the line through the canonical validation path before
            # aggregating it. This prevents invalid quantities, costs,
            # discounts, and product ids from bypassing PurchaseLine.total.
            line.total

            subtotal += money(quantity * unit_cost)
            discount += line_discount

        subtotal = money(subtotal)
        discount = money(discount)
        total = money(subtotal - discount)
        if total <= 0:
            raise ValidationError("إجمالي فاتورة المشتريات يجب أن يكون أكبر من صفر.")
        return PurchaseTotals(subtotal, discount, total)

    def receive(self, ledger: StockLedger, line: PurchaseLine) -> Decimal:
        total = line.total
        effective_cost = total / line.quantity if line.quantity else Decimal("0")
        ledger.receive(line.quantity, effective_cost)
        return total
