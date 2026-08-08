from decimal import Decimal
from core.daily_report import DailyReport

def test_daily_report():
    r=DailyReport().summarize([{'total':100},{'total':50}],[{'paid':20}],[{'total':10}])
    assert r['sales_count']==2
    assert r['gross_sales']==Decimal('150')
    assert r['net_sales']==Decimal('140')
