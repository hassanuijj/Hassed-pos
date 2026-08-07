from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from accounting.journal import validate_lines
from core.exceptions import InsufficientStockError, UnbalancedEntryError
from database import Base
from inventory.stock import StockService
from models import Company, Currency, Product, Unit, User, Warehouse


def make_session():
    import accounting.journal  # noqa: F401
    import purchases.models  # noqa: F401
    import sales.models  # noqa: F401

    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True, expire_on_commit=False)()


def make_stock(session, costing_method="FIFO"):
    company = Company(name="Test", base_currency_code="YER")
    session.add(company)
    session.flush()
    unit = Unit(company_id=company.id, code="PCS", name="Piece")
    user = User(company_id=company.id, username="tester", full_name="Tester", password_hash="x")
    warehouse = Warehouse(company_id=company.id, code="MAIN", name="Main")
    currency = Currency(company_id=company.id, code="YER", name="Yemeni Rial", is_base=True)
    session.add_all([unit, user, warehouse, currency])
    session.flush()
    product = Product(company_id=company.id, code="P1", name="Product", unit_id=unit.id, costing_method=costing_method)
    session.add(product)
    session.commit()
    return company, user, warehouse, product


def test_journal_lines_must_balance():
    validate_lines([{"debit": Decimal("100"), "credit": Decimal("100")}])
    with pytest.raises(UnbalancedEntryError):
        validate_lines([{"debit": Decimal("100"), "credit": Decimal("90")}])


def test_fifo_stock_costing():
    session = make_session()
    company, user, warehouse, product = make_stock(session, "FIFO")
    service = StockService(session)
    service.receive(company_id=company.id, warehouse_id=warehouse.id, product_id=product.id, quantity=100, unit_cost=10, user_id=user.id)
    service.receive(company_id=company.id, warehouse_id=warehouse.id, product_id=product.id, quantity=50, unit_cost=12, user_id=user.id)
    movement = service.issue(company_id=company.id, warehouse_id=warehouse.id, product_id=product.id, quantity=120, user_id=user.id)
    assert movement.total_cost == Decimal("1240")


def test_stock_rejects_over_issue():
    session = make_session()
    company, user, warehouse, product = make_stock(session, "WEIGHTED_AVERAGE")
    service = StockService(session)
    service.receive(company_id=company.id, warehouse_id=warehouse.id, product_id=product.id, quantity=5, unit_cost=10, user_id=user.id)
    with pytest.raises(InsufficientStockError):
        service.issue(company_id=company.id, warehouse_id=warehouse.id, product_id=product.id, quantity=6, user_id=user.id)
