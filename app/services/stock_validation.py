from __future__ import annotations

from decimal import Decimal

from core.exceptions import ValidationError


class StockValidationService:
    def validate_available(self, available, requested) -> Decimal:
        available = Decimal(str(available or 0))
        requested = Decimal(str(requested or 0))
        if requested <= 0:
            raise ValidationError("الكمية المطلوبة يجب أن تكون أكبر من صفر.")
        if available < requested:
            raise ValidationError(
                f"الرصيد المخزني غير كافٍ. المتاح: {available}، المطلوب: {requested}."
            )
        return requested
