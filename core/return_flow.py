from __future__ import annotations
from core.returns import ReturnService


class ReturnFlow:
    def __init__(self, db, inventory=None, finance=None):
        self.db = db
        self.returns = ReturnService(db)
        self.inventory = inventory
        self.finance = finance

    def prepare_sales(self, returned_lines, original_lines):
        return self.returns.prepare_sales_return(returned_lines, original_lines)

    def prepare_purchase(self, returned_lines, original_lines):
        return self.returns.prepare_purchase_return(returned_lines, original_lines)

    def validate_only(self, returned_lines, original_lines):
        self.returns.validate_against_original(returned_lines, original_lines)
        return True
