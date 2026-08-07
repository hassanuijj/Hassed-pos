from __future__ import annotations

from decimal import Decimal

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ui.help import show_help
from ui.shortcuts import install_shortcuts


class POSWindow(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("HASSED ERP - نقطة البيع")
        self.resize(1100, 700)
        self._total = Decimal("0")
        self._build()
        self._shortcuts = install_shortcuts(self, {
            "F1": lambda: show_help(self, "pos"),
            "F2": self.new_invoice,
            "F4": self.save_invoice,
            "F5": self.refresh,
            "F10": self.print_invoice,
            "Esc": self.close,
        })

    def _build(self):
        root = QVBoxLayout(self)
        top = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("باركود أو اسم الصنف...")
        self.search.returnPressed.connect(self.add_product)
        top.addWidget(QLabel("الصنف:"))
        top.addWidget(self.search, 1)
        self.customer = QComboBox()
        self.customer.addItem("عميل نقدي", None)
        top.addWidget(QLabel("العميل:"))
        top.addWidget(self.customer)
        root.addLayout(top)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["الصنف", "الكمية", "السعر", "الخصم", "الإجمالي"])
        self.table.setAlternatingRowColors(True)
        root.addWidget(self.table, 1)

        bottom = QHBoxLayout()
        self.total_label = QLabel("الإجمالي: 0.00")
        self.payment = QComboBox()
        self.payment.addItems(["نقدي", "بطاقة", "بنك", "آجل"])
        save = QPushButton("حفظ وترحيل  F4")
        save.clicked.connect(self.save_invoice)
        new = QPushButton("جديد  F2")
        new.clicked.connect(self.new_invoice)
        help_button = QPushButton("مساعدة  F1")
        help_button.clicked.connect(lambda: show_help(self, "pos"))
        bottom.addWidget(self.total_label)
        bottom.addStretch()
        bottom.addWidget(self.payment)
        bottom.addWidget(new)
        bottom.addWidget(save)
        bottom.addWidget(help_button)
        root.addLayout(bottom)

    def add_product(self):
        text = self.search.text().strip()
        if not text:
            return
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(text))
        quantity = QSpinBox()
        quantity.setMinimum(1)
        quantity.setMaximum(999999)
        quantity.valueChanged.connect(self.recalculate)
        self.table.setCellWidget(row, 1, quantity)
        self.table.setItem(row, 2, QTableWidgetItem("0.00"))
        self.table.setItem(row, 3, QTableWidgetItem("0.00"))
        self.table.setItem(row, 4, QTableWidgetItem("0.00"))
        self.search.clear()
        self.recalculate()

    def recalculate(self):
        total = Decimal("0")
        for row in range(self.table.rowCount()):
            quantity = Decimal(str(self.table.cellWidget(row, 1).value()))
            price = Decimal(self.table.item(row, 2).text() or "0")
            discount = Decimal(self.table.item(row, 3).text() or "0")
            line_total = max(quantity * price - discount, Decimal("0"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{line_total:.2f}"))
            total += line_total
        self._total = total
        self.total_label.setText(f"الإجمالي: {total:.2f}")

    def new_invoice(self):
        self.table.setRowCount(0)
        self.search.clear()
        self.recalculate()
        self.search.setFocus()

    def save_invoice(self):
        self.recalculate()
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "الفاتورة", "أضف صنفًا واحدًا على الأقل.")
            return
        QMessageBox.information(self, "الفاتورة", "تم تجهيز الفاتورة للحفظ والترحيل. سيتم ربطها بمحرك الترحيل في طبقة التطبيق.")

    def refresh(self):
        self.recalculate()

    def print_invoice(self):
        QMessageBox.information(self, "الطباعة", "سيتم إرسال الفاتورة إلى محرك ReportLab عند ربط طبقة التقارير.")
