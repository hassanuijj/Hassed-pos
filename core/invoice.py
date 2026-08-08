from __future__ import annotations
from datetime import datetime

class InvoiceRenderer:
    def render_text(self, sale, store_name='Hassed POS'):
        lines=[store_name,'='*40,f"Invoice: {sale.get('reference','')}",datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'='*40]
        for item in sale.get('items',[]):
            lines.append(f"{item['name']} x{item['quantity']} @ {item['price']} = {item['total']}")
        lines += ['-'*40,f"Subtotal: {sale.get('subtotal',0)}",f"Discount: {sale.get('discount',0)}",f"Total: {sale.get('total',0)}",f"Paid: {sale.get('paid',0)}",f"Balance: {sale.get('balance',0)}",f"Change: {sale.get('change',0)}"]
        return '\n'.join(lines)
