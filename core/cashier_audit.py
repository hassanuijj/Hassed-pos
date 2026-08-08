from __future__ import annotations
from datetime import datetime

class CashierAudit:
    def __init__(self, db): self.db=db

    def record_sale(self, reference, total, paid, balance, cashier='system'):
        self.db.execute("""INSERT INTO cash_transactions(reference,transaction_type,amount,description,created_at) VALUES(?,?,?,?,?)""", (reference,'sale',paid,f'Cashier:{cashier}; balance:{balance}',datetime.now().isoformat(timespec='seconds')))
        return {'reference':reference,'cashier':cashier,'total':total,'paid':paid,'balance':balance}

    def today(self):
        return self.db.fetchall("SELECT reference,transaction_type,amount,description,created_at FROM cash_transactions WHERE DATE(created_at)=DATE('now') ORDER BY created_at DESC")
