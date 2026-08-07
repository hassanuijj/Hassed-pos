from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from core.exceptions import ValidationError
from inventory.stock_ledger import StockLedger
from inventory.stock_movement_service import StockMovementService


@dataclass(frozen=True)
class TransferResult:
    quantity: Decimal
    total_cost: Decimal
    unit_cost: Decimal


class StockTransferService:
    def __init__(self):
        self.movements = StockMovementService()

    def transfer(self, source: StockLedger, destination: StockLedger, quantity, method: str = "FIFO") -> TransferResult:
        quantity = Decimal(str(quantity))
        if quantity <= 0:
            raise ValidationError("كمية التحويل يجب أن تكون أكبر من صفر.")
        issued = self.movements.issue(source, quantity, method)
        destination.receive(issued.quantity, issued.unit_cost)
        return TransferResult(issued.quantity, issued.total_cost, issued.unit_cost)
