from __future__ import annotations

from decimal import Decimal

from core.exceptions import ValidationError


class PostingValidator:
    def validate_balanced(self, lines) -> None:
        debit = sum((Decimal(str(line[1])) for line in lines), Decimal("0"))
        credit = sum((Decimal(str(line[2])) for line in lines), Decimal("0"))
        if debit.quantize(Decimal("0.01")) != credit.quantize(Decimal("0.01")):
            raise ValidationError(f"القيد غير متوازن: المدين {debit} مقابل الدائن {credit}.")

    def validate_postable(self, document_status: str, total: Decimal) -> None:
        if document_status not in {"DRAFT", "APPROVED"}:
            raise ValidationError("المستند ليس في حالة تسمح بالترحيل.")
        if Decimal(str(total)) <= 0:
            raise ValidationError("لا يمكن ترحيل مستند بإجمالي غير موجب.")
