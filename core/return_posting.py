from __future__ import annotations
from decimal import Decimal
from core.exceptions import ValidationError


class ReturnPostingService:
    """Builds deterministic posting instructions; callers execute them transactionally."""
    def build(self, return_data, return_type):
        if return_type not in ('sales_return','purchase_return'):
            raise ValidationError('نوع المرتجع غير مدعوم.')
        items=return_data.get('items') or []
        if not items:
            raise ValidationError('لا توجد أصناف في المرتجع.')
        lines=[]
        for item in items:
            qty=Decimal(str(item.get('quantity',0)))
            amount=Decimal(str(item.get('unit_amount',item.get('price',0)) or 0))
            if qty<=0 or amount<0:
                raise ValidationError('بيانات المرتجع غير صحيحة.')
            value=qty*amount
            lines.append({'product_id':item.get('product_id'),'quantity':qty,'value':value})
        total=sum((x['value'] for x in lines),Decimal('0'))
        direction='increase_stock' if return_type=='sales_return' else 'decrease_stock'
        return {'type':return_type,'inventory':{'direction':direction,'lines':lines},'accounting':{'total':total,'event':return_type},'total':total}
