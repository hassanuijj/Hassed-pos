from decimal import Decimal
from core.sales_analytics import SalesAnalytics

def test_sales_analytics():
    r=SalesAnalytics().summarize([{'cashier':'A','total':100,'items':[{'product_id':1,'quantity':2,'total':100}]},{'cashier':'B','total':50,'items':[]}])
    assert r['count']==2
    assert r['total']==Decimal('150')
    assert r['by_cashier']['A']['total']==Decimal('100')
    assert r['by_product'][1]['quantity']==Decimal('2')
