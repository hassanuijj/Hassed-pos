from __future__ import annotations
from datetime import datetime


class TaskCenter:
    def __init__(self, automation):
        self.automation = automation

    def pending(self):
        return self.automation.plan()

    def run_safe(self):
        """Execute only non-destructive automation; financial posting remains explicit."""
        executed=[]
        for task in self.pending():
            if task.get('action') == 'review':
                executed.append({**task, 'status':'queued', 'executed_at':datetime.now().isoformat(timespec='seconds')})
        return executed

    def dashboard(self):
        tasks=self.pending()
        return {'count':len(tasks),'high':sum(t.get('priority')=='high' for t in tasks),'tasks':tasks}
