from __future__ import annotations

class Dashboard:
    def __init__(self, sales, profit, stock, customers):
        self.sales=sales; self.profit=profit; self.stock=stock; self.customers=customers

    def snapshot(self, sales=None, purchases=None, returns=None, expenses=None, products=None, customer_entries=None):
        return {
            'sales': self.sales.summarize(sales or []),
            'profit': self.profit.summarize(sales or [], purchases or [], returns or [], expenses or []),
            'stock': self.stock.summarize(products or []),
            'customers': self.customers.summarize(customer_entries or []),
        }
