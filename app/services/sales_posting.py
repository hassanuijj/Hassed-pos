from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.orm import Session

from accounting.journal import JournalEntry, JournalLine, validate_lines
from core.exceptions import ValidationError
from models import AuditLog, Product, StockBalance, StockMovement
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
        totals = self.calculator.calculate(request)
        if exchange_rate <= 0:
            raise ValidationError("سعر الصرف يجب أن يكون أكبر من صفر.")
        if request.payment_method.upper() == "CREDIT" and request.customer_id is None:
            raise ValidationError("البيع الآجل يتطلب اختيار عميل.")

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
                stock = self.session.scalar(
                    select(StockBalance)
                    .where(
                        StockBalance.company_id == company_id,
                        StockBalance.warehouse_id == request.warehouse_id,
                        StockBalance.product_id == line.product_id,
                    )
                    .with_for_update()
                )
                if stock is None:
                    raise ValidationError(f"لا يوجد رصيد مخزني للصنف {line.product_id}.")
                if stock.quantity < qty:
                    raise ValidationError(f"الرصيد غير كاف للصنف {line.product_id}: المتاح {stock.quantity}، المطلوب {qty}.")

                product = self.session.get(Product, line.product_id)
                if product is None or product.company_id != company_id:
                    raise ValidationError(f"الصنف {line.product_id} غير صالح للشركة الحالية.")

                unit_cost = Decimal(str(stock.average_cost or product.purchase_price or 0))
                line_cost = money(qty * unit_cost)
                total_cost += line_cost
                invoice_line = SalesInvoiceLine(
                    invoice_id=invoice.id,
                    product_id=line.product_id,
                    quantity=qty,
                    unit_price=money(line.unit_price),
                    discount=money(line.discount),
                    tax=Decimal("0"),
                    total=line.total,
                    cost=line_cost,
                )
                self.session.add(invoice_line)

                stock.quantity = quantity(stock.quantity - qty)
                stock.total_cost = money(stock.quantity * Decimal(str(stock.average_cost or 0)))
                movement = StockMovement(
                    company_id=company_id,
                    warehouse_id=request.warehouse_id,
                    product_id=line.product_id,
                    movement_type="SALE",
                    quantity=-qty,
                    unit_cost=unit_cost,
                    total_cost=-line_cost,
                    balance_quantity=stock.quantity,
                    balance_cost=stock.total_cost,
                    reference_type="SALES_INVOICE",
                    reference_id=invoice.id,
                    reference_number=invoice_number,
                    created_by=user_id,
                )
                self.session.add(movement)

            debit_account = self.accounts.cash_account_id if request.payment_method.upper() != "CREDIT" else self.accounts.receivable_account_id
            lines = [
                {"account_id": debit_account, "debit": totals.total, "credit": 0, "currency_id": currency_id, "exchange_rate": exchange_rate},
                {"account_id": self.accounts.sales_account_id, "debit": 0, "credit": totals.total, "currency_id": currency_id, "exchange_rate": exchange_rate},
            ]
            if total_cost > 0:
                lines.extend([
                    {"account_id": self.accounts.cogs_account_id, "debit": total_cost, "credit": 0, "currency_id": currency_id, "exchange_rate": exchange_rate},
                    {"account_id": self.accounts.inventory_account_id, "debit": 0, "credit": total_cost, "currency_id": currency_id, "exchange_rate": exchange_rate},
                ])
            validate_lines(lines)

            journal = JournalEntry(
                company_id=company_id,
                fiscal_year_id=fiscal_year_id,
                entry_number=f"SI-{invoice_number}",
                entry_date=datetime.utcnow(),
                status="POSTED",
                description=f"Sales invoice {invoice_number}",
                created_by=user_id,
                posted_at=datetime.utcnow(),
                posted_by=user_id,
            )
            self.session.add(journal)
            self.session.flush()
            for line in lines:
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
            invoice.posted_at = datetime.utcnow()
            self.session.add(AuditLog(
                company_id=company_id,
                user_id=user_id,
                action="POST",
                entity_type="SalesInvoice",
                entity_id=invoice.id,
                details=f"Posted sales invoice {invoice_number}",
            ))
            return PostedSale(invoice.id, invoice_number, totals.total, totals.paid, totals.remaining, journal.id)
