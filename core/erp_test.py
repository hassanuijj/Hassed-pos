from .database import Database
from .services import ChartOfAccountsService, MasterDataService
from .erp import ERPService, InsufficientStockError


def setup(tmp_path):
    db = Database(str(tmp_path / "erp.db"))
    ChartOfAccountsService(db).seed_defaults()
    master = MasterDataService(db)
    product = master.create_product("منتج", "10001", 100, 150, 1)
    customer = master.create_customer("عميل")
    supplier = master.create_supplier("مورد")
    return db, ERPService(db), product, customer, supplier


def test_purchase_and_sale_are_persistent_and_balanced(tmp_path):
    db, erp, product, customer, supplier = setup(tmp_path)
    purchase = erp.purchase("PUR-1", supplier, [{"product_id": product, "quantity": 10, "unit_cost": 100}], 500)
    assert purchase["total"] == 1000
    sale = erp.sale("SAL-1", customer, [{"product_id": product, "quantity": 2, "unit_price": 150}], 100)
    assert sale["sales_total"] == 300
    assert sale["cogs"] == 200
    rows = db.fetchall("SELECT SUM(debit) d, SUM(credit) c FROM journal_lines")
    assert rows[0]["d"] == rows[0]["c"]


def test_sale_rollback_on_insufficient_stock(tmp_path):
    db, erp, product, customer, supplier = setup(tmp_path)
    erp.purchase("PUR-2", supplier, [{"product_id": product, "quantity": 1, "unit_cost": 100}], 100)
    try:
        erp.sale("SAL-FAIL", customer, [{"product_id": product, "quantity": 2, "unit_price": 150}], 0)
    except InsufficientStockError:
        pass
    assert db.fetchone("SELECT COUNT(*) c FROM documents WHERE reference='SAL-FAIL'")["c"] == 0
    assert db.fetchone("SELECT COUNT(*) c FROM journal_entries WHERE reference='SAL-FAIL'")["c"] == 0
