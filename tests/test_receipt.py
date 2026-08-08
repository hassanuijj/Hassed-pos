from core.receipt import ThermalReceipt


def test_thermal_receipt_widths():
    sale={'reference':'S-1','items':[{'name':'USB Cable','quantity':2,'total':100}],'total':100,'paid':100,'balance':0,'change':0}
    for width in ('58mm','80mm'):
        text=ThermalReceipt(width).render(sale)
        assert 'S-1' in text
        assert 'USB Cable' in text
