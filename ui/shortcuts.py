from __future__ import annotations

from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QWidget


def install_shortcuts(window: QWidget, handlers: dict[str, callable]) -> list[QShortcut]:
    shortcuts = []
    for key, handler in handlers.items():
        shortcut = QShortcut(QKeySequence(key), window)
        shortcut.activated.connect(handler)
        shortcuts.append(shortcut)
    return shortcuts
