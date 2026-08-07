from datetime import datetime
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session
from core.exceptions import InsufficientStockError, NotFoundError, ValidationError
from models import Product, Warehouse, StockBalance, StockMovement, StockCostLayer


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
        self.session.add(StockCostLayer(company_id=company_id, warehouse_id=warehouse_id, product_id=product_id, source_movement_id=movement.id, original_quantity=qty, remaining_quantity=qty, unit_cost=cost, created_at=datetime.utcnow(), active=True))
        self.session.flush()
        return movement

    def _issue_fifo(self, company_id: int, warehouse_id: int, product_id: int, quantity: Decimal) -> Decimal:
        layers = self.session.scalars(select(StockCostLayer).where(StockCostLayer.company_id == company_id, StockCostLayer.warehouse_id == warehouse_id, StockCostLayer.product_id == product_id, StockCostLayer.remaining_quantity > 0, StockCostLayer.active.is_(True)).order_by(StockCostLayer.created_at, StockCostLayer.id).with_for_update()).all()
        available = sum((self.dec(layer.remaining_quantity) for layer in layers), Decimal("0"))
        if quantity > available:
            raise InsufficientStockError(f"المخزون غير كافٍ: المتاح {available} والمطلوب {quantity}")
        remaining = quantity
        total_cost = Decimal("0")
        for layer in layers:
            if remaining <= 0:
                break
            used = min(remaining, self.dec(layer.remaining_quantity))
            total_cost += used * self.dec(layer.unit_cost)
            layer.remaining_quantity = self.dec(layer.remaining_quantity) - used
            if layer.remaining_quantity <= 0:
                layer.remaining_quantity = Decimal("0")
                layer.active = False
            remaining -= used
        return total_cost

    def issue(self, *, company_id: int, warehouse_id: int, product_id: int, quantity, user_id: int, reference_type=None, reference_id=None, reference_number=None):
        qty = self.dec(quantity)
        if qty <= 0:
            raise ValidationError("كمية الإخراج يجب أن تكون أكبر من صفر")
        product = self._product(company_id, product_id)
        balance = self.balance(company_id, warehouse_id, product_id)
        available = self.dec(balance.quantity)
        if qty > available:
            raise InsufficientStockError(f"المخزون غير كافٍ: المتاح {available} والمطلوب {qty}")
        method = (product.costing_method or "WEIGHTED_AVERAGE").upper()
        if method == "FIFO":
            total_cost = self._issue_fifo(company_id, warehouse_id, product_id, qty)
        elif method in {"WEIGHTED_AVERAGE", "AVERAGE"}:
            unit_cost = self.dec(balance.average_cost)
            total_cost = qty * unit_cost
            layers = self.session.scalars(select(StockCostLayer).where(StockCostLayer.company_id == company_id, StockCostLayer.warehouse_id == warehouse_id, StockCostLayer.product_id == product_id, StockCostLayer.remaining_quantity > 0, StockCostLayer.active.is_(True)).order_by(StockCostLayer.created_at, StockCostLayer.id).with_for_update()).all()
            remaining = qty
            for layer in layers:
                if remaining <= 0:
                    break
                used = min(remaining, self.dec(layer.remaining_quantity))
                layer.remaining_quantity = self.dec(layer.remaining_quantity) - used
                if layer.remaining_quantity <= 0:
                    layer.remaining_quantity = Decimal("0")
                    layer.active = False
                remaining -= used
        else:
            raise ValidationError(f"طريقة تقييم المخزون غير مدعومة: {product.costing_method}")
        unit_cost = total_cost / qty if qty else Decimal("0")
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
