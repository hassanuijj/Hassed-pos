from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from database import Base


class Company(Base):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country_code: Mapped[str] = mapped_column(String(10), nullable=False, default="YE")
    base_currency_code: Mapped[str] = mapped_column(String(10), nullable=False, default="YER")
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class Currency(Base):
    __tablename__ = "currencies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    symbol: Mapped[str | None] = mapped_column(String(20))
    decimal_places: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    is_base: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_currency_company_code"),)


class ExchangeRate(Base):
    __tablename__ = "exchange_rates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    currency_id: Mapped[int] = mapped_column(ForeignKey("currencies.id", ondelete="RESTRICT"), nullable=False, index=True)
    rate_date: Mapped[datetime] = mapped_column(Date, nullable=False, index=True)
    rate: Mapped[Decimal] = mapped_column(Numeric(28, 12), nullable=False)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    updated_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    __table_args__ = (UniqueConstraint("company_id", "currency_id", "rate_date", name="uq_exchange_rate_day"),)


class FiscalYear(Base):
    __tablename__ = "fiscal_years"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    start_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    end_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="OPEN")
    __table_args__ = (UniqueConstraint("company_id", "name", name="uq_fiscal_year"),)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(80), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("company_id", "username", name="uq_user_company_username"),)


class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id", ondelete="RESTRICT"), index=True)
    code: Mapped[str] = mapped_column(String(60), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_type: Mapped[str] = mapped_column(String(20), nullable=False)
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    is_group: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_account_company_code"), Index("ix_account_parent", "parent_id"))


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(60), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), index=True)
    address: Mapped[str | None] = mapped_column(String(500))
    credit_limit: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False, default=0)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_customer_company_code"), Index("ix_customer_name", "name"))


class Supplier(Base):
    __tablename__ = "suppliers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(60), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), index=True)
    address: Mapped[str | None] = mapped_column(String(500))
    credit_limit: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False, default=0)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_supplier_company_code"), Index("ix_supplier_name", "name"))


class Unit(Base):
    __tablename__ = "units"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    symbol: Mapped[str | None] = mapped_column(String(20))
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_unit_company_code"),)


class ProductCategory(Base):
    __tablename__ = "product_categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("product_categories.id", ondelete="RESTRICT"), index=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_category_company_code"),)


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    barcode: Mapped[str | None] = mapped_column(String(100), index=True)
    sku: Mapped[str | None] = mapped_column(String(100), index=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("product_categories.id", ondelete="RESTRICT"), index=True)
    unit_id: Mapped[int] = mapped_column(ForeignKey("units.id", ondelete="RESTRICT"), nullable=False)
    purchase_price: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False, default=0)
    sale_price: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False, default=0)
    minimum_stock: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False, default=0)
    maximum_stock: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False, default=0)
    costing_method: Mapped[str] = mapped_column(String(30), nullable=False, default="WEIGHTED_AVERAGE")
    track_stock: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_product_company_code"), UniqueConstraint("company_id", "barcode", name="uq_product_company_barcode"))


class Warehouse(Base):
    __tablename__ = "warehouses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(String(500))
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    __table_args__ = (UniqueConstraint("company_id", "code", name="uq_warehouse_company_code"),)


class StockBalance(Base):
    __tablename__ = "stock_balances"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False, default=0)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False, default=0)
    average_cost: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (UniqueConstraint("warehouse_id", "product_id", name="uq_stock_warehouse_product"),)


class StockMovement(Base):
    __tablename__ = "stock_movements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    movement_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    balance_quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    balance_cost: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    reference_type: Mapped[str | None] = mapped_column(String(50))
    reference_id: Mapped[int | None] = mapped_column(Integer)
    reference_number: Mapped[str | None] = mapped_column(String(100))
    movement_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    __table_args__ = (Index("ix_stock_movement_product_date", "product_id", "movement_date"), Index("ix_stock_movement_reference", "reference_type", "reference_id"))


class StockCostLayer(Base):
    __tablename__ = "stock_cost_layers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"), nullable=False, index=True)
    source_movement_id: Mapped[int] = mapped_column(ForeignKey("stock_movements.id", ondelete="RESTRICT"), nullable=False)
    original_quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    remaining_quantity: Mapped[Decimal] = mapped_column(Numeric(20, 6), nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    action: Mapped[str] = mapped_column(String(30), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_id: Mapped[int | None] = mapped_column(Integer)
    details: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, index=True)
