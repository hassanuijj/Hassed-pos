from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote

from core.exceptions import ValidationError


@dataclass(frozen=True)
class WhatsAppMessage:
    phone: str
    message: str


class WhatsAppService:
    """WhatsApp integration abstraction.

    The default implementation generates an official click-to-chat URL.
    A future WhatsApp Business Cloud API adapter can implement the same
    interface without changing sales/customer code.
    """

    def normalize_phone(self, phone: str) -> str:
        value = "".join(ch for ch in str(phone or "") if ch.isdigit() or ch == "+")
        if value.startswith("+"):
            value = value[1:]
        if not value or not value.isdigit():
            raise ValidationError("رقم واتساب غير صالح.")
        return value

    def build_chat_url(self, phone: str, message: str) -> str:
        normalized = self.normalize_phone(phone)
        text = str(message or "").strip()
        if not text:
            raise ValidationError("رسالة واتساب لا يمكن أن تكون فارغة.")
        return f"https://wa.me/{normalized}?text={quote(text)}"

    def build_invoice_message(
        self,
        *,
        customer_name: str,
        invoice_number: str,
        total: str,
        paid: str,
        remaining: str,
    ) -> str:
        return (
            f"مرحبًا {customer_name}\n"
            f"فاتورة رقم: {invoice_number}\n"
            f"الإجمالي: {total}\n"
            f"المدفوع: {paid}\n"
            f"المتبقي: {remaining}\n"
            "شكرًا لتعاملكم معنا."
        )
