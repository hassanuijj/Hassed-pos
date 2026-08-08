from decimal import Decimal
from core.collection_flow import CollectionFlow


def test_collection_flow():
    result=CollectionFlow().complete(7,100,40,'COL-1')
    assert result['type']=='customer_collection'
    assert result['customer_id']==7
    assert result['after']==Decimal('60.00')
