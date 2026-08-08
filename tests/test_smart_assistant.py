from core.system import SystemBootstrap
from core.smart import SmartAssistant


def test_smart_assistant_returns_insights(tmp_path):
    app=SystemBootstrap(str(tmp_path/'smart.db')).initialize()
    result=SmartAssistant(app.db).insights()
    assert isinstance(result,list)
    for item in result:
        assert {'type','priority','title','message'} <= set(item)
