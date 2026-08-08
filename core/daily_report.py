from __future__ import annotations
from decimal import Decimal

class DailyReport:
    def summarize(self, sales=None, collections=None, returns=None):
        sales=sales or []; collections=collections or []; returns=returns or []
        def amount(rows,key='total'):
            return sum((Decimal(str(r.get(key,0) or 0)) for r in rows),Decimal('0'))
        gross=amount(sales); collected=amount(collections,'paid'); returned=amount(returns)
        net=gross-returned
        return {'sales_count':len(sales),'gross_sales':gross,'collections':collected,'returns':returned,'net_sales':net,'cash_in':gross+collected-returned}
