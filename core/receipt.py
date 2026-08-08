from __future__ import annotations

class ThermalReceipt:
    WIDTHS={'58mm':32,'80mm':48}
    def __init__(self,width='80mm'): self.width=self.WIDTHS.get(width,48)
    def render(self,sale,store_name='Hassed POS'):
        w=self.width
        lines=[store_name.center(w),'='*w,f"فاتورة: {sale.get('reference','')}"[:w],'-'*w]
        for item in sale.get('items',[]):
            name=str(item.get('name',''))[:w-12]
            qty=item.get('quantity',0); total=item.get('total',0)
            lines.append(f'{name:<{w-12}} x{qty:<5} {total:>6}'[:w])
        lines += ['-'*w,f"الإجمالي: {sale.get('total',0)}",f"المدفوع: {sale.get('paid',0)}",f"المتبقي: {sale.get('balance',0)}",f"الباقي: {sale.get('change',0)}",'='*w]
        return '\n'.join(lines)
