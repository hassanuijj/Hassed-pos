from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP

CENT=Decimal('0.01')
def money(v): return Decimal(str(v or 0)).quantize(CENT, rounding=ROUND_HALF_UP)

class StockValuation:
    def summarize(self, products):
        rows=[]; total=Decimal('0')
        for p in products or []:
            qty=Decimal(str(p.get('quantity',0) or 0)); cost=money(p.get('cost_price',0))
            value=money(qty*cost); total+=value
            rows.append({'product_id':p.get('id'),'quantity':qty,'cost_price':cost,'stock_value':value})
        return {'items':rows,'total_value':total}
