from datetime import date
from decimal import Decimal
from core.customer_ledger import CustomerLedger

def test_customer_ledger():
    r=CustomerLedger().summarize([{'customer_id':1,'debit':100,'credit':40}])
    assert r[1]['balance']==Decimal('60')

def test_aging():
    r=CustomerLedger().aging([{'customer_id':1,'date':date(2026,7,1),'balance':60}],date(2026,8,8))
    assert r[0]['bucket']=='31-60'
