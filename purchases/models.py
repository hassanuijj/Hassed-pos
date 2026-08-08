from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class PurchaseInvoice(Base):
    __tablename__ = "purchase_invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id", ondelete="RESTRICT"), index=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False, index=True)
    currency_id: Mapped[int] = mapped_column(ForeignKey("currencies.id", ondelete="RESTRICT"), nullable=False)
    invoice_number: Mapped[str] = mapped_column(String(60), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="DRAFT", index=True)
    payment_method: Mapped[str] = mapped_column(String(30), nullable=False, default="CASH")
    subtotal: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False, default=0)
    discount: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False, default=0)
    tax: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False, default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False, default=0)
    paid: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False, default=0)
    exchange_rate: Mapped[Decimal] = mapped_column(Numeric(28, 12), nullable=False, default=1)
    notes: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime)

    __table_args__ = (
        Index("ix_purchase_invoice_company_number", "company_id", "invoice_number", unique=True),
    )


class PurchaseInvoiceLine(Base):
    __tablename__ = "purchase_invoice_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("purchase_invoices.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False, default=0)
    tax: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False, default=0)
    total: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
