from __future__ import annotations
from core.collections import CollectionService


class CollectionFlow:
    def __init__(self, cash_service=None, finance=None):
        self.collections = CollectionService()
        self.cash = cash_service
        self.finance = finance

    def prepare(self, customer_id, balance, payment, reference=''):
        result = self.collections.calculate(balance, payment)
        result.update({'customer_id': customer_id, 'reference': reference, 'type': 'customer_collection'})
        return result

    def complete(self, customer_id, balance, payment, reference=''):
        result = self.prepare(customer_id, balance, payment, reference)
        if self.cash and result['paid']:
            self.cash.record_collection(result)
        return result
