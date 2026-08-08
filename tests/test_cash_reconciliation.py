from decimal import Decimal
from core.cash_reconciliation import CashReconciliation

def test_cash_reconciliation():
    r=CashReconciliation().calculate('1000','950')
    assert r['difference']==Decimal('-50')
    assert r['status']=='shortage'
