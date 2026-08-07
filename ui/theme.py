from __future__ import annotations

from PyQt6.QtWidgets import QApplication

DARK_THEME = """
QWidget { background: #1e1f22; color: #f2f2f2; font-family: 'Segoe UI'; font-size: 10pt; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QDateEdit { background: #2b2d31; border: 1px solid #45474d; border-radius: 5px; padding: 6px; }
QPushButton { background: #3a3d44; border: 1px solid #50535b; border-radius: 5px; padding: 7px 12px; }
QPushButton:hover { background: #484b53; }
QTableWidget, QTreeWidget { background: #25262a; alternate-background-color: #2b2d31; gridline-color: #41434a; }
QHeaderView::section { background: #303238; padding: 6px; border: 0; }
"""

LIGHT_THEME = """
QWidget { background: #f5f6f8; color: #202124; font-family: 'Segoe UI'; font-size: 10pt; }
QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit, QDateEdit { background: white; border: 1px solid #c8ccd2; border-radius: 5px; padding: 6px; }
QPushButton { background: #ffffff; border: 1px solid #c4c8ce; border-radius: 5px; padding: 7px 12px; }
QPushButton:hover { background: #e9ebef; }
QTableWidget, QTreeWidget { background: white; alternate-background-color: #f0f2f5; gridline-color: #d8dbe0; }
QHeaderView::section { background: #e8eaed; padding: 6px; border: 0; }
"""


def apply_theme(app: QApplication, dark: bool = True) -> None:
    app.setStyleSheet(DARK_THEME if dark else LIGHT_THEME)
