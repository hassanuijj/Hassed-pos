from core.invoice import InvoiceRenderer


def test_invoice_rendering():
    text=InvoiceRenderer().render_text({'reference':'S-1','items':[{'name':'Cable','quantity':2,'price':50,'total':100}],'subtotal':100,'discount':10,'total':90,'paid':100,'balance':0,'change':10})
    assert 'Invoice: S-1' in text
    assert 'Cable x2' in text
    assert 'Total: 90' in text
