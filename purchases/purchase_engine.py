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
        subtotal = money(sum((money(Decimal(str(x.quantity)) * Decimal(str(x.unit_cost))) for x in lines), Decimal("0")))
        discount = money(sum((money(x.discount) for x in lines), Decimal("0")))
        return PurchaseTotals(subtotal, discount, money(subtotal - discount))

    def receive(self, ledger: StockLedger, line: PurchaseLine) -> Decimal:
        total = line.total
        effective_cost = total / line.quantity if line.quantity else Decimal("0")
        ledger.receive(line.quantity, effective_cost)
        return total
