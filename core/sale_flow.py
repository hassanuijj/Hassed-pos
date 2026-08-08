from __future__ import annotations
from core.payment import PaymentService
from core.invoice import InvoiceRenderer
from core.receipt import ThermalReceipt

class SaleFlow:
    def __init__(self, pos_service, cash_service=None, cashier=''):
        self.pos=pos_service; self.cash=cash_service; self.cashier=cashier; self.payment=PaymentService()

    def prepare(self, items, discount=0, paid=0):
        subtotal=sum(float(i['quantity'])*float(i['product']['sale_price']) for i in items)
        return self.payment.calculate(subtotal,discount,paid)

    def complete(self, items, discount=0, paid=0, customer_id=None):
        payment=self.prepare(items,discount,paid)
        result=self.pos.checkout(items,discount=payment['discount'],paid=payment['paid'],customer_id=customer_id)
        result.update(payment); result['cashier']=self.cashier
        if self.cash and payment['paid']:
            self.cash.record_sale(result)
        result['invoice_text']=InvoiceRenderer().render_text(result)
        result['receipt_58']=ThermalReceipt('58mm').render(result)
        result['receipt_80']=ThermalReceipt('80mm').render(result)
        return result
