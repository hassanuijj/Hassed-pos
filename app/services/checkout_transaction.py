from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import Session

from core.exceptions import ValidationError
from app.services.pos_checkout import CheckoutRequest, POSCheckoutService
from app.services.stock_validation import StockValidationService


@dataclass(frozen=True)
class CheckoutResult:
    subtotal: Decimal
    discount: Decimal
    total: Decimal
    paid: Decimal
    remaining: Decimal


class CheckoutTransactionService:
    def __init__(self, session: Session):
        self.session = session
        self.calculator = POSCheckoutService()
        self.stock = StockValidationService()

    def execute(self, request: CheckoutRequest) -> CheckoutResult:
        totals = self.calculator.calculate(request)
        try:
            with self.session.begin():
                for line in request.lines:
                    row = self.session.execute(
                        text("SELECT quantity FROM stock_balances WHERE product_id=:product_id AND warehouse_id=:warehouse_id FOR UPDATE"),
                        {"product_id": line.product_id, "warehouse_id": request.warehouse_id},
                    ).mappings().first()
                    if row is None:
                        raise ValidationError(f"الصنف {line.product_id} غير موجود في المخزن المحدد.")
                    self.stock.validate_available(row["quantity"], line.quantity)
                raise NotImplementedError("ربط جداول الفواتير والمخزون والقيود سيُفعّل بعد مطابقة مخطط database.py الحالي.")
        except NotImplementedError:
            raise
        except Exception:
            self.session.rollback()
            raise
