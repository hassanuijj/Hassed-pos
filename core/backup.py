from __future__ import annotations
from datetime import datetime
from pathlib import Path
import shutil


class BackupService:
    def __init__(self, db_path): self.db_path=Path(db_path)
    def create(self, directory='backups'):
        src=self.db_path
        if not src.exists(): raise FileNotFoundError(str(src))
        target_dir=Path(directory); target_dir.mkdir(parents=True,exist_ok=True)
        target=target_dir/f"hassed_pos_{datetime.now():%Y%m%d_%H%M%S}.db"
        shutil.copy2(src,target)
        return str(target)
