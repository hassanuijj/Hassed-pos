from __future__ import annotations
from datetime import datetime
from core.intelligence import BusinessIntelligence
from core.backup import BackupService

class AutomationService:
    def __init__(self, db, db_path):
        self.db=db; self.db_path=db_path
        self.intelligence=BusinessIntelligence(db)

    def plan(self):
        tasks=[]
        for item in self.intelligence.insights():
            tasks.append({"action":"review","priority":item["priority"],"title":item["title"],"message":item["message"]})
        return tasks

    def run_backup(self, directory="backups"):
        return BackupService(self.db_path).create(directory)

    def status(self):
        return {"generated_at":datetime.now().isoformat(timespec="seconds"),"tasks":self.plan()}
