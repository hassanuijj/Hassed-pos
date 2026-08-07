from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4

from .database import Database


Q = Decimal("0.01")


def money(value) -> Decimal:
    return Decimal(str(value)).quantize(Q, rounding=ROUND_HALF_UP)


class MasterDataService:
    def __init__(self, db: Database):
        self.db = db

    def create_product(self, name, barcode=None, cost=0, sale_price=0, min_stock=0, product_id=None):
        product_id = product_id or str(uuid4())
        self.db.execute(
            "INSERT INTO products(id, barcode, name, cost, sale_price, min_stock) VALUES(?,?,?,?,?,?)",
            (product_id, barcode, name.strip(), str(money(cost)), str(money(sale_price)), str(money(min_stock))),
        )
        return product_id

    def update_product(self, product_id, **fields):
        allowed = {"barcode", "name", "cost", "sale_price", "min_stock", "active"}
        fields = {k: v for k, v in fields.items() if k in allowed}
        if not fields:
            return
        if "name" in fields:
            fields["name"] = fields["name"].strip()
        for key in ("cost", "sale_price", "min_stock"):
            if key in fields:
                fields[key] = str(money(fields[key]))
        sql = ", ".join(f"{k}=?" for k in fields)
        self.db.execute(f"UPDATE products SET {sql} WHERE id=?", (*fields.values(), product_id))

    def products(self, active_only=True):
        sql = "SELECT * FROM products"
        if active_only:
            sql += " WHERE active=1"
        return self.db.fetchall(sql + " ORDER BY name")

    def create_customer(self, name, phone="", address="", opening_balance=0, customer_id=None):
        customer_id = customer_id or str(uuid4())
        self.db.execute(
            "INSERT INTO customers(id,name,phone,address,opening_balance) VALUES(?,?,?,?,?)",
            (customer_id, name.strip(), phone, address, str(money(opening_balance))),
        )
        return customer_id

    def create_supplier(self, name, phone="", address="", opening_balance=0, supplier_id=None):
        supplier_id = supplier_id or str(uuid4())
        self.db.execute(
            "INSERT INTO suppliers(id,name,phone,address,opening_balance) VALUES(?,?,?,?,?)",
            (supplier_id, name.strip(), phone, address, str(money(opening_balance))),
        )
        return supplier_id

    def customers(self):
        return self.db.fetchall("SELECT * FROM customers WHERE active=1 ORDER BY name")

    def suppliers(self):
        return self.db.fetchall("SELECT * FROM suppliers WHERE active=1 ORDER BY name")


class ChartOfAccountsService:
    DEFAULTS = [
        ("1100", "الصندوق", "asset"),
        ("1110", "البنك", "asset"),
        ("1200", "العملاء", "asset"),
        ("1300", "المخزون", "asset"),
        ("2100", "الموردون", "liability"),
        ("4100", "المبيعات", "revenue"),
        ("4110", "مرتجعات المبيعات", "revenue"),
        ("5100", "تكلفة المبيعات", "expense"),
        ("5110", "مرتجعات المشتريات", "expense"),
        ("5200", "المصروفات التشغيلية", "expense"),
        ("3100", "رأس المال", "equity"),
    ]

    def __init__(self, db: Database):
        self.db = db

    def seed_defaults(self):
        for code, name, account_type in self.DEFAULTS:
            row = self.db.fetchone("SELECT id FROM accounts WHERE code=?", (code,))
            if not row:
                self.db.execute(
                    "INSERT INTO accounts(id,code,name,account_type) VALUES(?,?,?,?)",
                    (str(uuid4()), code, name, account_type),
                )

    def all(self):
        return self.db.fetchall("SELECT * FROM accounts WHERE active=1 ORDER BY code")


class ReportingService:
    def __init__(self, db: Database):
        self.db = db

    def sales_summary(self):
        row = self.db.fetchone(
            "SELECT COALESCE(SUM(total),0) total, COUNT(*) count FROM documents WHERE document_type='sale' AND status='posted'"
        )
        return {"total": money(row["total"]), "count": row["count"]}

    def purchases_summary(self):
        row = self.db.fetchone(
            "SELECT COALESCE(SUM(total),0) total, COUNT(*) count FROM documents WHERE document_type='purchase' AND status='posted'"
        )
        return {"total": money(row["total"]), "count": row["count"]}

    def stock_summary(self):
        return self.db.fetchall("""
            SELECT p.id, p.name, p.barcode,
                   COALESCE(SUM(CASE WHEN sm.movement_type='IN' THEN sm.quantity ELSE -sm.quantity END),0) quantity,
                   p.min_stock
            FROM products p
            LEFT JOIN stock_movements sm ON sm.product_id=p.id
            GROUP BY p.id
            ORDER BY p.name
        """)

    def low_stock(self):
        return [r for r in self.stock_summary() if Decimal(str(r["quantity"])) <= Decimal(str(r["min_stock"]))]

    def profit_summary(self):
        sales = self.db.fetchone("SELECT COALESCE(SUM(total),0) v FROM documents WHERE document_type='sale' AND status='posted'")["v"]
        cogs = self.db.fetchone("SELECT COALESCE(SUM(debit),0) v FROM journal_lines jl JOIN journal_entries je ON je.id=jl.entry_id JOIN accounts a ON a.id=jl.account_id WHERE a.code='5100'")["v"]
        sales_returns = self.db.fetchone("SELECT COALESCE(SUM(total),0) v FROM documents WHERE document_type='sales_return' AND status='posted'")["v"]
        return {
            "sales": money(sales),
            "sales_returns": money(sales_returns),
            "cogs": money(cogs),
            "gross_profit": money(Decimal(str(sales)) - Decimal(str(sales_returns)) - Decimal(str(cogs)),),
        }
