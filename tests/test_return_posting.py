from decimal import Decimal
from core.return_posting import ReturnPostingService


def test_sales_return_increases_stock():
    result=ReturnPostingService().build({'items':[{'product_id':1,'quantity':2,'unit_amount':50}]},'sales_return')
    assert result['inventory']['direction']=='increase_stock'
    assert result['total']==Decimal('100')


def test_purchase_return_decreases_stock():
    result=ReturnPostingService().build({'items':[{'product_id':1,'quantity':2,'unit_amount':50}]},'purchase_return')
    assert result['inventory']['direction']=='decrease_stock'
