from __future__ import annotations

from decimal import Decimal

from .erp import D, M


class FinancialReports:
    def __init__(self, db):
        self.db = db

    def trial_balance(self):
        return self.db.fetchall("""
            SELECT a.code, a.name, a.account_type,
                   COALESCE(SUM(jl.debit),0) debit,
                   COALESCE(SUM(jl.credit),0) credit,
                   COALESCE(SUM(jl.debit-jl.credit),0) balance
            FROM accounts a LEFT JOIN journal_lines jl ON jl.account_id=a.id
            WHERE a.active=1 GROUP BY a.id ORDER BY a.code
        """)

    def income_statement(self):
        rows = self.trial_balance()
        revenue = sum((D(r["credit"]) - D(r["debit"]) for r in rows if r["account_type"] == "revenue"), D(0))
        expenses = sum((D(r["debit"]) - D(r["credit"]) for r in rows if r["account_type"] == "expense"), D(0))
        return {"revenue": M(revenue), "expenses": M(expenses), "net_profit": M(revenue-expenses)}

    def balance_sheet(self):
        rows = self.trial_balance()
        assets = sum((D(r["balance"]) for r in rows if r["account_type"] == "asset"), D(0))
        liabilities = sum((-D(r["balance"]) for r in rows if r["account_type"] == "liability"), D(0))
        equity = sum((-D(r["balance"]) for r in rows if r["account_type"] == "equity"), D(0))
        profit = self.income_statement()["net_profit"]
        return {"assets": M(assets), "liabilities": M(liabilities), "equity": M(equity), "current_profit": profit, "liabilities_equity": M(liabilities+equity+D(profit))}

    def sales_by_day(self):
        return self.db.fetchall("""
            SELECT substr(created_at,1,10) day, COUNT(*) invoices, COALESCE(SUM(total),0) total
            FROM documents WHERE document_type='sale' AND status='posted'
            GROUP BY substr(created_at,1,10) ORDER BY day DESC
        """)

    def purchases_by_day(self):
        return self.db.fetchall("""
            SELECT substr(created_at,1,10) day, COUNT(*) invoices, COALESCE(SUM(total),0) total
            FROM documents WHERE document_type='purchase' AND status='posted'
            GROUP BY substr(created_at,1,10) ORDER BY day DESC
        """)

    def top_products(self, limit=20):
        return self.db.fetchall("""
            SELECT p.id, p.name, COALESCE(SUM(dl.quantity),0) quantity,
                   COALESCE(SUM(dl.quantity*dl.unit_price-dl.discount),0) sales
            FROM products p JOIN document_lines dl ON dl.product_id=p.id
            JOIN documents d ON d.id=dl.document_id
            WHERE d.document_type='sale' AND d.status='posted'
            GROUP BY p.id ORDER BY sales DESC LIMIT ?
        """, (int(limit),))
