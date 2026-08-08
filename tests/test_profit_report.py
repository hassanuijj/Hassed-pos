from decimal import Decimal
from core.profit_report import ProfitReport

def test_profit_report():
    r=ProfitReport().summarize(
        sales=[{'total':1000}],
        purchases=[{'cost_total':600}],
        returns=[{'total':100}],
        expenses=[{'amount':50}],
    )
    assert r['revenue']==Decimal('900.00')
    assert r['gross_profit']==Decimal('300.00')
    assert r['net_profit']==Decimal('250.00')
