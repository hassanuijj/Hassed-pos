from core.system import SystemBootstrap
from core.automation import AutomationService
from core.task_center import TaskCenter


def test_task_center(tmp_path):
    db=str(tmp_path/'tasks.db')
    app=SystemBootstrap(db).initialize()
    center=TaskCenter(AutomationService(app.db,db))
    dashboard=center.dashboard()
    assert dashboard['count'] >= 0
    assert dashboard['high'] >= 0
    assert isinstance(center.run_safe(),list)
