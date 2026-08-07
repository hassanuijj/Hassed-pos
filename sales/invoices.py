from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable

from sqlalchemy.orm import Session

from core.exceptions import ValidationError, NotFoundError
from models import Product


MONEY_QUANTUM = Decimal("0.01")


def money(value: Decimal | int | float | str) -> Decimal:
    return Decimal(str(value or 0)).quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class SaleLine:
    product_id: int
    quantity: Decimal
    unit_price: Decimal
    discount: Decimal = Decimal("0")
    tax: Decimal = Decimal("0")

    @property
    def gross(self) -> Decimal:
        return money(self.quantity * self.unit_price)

    @property
    def net(self) -> Decimal:
        value = self.gross - money(self.discount)
        if value < 0:
            raise ValidationError("خصم السطر لا يمكن أن يتجاوز إجمالي السطر.")
        return money(value)

    @property
    def total(self) -> Decimal:
        return money(self.net + money(self.tax))


@dataclass(frozen=True)
class SaleTotals:
    gross: Decimal
    discount: Decimal
    tax: Decimal
    net: Decimal
    total: Decimal


class SalesInvoiceService:
    """Domain validation and calculation layer for sales invoices."""

    def __init__(self, session: Session):
        self.session = session

    def validate_lines(self, company_id: int, lines: Iterable[SaleLine]) -> list[SaleLine]:
        normalized = list(lines)
        if not normalized:
            raise ValidationError("الفاتورة يجب أن تحتوي على صنف واحد على الأقل.")

        product_ids = {line.product_id for line in normalized}
        products = (
            self.session.query(Product)
            .filter(Product.company_id == company_id, Product.id.in_(product_ids), Product.active.is_(True))
            .all()
        )
        products_by_id = {product.id: product for product in products}

        for line in normalized:
            if line.quantity <= 0:
                raise ValidationError("كمية البيع يجب أن تكون أكبر من صفر.")
            if line.unit_price < 0:
                raise ValidationError("سعر البيع لا يمكن أن يكون سالبًا.")
            if line.discount < 0 or line.tax < 0:
                raise ValidationError("الخصم والضريبة لا يمكن أن يكونا سالبين.")
            if line.product_id not in products_by_id:
                raise NotFoundError(f"الصنف رقم {line.product_id} غير موجود.")

        return normalized

    def calculate_totals(self, lines: Iterable[SaleLine]) -> SaleTotals:
        lines = list(lines)
        gross = money(sum((line.gross for line in lines), Decimal("0")))
        discount = money(sum((money(line.discount) for line in lines), Decimal("0")))
        tax = money(sum((money(line.tax) for line in lines), Decimal("0")))
        net = money(gross - discount)
        total = money(net + tax)
        return SaleTotals(
            gross=gross,
            discount=discount,
            tax=tax,
            net=net,
            total=total,
        )
