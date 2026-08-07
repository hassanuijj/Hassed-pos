from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from core.exceptions import ValidationError
from inventory.stock_ledger import StockLedger
from inventory.return_service import StockReturnService


@dataclass(frozen=True)
class ReturnPosting:
    quantity: Decimal
    total_cost: Decimal
    unit_cost: Decimal
    movement_type: str
    debit_account_id: int
    credit_account_id: int


class ReturnPostingService:
    def __init__(self):
        self.returns = StockReturnService()

    def customer_return(self, ledger: StockLedger, quantity, unit_cost, inventory_account_id: int, cogs_account_id: int) -> ReturnPosting:
        if inventory_account_id <= 0 or cogs_account_id <= 0:
            raise ValidationError("حسابات مرتجع العميل غير مهيأة.")
        result = self.returns.return_to_stock(ledger, quantity, unit_cost)
        return ReturnPosting(result.quantity, result.total_cost, result.unit_cost, result.movement_type, inventory_account_id, cogs_account_id)

    def supplier_return(self, ledger: StockLedger, quantity, method: str, payable_account_id: int, inventory_account_id: int) -> ReturnPosting:
        if payable_account_id <= 0 or inventory_account_id <= 0:
            raise ValidationError("حسابات مرتجع المورد غير مهيأة.")
        result = self.returns.return_to_supplier(ledger, quantity, method)
        return ReturnPosting(result.quantity, result.total_cost, result.unit_cost, result.movement_type, payable_account_id, inventory_account_id)
