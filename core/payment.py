from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP


def money(value):
    return Decimal(str(value or 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class PaymentService:
    def calculate(self, subtotal, discount=0, paid=0):
        subtotal=money(subtotal); discount=money(discount); paid=money(paid)
        if discount < 0 or discount > subtotal:
            raise ValueError('قيمة الخصم غير صحيحة')
        total=money(subtotal-discount)
        balance=money(max(total-paid, 0))
        change=money(max(paid-total, 0))
        return {'subtotal':subtotal,'discount':discount,'total':total,'paid':paid,'balance':balance,'change':change,'credit':balance>0}
