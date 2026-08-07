from decimal import Decimal
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from core.exceptions import InsufficientStockError, NotFoundError, ValidationError
from models import Product, Warehouse, StockBalance, StockMovement


class StockService:
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def dec(value) -> Decimal:
        return Decimal(str(value or 0))

    def _product(self, company_id: int, product_id: int) -> Product:
        item = self.session.scalar(select(Product).where(Product.id == product_id, Product.company_id == company_id, Product.active.is_(True)))
        if item is None:
            raise NotFoundError("الصنف غير موجود أو غير نشط")
        return item

    def _warehouse(self, company_id: int, warehouse_id: int) -> Warehouse:
        item = self.session.scalar(select(Warehouse).where(Warehouse.id == warehouse_id, Warehouse.company_id == company_id, Warehouse.active.is_(True)))
        if item is None:
            raise NotFoundError("المخزن غير موجود أو غير نشط")
        return item

    def balance(self, company_id: int, warehouse_id: int, product_id: int) -> StockBalance:
        self._warehouse(company_id, warehouse_id)
        self._product(company_id, product_id)
        item = self.session.scalar(select(StockBalance).where(StockBalance.company_id == company_id, StockBalance.warehouse_id == warehouse_id, StockBalance.product_id == product_id).with_for_update())
        if item is None:
            item = StockBalance(company_id=company_id, warehouse_id=warehouse_id, product_id=product_id, quantity=0, total_cost=0, average_cost=0)
            self.session.add(item)
            self.session.flush()
        return item

    def receive(self, *, company_id: int, warehouse_id: int, product_id: int, quantity, unit_cost, user_id: int, reference_type=None, reference_id=None, reference_number=None):
        qty = self.dec(quantity)
        cost = self.dec(unit_cost)
        if qty <= 0:
            raise ValidationError("كمية الإدخال يجب أن تكون أكبر من صفر")
        if cost < 0:
            raise ValidationError("تكلفة الإدخال لا يمكن أن تكون سالبة")
        product = self._product(company_id, product_id)
        balance = self.balance(company_id, warehouse_id, product_id)
        old_qty = self.dec(balance.quantity)
        old_cost = self.dec(balance.total_cost)
        movement_cost = qty * cost
        new_qty = old_qty + qty
        new_cost = old_cost + movement_cost
        movement = StockMovement(company_id=company_id, warehouse_id=warehouse_id, product_id=product_id, movement_type="IN", quantity=qty, unit_cost=cost, total_cost=movement_cost, balance_quantity=new_qty, balance_cost=new_cost, reference_type=reference_type, reference_id=reference_id, reference_number=reference_number, movement_date=datetime.utcnow(), created_by=user_id)
        balance.quantity = new_qty
        balance.total_cost = new_cost
        balance.average_cost = new_cost / new_qty if new_qty else Decimal("0")
        self.session.add(movement)
        self.session.flush()
        return movement

    def issue(self, *, company_id: int, warehouse_id: int, product_id: int, quantity, user_id: int, reference_type=None, reference_id=None, reference_number=None):
        qty = self.dec(quantity)
        if qty <= 0:
            raise ValidationError("كمية الإخراج يجب أن تكون أكبر من صفر")
        product = self._product(company_id, product_id)
        balance = self.balance(company_id, warehouse_id, product_id)
        available = self.dec(balance.quantity)
        if qty > available:
            raise InsufficientStockError(f"المخزون غير كافٍ: المتاح {available} والمطلوب {qty}")
        unit_cost = self.dec(balance.average_cost)
        total_cost = qty * unit_cost
        new_qty = available - qty
        new_cost = self.dec(balance.total_cost) - total_cost
        if new_qty == 0:
            new_cost = Decimal("0")
        if new_cost < 0:
            new_cost = Decimal("0")
        movement = StockMovement(company_id=company_id, warehouse_id=warehouse_id, product_id=product_id, movement_type="OUT", quantity=qty, unit_cost=unit_cost, total_cost=total_cost, balance_quantity=new_qty, balance_cost=new_cost, reference_type=reference_type, reference_id=reference_id, reference_number=reference_number, movement_date=datetime.utcnow(), created_by=user_id)
        balance.quantity = new_qty
        balance.total_cost = new_cost
        balance.average_cost = new_cost / new_qty if new_qty else Decimal("0")
        self.session.add(movement)
        self.session.flush()
        return movement
