from core.system import SystemBootstrap
from core.intelligence import BusinessIntelligence


def test_business_intelligence(tmp_path):
    app=SystemBootstrap(str(tmp_path/'intelligence.db')).initialize()
    result=BusinessIntelligence(app.db).insights()
    assert isinstance(result,list)
    for item in result:
        assert {'type','priority','title','message'} <= set(item)
