from decimal import Decimal

import pytest

from accounting.journal import validate_lines
from core.exceptions import UnbalancedEntryError, ValidationError


def line(account_id, currency_id, debit=0, credit=0, rate=1):
    debit = Decimal(str(debit))
    credit = Decimal(str(credit))
    rate = Decimal(str(rate))
    return {
        "account_id": account_id,
        "currency_id": currency_id,
        "debit": debit,
        "credit": credit,
        "exchange_rate": rate,
        "debit_base": debit * rate,
        "credit_base": credit * rate,
    }


def test_balanced_entry_passes():
    validate_lines([line(1, 1, debit=100), line(2, 1, credit=100)])


def test_unbalanced_entry_fails():
    with pytest.raises(UnbalancedEntryError):
        validate_lines([line(1, 1, debit=100), line(2, 1, credit=90)])


def test_base_currency_mismatch_fails():
    with pytest.raises(UnbalancedEntryError):
        validate_lines([line(1, 1, debit=100, rate=2), line(2, 1, credit=100, rate=1)])


def test_line_cannot_be_both_debit_and_credit():
    with pytest.raises(ValidationError):
        validate_lines([line(1, 1, debit=100, credit=100)])
