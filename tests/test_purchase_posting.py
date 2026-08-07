from decimal import Decimal

import pytest

from core.exceptions import ValidationError
from purchases.purchase_engine import PurchaseLine
from purchases.purchase_posting import PurchaseAccounts, PurchasePostingService


def accounts() -> PurchaseAccounts:
    return PurchaseAccounts(
        inventory_account_id=101,
        cash_account_id=102,
        payable_account_id=103,
    )


def test_cash_purchase_posts_inventory_against_cash():
    posting = PurchasePostingService().build(
        (
            PurchaseLine(
                product_id=1,
                quantity=Decimal("2"),
                unit_cost=Decimal("50"),
            ),
        ),
        accounts(),
        paid=Decimal("100"),
    )

    assert posting.total == Decimal("100.00")
    assert posting.paid == Decimal("100.00")
    assert posting.payable == Decimal("0.00")
    assert posting.lines == (
        (101, Decimal("100.00"), Decimal("0")),
        (102, Decimal("0"), Decimal("100.00")),
    )


def test_credit_purchase_posts_supplier_payable():
    posting = PurchasePostingService().build(
        (
            PurchaseLine(
                product_id=1,
                quantity=Decimal("3"),
                unit_cost=Decimal("40"),
            ),
        ),
        accounts(),
    )

    assert posting.total == Decimal("120.00")
    assert posting.paid == Decimal("0.00")
    assert posting.payable == Decimal("120.00")
    assert posting.lines == (
        (101, Decimal("120.00"), Decimal("0")),
        (103, Decimal("0"), Decimal("120.00")),
    )


def test_partial_purchase_splits_cash_and_payable():
    posting = PurchasePostingService().build(
        (
            PurchaseLine(
                product_id=1,
                quantity=Decimal("5"),
                unit_cost=Decimal("20"),
            ),
        ),
        accounts(),
        paid=Decimal("30"),
    )

    assert posting.total == Decimal("100.00")
    assert posting.paid == Decimal("30.00")
    assert posting.payable == Decimal("70.00")
    assert posting.lines == (
        (101, Decimal("100.00"), Decimal("0")),
        (102, Decimal("0"), Decimal("30.00")),
        (103, Decimal("0"), Decimal("70.00")),
    )


def test_purchase_rejects_overpayment():
    with pytest.raises(ValidationError):
        PurchasePostingService().build(
            (PurchaseLine(1, Decimal("1"), Decimal("25")),),
            accounts(),
            paid=Decimal("25.01"),
        )


def test_purchase_rejects_invalid_account_mapping():
    with pytest.raises(ValidationError):
        PurchasePostingService().build(
            (PurchaseLine(1, Decimal("1"), Decimal("25")),),
            PurchaseAccounts(0, 102, 103),
        )
