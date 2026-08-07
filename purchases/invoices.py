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
class PurchaseLine:
    product_id: int
    quantity: Decimal
    unit_cost: Decimal
    discount: Decimal = Decimal("0")
    tax: Decimal = Decimal("0")

    @property
    def gross(self) -> Decimal:
        return money(self.quantity * self.unit_cost)

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
class PurchaseTotals:
    gross: Decimal
    discount: Decimal
    tax: Decimal
    net: Decimal
    total: Decimal


class PurchaseInvoiceService:
    def __init__(self, session: Session):
        self.session = session

    def validate_lines(self, company_id: int, lines: Iterable[PurchaseLine]) -> list[PurchaseLine]:
        normalized = list(lines)
        if not normalized:
            raise ValidationError("فاتورة الشراء يجب أن تحتوي على صنف واحد على الأقل.")

        product_ids = {line.product_id for line in normalized}
        products = (
            self.session.query(Product)
            .filter(Product.company_id == company_id, Product.id.in_(product_ids), Product.active.is_(True))
            .all()
        )
        products_by_id = {product.id: product for product in products}

        for line in normalized:
            if line.quantity <= 0:
                raise ValidationError("كمية الشراء يجب أن تكون أكبر من صفر.")
            if line.unit_cost < 0:
                raise ValidationError("تكلفة الشراء لا يمكن أن تكون سالبة.")
            if line.discount < 0 or line.tax < 0:
                raise ValidationError("الخصم والضريبة لا يمكن أن يكونا سالبين.")
            if line.product_id not in products_by_id:
                raise NotFoundError(f"الصنف رقم {line.product_id} غير موجود.")

        return normalized

    def calculate_totals(self, lines: Iterable[PurchaseLine]) -> PurchaseTotals:
        lines = list(lines)
        gross = money(sum((line.gross for line in lines), Decimal("0")))
        discount = money(sum((money(line.discount) for line in lines), Decimal("0")))
        tax = money(sum((money(line.tax) for line in lines), Decimal("0")))
        net = money(gross - discount)
        total = money(net + tax)
        return PurchaseTotals(gross, discount, tax, net, total)
