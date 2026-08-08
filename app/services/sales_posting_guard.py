from __future__ import annotations

from decimal import Decimal

from core.exceptions import ValidationError
from app.services.account_mapping import AccountMappingService, SalesAccounts
from app.services.posting_validator import PostingValidator


class SalesPostingGuard:
    def __init__(self):
        self.accounts = AccountMappingService()
        self.validator = PostingValidator()

    def validate(self, accounts: SalesAccounts, status: str, total, paid, cost):
        accounts = self.accounts.validate_sales(accounts)
        total = Decimal(str(total))
        paid = Decimal(str(paid))
        cost = Decimal(str(cost))
        self.validator.validate_postable(status, total)
        lines = self.accounts.build_lines(accounts, total, paid, cost)
        self.validator.validate_balanced(lines)
        if not lines:
            raise ValidationError("لا يمكن إنشاء قيد بيع فارغ.")
        return lines
