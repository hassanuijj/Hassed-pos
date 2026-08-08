from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from inventory.stock_ledger import StockLedger, StockIssue
from core.exceptions import ValidationError


@dataclass(frozen=True)
class StockMovementResult:
    quantity: Decimal
    unit_cost: Decimal
    total_cost: Decimal
    movement_type: str


class StockMovementService:
    def receive(self, ledger: StockLedger, quantity, unit_cost) -> StockMovementResult:
        quantity = Decimal(str(quantity))
        unit_cost = Decimal(str(unit_cost))
        ledger.receive(quantity, unit_cost)
        return StockMovementResult(quantity, unit_cost, quantity * unit_cost, "RECEIPT")

    def issue(self, ledger: StockLedger, quantity, method: str = "FIFO") -> StockMovementResult:
        if method.upper() == "FIFO":
            result: StockIssue = ledger.fifo_issue(quantity)
        elif method.upper() in {"AVERAGE", "WEIGHTED_AVERAGE"}:
            result = ledger.average_issue(quantity)
        else:
            raise ValidationError("طريقة تقييم المخزون غير مدعومة.")
        unit_cost = result.cost / result.quantity if result.quantity else Decimal("0")
        return StockMovementResult(result.quantity, unit_cost, result.cost, "ISSUE")
