from __future__ import annotations
from decimal import Decimal
from collections import defaultdict

class CustomerLedger:
    def summarize(self, entries):
        result=defaultdict(lambda:{'debit':Decimal('0'),'credit':Decimal('0'),'balance':Decimal('0')})
        for e in entries or []:
            cid=e.get('customer_id'); debit=Decimal(str(e.get('debit',0) or 0)); credit=Decimal(str(e.get('credit',0) or 0))
            result[cid]['debit']+=debit; result[cid]['credit']+=credit; result[cid]['balance']+=debit-credit
        return dict(result)

    def aging(self, entries, today):
        rows=[]
        for e in entries or []:
            balance=Decimal(str(e.get('balance',0) or 0))
            if balance>0:
                age=max(0,(today-e['date']).days)
                bucket='0-30' if age<=30 else '31-60' if age<=60 else '61-90' if age<=90 else '90+'
                rows.append({'customer_id':e.get('customer_id'),'age_days':age,'bucket':bucket,'balance':balance})
        return rows
