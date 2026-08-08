from __future__ import annotations
from datetime import datetime
from core.cash_reconciliation import CashReconciliation

class CashClosing:
    def __init__(self, reconciliation=None):
        self.reconciliation = reconciliation or CashReconciliation()
        self.history=[]

    def close(self, expected, counted, cashier='', note=''):
        result=self.reconciliation.calculate(expected,counted)
        record={**result,'cashier':cashier,'note':note,'closed_at':datetime.now().isoformat(timespec='seconds')}
        self.history.append(record)
        return record

    def last(self):
        return self.history[-1] if self.history else None
