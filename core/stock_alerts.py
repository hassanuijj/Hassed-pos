from __future__ import annotations
from decimal import Decimal

class StockAlerts:
    def analyze(self, products):
        alerts=[]
        for p in products or []:
            qty=Decimal(str(p.get('quantity',0) or 0)); minimum=Decimal(str(p.get('min_quantity',0) or 0))
            if qty<=0: alerts.append({'product_id':p.get('id'),'type':'out_of_stock','message':'الصنف نافد من المخزون'})
            elif minimum>0 and qty<=minimum: alerts.append({'product_id':p.get('id'),'type':'low_stock','message':'المخزون منخفض'})
        return alerts
