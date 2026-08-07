from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from core.exceptions import ValidationError
from purchases.purchase_engine import PurchaseEngine, PurchaseLine
from app.services.account_mapping import AccountMappingService, SalesAccounts
from app.services.posting_validator import PostingValidator


@dataclass(frozen=True)
class PurchaseAccounts:
    inventory_account_id: int
    payable_account_id: int


@dataclass(frozen=True)
class PurchasePosting:
    total: Decimal
    paid: Decimal
    payable: Decimal
    lines: tuple[tuple[int, Decimal, Decimal], ...]


class PurchasePostingService:
    def __init__(self):
        self.engine = PurchaseEngine()
        self.validator = PostingValidator()

    def build(self, lines: tuple[PurchaseLine, ...], accounts: PurchaseAccounts, paid: Decimal = Decimal("0")) -> PurchasePosting:
        totals = self.engine.calculate(lines)
        paid = Decimal(str(paid))
        if paid < 0 or paid > totals.total:
            raise ValidationError("قيمة المدفوع للمشتريات غير صالحة.")
        if accounts.inventory_account_id <= 0 or accounts.payable_account_id <= 0:
            raise ValidationError("يجب إعداد حساب المخزون والموردين قبل ترحيل المشتريات.")
        payable = totals.total - paid
        posting = (
            (accounts.inventory_account_id, totals.total, Decimal("0")),
            (accounts.payable_account_id, Decimal("0"), payable),
        )
        if paid:
            posting = (
                (accounts.inventory_account_id, totals.total, Decimal("0")),
                (accounts.payable_account_id, Decimal("0"), payable),
                (accounts.payable_account_id, paid, Decimal("0")),
            )
        self.validator.validate_balanced(posting)
        return PurchasePosting(totals.total, paid, payable, posting)
