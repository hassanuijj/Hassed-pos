from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.orm import Session

from accounting.journal import JournalEntry, JournalLine, validate_lines
from core.exceptions import ValidationError
from inventory.stock import StockService
from models import AuditLog
from sales.models import SalesInvoice, SalesInvoiceLine
from app.services.pos_checkout import CheckoutRequest, POSCheckoutService

CENT = Decimal("0.01")
QTY = Decimal("0.000001")


def money(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(CENT, rounding=ROUND_HALF_UP)


def quantity(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(QTY, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class SalesAccountMap:
    cash_account_id: int
    receivable_account_id: int
    sales_account_id: int
    inventory_account_id: int
    cogs_account_id: int
    bank_account_id: int | None = None
    card_account_id: int | None = None


@dataclass(frozen=True)
class PostedSale:
    invoice_id: int
    invoice_number: str
    total: Decimal
    paid: Decimal
    remaining: Decimal
    journal_entry_id: int


class SalesPostingService:
    def __init__(self, session: Session, accounts: SalesAccountMap):
        self.session = session
        self.accounts = accounts
        self.calculator = POSCheckoutService()
        self.stock = StockService(session)

    def _payment_account(self, method: str) -> int:
        method = method.upper()
        if method == "CASH":
            return self.accounts.cash_account_id
        if method == "BANK":
            if self.accounts.bank_account_id is None:
                raise ValidationError("يجب إعداد حساب البنك قبل البيع بالدفع البنكي.")
            return self.accounts.bank_account_id
        if method == "CARD":
            if self.accounts.card_account_id is None:
                raise ValidationError("يجب إعداد حساب المدفوعات بالبطاقة قبل البيع بالبطاقة.")
            return self.accounts.card_account_id
        raise ValidationError("طريقة الدفع غير مدعومة.")

    def post(
        self,
        *,
        company_id: int,
        fiscal_year_id: int,
        currency_id: int,
        user_id: int,
        invoice_number: str,
        request: CheckoutRequest,
        exchange_rate: Decimal = Decimal("1"),
        notes: str | None = None,
    ) -> PostedSale:
        if request.company_id != company_id:
            raise ValidationError("الشركة في الطلب لا تطابق الشركة الحالية.")
        totals = self.calculator.calculate(request)
        exchange_rate = Decimal(str(exchange_rate))
        if exchange_rate <= 0:
            raise ValidationError("سعر الصرف يجب أن يكون أكبر من صفر.")
        if request.payment_method.upper() == "CREDIT" and request.customer_id is None:
            raise ValidationError("البيع الآجل يتطلب اختيار عميل.")
        if request.payment_method.upper() == "CREDIT" and totals.paid != 0:
            raise ValidationError("البيع الآجل لا يقبل دفعة عند إنشاء الفاتورة.")
        if request.payment_method.upper() != "CREDIT" and totals.paid == 0:
            raise ValidationError("يجب إدخال دفعة لطريقة الدفع المختارة.")

        with self.session.begin():
            invoice = SalesInvoice(
                company_id=company_id,
                customer_id=request.customer_id,
                warehouse_id=request.warehouse_id,
                currency_id=currency_id,
                invoice_number=invoice_number,
                status="DRAFT",
                payment_method=request.payment_method.upper(),
                subtotal=totals.subtotal,
                discount=totals.discount,
                tax=Decimal("0"),
                total=totals.total,
                paid=totals.paid,
                exchange_rate=exchange_rate,
                notes=notes,
                created_by=user_id,
            )
            self.session.add(invoice)
            self.session.flush()

            total_cost = Decimal("0")
            for line in request.lines:
                qty = quantity(line.quantity)
                movement = self.stock.issue(
                    company_id=company_id,
                    warehouse_id=request.warehouse_id,
                    product_id=line.product_id,
                    quantity=qty,
                    user_id=user_id,
                    reference_type="SALES_INVOICE",
                    reference_id=invoice.id,
                    reference_number=invoice_number,
                )
                line_cost = money(movement.total_cost)
                total_cost += line_cost
                self.session.add(SalesInvoiceLine(
                    invoice_id=invoice.id,
                    product_id=line.product_id,
                    quantity=qty,
                    unit_price=money(line.unit_price),
                    discount=money(line.discount),
                    tax=Decimal("0"),
                    total=line.total,
                    cost=line_cost,
                ))

            journal_lines: list[dict] = []
            method = request.payment_method.upper()
            if method == "CREDIT":
                journal_lines.append({"account_id": self.accounts.receivable_account_id, "debit": totals.total, "credit": 0})
            else:
                journal_lines.append({"account_id": self._payment_account(method), "debit": totals.paid, "credit": 0})
                remaining = money(totals.total - totals.paid)
                if remaining:
                    if request.customer_id is None:
                        raise ValidationError("الدفعة الجزئية تتطلب اختيار عميل لباقي المبلغ.")
                    journal_lines.append({"account_id": self.accounts.receivable_account_id, "debit": remaining, "credit": 0})

            journal_lines.append({"account_id": self.accounts.sales_account_id, "debit": 0, "credit": totals.total})
            if total_cost > 0:
                journal_lines.extend([
                    {"account_id": self.accounts.cogs_account_id, "debit": total_cost, "credit": 0},
                    {"account_id": self.accounts.inventory_account_id, "debit": 0, "credit": total_cost},
                ])

            for line in journal_lines:
                line.update({"currency_id": currency_id, "exchange_rate": exchange_rate})
            validate_lines(journal_lines)

            now = datetime.utcnow()
            journal = JournalEntry(
                company_id=company_id,
                fiscal_year_id=fiscal_year_id,
                entry_number=f"SI-{invoice_number}",
                entry_date=now,
                status="POSTED",
                description=f"Sales invoice {invoice_number}",
                created_by=user_id,
                posted_at=now,
                posted_by=user_id,
            )
            self.session.add(journal)
            self.session.flush()
            for line in journal_lines:
                debit = money(line["debit"])
                credit = money(line["credit"])
                self.session.add(JournalLine(
                    journal_entry_id=journal.id,
                    account_id=line["account_id"],
                    currency_id=currency_id,
                    debit=debit,
                    credit=credit,
                    exchange_rate=exchange_rate,
                    debit_base=money(debit * exchange_rate),
                    credit_base=money(credit * exchange_rate),
                    description=f"Sales invoice {invoice_number}",
                ))

            invoice.status = "POSTED"
            invoice.posted_at = now
            self.session.add(AuditLog(
                company_id=company_id,
                user_id=user_id,
                action="POST",
                entity_type="SalesInvoice",
                entity_id=invoice.id,
                details=f"Posted sales invoice {invoice_number}",
            ))
            return PostedSale(invoice.id, invoice_number, totals.total, totals.paid, totals.remaining, journal.id)
