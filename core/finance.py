from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from .erp import ERPService, ERPValidationError, D, M


class FinanceService(ERPService):
    def customer_balance(self, customer_id):
        row = self.db.fetchone("""
            SELECT COALESCE((SELECT opening_balance FROM customers WHERE id=?),0)
             + COALESCE((SELECT SUM(total-paid) FROM documents WHERE party_id=? AND document_type='sale' AND status='posted'),0)
             - COALESCE((SELECT SUM(amount) FROM cash_transactions WHERE transaction_type='receipt' AND reference IN (SELECT reference FROM documents WHERE party_id=?)),0) balance
        """, (customer_id, customer_id, customer_id))
        return M(row["balance"] if row else 0)

    def supplier_balance(self, supplier_id):
        row = self.db.fetchone("""
            SELECT COALESCE((SELECT opening_balance FROM suppliers WHERE id=?),0)
             + COALESCE((SELECT SUM(total-paid) FROM documents WHERE party_id=? AND document_type='purchase' AND status='posted'),0)
             - COALESCE((SELECT SUM(amount) FROM cash_transactions WHERE transaction_type='payment' AND reference IN (SELECT reference FROM documents WHERE party_id=?)),0) balance
        """, (supplier_id, supplier_id, supplier_id))
        return M(row["balance"] if row else 0)

    def expense(self, reference, account_code, amount, description):
        amount = M(amount)
        if amount <= 0 or not description.strip():
            raise ERPValidationError("بيانات المصروف غير صحيحة")
        with self.db.connection() as conn:
            account = conn.execute("SELECT id FROM accounts WHERE code=? AND active=1", (account_code,)).fetchone()
            if not account:
                raise ERPValidationError("حساب المصروف غير موجود")
            exists = conn.execute("SELECT 1 FROM expenses WHERE reference=?", (reference,)).fetchone()
            if exists:
                raise ERPValidationError("مرجع المصروف مستخدم مسبقًا")
            expense_id = str(uuid4())
            conn.execute("INSERT INTO expenses(id,reference,account_id,amount,description) VALUES(?,?,?,?,?)", (expense_id, reference, account["id"], str(amount), description.strip()))
            conn.execute("INSERT INTO cash_transactions(id,reference,transaction_type,amount,description) VALUES(?,?,?,?,?)", (str(uuid4()), reference, "payment", str(amount), description.strip()))
            self._post_journal(conn, reference, description.strip(), [(account_code, amount, 0), ("1100", 0, amount)])
            conn.execute("INSERT INTO audit_log(action,entity_type,entity_id,details) VALUES(?,?,?,?)", ("POST", "expense", expense_id, reference))
            return {"reference": reference, "amount": amount}

    def cash_balance(self):
        row = self.db.fetchone("SELECT COALESCE(SUM(CASE WHEN transaction_type='receipt' THEN amount ELSE -amount END),0) balance FROM cash_transactions")
        return M(row["balance"] if row else 0)

    def ledger(self, account_code):
        row = self.db.fetchone("SELECT id FROM accounts WHERE code=?", (account_code,))
        if not row:
            raise ERPValidationError("الحساب غير موجود")
        return self.db.fetchall("""
            SELECT je.reference, je.description, je.created_at, jl.debit, jl.credit
            FROM journal_lines jl JOIN journal_entries je ON je.id=jl.entry_id
            WHERE jl.account_id=? ORDER BY je.created_at, jl.id
        """, (row["id"],))
