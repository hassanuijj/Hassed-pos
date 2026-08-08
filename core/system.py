from __future__ import annotations

from pathlib import Path

from .application import HassedPOSApplication
from .validation import IntegrityValidator


class SystemBootstrap:
    def __init__(self, db_path="data/hassed_pos.db"):
        self.db_path = db_path
        self.app = None

    def initialize(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.app = HassedPOSApplication(self.db_path)
        return self.app

    def health_check(self):
        if self.app is None:
            self.initialize()
        return IntegrityValidator(self.app.db).run().as_dict()
