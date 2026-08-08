from core.system import SystemBootstrap


def test_system_health_check(tmp_path):
    app = SystemBootstrap(str(tmp_path / "health.db")).initialize()
    result = SystemBootstrap(str(tmp_path / "health.db"))
    result.app = app
    health = result.health_check()
    assert isinstance(health, dict)
    assert "ok" in health
    assert "errors" in health
    assert "warnings" in health
