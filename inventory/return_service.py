from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from core.exceptions import ValidationError
from inventory.stock_ledger import StockLedger


@dataclass(frozen=True)
class StockReturnResult:
    quantity: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    movement_type: str


class StockReturnService:
    def return_to_stock(self, ledger: StockLedger, quantity, unit_cost) -> StockReturnResult:
        quantity = Decimal(str(quantity))
        unit_cost = Decimal(str(unit_cost))
        if quantity <= 0:
            raise ValidationError("كمية المرتجع يجب أن تكون أكبر من صفر.")
        if unit_cost < 0:
            raise ValidationError("تكلفة المرتجع لا يمكن أن تكون سالبة.")
        ledger.receive(quantity, unit_cost)
        return StockReturnResult(quantity, unit_cost, quantity * unit_cost, "RETURN_IN")

    def return_to_supplier(self, ledger: StockLedger, quantity, method: str = "FIFO") -> StockReturnResult:
        quantity = Decimal(str(quantity))
        if quantity <= 0:
            raise ValidationError("كمية مرتجع المورد يجب أن تكون أكبر من صفر.")
        if method.upper() == "FIFO":
            issue = ledger.fifo_issue(quantity)
        elif method.upper() in {"AVERAGE", "WEIGHTED_AVERAGE"}:
            issue = ledger.average_issue(quantity)
        else:
            raise ValidationError("طريقة تقييم المخزون غير مدعومة.")
        unit_cost = issue.cost / issue.quantity if issue.quantity else Decimal("0")
        return StockReturnResult(issue.quantity, unit_cost, issue.cost, "RETURN_OUT")
