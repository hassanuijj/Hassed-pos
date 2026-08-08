from app.application import Application

def test_all_screens_are_registered():
    app=Application()
    keys={x['key'] for x in app.navigation()}
    assert {'dashboard','pos','purchases','inventory','customers','suppliers','returns','cash','accounting','reports','settings','audit'} <= keys

def test_inventory_screen_is_wired():
    result=Application().open('inventory', products=[{'id':1,'quantity':2,'cost_price':10}])
    assert result['total_value']==20
