from core.payment import PaymentService


def test_payment_cash_and_credit():
    s=PaymentService()
    cash=s.calculate('100','10','100')
    assert cash['total']==90 and cash['change']==10 and cash['balance']==0
    credit=s.calculate(100,10,50)
    assert credit['total']==90 and credit['balance']==40 and credit['credit'] is True
