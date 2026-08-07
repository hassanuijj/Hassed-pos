from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.orm import Session

from core.exceptions import ValidationError
from app.services.pos_checkout import CheckoutRequest, POSCheckoutService
from inventory.stock import StockService


@dataclass(frozen=True)
class CheckoutResult:
    subtotal: Decimal
    discount: Decimal
    total: Decimal
    paid: Decimal
    remaining: Decimal


class CheckoutTransactionService:
    """Validate a POS request inside the caller's SQLAlchemy transaction.

    Persistence and accounting posting are intentionally delegated to the
    invoice and posting services so this class cannot create a partial sale.
    """

    def __init__(self, session: Session):
        self.session = session
        self.calculator = POSCheckoutService()
        self.stock = StockService(session)

    def validate(self, request: CheckoutRequest) -> CheckoutResult:
        totals = self.calculator.calculate(request)
        for line in request.lines:
            balance = self.stock.balance(request.company_id, request.warehouse_id, line.product_id)
            self.stock._product(request.company_id, line.product_id)
            available = Decimal(str(balance.quantity or 0))
            if line.quantity > available:
                raise ValidationError(f"المخزون غير كافٍ للصنف {line.product_id}: المتاح {available} والمطلوب {line.quantity}")
        return CheckoutResult(
            subtotal=totals.subtotal,
            discount=totals.discount,
            total=totals.total,
            paid=totals.paid,
            remaining=totals.remaining,
        )

    def execute(self, request: CheckoutRequest) -> CheckoutResult:
        """Run validation without opening or committing a second transaction.

        The caller should create the invoice and call InvoicePostingService
        within its own `session.begin()` block. This avoids the previous
        SQLite-incompatible FOR UPDATE SQL and the unconditional
        NotImplementedError.
        """
        return self.validate(request)
