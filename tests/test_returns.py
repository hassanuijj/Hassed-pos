from decimal import Decimal
import pytest
from core.exceptions import ValidationError
from core.returns import ReturnLine, ReturnService


def test_return_total_and_quantity():
    service=ReturnService()
    assert service.total([ReturnLine(2,50,5)]) == Decimal('105.00')
    assert service.validate_quantity(2,3) == Decimal('2')


def test_return_cannot_exceed_original():
    service=ReturnService()
    with pytest.raises(ValidationError):
        service.validate_quantity(4,3)


def test_return_cannot_be_empty():
    with pytest.raises(ValidationError):
        ReturnService().total([])


def test_duplicate_product_lines_are_aggregated():
    service=ReturnService()
    original=[{'product_id':1,'quantity':5}]
    returned=[{'product_id':1,'quantity':2},{'product_id':1,'quantity':3}]
    assert service.validate_against_original(returned,original)
