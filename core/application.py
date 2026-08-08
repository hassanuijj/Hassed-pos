from __future__ import annotations

from .database import Database
from .services import MasterDataService, ChartOfAccountsService, ReportingService
from .erp import ERPService
from .returns import ReturnsService
from .finance import FinanceService
from .reports import FinancialReports
from .security import SecurityService, SecurityError


class HassedPOSApplication:
    """Single application facade used by GUI, CLI and future API adapters."""
    def __init__(self, db_path="data/hassed_pos.db"):
        self.db = Database(db_path)
        self.master = MasterDataService(self.db)
        self.accounts = ChartOfAccountsService(self.db)
        self.erp = ERPService(self.db)
        self.returns = ReturnsService(self.db)
        self.finance = FinanceService(self.db)
        self.reporting = ReportingService(self.db)
        self.financial_reports = FinancialReports(self.db)
        self.security = SecurityService(self.db)
        self.accounts.seed_defaults()
        self.current_user = None

    def login(self, username, password):
        self.current_user = self.security.authenticate(username, password)
        return self.current_user

    def require(self, permission):
        if not self.current_user:
            raise SecurityError("يجب تسجيل الدخول أولاً")
        if not self.security.has_permission(self.current_user["id"], permission):
            raise SecurityError("ليس لديك صلاحية لتنفيذ هذه العملية")

    def create_product(self, *args, **kwargs):
        self.require("products.edit")
        return self.master.create_product(*args, **kwargs)

    def create_customer(self, *args, **kwargs):
        self.require("customers.edit")
        return self.master.create_customer(*args, **kwargs)

    def create_supplier(self, *args, **kwargs):
        self.require("suppliers.edit")
        return self.master.create_supplier(*args, **kwargs)

    def purchase(self, *args, **kwargs):
        self.require("purchases.post")
        return self.erp.purchase(*args, **kwargs)

    def sale(self, *args, **kwargs):
        self.require("sales.post")
        return self.erp.sale(*args, **kwargs)

    def sales_return(self, *args, **kwargs):
        self.require("returns.post")
        return self.returns.sales_return(*args, **kwargs)

    def purchase_return(self, *args, **kwargs):
        self.require("returns.post")
        return self.returns.purchase_return(*args, **kwargs)

    def cash_receipt(self, *args, **kwargs):
        self.require("cash.receipt")
        return self.finance.cash_receipt(*args, **kwargs)

    def cash_payment(self, *args, **kwargs):
        self.require("cash.payment")
        return self.finance.cash_payment(*args, **kwargs)

    def expense(self, *args, **kwargs):
        self.require("expenses.post")
        return self.finance.expense(*args, **kwargs)

    def dashboard(self):
        self.require("dashboard.view")
        return {
            "sales": self.reporting.sales_summary(),
            "purchases": self.reporting.purchases_summary(),
            "cash": self.finance.cash_balance(),
            "profit": self.reporting.profit_summary(),
            "low_stock": self.reporting.low_stock(),
        }

    def trial_balance(self):
        self.require("reports.view")
        return self.financial_reports.trial_balance()

    def income_statement(self):
        self.require("reports.view")
        return self.financial_reports.income_statement()

    def balance_sheet(self):
        self.require("reports.view")
        return self.financial_reports.balance_sheet()
