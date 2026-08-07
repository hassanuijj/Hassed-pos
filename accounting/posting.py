from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from accounting.journal import JournalEntry, JournalLine, validate_lines
from core.exceptions import NotFoundError, ValidationError
from inventory.stock import StockService
from models import FiscalYear
from sales.models import SalesInvoice, SalesInvoiceLine
from purchases.models import PurchaseInvoice, PurchaseInvoiceLine


class InvoicePostingService:
    """Build and post balanced sales/purchase journals using one caller-owned transaction."""

    def __init__(self, session: Session):
        self.session = session
        self.stock = StockService(session)

    @staticmethod
    def dec(value) -> Decimal:
        return Decimal(str(value or 0))

    @staticmethod
    def _require_accounts(*account_ids: int | None) -> None:
        if any(account_id is None or int(account_id) <= 0 for account_id in account_ids):
            raise ValidationError("يجب تحديد جميع الحسابات المحاسبية المطلوبة قبل الترحيل.")

    def _fiscal_year(self, company_id: int, at: datetime) -> FiscalYear:
        fiscal = self.session.scalar(
            select(FiscalYear).where(
                FiscalYear.company_id == company_id,
                FiscalYear.start_date <= at.date(),
                FiscalYear.end_date >= at.date(),
                FiscalYear.status == "OPEN",
            )
        )
        if fiscal is None:
            raise ValidationError("لا توجد سنة مالية مفتوحة لهذا التاريخ.")
        return fiscal

    def _journal(self, *, company_id, user_id, number, at, description, lines):
        validate_lines(lines)
        fiscal = self._fiscal_year(company_id, at)
        existing = self.session.scalar(
            select(JournalEntry).where(
                JournalEntry.company_id == company_id,
                JournalEntry.entry_number == number,
            )
        )
        if existing is not None:
            raise ValidationError(f"القيد {number} موجود مسبقًا ولا يجوز ترحيله مرة أخرى.")
        entry = JournalEntry(
            company_id=company_id,
            fiscal_year_id=fiscal.id,
            entry_number=number,
            entry_date=at,
            status="POSTED",
            description=description,
            created_by=user_id,
            posted_at=at,
            posted_by=user_id,
        )
        self.session.add(entry)
        self.session.flush()
        for data in lines:
            self.session.add(
                JournalLine(
                    journal_entry_id=entry.id,
                    account_id=data["account_id"],
                    currency_id=data["currency_id"],
                    debit=data.get("debit", 0),
                    credit=data.get("credit", 0),
                    exchange_rate=data.get("exchange_rate", 1),
                    debit_base=data.get("debit_base", 0),
                    credit_base=data.get("credit_base", 0),
                    description=data.get("description"),
                )
            )
        self.session.flush()
        return entry

    def post_sale(self, *, company_id: int, invoice_id: int, user_id: int, revenue_account_id: int, inventory_account_id: int, cogs_account_id: int, receivable_account_id: int, cash_account_id: int | None = None, tax_account_id: int | None = None, posted_at: datetime | None = None):
        at = posted_at or datetime.utcnow()
        self._require_accounts(revenue_account_id, inventory_account_id, cogs_account_id, receivable_account_id)
        invoice = self.session.scalar(select(SalesInvoice).where(SalesInvoice.id == invoice_id, SalesInvoice.company_id == company_id).with_for_update())
        if invoice is None:
            raise NotFoundError("فاتورة البيع غير موجودة.")
        if invoice.status == "POSTED":
            raise ValidationError("الفاتورة مرحّلة مسبقًا ولا يمكن ترحيلها مرة أخرى.")
        if invoice.status not in {"DRAFT", "APPROVED"}:
            raise ValidationError("حالة فاتورة البيع لا تسمح بالترحيل.")
        lines = self.session.scalars(select(SalesInvoiceLine).where(SalesInvoiceLine.invoice_id == invoice.id)).all()
        if not lines:
            raise ValidationError("فاتورة البيع لا تحتوي على أصناف.")
        rate = self.dec(invoice.exchange_rate)
        total = self.dec(invoice.total)
        paid = self.dec(invoice.paid)
        if rate <= 0 or paid < 0 or paid > total or total <= 0:
            raise ValidationError("بيانات مبلغ أو سعر صرف فاتورة البيع غير صحيحة.")
        if paid > 0 and cash_account_id is None:
            raise ValidationError("يجب تحديد حساب الصندوق/الدفع للفواتير المسددة.")
        tax = self.dec(invoice.tax)
        if tax > 0 and tax_account_id is None:
            raise ValidationError("يوجد ضريبة في الفاتورة ويجب تحديد حساب الضريبة.")

        cost_total = Decimal("0")
        stock_movements = []
        for line in lines:
            movement = self.stock.issue(company_id=company_id, warehouse_id=invoice.warehouse_id, product_id=line.product_id, quantity=line.quantity, user_id=user_id, reference_type="SALES_INVOICE", reference_id=invoice.id, reference_number=invoice.invoice_number)
            line.cost = self.dec(movement.total_cost)
            cost_total += line.cost
            stock_movements.append(movement)

        net = self.dec(invoice.subtotal) - self.dec(invoice.discount)
        balance = total - paid
        lines_data = []
        if paid > 0:
            lines_data.append({"account_id": cash_account_id, "currency_id": invoice.currency_id, "debit": paid, "credit": 0, "exchange_rate": rate, "debit_base": paid * rate, "credit_base": 0, "description": "تحصيل فاتورة مبيعات"})
        if balance > 0:
            lines_data.append({"account_id": receivable_account_id, "currency_id": invoice.currency_id, "debit": balance, "credit": 0, "exchange_rate": rate, "debit_base": balance * rate, "credit_base": 0, "description": "ذمم عميل"})
        lines_data.append({"account_id": revenue_account_id, "currency_id": invoice.currency_id, "debit": 0, "credit": net, "exchange_rate": rate, "debit_base": 0, "credit_base": net * rate, "description": "مبيعات"})
        if tax > 0:
            lines_data.append({"account_id": tax_account_id, "currency_id": invoice.currency_id, "debit": 0, "credit": tax, "exchange_rate": rate, "debit_base": 0, "credit_base": tax * rate, "description": "ضريبة مخرجات"})
        lines_data.extend([
            {"account_id": cogs_account_id, "currency_id": invoice.currency_id, "debit": cost_total, "credit": 0, "exchange_rate": rate, "debit_base": cost_total * rate, "credit_base": 0, "description": "تكلفة البضاعة المباعة"},
            {"account_id": inventory_account_id, "currency_id": invoice.currency_id, "debit": 0, "credit": cost_total, "exchange_rate": rate, "debit_base": 0, "credit_base": cost_total * rate, "description": "إخراج من المخزون"},
        ])
        entry = self._journal(company_id=company_id, user_id=user_id, number=f"SALE-{invoice.invoice_number}", at=at, description=f"ترحيل فاتورة البيع {invoice.invoice_number}", lines=lines_data)
        invoice.status = "POSTED"
        invoice.posted_at = at
        self.session.flush()
        return {"invoice": invoice, "journal_entry": entry, "cost": cost_total, "stock_movements": stock_movements}

    def post_purchase(self, *, company_id: int, invoice_id: int, user_id: int, inventory_account_id: int, payable_account_id: int, cash_account_id: int | None = None, tax_input_account_id: int | None = None, posted_at: datetime | None = None):
        at = posted_at or datetime.utcnow()
        self._require_accounts(inventory_account_id, payable_account_id)
        invoice = self.session.scalar(select(PurchaseInvoice).where(PurchaseInvoice.id == invoice_id, PurchaseInvoice.company_id == company_id).with_for_update())
        if invoice is None:
            raise NotFoundError("فاتورة الشراء غير موجودة.")
        if invoice.status == "POSTED":
            raise ValidationError("الفاتورة مرحّلة مسبقًا ولا يمكن ترحيلها مرة أخرى.")
        if invoice.status not in {"DRAFT", "APPROVED"}:
            raise ValidationError("حالة فاتورة الشراء لا تسمح بالترحيل.")
        lines = self.session.scalars(select(PurchaseInvoiceLine).where(PurchaseInvoiceLine.invoice_id == invoice.id)).all()
        if not lines:
            raise ValidationError("فاتورة الشراء لا تحتوي على أصناف.")
        rate = self.dec(invoice.exchange_rate)
        total = self.dec(invoice.total)
        paid = self.dec(invoice.paid)
        if rate <= 0 or paid < 0 or paid > total or total <= 0:
            raise ValidationError("بيانات مبلغ أو سعر صرف فاتورة الشراء غير صحيحة.")
        if paid > 0 and cash_account_id is None:
            raise ValidationError("يجب تحديد حساب الصندوق/الدفع للفواتير المسددة.")
        tax = self.dec(invoice.tax)
        if tax > 0 and tax_input_account_id is None:
            raise ValidationError("يوجد ضريبة مشتريات ويجب تحديد حساب ضريبة المدخلات.")

        inventory_value = Decimal("0")
        for line in lines:
            net_line = self.dec(line.total) - self.dec(line.tax)
            if self.dec(line.quantity) <= 0 or net_line < 0:
                raise ValidationError("بيانات سطر المشتريات غير صحيحة.")
            unit_cost = net_line / self.dec(line.quantity)
            self.stock.receive(company_id=company_id, warehouse_id=invoice.warehouse_id, product_id=line.product_id, quantity=line.quantity, unit_cost=unit_cost, user_id=user_id, reference_type="PURCHASE_INVOICE", reference_id=invoice.id, reference_number=invoice.invoice_number)
            inventory_value += net_line

        journal_lines = []
        if inventory_value > 0:
            journal_lines.append({"account_id": inventory_account_id, "currency_id": invoice.currency_id, "debit": inventory_value, "credit": 0, "exchange_rate": rate, "debit_base": inventory_value * rate, "credit_base": 0, "description": "إضافة مشتريات للمخزون"})
        if tax > 0:
            journal_lines.append({"account_id": tax_input_account_id, "currency_id": invoice.currency_id, "debit": tax, "credit": 0, "exchange_rate": rate, "debit_base": tax * rate, "credit_base": 0, "description": "ضريبة مدخلات"})
        if paid > 0:
            journal_lines.append({"account_id": cash_account_id, "currency_id": invoice.currency_id, "debit": 0, "credit": paid, "exchange_rate": rate, "debit_base": 0, "credit_base": paid * rate, "description": "سداد فاتورة مشتريات"})
        balance = total - paid
        if balance > 0:
            journal_lines.append({"account_id": payable_account_id, "currency_id": invoice.currency_id, "debit": 0, "credit": balance, "exchange_rate": rate, "debit_base": 0, "credit_base": balance * rate, "description": "ذمم مورد"})
        entry = self._journal(company_id=company_id, user_id=user_id, number=f"PUR-{invoice.invoice_number}", at=at, description=f"ترحيل فاتورة الشراء {invoice.invoice_number}", lines=journal_lines)
        invoice.status = "POSTED"
        invoice.posted_at = at
        self.session.flush()
        return {"invoice": invoice, "journal_entry": entry, "inventory_value": inventory_value}
