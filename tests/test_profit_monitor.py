from core.system import SystemBootstrap
from core.profit_monitor import ProfitMonitor


def test_profit_monitor(tmp_path):
    app=SystemBootstrap(str(tmp_path/'profit.db')).initialize()
    result=ProfitMonitor(app.db).alerts()
    assert isinstance(result,list)
