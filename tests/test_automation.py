from core.system import SystemBootstrap
from core.automation import AutomationService


def test_automation_plan(tmp_path):
    db=str(tmp_path/'automation.db')
    app=SystemBootstrap(db).initialize()
    service=AutomationService(app.db, db)
    result=service.status()
    assert 'generated_at' in result
    assert isinstance(result['tasks'], list)
