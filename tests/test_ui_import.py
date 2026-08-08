def test_ui_module_imports():
    import ui.app
    assert callable(ui.app.main)
