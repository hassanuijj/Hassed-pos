from __future__ import annotations

from decimal import Decimal

from core.exceptions import ValidationError


def positive_decimal(value, field: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except Exception as exc:
        raise ValidationError(f"قيمة {field} غير صالحة.") from exc
    if result <= 0:
        raise ValidationError(f"يجب أن تكون {field} أكبر من صفر.")
    return result


def non_negative_decimal(value, field: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except Exception as exc:
        raise ValidationError(f"قيمة {field} غير صالحة.") from exc
    if result < 0:
        raise ValidationError(f"لا يمكن أن تكون {field} سالبة.")
    return result
