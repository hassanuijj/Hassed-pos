from __future__ import annotations
from decimal import Decimal
from core.exceptions import ValidationError

class CashReconciliation:
    def calculate(self, expected, counted):
        try:
            expected=Decimal(str(expected or 0)); counted=Decimal(str(counted or 0))
        except Exception as exc: raise ValidationError('قيمة الصندوق غير صحيحة.') from exc
        if expected < 0 or counted < 0: raise ValidationError('قيمة الصندوق لا يمكن أن تكون سالبة.')
        difference=counted-expected
        return {'expected':expected,'counted':counted,'difference':difference,'status':'balanced' if difference==0 else ('surplus' if difference>0 else 'shortage')}
