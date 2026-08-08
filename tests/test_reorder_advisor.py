from decimal import Decimal
from core.reorder_advisor import ReorderAdvisor

def test_reorder_advisor():
    result=ReorderAdvisor().analyze([{'id':1,'quantity':2,'min_quantity':3,'target_quantity':10},{'id':2,'quantity':8,'min_quantity':3,'target_quantity':10}])
    assert result[0]['suggested_quantity']==Decimal('8')
    assert len(result)==1
