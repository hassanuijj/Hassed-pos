from __future__ import annotations

from core.customer_ledger import CustomerLedger
from core.daily_report import DailyReport
from core.profit_report import ProfitReport
from core.sales_analytics import SalesAnalytics
from core.stock_valuation import StockValuation
from app.dashboard import Dashboard


def build_dashboard():
    return Dashboard(SalesAnalytics(), ProfitReport(), StockValuation(), CustomerLedger())


def main():
    dashboard=build_dashboard()
    print('Hassed POS ERP')
    print('Dashboard initialized:', type(dashboard).__name__)


if __name__ == '__main__':
    main()
