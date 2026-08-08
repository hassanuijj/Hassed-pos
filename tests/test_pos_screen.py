import tkinter as tk
from ui.pos_screen import POSScreen


def test_pos_screen_builds():
    root=tk.Tk(); root.withdraw()
    class FakePOS: pass
    screen=POSScreen(root,FakePOS())
    assert screen.entry is not None
    assert screen.tree is not None
    root.destroy()
