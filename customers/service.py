from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from core.exceptions import NotFoundError, ValidationError
from models import Customer


class CustomerService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, *, company_id: int, code: str, name: str, phone: str | None = None, credit_limit: Decimal = Decimal("0")) -> Customer:
        code = code.strip()
        name = name.strip()
        if not code or not name:
            raise ValidationError("كود واسم العميل مطلوبان.")
        if Decimal(str(credit_limit)) < 0:
            raise ValidationError("حد الائتمان لا يمكن أن يكون سالبًا.")
        if self.session.query(Customer).filter(Customer.company_id == company_id, Customer.code == code).first():
            raise ValidationError("كود العميل مستخدم مسبقًا.")
        customer = Customer(company_id=company_id, code=code, name=name, phone=phone, credit_limit=credit_limit, active=True)
        self.session.add(customer)
        self.session.flush()
        return customer

    def get(self, *, company_id: int, customer_id: int) -> Customer:
        customer = self.session.query(Customer).filter(Customer.company_id == company_id, Customer.id == customer_id, Customer.active.is_(True)).first()
        if not customer:
            raise NotFoundError("العميل غير موجود أو غير نشط.")
        return customer

    def search(self, *, company_id: int, text: str) -> list[Customer]:
        pattern = f"%{text.strip()}%"
        return self.session.query(Customer).filter(Customer.company_id == company_id, Customer.active.is_(True), (Customer.code.ilike(pattern) | Customer.name.ilike(pattern) | Customer.phone.ilike(pattern))).order_by(Customer.name.asc()).all()
