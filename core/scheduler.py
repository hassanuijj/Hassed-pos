from __future__ import annotations
from datetime import datetime
from core.task_center import TaskCenter

class AutomationScheduler:
    def __init__(self, center):
        self.center=center
        self.last_run=None
        self.history=[]

    def run_once(self):
        result=self.center.run_safe()
        self.last_run=datetime.now().isoformat(timespec='seconds')
        self.history.append({'at':self.last_run,'count':len(result)})
        return result

    def status(self):
        return {'last_run':self.last_run,'runs':len(self.history),'last_count':self.history[-1]['count'] if self.history else 0}
