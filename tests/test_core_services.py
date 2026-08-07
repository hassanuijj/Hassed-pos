from decimal import Decimal

import pytest

from core.cash import CashAccountService, CashMovement
from core.discounts import fixed_discount, percentage_discount
from core.payments import PaymentAllocation, PaymentService
from core.returns import ReturnLine, ReturnService
from core.transfers import Transfer, TransferService
from core.exceptions import ValidationError


def test_cash_receipt_is_positive():
    service = CashAccountService()
    movement = CashMovement(Decimal("100.00"), "receipt")
    assert service.signed_amount(movement) == Decimal("100.00")


def test_cash_payment_is_negative():
    service = CashAccountService()
    movement = CashMovement(Decimal("40.00"), "payment")
    assert service.signed_amount(movement) == Decimal("-40.00")


def test_discount_percentage():
    assert percentage_discount(Decimal("1000"), Decimal("15")) == Decimal("150.00")


def test_fixed_discount_cannot_exceed_base():
    with pytest.raises(ValidationError):
        fixed_discount(Decimal("100"), Decimal("101"))


def test_payment_cannot_exceed_invoice():
    service = PaymentService(None)
    with pytest.raises(ValidationError):
        service.validate(Decimal("100"), [PaymentAllocation(Decimal("101"), "CASH")])


def test_return_quantity_cannot_exceed_original():
    service = ReturnService()
    with pytest.raises(ValidationError):
        service.validate_quantity(Decimal("11"), Decimal("10"))


def test_return_total():
    service = ReturnService()
    lines = [ReturnLine(Decimal("2"), Decimal("50"), Decimal("5"))]
    assert service.total(lines) == Decimal("105.00")


def test_transfer_cannot_use_same_account():
    service = TransferService()
    with pytest.raises(ValidationError):
        service.validate(Transfer(Decimal("100"), 1, 1))
