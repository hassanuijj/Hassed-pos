from __future__ import annotations
from collections import defaultdict
from decimal import Decimal

class SalesAnalytics:
    def summarize(self, sales):
        sales=sales or []
        by_cashier=defaultdict(lambda:{'count':0,'total':Decimal('0')})
        by_product=defaultdict(lambda:{'quantity':Decimal('0'),'total':Decimal('0')})
        total=Decimal('0')
        for sale in sales:
            amount=Decimal(str(sale.get('total',0) or 0)); total+=amount
            cashier=sale.get('cashier') or 'غير محدد'
            by_cashier[cashier]['count']+=1; by_cashier[cashier]['total']+=amount
            for item in sale.get('items',[]):
                pid=item.get('product_id',item.get('name'))
                by_product[pid]['quantity']+=Decimal(str(item.get('quantity',0) or 0))
                by_product[pid]['total']+=Decimal(str(item.get('total',0) or 0))
        return {'count':len(sales),'total':total,'by_cashier':dict(by_cashier),'by_product':dict(by_product)}
