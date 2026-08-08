from __future__ import annotations

from app.ui_router import UIRouter
from app.dashboard import Dashboard
from core.sales_analytics import SalesAnalytics
from core.profit_report import ProfitReport
from core.stock_valuation import StockValuation
from core.customer_ledger import CustomerLedger
from core.collections import CollectionService
from core.return_flow import ReturnFlow
from core.cash_reconciliation import CashReconciliation
from core.stock_alerts import StockAlerts
from core.reorder_advisor import ReorderAdvisor
from core.daily_report import DailyReport


class Application:
    def __init__(self, services=None):
        self.services = services or {}
        self.router = UIRouter()
        self._wire_services()
        self._wire_screens()

    def _wire_services(self):
        defaults = {
            'sales': SalesAnalytics(), 'profit': ProfitReport(),
            'stock': StockValuation(), 'customers': CustomerLedger(),
            'collections': CollectionService(), 'cash': CashReconciliation(),
            'stock_alerts': StockAlerts(), 'reorder': ReorderAdvisor(),
            'daily': DailyReport(), 'returns': ReturnFlow(self.services.get('db')),
        }
        for key, value in defaults.items(): self.services.setdefault(key, value)
        self.services['dashboard'] = Dashboard(self.services['sales'], self.services['profit'], self.services['stock'], self.services['customers'])

    def _wire_screens(self):
        factories = {
            'dashboard': lambda **kw: self.services['dashboard'].snapshot(**kw),
            'pos': lambda **kw: {'service': 'sales', 'context': kw},
            'purchases': lambda **kw: {'service': 'purchases', 'context': kw},
            'inventory': lambda **kw: self.services['stock'].summarize(kw.get('products', [])),
            'customers': lambda **kw: self.services['customers'].summarize(kw.get('entries', [])),
            'suppliers': lambda **kw: {'service': 'suppliers', 'context': kw},
            'returns': lambda **kw: self.services['returns'].prepare_sales(kw['returned_lines'], kw['original_lines']),
            'cash': lambda **kw: self.services['cash'].calculate(kw.get('expected', 0), kw.get('counted', 0)),
            'accounting': lambda **kw: {'service': 'accounting', 'context': kw},
            'reports': lambda **kw: self.services['daily'].summarize(kw.get('sales'), kw.get('collections'), kw.get('returns')),
            'settings': lambda **kw: {'service': 'settings', 'context': kw},
            'audit': lambda **kw: {'service': 'audit', 'context': kw},
        }
        self.router.register_defaults(factories)

    def open(self, screen, **kwargs):
        return self.router.open(screen, **kwargs)

    def navigation(self):
        return self.router.menu()
