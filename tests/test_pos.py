from core.system import SystemBootstrap
from core.pos import POSService


def test_pos_service_quote_requires_valid_items(tmp_path):
    app=SystemBootstrap(str(tmp_path/'pos.db')).initialize()
    pos=POSService(app)
    try:
        pos.quote([])
    except Exception as exc:
        assert exc is not None
    else:
        assert False, 'empty cart must be rejected'
