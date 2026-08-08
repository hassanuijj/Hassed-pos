from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import Session

from core.exceptions import ValidationError
from app.services.checkout_result import CheckoutResult
from app.services.pos_checkout import CheckoutRequest, POSCheckoutService
from app.services.stock_validation import StockValidationService
from app.services.account_mapping import AccountMappingService, SalesAccounts
from app.services.posting_validator import PostingValidator


@dataclass(frozen=True)
class CheckoutAccountConfig:
    cash_account_id: int
    receivable_account_id: int
    sales_account_id: int
    cogs_account_id: int
    inventory_account_id: int


class CheckoutTransactionAdapter:
    def __init__(self, session: Session):
        self.session = session
        self.calculator = POSCheckoutService()
        self.stock = StockValidationService()
        self.accounts = AccountMappingService()
        self.validator = PostingValidator()

    def validate_only(self, request: CheckoutRequest, config: CheckoutAccountConfig, status: str = "DRAFT"):
        totals = self.calculator.calculate(request)
        available = {}
        for line in request.lines:
            row = self.session.execute(text("SELECT quantity FROM stock_balances WHERE product_id=:product_id AND warehouse_id=:warehouse_id"), {"product_id": line.product_id, "warehouse_id": request.warehouse_id}).mappings().first()
            if row is None:
                raise ValidationError(f"الصنف {line.product_id} غير موجود في المخزن المحدد.")
            self.stock.validate_available(row["quantity"], line.quantity)
            available[line.product_id] = Decimal(str(row["quantity"]))
        accounts = SalesAccounts(config.cash_account_id, config.receivable_account_id, config.sales_account_id, config.cogs_account_id, config.inventory_account_id)
        self.accounts.validate_sales(accounts)
        self.validator.validate_postable(status, totals.total)
        return totals, available
