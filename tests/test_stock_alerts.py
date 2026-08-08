from core.stock_alerts import StockAlerts

def test_stock_alerts():
    alerts=StockAlerts().analyze([{'id':1,'quantity':0},{'id':2,'quantity':2,'min_quantity':3},{'id':3,'quantity':10,'min_quantity':3}])
    assert [a['type'] for a in alerts]==['out_of_stock','low_stock']
