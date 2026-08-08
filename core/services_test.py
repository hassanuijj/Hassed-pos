from pathlib import Path

from .database import Database
from .services import ChartOfAccountsService, MasterDataService, ReportingService


def test_master_data_and_reports(tmp_path: Path):
    db = Database(str(tmp_path / "erp.db"))
    master = MasterDataService(db)
    accounts = ChartOfAccountsService(db)
    reports = ReportingService(db)

    accounts.seed_defaults()
    product_id = master.create_product("شاحن", "6280001", 500, 800, 2)
    customer_id = master.create_customer("عميل تجريبي", "777000000")
    supplier_id = master.create_supplier("مورد تجريبي", "733000000")

    assert product_id
    assert customer_id
    assert supplier_id
    assert len(master.products()) == 1
    assert len(master.customers()) == 1
    assert len(master.suppliers()) == 1
    assert reports.sales_summary()["count"] == 0
    assert reports.purchases_summary()["count"] == 0
    assert len(accounts.all()) >= 10
