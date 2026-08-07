from __future__ import annotations

from PyQt6.QtWidgets import QMessageBox, QWidget


SCREEN_HELP = {
    "dashboard": "لوحة التحكم: تعرض مؤشرات المبيعات والمشتريات والصندوق والمخزون. F2 جديد، F3 بحث، F5 تحديث، F10 طباعة.",
    "pos": "نقطة البيع: ابحث بالباركود أو الاسم، أدخل الكمية، راجع الخصم والضريبة، اختر العميل وطريقة الدفع ثم احفظ واعتمد ورحّل حسب الصلاحية.",
    "customers": "العملاء: إدارة بيانات العملاء والحد الائتماني وكشف الحساب وأعمار الديون ورسائل WhatsApp.",
    "inventory": "المخزون: إدارة الأصناف والمخازن والتحويلات والجرد والحركات والتكلفة.",
    "accounting": "المحاسبة: القيود اليومية والسندات والترحيل وميزان المراجعة والحسابات.",
}


def show_help(parent: QWidget, screen: str) -> None:
    text = SCREEN_HELP.get(screen, "اضغط F1 للحصول على مساعدة الشاشة الحالية.")
    QMessageBox.information(parent, "مساعدة HASSED ERP", text)
