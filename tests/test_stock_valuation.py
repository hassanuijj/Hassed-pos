from decimal import Decimal
from core.stock_valuation import StockValuation

def test_stock_valuation():
    r=StockValuation().summarize([{'id':1,'quantity':10,'cost_price':25},{'id':2,'quantity':2,'cost_price':50}])
    assert r['total_value']==Decimal('350.00')
    assert r['items'][0]['stock_value']==Decimal('250.00')
