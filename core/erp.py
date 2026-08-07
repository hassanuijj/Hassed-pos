from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4

from .database import Database

Q = Decimal("0.01")


def D(value) -> Decimal:
    return Decimal(str(value))


def M(value) -> Decimal:
    return D(value).quantize(Q, rounding=ROUND_HALF_UP)


class ERPValidationError(ValueError):
    pass


class InsufficientStockError(ERPValidationError):
    pass


class ERPService:
    """Persistent purchase/sales layer. Every posted document is atomic."""

    def __init__(self, db: Database):
        self.db = db

    def _account(self, code):
        row = self.db.fetchone("SELECT id FROM accounts WHERE code=? AND active=1", (code,))
        if not row:
            raise ERPValidationError(f"الحساب {code} غير موجود")
        return row["id"]

    def _stock(self, conn, product_id):
        row = conn.execute(
            "SELECT COALESCE(SUM(CASE WHEN movement_type='IN' THEN quantity ELSE -quantity END),0) q "
            "FROM stock_movements WHERE product_id=?",
            (product_id,),
        ).fetchone()
        return D(row[0])

    def _post_journal(self, conn, reference, description, lines):
        debit = sum((D(x[1]) for x in lines), D(0))
        credit = sum((D(x[2]) for x in lines), D(0))
        if debit != credit:
            raise ERPValidationError("القيد المحاسبي غير متوازن")
        entry_id = str(uuid4())
        conn.execute("INSERT INTO journal_entries(id,reference,description) VALUES(?,?,?)", (entry_id, reference, description))
        for account_code, dr, cr in lines:
            if D(dr) < 0 or D(cr) < 0 or (D(dr) > 0 and D(cr) > 0):
                raise ERPValidationError("كل سطر يجب أن يكون مدينًا أو دائنًا فقط")
            conn.execute(
                "INSERT INTO journal_lines(entry_id,account_id,debit,credit) VALUES(?,?,?,?)",
                (entry_id, self._account(account_code), str(M(dr)), str(M(cr))),
            )

    def _document(self, conn, reference, document_type, party_id, total, paid, lines):
        if not reference or not lines:
            raise ERPValidationError("المرجع وبنود المستند مطلوبة")
        exists = conn.execute("SELECT 1 FROM documents WHERE reference=?", (reference,)).fetchone()
        if exists:
            raise ERPValidationError("المرجع مستخدم مسبقًا")
        document_id = str(uuid4())
        conn.execute(
            "INSERT INTO documents(id,reference,document_type,party_id,total,paid,status) VALUES(?,?,?,?,?,?,?)",
            (document_id, reference, document_type, party_id, str(M(total)), str(M(paid)), "posted"),
        )
        for line in lines:
            conn.execute(
                "INSERT INTO document_lines(document_id,product_id,quantity,unit_price,discount,unit_cost) VALUES(?,?,?,?,?,?)",
                (document_id, line["product_id"], str(line["quantity"]), str(M(line["unit_price"])), str(M(line.get("discount", 0))), str(M(line.get("unit_cost", 0)))),
            )
        return document_id

    def purchase(self, reference, supplier_id, lines, paid=0):
        with self.db.connection() as conn:
            total = D(0)
            normalized = []
            for line in lines:
                qty, cost = D(line["quantity"]), M(line["unit_cost"])
                if qty <= 0 or cost < 0:
                    raise ERPValidationError("كمية أو تكلفة غير صحيحة")
                product = conn.execute("SELECT id FROM products WHERE id=? AND active=1", (line["product_id"],)).fetchone()
                if not product:
                    raise ERPValidationError("الصنف غير موجود")
                value = qty * cost - M(line.get("discount", 0))
                if value < 0:
                    raise ERPValidationError("الخصم أكبر من قيمة السطر")
                total += value
                normalized.append({**line, "quantity": qty, "unit_price": cost, "unit_cost": cost})
            paid = M(paid)
            total = M(total)
            if paid < 0 or paid > total:
                raise ERPValidationError("قيمة المدفوع غير صحيحة")
            doc_id = self._document(conn, reference, "purchase", supplier_id, total, paid, normalized)
            for line in normalized:
                conn.execute("INSERT INTO stock_movements(id,product_id,quantity,unit_cost,movement_type,reference) VALUES(?,?,?,?,?,?)", (str(uuid4()), line["product_id"], str(line["quantity"]), str(line["unit_cost"]), "IN", reference))
            credit_cash = paid
            credit_supplier = total - paid
            self._post_journal(conn, reference, "فاتورة شراء", [("1300", total, 0), ("1100", 0, credit_cash), ("2100", 0, credit_supplier)])
            conn.execute("INSERT INTO audit_log(action,entity_type,entity_id,details) VALUES(?,?,?,?)", ("POST", "purchase", doc_id, reference))
            return {"reference": reference, "total": total, "paid": paid, "supplier_balance": credit_supplier}

    def sale(self, reference, customer_id, lines, paid=0):
        with self.db.connection() as conn:
            total = D(0)
            cogs = D(0)
            normalized = []
            for line in lines:
                qty, price = D(line["quantity"]), M(line["unit_price"])
                if qty <= 0 or price < 0:
                    raise ERPValidationError("كمية أو سعر غير صحيح")
                product = conn.execute("SELECT id FROM products WHERE id=? AND active=1", (line["product_id"],)).fetchone()
                if not product:
                    raise ERPValidationError("الصنف غير موجود")
                available = self._stock(conn, line["product_id"])
                if available < qty:
                    raise InsufficientStockError(f"المخزون غير كاف للصنف {line['product_id']}")
                layers = conn.execute("SELECT quantity,unit_cost FROM stock_movements WHERE product_id=? AND movement_type='IN' AND quantity>0 ORDER BY created_at,id", (line["product_id"],)).fetchall()
                remaining = qty
                line_cogs = D(0)
                for layer in layers:
                    take = min(remaining, D(layer[0]))
                    line_cogs += take * D(layer[1])
                    remaining -= take
                    if remaining <= 0:
                        break
                if remaining > 0:
                    raise InsufficientStockError("تعذر تحديد تكلفة المخزون")
                total += qty * price - M(line.get("discount", 0))
                cogs += line_cogs
                normalized.append({**line, "quantity": qty, "unit_price": price, "unit_cost": line_cogs / qty})
            total, paid = M(total), M(paid)
            if paid < 0 or paid > total:
                raise ERPValidationError("قيمة المدفوع غير صحيحة")
            doc_id = self._document(conn, reference, "sale", customer_id, total, paid, normalized)
            for line in normalized:
                conn.execute("INSERT INTO stock_movements(id,product_id,quantity,unit_cost,movement_type,reference) VALUES(?,?,?,?,?,?)", (str(uuid4()), line["product_id"], str(line["quantity"]), str(line["unit_cost"]), "OUT", reference))
            self._post_journal(conn, reference, "فاتورة بيع", [("1100", paid, 0), ("1200", total-paid, 0), ("4100", 0, total), ("5100", cogs, 0), ("1300", 0, cogs)])
            conn.execute("INSERT INTO audit_log(action,entity_type,entity_id,details) VALUES(?,?,?,?)", ("POST", "sale", doc_id, reference))
            return {"reference": reference, "sales_total": total, "paid": paid, "customer_balance": total-paid, "cogs": M(cogs)}

    def cash_receipt(self, reference, amount, description="تحصيل نقدي"):
        amount = M(amount)
        if amount <= 0:
            raise ERPValidationError("قيمة السند يجب أن تكون موجبة")
        with self.db.connection() as conn:
            conn.execute("INSERT INTO cash_transactions(id,reference,transaction_type,amount,description) VALUES(?,?,?,?,?)", (str(uuid4()), reference, "receipt", str(amount), description))
            self._post_journal(conn, reference, description, [("1100", amount, 0), ("1200", 0, amount)])
        return amount

    def cash_payment(self, reference, amount, description="صرف نقدي"):
        amount = M(amount)
        if amount <= 0:
            raise ERPValidationError("قيمة السند يجب أن تكون موجبة")
        with self.db.connection() as conn:
            conn.execute("INSERT INTO cash_transactions(id,reference,transaction_type,amount,description) VALUES(?,?,?,?,?)", (str(uuid4()), reference, "payment", str(amount), description))
            self._post_journal(conn, reference, description, [("5200", amount, 0), ("1100", 0, amount)])
        return amount
