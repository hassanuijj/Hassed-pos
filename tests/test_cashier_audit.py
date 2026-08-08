from core.system import SystemBootstrap
from core.cashier_audit import CashierAudit


def test_cashier_audit(tmp_path):
    app=SystemBootstrap(str(tmp_path/'cash.db')).initialize()
    audit=CashierAudit(app.db)
    result=audit.record_sale('S-1',100,100,0,'cashier')
    assert result['reference']=='S-1'
    rows=audit.today()
    assert any(r['reference']=='S-1' for r in rows)
