from core.system import SystemBootstrap
from core.startup_automation import StartupAutomation


def test_startup_automation(tmp_path):
    db=str(tmp_path/'startup.db')
    app=SystemBootstrap(db).initialize()
    result=StartupAutomation(app).run(backup=True, backup_dir=str(tmp_path/'backups'))
    assert result['events']
    assert any(e['type']=='backup' for e in result['events'])
