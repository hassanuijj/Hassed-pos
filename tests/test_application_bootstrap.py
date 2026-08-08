from core.system import SystemBootstrap


def test_application_bootstrap(tmp_path):
    app = SystemBootstrap(str(tmp_path / "test.db")).initialize()
    assert app.db is not None
    assert app.security is not None
    assert app.accounts is not None
    assert app.erp is not None
