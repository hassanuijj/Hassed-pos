from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from core.exceptions import NotFoundError, ValidationError
from models import Supplier


class SupplierService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, *, company_id: int, code: str, name: str, phone: str | None = None, credit_limit: Decimal = Decimal("0")) -> Supplier:
        code = code.strip()
        name = name.strip()
        if not code or not name:
            raise ValidationError("كود واسم المورد مطلوبان.")
        if Decimal(str(credit_limit)) < 0:
            raise ValidationError("حد الائتمان لا يمكن أن يكون سالبًا.")
        if self.session.query(Supplier).filter(Supplier.company_id == company_id, Supplier.code == code).first():
            raise ValidationError("كود المورد مستخدم مسبقًا.")
        supplier = Supplier(company_id=company_id, code=code, name=name, phone=phone, credit_limit=credit_limit, active=True)
        self.session.add(supplier)
        self.session.flush()
        return supplier

    def get(self, *, company_id: int, supplier_id: int) -> Supplier:
        supplier = self.session.query(Supplier).filter(Supplier.company_id == company_id, Supplier.id == supplier_id, Supplier.active.is_(True)).first()
        if not supplier:
            raise NotFoundError("المورد غير موجود أو غير نشط.")
        return supplier

    def search(self, *, company_id: int, text: str) -> list[Supplier]:
        pattern = f"%{text.strip()}%"
        return self.session.query(Supplier).filter(Supplier.company_id == company_id, Supplier.active.is_(True), (Supplier.code.ilike(pattern) | Supplier.name.ilike(pattern) | Supplier.phone.ilike(pattern))).order_by(Supplier.name.asc()).all()
