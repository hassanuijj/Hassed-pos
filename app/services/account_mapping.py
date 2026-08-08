from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from core.exceptions import ValidationError


@dataclass(frozen=True)
class SalesAccounts:
    cash_account_id: int
    receivable_account_id: int
    sales_account_id: int
    cogs_account_id: int
    inventory_account_id: int


class AccountMappingService:
    def validate_sales(self, accounts: SalesAccounts) -> SalesAccounts:
        values = (
            accounts.cash_account_id,
            accounts.receivable_account_id,
            accounts.sales_account_id,
            accounts.cogs_account_id,
            accounts.inventory_account_id,
        )
        if any(value <= 0 for value in values):
            raise ValidationError("يجب إعداد جميع الحسابات المحاسبية الخاصة بالمبيعات قبل الترحيل.")
        return accounts

    def build_lines(self, accounts: SalesAccounts, total: Decimal, paid: Decimal, cost: Decimal):
        total = Decimal(str(total))
        paid = Decimal(str(paid))
        cost = Decimal(str(cost))
        if total < 0 or paid < 0 or cost < 0 or paid > total:
            raise ValidationError("قيم القيد المحاسبي غير صحيحة.")
        receivable = total - paid
        lines = []
        if paid:
            lines.append((accounts.cash_account_id, paid, Decimal("0")))
        if receivable:
            lines.append((accounts.receivable_account_id, receivable, Decimal("0")))
        if total:
            lines.append((accounts.sales_account_id, Decimal("0"), total))
        if cost:
            lines.append((accounts.cogs_account_id, cost, Decimal("0")))
            lines.append((accounts.inventory_account_id, Decimal("0"), cost))
        return lines
