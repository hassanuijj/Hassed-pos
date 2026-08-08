from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

try:
    from inventory_accounting_integration import InventoryAccountingService
except ImportError as exc:
    raise SystemExit(f"تعذر تحميل طبقة المحاسبة والمخزون: {exc}")


class HassedPOSApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hassed POS - النظام المحاسبي وإدارة المخزون")
        self.geometry("1200x760")
        self.minsize(1000, 650)

        self.service = InventoryAccountingService()
        self._configure_style()
        self._build_ui()
        self.refresh_dashboard()

    def _configure_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"))
        style.configure("Card.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("Treeview", rowheight=28)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def _build_ui(self):
        header = ttk.Frame(self, padding=16)
        header.pack(fill="x")
        ttk.Label(header, text="Hassed POS", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text="النظام المحاسبي والمخزون والمشتريات والمبيعات").pack(side="right")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.dashboard_tab = ttk.Frame(notebook, padding=12)
        self.inventory_tab = ttk.Frame(notebook, padding=12)
        self.purchase_tab = ttk.Frame(notebook, padding=12)
        self.sale_tab = ttk.Frame(notebook, padding=12)
        self.accounting_tab = ttk.Frame(notebook, padding=12)

        notebook.add(self.dashboard_tab, text="الرئيسية")
        notebook.add(self.inventory_tab, text="المخزون")
        notebook.add(self.purchase_tab, text="المشتريات")
        notebook.add(self.sale_tab, text="المبيعات")
        notebook.add(self.accounting_tab, text="المحاسبة")

        self._build_dashboard()
        self._build_inventory()
        self._build_purchase()
        self._build_sale()
        self._build_accounting()

    def _build_dashboard(self):
        for i in range(4):
            self.dashboard_tab.columnconfigure(i, weight=1)

        self.stock_card = ttk.Label(self.dashboard_tab, text="المخزون\n0", style="Card.TLabel", anchor="center")
        self.purchase_card = ttk.Label(self.dashboard_tab, text="المشتريات\n0", style="Card.TLabel", anchor="center")
        self.sales_card = ttk.Label(self.dashboard_tab, text="المبيعات\n0", style="Card.TLabel", anchor="center")
        self.entries_card = ttk.Label(self.dashboard_tab, text="القيود\n0", style="Card.TLabel", anchor="center")

        for i, card in enumerate((self.stock_card, self.purchase_card, self.sales_card, self.entries_card)):
            card.grid(row=0, column=i, sticky="nsew", padx=6, pady=6, ipady=30)

        ttk.Button(self.dashboard_tab, text="تحديث", command=self.refresh_dashboard).grid(row=1, column=0, pady=20)

    def _build_inventory(self):
        self.inventory_tree = ttk.Treeview(
            self.inventory_tab,
            columns=("product", "qty", "cost"),
            show="headings",
        )
        for col, title in (("product", "الصنف"), ("qty", "الكمية"), ("cost", "متوسط التكلفة")):
            self.inventory_tree.heading(col, text=title)
            self.inventory_tree.column(col, width=240)
        self.inventory_tree.pack(fill="both", expand=True)

    def _build_purchase(self):
        form = ttk.Frame(self.purchase_tab)
        form.pack(fill="x", pady=8)
        self.p_product = tk.StringVar()
        self.p_qty = tk.StringVar(value="1")
        self.p_cost = tk.StringVar(value="0")
        self.p_paid = tk.StringVar(value="0")
        for row, (label, var) in enumerate((("الصنف", self.p_product), ("الكمية", self.p_qty), ("تكلفة الوحدة", self.p_cost), ("المدفوع", self.p_paid))):
            ttk.Label(form, text=label).grid(row=0, column=row * 2, padx=5)
            ttk.Entry(form, textvariable=var, width=18).grid(row=0, column=row * 2 + 1, padx=5)
        ttk.Button(form, text="ترحيل شراء", command=self.post_purchase).grid(row=0, column=8, padx=10)

        self.purchase_log = tk.Text(self.purchase_tab, height=20, state="disabled")
        self.purchase_log.pack(fill="both", expand=True, pady=10)

    def _build_sale(self):
        form = ttk.Frame(self.sale_tab)
        form.pack(fill="x", pady=8)
        self.s_product = tk.StringVar()
        self.s_qty = tk.StringVar(value="1")
        self.s_price = tk.StringVar(value="0")
        self.s_paid = tk.StringVar(value="0")
        for row, (label, var) in enumerate((("الصنف", self.s_product), ("الكمية", self.s_qty), ("سعر الوحدة", self.s_price), ("المدفوع", self.s_paid))):
            ttk.Label(form, text=label).grid(row=0, column=row * 2, padx=5)
            ttk.Entry(form, textvariable=var, width=18).grid(row=0, column=row * 2 + 1, padx=5)
        ttk.Button(form, text="ترحيل بيع", command=self.post_sale).grid(row=0, column=8, padx=10)

        self.sale_log = tk.Text(self.sale_tab, height=20, state="disabled")
        self.sale_log.pack(fill="both", expand=True, pady=10)

    def _build_accounting(self):
        self.accounting_tree = ttk.Treeview(
            self.accounting_tab,
            columns=("reference", "description", "debit", "credit"),
            show="headings",
        )
        for col, title, width in (("reference", "المرجع", 180), ("description", "البيان", 350), ("debit", "مدين", 160), ("credit", "دائن", 160)):
            self.accounting_tree.heading(col, text=title)
            self.accounting_tree.column(col, width=width)
        self.accounting_tree.pack(fill="both", expand=True)

    def post_purchase(self):
        try:
            reference = f"PUR-{len(self.service.accounting.entries) + 1:06d}"
            result = self.service.purchase(
                reference=reference,
                supplier_id="SUP-DEFAULT",
                paid=self.p_paid.get(),
                lines=[{
                    "product_id": self.p_product.get().strip(),
                    "quantity": self.p_qty.get(),
                    "unit_cost": self.p_cost.get(),
                }],
            )
            self._log(self.purchase_log, f"تم ترحيل {reference}: {result}")
            self.refresh_dashboard()
        except Exception as exc:
            messagebox.showerror("خطأ في الشراء", str(exc))

    def post_sale(self):
        try:
            reference = f"SAL-{len(self.service.accounting.entries) + 1:06d}"
            result = self.service.sale(
                reference=reference,
                customer_id="CUS-DEFAULT",
                paid=self.s_paid.get(),
                lines=[{
                    "product_id": self.s_product.get().strip(),
                    "quantity": self.s_qty.get(),
                    "unit_price": self.s_price.get(),
                }],
            )
            self._log(self.sale_log, f"تم ترحيل {reference}: {result}")
            self.refresh_dashboard()
        except Exception as exc:
            messagebox.showerror("خطأ في البيع", str(exc))

    @staticmethod
    def _log(widget, text):
        widget.configure(state="normal")
        widget.insert("end", text + "\n")
        widget.configure(state="disabled")
        widget.see("end")

    def refresh_dashboard(self):
        products = set(self.service.stock.layers)
        total_stock = sum(self.service.stock.available(p) for p in products)
        purchase_count = sum(1 for x in self.service.accounting.entries if x.reference.startswith("PUR-"))
        sales_count = sum(1 for x in self.service.accounting.entries if x.reference.startswith("SAL-"))

        self.stock_card.configure(text=f"المخزون\n{total_stock}")
        self.purchase_card.configure(text=f"المشتريات\n{purchase_count}")
        self.sales_card.configure(text=f"المبيعات\n{sales_count}")
        self.entries_card.configure(text=f"القيود\n{len(self.service.accounting.entries)}")

        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        for product in sorted(products):
            self.inventory_tree.insert("", "end", values=(product, self.service.stock.available(product), self.service.stock.average_cost(product) if hasattr(self.service.stock, "average_cost") else "-"))

        for item in self.accounting_tree.get_children():
            self.accounting_tree.delete(item)
        for entry in self.service.accounting.entries:
            self.accounting_tree.insert("", "end", values=(entry.reference, entry.description, entry.debit, entry.credit))


def main():
    app = HassedPOSApp()
    app.mainloop()


if __name__ == "__main__":
    main()
