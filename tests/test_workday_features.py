from core.system import SystemBootstrap
from core.workday import WorkdayService
from core.backup import BackupService


def test_workday_and_backup(tmp_path):
    db=str(tmp_path/'app.db'); app=SystemBootstrap(db).initialize()
    work=WorkdayService(app.db)
    today=work.today()
    assert 'sales' in today and 'alerts' in today
    backup=BackupService(db).create(str(tmp_path/'backups'))
    assert backup.endswith('.db')
