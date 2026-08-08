from __future__ import annotations
from datetime import date


class WorkdayService:
    """Fast daily-work queries kept read-only and independent from posting logic."""
    def __init__(self, db):
        self.db = db

    def search(self, text, limit=30):
        q=f"%{text.strip()}%"
        return self.db.fetchall("""
            SELECT 'product' type,id,name,barcode FROM products WHERE name LIKE ? OR barcode LIKE ?
            UNION ALL SELECT 'customer',id,name,phone FROM customers WHERE name LIKE ? OR phone LIKE ?
            UNION ALL SELECT 'supplier',id,name,phone FROM suppliers WHERE name LIKE ? OR phone LIKE ?
            ORDER BY name LIMIT ?
        """, (q,q,q,q,q,q,limit))

    def alerts(self):
        alerts=[]
        low=self.db.fetchall("SELECT name,quantity,min_stock FROM products WHERE quantity<=min_stock ORDER BY quantity")
        for r in low: alerts.append({"type":"low_stock","title":"مخزون منخفض","message":f"{r['name']}: المتاح {r['quantity']} والحد {r['min_stock']}"})
        try:
            debt=self.db.fetchone("SELECT COALESCE(SUM(total-paid),0) amount FROM documents WHERE document_type='sale' AND total>paid")
            if debt and float(debt['amount'])>0: alerts.append({"type":"receivables","title":"تحصيلات مستحقة","message":f"إجمالي المستحق: {debt['amount']}"})
        except Exception: pass
        return alerts

    def today(self):
        d=date.today().isoformat()
        def scalar(sql):
            r=self.db.fetchone(sql,(d,)); return r[0] if r else 0
        return {
            "date": d,
            "sales": scalar("SELECT COALESCE(SUM(total),0) FROM documents WHERE document_type='sale' AND DATE(created_at)=?"),
            "purchases": scalar("SELECT COALESCE(SUM(total),0) FROM documents WHERE document_type='purchase' AND DATE(created_at)=?"),
            "expenses": scalar("SELECT COALESCE(SUM(amount),0) FROM cash_transactions WHERE transaction_type='PAYMENT' AND DATE(created_at)=?"),
            "alerts": self.alerts(),
        }
