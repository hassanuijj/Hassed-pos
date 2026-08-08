from __future__ import annotations
from datetime import datetime
from pathlib import Path
from core.automation import AutomationService
from core.task_center import TaskCenter
from core.scheduler import AutomationScheduler


class StartupAutomation:
    """Runs only safe read/check/backup operations during application startup."""
    def __init__(self, app):
        self.app=app
        self.scheduler=AutomationScheduler(TaskCenter(AutomationService(app.db, app.db.path)))

    def run(self, backup=True, backup_dir='backups'):
        events=[]
        try:
            health=self.app.health_check() if hasattr(self.app,'health_check') else {'ok':True}
            events.append({'type':'health_check','status':'ok' if health.get('ok',True) else 'warning','data':health})
        except Exception as exc:
            events.append({'type':'health_check','status':'error','message':str(exc)})
        try:
            tasks=self.scheduler.run_once()
            events.append({'type':'automation','status':'ok','count':len(tasks)})
        except Exception as exc:
            events.append({'type':'automation','status':'error','message':str(exc)})
        if backup:
            try:
                Path(backup_dir).mkdir(parents=True,exist_ok=True)
                path=self.scheduler.center.automation.run_backup(backup_dir)
                events.append({'type':'backup','status':'ok','path':path})
            except Exception as exc:
                events.append({'type':'backup','status':'error','message':str(exc)})
        return {'at':datetime.now().isoformat(timespec='seconds'),'events':events}
