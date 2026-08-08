from core.system import SystemBootstrap
from core.automation import AutomationService
from core.task_center import TaskCenter
from core.scheduler import AutomationScheduler


def test_scheduler(tmp_path):
    db=str(tmp_path/'scheduler.db')
    app=SystemBootstrap(db).initialize()
    scheduler=AutomationScheduler(TaskCenter(AutomationService(app.db,db)))
    scheduler.run_once()
    status=scheduler.status()
    assert status['runs']==1
    assert status['last_run']
