from __future__ import annotations
from decimal import Decimal
from uuid import uuid4
from .erp import D, M, ERPValidationError, InsufficientStockError

class POSService:
    def __init__(self, app):
        self.app=app
        self.db=app.db
        self.erp=app.erp

    def product_by_barcode(self, barcode):
        row=self.db.fetchone("SELECT id,name,barcode,sale_price,cost_price,quantity,min_stock,active FROM products WHERE barcode=? AND active=1",(barcode.strip(),))
        if not row: raise ERPValidationError("الباركود غير موجود")
        return row

    def quote(self, items, discount=0):
        total=Decimal("0.00")
        normalized=[]
        for item in items:
            p=self.db.fetchone("SELECT id,name,sale_price,quantity FROM products WHERE id=? AND active=1",(item["product_id"],))
            if not p: raise ERPValidationError("الصنف غير موجود")
            qty=D(item.get("quantity",1)); price=M(item.get("unit_price",p["sale_price"]))
            if qty<=0: raise ERPValidationError("الكمية يجب أن تكون موجبة")
            if D(p["quantity"])<qty: raise InsufficientStockError(f"المخزون غير كاف للصنف {p['name']}")
            total += qty*price-M(item.get("discount",0))
            normalized.append({**item,"quantity":qty,"unit_price":price,"unit_cost":D(0)})
        discount=M(discount)
        if discount<0 or discount>total: raise ERPValidationError("الخصم غير صحيح")
        return {"items":normalized,"subtotal":M(total),"discount":discount,"total":M(total-discount)}

    def checkout(self, reference, customer_id, items, paid, discount=0):
        q=self.quote(items,discount)
        result=self.erp.sale(reference,customer_id,q["items"],paid=M(paid))
        return {**result,"subtotal":q["subtotal"],"discount":q["discount"],"total":q["total"],"change":M(D(paid)-q["total"]) if D(paid)>q["total"] else M(0),"remaining":M(q["total"]-D(paid))}
