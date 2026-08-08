from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP

CENT=Decimal('0.01')
def money(v): return Decimal(str(v or 0)).quantize(CENT, rounding=ROUND_HALF_UP)

class ProfitReport:
    def summarize(self, sales=None, purchases=None, returns=None, expenses=None):
        sales=sales or []; purchases=purchases or []; returns=returns or []; expenses=expenses or []
        revenue=sum((money(x.get('total')) for x in sales),Decimal('0'))
        cost=sum((money(x.get('cost_total',x.get('total'))) for x in purchases),Decimal('0'))
        returned=sum((money(x.get('total')) for x in returns),Decimal('0'))
        operating=sum((money(x.get('amount')) for x in expenses),Decimal('0'))
        net_revenue=revenue-returned
        gross_profit=net_revenue-cost
        net_profit=gross_profit-operating
        return {'revenue':net_revenue,'cost':cost,'gross_profit':gross_profit,'expenses':operating,'net_profit':net_profit}
