from __future__ import annotations
from collections import defaultdict


class SmartAssistant:
    """Deterministic business suggestions based only on local ERP data."""
    def __init__(self, db): self.db=db

    def insights(self):
        out=[]
        try:
            rows=self.db.fetchall("SELECT name,quantity,min_stock FROM products WHERE quantity<=min_stock ORDER BY quantity")
            for r in rows[:10]: out.append({"type":"reorder","priority":"high","title":"اقتراح إعادة شراء","message":f"{r['name']} وصل إلى {r['quantity']}، والحد الأدنى {r['min_stock']}"})
        except Exception: pass
        try:
            rows=self.db.fetchall("""SELECT p.name,SUM(i.quantity) qty FROM document_items i JOIN products p ON p.id=i.product_id JOIN documents d ON d.id=i.document_id WHERE d.document_type='sale' GROUP BY p.id,p.name ORDER BY qty DESC LIMIT 5""")
            for r in rows: out.append({"type":"best_seller","priority":"info","title":"صنف سريع الحركة","message":f"{r['name']}: مبيعات {r['qty']} وحدة"})
        except Exception: pass
        try:
            rows=self.db.fetchall("SELECT reference,total,paid FROM documents WHERE document_type='sale' AND total>paid ORDER BY created_at LIMIT 10")
            for r in rows: out.append({"type":"collection","priority":"medium","title":"متابعة تحصيل","message":f"الفاتورة {r['reference']} متبقي منها {float(r['total'])-float(r['paid'])}"})
        except Exception: pass
        return out
