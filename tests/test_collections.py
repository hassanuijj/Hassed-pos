from decimal import Decimal
import pytest
from core.collections import CollectionService
from core.exceptions import ValidationError

def test_collection():
    r=CollectionService().calculate(100,40)
    assert r['after']==Decimal('60.00') and not r['settled']

def test_collection_cannot_exceed_balance():
    with pytest.raises(ValidationError): CollectionService().calculate(100,101)
