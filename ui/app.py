from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from core.system import SystemBootstrap
from core.security import SecurityError


class HassedPOSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hassed POS - ERP")
        self.geometry("1200x760")
        self.minsize(1000, 650)
        self.bootstrap = SystemBootstrap()
        self.app = self.bootstrap.initialize()
        self._build_login()

    def _clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def _build_login(self):
        self._clear()
        frame = ttk.Frame(self, padding=40)
        frame.place(relx=.5, rely=.5, anchor="center")
        ttk.Label(frame, text="Hassed POS", font=("Arial", 28, "bold")).grid(row=0, column=0, columnspan=2, pady=15)
        ttk.Label(frame, text="اسم المستخدم").grid(row=1, column=0, sticky="w", pady=6)
        user = ttk.Entry(frame, width=32)
        user.grid(row=1, column=1, pady=6)
        ttk.Label(frame, text="كلمة المرور").grid(row=2, column=0, sticky="w", pady=6)
        password = ttk.Entry(frame, width=32, show="*")
        password.grid(row=2, column=1, pady=6)
        ttk.Button(frame, text="دخول", command=lambda: self._login(user.get(), password.get())).grid(row=3, column=0, columnspan=2, pady=18, sticky="ew")

    def _login(self, username, password):
        try:
            self.app.login(username, password)
            self._build_dashboard()
        except SecurityError as exc:
            messagebox.showerror("تسجيل الدخول", str(exc))

    def _build_dashboard(self):
        self._clear()
        top = ttk.Frame(self, padding=12)
        top.pack(fill="x")
        ttk.Label(top, text="Hassed POS", font=("Arial", 22, "bold")).pack(side="left")
        ttk.Button(top, text="تسجيل الخروج", command=self._build_login).pack(side="right")
        body = ttk.Frame(self, padding=15)
        body.pack(fill="both", expand=True)
        cards = ttk.Frame(body)
        cards.pack(fill="x")
        dashboard = self.app.dashboard()
        values = [
            ("المبيعات", dashboard["sales"]["total"]),
            ("المشتريات", dashboard["purchases"]["total"]),
            ("الصندوق", dashboard["cash"]),
            ("الربح الإجمالي", dashboard["profit"]["gross_profit"]),
        ]
        for i, (title, value) in enumerate(values):
            card = ttk.LabelFrame(cards, text=title, padding=18)
            card.grid(row=0, column=i, padx=6, sticky="nsew")
            ttk.Label(card, text=str(value), font=("Arial", 18, "bold")).pack()
            cards.columnconfigure(i, weight=1)

        modules = ttk.LabelFrame(body, text="الوحدات", padding=15)
        modules.pack(fill="both", expand=True, pady=20)
        names = ["المبيعات", "المشتريات", "المخزون", "العملاء", "الموردون", "الصندوق", "المحاسبة", "التقارير"]
        for i, name in enumerate(names):
            ttk.Button(modules, text=name, command=lambda n=name: self._module(n)).grid(row=i // 4, column=i % 4, padx=8, pady=8, sticky="nsew", ipadx=25, ipady=18)
        for i in range(4):
            modules.columnconfigure(i, weight=1)

    def _module(self, name):
        messagebox.showinfo(name, f"وحدة {name} مرتبطة بطبقة ERP وسيتم فتح شاشة الوحدة هنا.")


def main():
    HassedPOSApp().mainloop()


if __name__ == "__main__":
    main()
