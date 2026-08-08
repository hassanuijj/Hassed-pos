from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Callable

from core.exceptions import ValidationError
from app.services.account_mapping import AccountMappingService, SalesAccounts
from app.services.checkout_result import CheckoutResult
from app.services.pos_checkout import CheckoutRequest, POSCheckoutService
from app.services.posting_validator import PostingValidator
from app.services.stock_validation import StockValidationService


@dataclass(frozen=True)
class PostingContext:
    invoice_id: int
    invoice_number: str
    journal_entry_id: int
    total: Decimal
    paid: Decimal
    remaining: Decimal


class CheckoutPipeline:
    def __init__(self):
        self.calculator = POSCheckoutService()
        self.stock = StockValidationService()
        self.accounts = AccountMappingService()
        self.validator = PostingValidator()

    def validate(self, request: CheckoutRequest, available_by_product: dict[int, Decimal], accounts: SalesAccounts, status: str, cost: Decimal) -> tuple[CheckoutResult, list[tuple[int, Decimal, Decimal]]]:
        totals = self.calculator.calculate(request)
        for line in request.lines:
            available = available_by_product.get(line.product_id)
            if available is None:
                raise ValidationError(f"الصنف {line.product_id} غير موجود في المخزن.")
            self.stock.validate_available(available, line.quantity)
        lines = self.accounts.build_lines(accounts, totals.total, totals.paid, cost)
        self.validator.validate_postable(status, totals.total)
        self.validator.validate_balanced(lines)
        return CheckoutResult(0, "", totals.total, totals.paid, totals.remaining, 0), lines

    def execute_atomic(self, transaction: Callable[[], PostingContext]) -> PostingContext:
        try:
            return transaction()
        except Exception:
            raise
