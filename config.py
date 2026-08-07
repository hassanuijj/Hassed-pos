from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
BACKUP_DIR = BASE_DIR / "backups"
REPORT_DIR = BASE_DIR / "reports_output"
LOG_DIR = BASE_DIR / "logs"
for directory in (DATA_DIR, BACKUP_DIR, REPORT_DIR, LOG_DIR):
    directory.mkdir(parents=True, exist_ok=True)

APP_NAME = "HASSED ERP"
APP_VERSION = "1.0.0"
DEFAULT_CURRENCY = "YER"
DATABASE_URL = os.getenv("HASSED_DATABASE_URL", f"sqlite:///{DATA_DIR / 'hassed_erp.db'}")
SECRET_KEY = os.getenv("HASSED_SECRET_KEY", "change-this-secret-key")
MAX_BACKUPS = int(os.getenv("HASSED_MAX_BACKUPS", "30"))
