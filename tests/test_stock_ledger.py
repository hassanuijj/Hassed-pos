from decimal import Decimal

import pytest

from core.exceptions import ValidationError
from inventory.stock_ledger import StockLedger


def test_fifo_issue_uses_oldest_layers_first():
    ledger = StockLedger()
    ledger.receive(Decimal("10"), Decimal("10"))
    ledger.receive(Decimal("5"), Decimal("20"))
    result = ledger.fifo_issue(Decimal("12"))
    assert result.quantity == Decimal("12.000000")
    assert result.cost == Decimal("140.00")
    assert ledger.quantity == Decimal("3.000000")


def test_weighted_average_issue():
    ledger = StockLedger()
    ledger.receive(Decimal("10"), Decimal("10"))
    ledger.receive(Decimal("10"), Decimal("20"))
    result = ledger.average_issue(Decimal("5"))
    assert result.cost == Decimal("75.00")
    assert ledger.quantity == Decimal("15.000000")


def test_issue_more_than_balance_fails():
    ledger = StockLedger()
    ledger.receive(Decimal("2"), Decimal("10"))
    with pytest.raises(ValidationError):
        ledger.fifo_issue(Decimal("3"))
