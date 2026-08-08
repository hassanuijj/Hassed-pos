from __future__ import annotations
from decimal import Decimal

class ReorderAdvisor:
    def analyze(self, products):
        recommendations=[]
        for p in products or []:
            qty=Decimal(str(p.get('quantity',0) or 0)); minimum=Decimal(str(p.get('min_quantity',0) or 0)); target=Decimal(str(p.get('target_quantity',minimum) or 0))
            if qty<=minimum and target>qty:
                recommendations.append({'product_id':p.get('id'),'suggested_quantity':target-qty,'reason':'إعادة الطلب للوصول إلى الحد المستهدف'})
        return recommendations
