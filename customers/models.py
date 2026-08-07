from __future__ import annotations

from decimal import Decimal
from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from models import Base


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    code = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True, index=True)
    address = Column(String(500), nullable=True)
    credit_limit = Column(Numeric(20, 8), nullable=False, default=Decimal("0"))
    active = Column(Boolean, nullable=False, default=True, index=True)
    notes = Column(Text, nullable=True)
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_customer_company_code"),)
