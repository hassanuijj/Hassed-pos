from core.return_flow import ReturnFlow


def test_return_flow_validation(tmp_path):
    flow=ReturnFlow(None)
    original=[{'product_id':1,'quantity':5,'price':50}]
    returned=[{'product_id':1,'quantity':2,'price':50}]
    assert flow.validate_only(returned,original) is True
    result=flow.prepare_sales(returned,original)
    assert result['type']=='sales_return'
    assert result['total'] == 100
