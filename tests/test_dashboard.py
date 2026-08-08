from app.main import build_dashboard

def test_dashboard_builds():
    dashboard=build_dashboard()
    snapshot=dashboard.snapshot(
        sales=[{'cashier':'admin','total':100}],
        purchases=[{'cost_total':60}],
        products=[{'id':1,'quantity':2,'cost_price':10}],
        customer_entries=[{'customer_id':1,'debit':100,'credit':40}],
    )
    assert snapshot['sales']['total']==100
    assert snapshot['profit']['gross_profit']==40
    assert snapshot['stock']['total_value']==20
    assert snapshot['customers'][1]['balance']==60
