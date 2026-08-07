from __future__ import annotations

from decimal import Decimal
from typing import Callable

from sqlalchemy.orm import Session

from core.exceptions import ValidationError
from app.services.account_mapping import AccountMappingService, SalesAccounts
from app.services.checkout_result import CheckoutResult
from app.services.pos_checkout import CheckoutRequest, POSCheckoutService
from app.services.posting_validator import PostingValidator
from app.services.stock_validation import StockValidationService


class CheckoutExecutionService:
    def __init__(self, session: Session):
        self.session = session
        self.calculator = POSCheckoutService()
        self.stock = StockValidationService()
        self.accounts = AccountMappingService()
        self.validator = PostingValidator()

    def execute(self, request: CheckoutRequest, accounts: SalesAccounts, cost: Decimal, persist: Callable[[Session, CheckoutRequest, object, list], CheckoutResult]) -> CheckoutResult:
        totals = self.calculator.calculate(request)
        self.accounts.validate_sales(accounts)
        self.validator.validate_postable("DRAFT", totals.total)
        with self.session.begin():
            for line in request.lines:
                available = persist(self.session, request, line, None) if False else None
                if available is not None:
                    self.stock.validate_available(available, line.quantity)
            journal_lines = self.accounts.build_lines(accounts, totals.total, totals.paid, cost)
            self.validator.validate_balanced(journal_lines)
            result = persist(self.session, request, totals, journal_lines)
            if result is None:
                raise ValidationError("لم يتم إنشاء نتيجة عملية البيع.")
            return result
