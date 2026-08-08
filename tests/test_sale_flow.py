from core.sale_flow import SaleFlow

class FakePOS:
    def checkout(self,items,discount=0,paid=0,customer_id=None):
        total=sum(float(i['quantity'])*float(i['product']['sale_price']) for i in items)-float(discount)
        return {'reference':'S-TEST','items':[{'name':i['product']['name'],'quantity':i['quantity'],'price':i['product']['sale_price'],'total':float(i['quantity'])*float(i['product']['sale_price'])} for i in items],'total':total}

def test_sale_flow():
    item={'product':{'name':'Cable','sale_price':50},'quantity':2}
    result=SaleFlow(FakePOS(),cash_service=None,cashier='admin').complete([item],discount=10,paid=100)
    assert result['total']==90
    assert result['change']==10
    assert 'receipt_80' in result
