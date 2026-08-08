from __future__ import annotations
from datetime import date, timedelta

class ForecastService:
    def __init__(self, db): self.db=db

    def product_forecast(self, days=30):
        rows=self.db.fetchall("""SELECT p.id,p.name,p.quantity,p.min_stock,COALESCE(SUM(i.quantity),0) sold
          FROM products p LEFT JOIN document_items i ON i.product_id=p.id
          LEFT JOIN documents d ON d.id=i.document_id AND d.document_type='sale'
          AND DATE(d.created_at)>=DATE('now',?)
          GROUP BY p.id,p.name,p.quantity,p.min_stock""",(f'-{days} day',))
        out=[]
        for r in rows:
            sold=float(r['sold'] or 0); daily=sold/days; qty=float(r['quantity'] or 0)
            cover=(qty/daily) if daily else None
            reorder=max(0, float(r['min_stock'] or 0)+daily*days-qty)
            if daily and (cover is None or cover<days): out.append({'name':r['name'],'daily':round(daily,2),'stock':qty,'days_cover':round(cover,1),'suggested_order':round(reorder,0)})
        return sorted(out,key=lambda x:x['days_cover'])

    def sales_summary(self, days=7):
        rows=self.db.fetchall("SELECT DATE(created_at) day,COALESCE(SUM(total),0) total,COUNT(*) count FROM documents WHERE document_type='sale' AND DATE(created_at)>=DATE('now',?) GROUP BY DATE(created_at) ORDER BY day",(f'-{days-1} day',))
        totals=[float(r['total'] or 0) for r in rows]
        avg=sum(totals)/len(totals) if totals else 0
        return {'days':days,'average_daily_sales':round(avg,2),'days':rows}
