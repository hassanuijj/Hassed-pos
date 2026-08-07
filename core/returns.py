from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from core.exceptions import ValidationError

CENT = Decimal("0.01")


def money(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(CENT, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class ReturnLine:
    quantity: Decimal
    unit_amount: Decimal
    tax: Decimal = Decimal("0")

    @property
    def net(self) -> Decimal:
        quantity = Decimal(str(self.quantity))
        amount = Decimal(str(self.unit_amount))
        if quantity <= 0:
            raise ValidationError("كمية المرتجع يجب أن تكون أكبر من صفر.")
        if amount < 0:
            raise ValidationError("قيمة السطر لا يمكن أن تكون سالبة.")
        return money(quantity * amount)

    @property
    def total(self) -> Decimal:
        tax = money(self.tax)
        if tax < 0:
            raise ValidationError("ضريبة المرتجع لا يمكن أن تكون سالبة.")
        return money(self.net + tax)


class ReturnService:
    def validate_quantity(self, returned, original) -> Decimal:
        returned = Decimal(str(returned))
        original = Decimal(str(original))
        if returned <= 0:
            raise ValidationError("كمية المرتجع يجب أن تكون أكبر من صفر.")
        if returned > original:
            raise ValidationError("لا يمكن إرجاع كمية أكبر من الكمية الأصلية.")
        return returned

    def total(self, lines: list[ReturnLine]) -> Decimal:
        if not lines:
            raise ValidationError("المرتجع يجب أن يحتوي على سطر واحد على الأقل.")
        return money(sum((line.total for line in lines), Decimal("0")))

    def validate_against_original(self, returned_lines, original_lines):
        original = {}
        for line in original_lines:
            product_id = line["product_id"]
            original[product_id] = original.get(product_id, Decimal("0")) + Decimal(str(line["quantity"]))

        returned = {}
        for line in returned_lines:
            product_id = line["product_id"]
            returned[product_id] = returned.get(product_id, Decimal("0")) + Decimal(str(line["quantity"]))

        for product_id, qty in returned.items():
            self.validate_quantity(qty, original.get(product_id, Decimal("0")))
        return True
