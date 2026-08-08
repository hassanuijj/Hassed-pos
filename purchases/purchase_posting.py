from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from core.exceptions import ValidationError
from purchases.purchase_engine import PurchaseEngine, PurchaseLine
from app.services.posting_validator import PostingValidator


@dataclass(frozen=True)
class PurchaseAccounts:
    inventory_account_id: int
    cash_account_id: int
    payable_account_id: int

    def validate(self) -> None:
        if min(self.inventory_account_id, self.cash_account_id, self.payable_account_id) <= 0:
            raise ValidationError("يجب إعداد حساب المخزون والصندوق والموردين قبل ترحيل المشتريات.")


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

    def build(
        self,
        lines: tuple[PurchaseLine, ...],
        accounts: PurchaseAccounts,
        paid: Decimal = Decimal("0"),
    ) -> PurchasePosting:
        totals = self.engine.calculate(lines)
        paid = Decimal(str(paid))
        accounts.validate()
        if paid < 0 or paid > totals.total:
            raise ValidationError("قيمة المدفوع للمشتريات غير صالحة.")

        payable = totals.total - paid
        posting = [(accounts.inventory_account_id, totals.total, Decimal("0"))]
        if paid:
            posting.append((accounts.cash_account_id, Decimal("0"), paid))
        if payable:
            posting.append((accounts.payable_account_id, Decimal("0"), payable))

        self.validator.validate_balanced(posting)
        return PurchasePosting(
            total=totals.total,
            paid=paid,
            payable=payable,
            lines=tuple(posting),
        )
