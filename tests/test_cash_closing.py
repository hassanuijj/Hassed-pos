from decimal import Decimal
from core.cash_closing import CashClosing

def test_cash_closing():
    result=CashClosing().close(1000,950,'admin','نقص 50')
    assert result['difference']==Decimal('-50')
    assert result['status']=='shortage'
    assert result['cashier']=='admin'
    assert result['closed_at']
