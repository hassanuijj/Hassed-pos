from __future__ import annotations

from PyQt6.QtWidgets import QMainWindow, QStackedWidget

from ui.help import show_help
from ui.pos_window import POSWindow
from ui.shortcuts import install_shortcuts


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HASSED ERP")
        self.resize(1280, 800)
        self.stack = QStackedWidget()
        self.pos = POSWindow(self)
        self.stack.addWidget(self.pos)
        self.setCentralWidget(self.stack)
        self._shortcuts = install_shortcuts(self, {
            "F1": lambda: show_help(self, "dashboard"),
            "F11": self.toggle_fullscreen,
        })

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
