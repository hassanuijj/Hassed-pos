from __future__ import annotations

class ProfitMonitor:
    def __init__(self, db): self.db=db

    def alerts(self, minimum_margin=0.10):
        out=[]
        try:
            rows=self.db.fetchall("""SELECT p.name,p.cost_price,p.sale_price FROM products p WHERE p.sale_price IS NOT NULL""")
            for r in rows:
                cost=float(r['cost_price'] or 0); sale=float(r['sale_price'] or 0)
                margin=(sale-cost)/sale if sale else 0
                if sale>0 and margin<minimum_margin:
                    out.append({'type':'low_margin','priority':'medium','title':'هامش ربح منخفض','message':f"{r['name']}: الهامش {margin:.1%}"})
        except Exception: pass
        return out
