from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP
from core.exceptions import ValidationError

CENT=Decimal('0.01')

def money(v): return Decimal(str(v or 0)).quantize(CENT,rounding=ROUND_HALF_UP)

class CollectionService:
    def calculate(self, balance, payment):
        balance=money(balance); payment=money(payment)
        if balance<0 or payment<=0: raise ValidationError('بيانات التحصيل غير صحيحة.')
        if payment>balance: raise ValidationError('مبلغ التحصيل أكبر من الرصيد المستحق.')
        return {'before':balance,'paid':payment,'after':money(balance-payment),'settled':payment==balance}
