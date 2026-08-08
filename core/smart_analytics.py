from __future__ import annotations

class SmartAnalytics:
    def __init__(self, db): self.db=db

    def insights(self):
        out=[]
        try:
            rows=self.db.fetchall("""SELECT p.name,p.quantity,p.min_stock,COALESCE(SUM(i.quantity),0) sold FROM products p LEFT JOIN document_items i ON i.product_id=p.id LEFT JOIN documents d ON d.id=i.document_id AND d.document_type='sale' GROUP BY p.id,p.name,p.quantity,p.min_stock""")
            for r in rows:
                sold=float(r['sold'] or 0); qty=float(r['quantity'] or 0); minimum=float(r['min_stock'] or 0)
                if sold==0 and qty>minimum: out.append({'type':'slow_stock','priority':'low','title':'صنف راكد','message':f"{r['name']} لا توجد له مبيعات مسجلة والمخزون {qty}"})
                if sold>0 and qty<=minimum: out.append({'type':'forecast','priority':'high','title':'إعادة طلب مبكرة','message':f"{r['name']} سريع الحركة والمخزون وصل {qty}"})
        except Exception: pass
        try:
            rows=self.db.fetchall("SELECT reference,total,paid FROM documents WHERE document_type='sale' AND paid>total")
            for r in rows: out.append({'type':'anomaly','priority':'high','title':'مراجعة فاتورة','message':f"الفاتورة {r['reference']} مدفوعها أكبر من إجماليها"})
        except Exception: pass
        return out
