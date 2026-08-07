from __future__ import annotations

from decimal import Decimal

from core.exceptions import ValidationError


def positive_decimal(value, field: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except Exception as exc:
        raise ValidationError(f"قيمة {field} غير صالحة.") from exc
    if result <= 0:
        raise ValidationError(f"يجب أن تكون {field} أكبر من صفر.")
    return result


def non_negative_decimal(value, field: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except Exception as exc:
        raise ValidationError(f"قيمة {field} غير صالحة.") from exc
    if result < 0:
        raise ValidationError(f"لا يمكن أن تكون {field} سالبة.")
    return result


class IntegrityReport:
    def __init__(self):
        self.errors = []
        self.warnings = []

    @property
    def ok(self):
        return not self.errors

    def error(self, message: str):
        self.errors.append(message)

    def warning(self, message: str):
        self.warnings.append(message)

    def as_dict(self):
        return {"ok": self.ok, "errors": list(self.errors), "warnings": list(self.warnings)}


class IntegrityValidator:
    """Read-only consistency checks for accounting, documents, and stock."""
    def __init__(self, db):
        self.db = db

    def run(self):
        report = IntegrityReport()
        self._journals(report)
        self._documents(report)
        self._stock(report)
        return report

    def _journals(self, report):
        rows = self.db.fetchall("""
            SELECT je.id, je.reference, COALESCE(SUM(jl.debit),0) debit,
                   COALESCE(SUM(jl.credit),0) credit
            FROM journal_entries je LEFT JOIN journal_lines jl ON jl.entry_id=je.id
            GROUP BY je.id
        """)
        for row in rows:
            if Decimal(str(row["debit"])) != Decimal(str(row["credit"])):
                report.error(f"القيد غير متوازن: {row['reference']}")
            for line in self.db.fetchall("SELECT debit,credit FROM journal_lines WHERE entry_id=?", (row["id"],)):
                debit, credit = Decimal(str(line["debit"])), Decimal(str(line["credit"]))
                if debit < 0 or credit < 0:
                    report.error(f"قيمة سالبة في القيد: {row['reference']}")
                if debit > 0 and credit > 0:
                    report.error(f"السطر مدين ودائن معًا: {row['reference']}")

    def _documents(self, report):
        rows = self.db.fetchall("""
            SELECT d.reference, d.total,
                   COALESCE(SUM(dl.quantity*dl.unit_price-dl.discount),0) calculated
            FROM documents d LEFT JOIN document_lines dl ON dl.document_id=d.id
            GROUP BY d.id
        """)
        for row in rows:
            if Decimal(str(row["total"])) != Decimal(str(row["calculated"])):
                report.error(f"إجمالي المستند لا يطابق البنود: {row['reference']}")

    def _stock(self, report):
        rows = self.db.fetchall("""
            SELECT p.name, COALESCE(SUM(CASE WHEN sm.movement_type='IN' THEN sm.quantity ELSE -sm.quantity END),0) quantity
            FROM products p LEFT JOIN stock_movements sm ON sm.product_id=p.id
            GROUP BY p.id
        """)
        for row in rows:
            if Decimal(str(row["quantity"])) < 0:
                report.warning(f"مخزون سالب: {row['name']}")
