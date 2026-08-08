from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from core.exceptions import ValidationError

CENT = Decimal("0.01")


def money(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(CENT, rounding=ROUND_HALF_UP)


def percentage_discount(base, percentage) -> Decimal:
    base = money(base)
    percentage = Decimal(str(percentage or 0))
    if percentage < 0 or percentage > 100:
        raise ValidationError("نسبة الخصم يجب أن تكون بين 0 و100.")
    return money(base * percentage / Decimal("100"))


def fixed_discount(base, discount) -> Decimal:
    base = money(base)
    discount = money(discount)
    if discount < 0 or discount > base:
        raise ValidationError("قيمة الخصم غير صحيحة.")
    return discount
