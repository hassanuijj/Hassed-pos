from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class WhatsAppTemplate:
    name: str
    text: str


DEFAULT_TEMPLATES = (
    WhatsAppTemplate("invoice", "مرحبًا {customer_name}، تم إصدار فاتورة رقم {invoice_number}. الإجمالي: {total}، المدفوع: {paid}، المتبقي: {remaining}. شكرًا لتعاملكم معنا."),
    WhatsAppTemplate("payment", "مرحبًا {customer_name}، تم تسجيل دفعة بقيمة {amount} على حسابكم. الرصيد المتبقي: {remaining}."),
    WhatsAppTemplate("debt_reminder", "مرحبًا {customer_name}، نذكركم بأن الرصيد المستحق عليكم هو {remaining}. نقدر تعاونكم."),
    WhatsAppTemplate("welcome", "مرحبًا {customer_name}، أهلاً بكم في {business_name}. يسعدنا خدمتكم دائمًا."),
)


def render(template: WhatsAppTemplate, **values) -> str:
    return template.text.format(**values)
