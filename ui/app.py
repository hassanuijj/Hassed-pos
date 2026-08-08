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
        for widget in self.winfo_children(): widget.destroy()

    def _build_login(self):
        self._clear(); frame=ttk.Frame(self,padding=40); frame.place(relx=.5,rely=.5,anchor="center")
        ttk.Label(frame,text="Hassed POS",font=("Arial",28,"bold")).grid(row=0,column=0,columnspan=2,pady=15)
        ttk.Label(frame,text="اسم المستخدم").grid(row=1,column=0,sticky="w",pady=6); user=ttk.Entry(frame,width=32); user.grid(row=1,column=1,pady=6)
        ttk.Label(frame,text="كلمة المرور").grid(row=2,column=0,sticky="w",pady=6); password=ttk.Entry(frame,width=32,show="*"); password.grid(row=2,column=1,pady=6)
        ttk.Button(frame,text="دخول",command=lambda:self._login(user.get(),password.get())).grid(row=3,column=0,columnspan=2,pady=18,sticky="ew")

    def _login(self,username,password):
        try: self.app.login(username,password); self._build_dashboard()
        except SecurityError as exc: messagebox.showerror("تسجيل الدخول",str(exc))

    def _build_dashboard(self):
        self._clear(); top=ttk.Frame(self,padding=12); top.pack(fill="x")
        ttk.Label(top,text="Hassed POS",font=("Arial",22,"bold")).pack(side="left")
        ttk.Button(top,text="تسجيل الخروج",command=self._build_login).pack(side="right")
        body=ttk.Frame(self,padding=15); body.pack(fill="both",expand=True); cards=ttk.Frame(body); cards.pack(fill="x")
        dashboard=self.app.dashboard(); values=[("المبيعات",dashboard["sales"]["total"]),("المشتريات",dashboard["purchases"]["total"]),("الصندوق",dashboard["cash"]),("الربح الإجمالي",dashboard["profit"]["gross_profit"])]
        for i,(title,value) in enumerate(values):
            card=ttk.LabelFrame(cards,text=title,padding=18); card.grid(row=0,column=i,padx=6,sticky="nsew"); ttk.Label(card,text=str(value),font=("Arial",18,"bold")).pack(); cards.columnconfigure(i,weight=1)
        modules=ttk.LabelFrame(body,text="الوحدات",padding=15); modules.pack(fill="both",expand=True,pady=20)
        names=["المبيعات","المشتريات","المخزون","العملاء","الموردون","الصندوق","المحاسبة","التقارير"]
        for i,name in enumerate(names): ttk.Button(modules,text=name,command=lambda n=name:self._module(n)).grid(row=i//4,column=i%4,padx=8,pady=8,sticky="nsew",ipadx=25,ipady=18)
        for i in range(4): modules.columnconfigure(i,weight=1)

    def _module(self,name):
        self._clear(); top=ttk.Frame(self,padding=12); top.pack(fill="x")
        ttk.Button(top,text="← الرئيسية",command=self._build_dashboard).pack(side="left")
        ttk.Label(top,text=name,font=("Arial",20,"bold")).pack(side="right")
        frame=ttk.Frame(self,padding=20); frame.pack(fill="both",expand=True)
        if name=="المخزون": self._inventory(frame)
        elif name=="العملاء": self._master(frame,"customers")
        elif name=="الموردون": self._master(frame,"suppliers")
        elif name=="التقارير": self._reports(frame)
        else: ttk.Label(frame,text=f"واجهة {name} جاهزة للربط بالعملية التشغيلية من خلال طبقة ERP.",font=("Arial",16)).pack(pady=40)

    def _inventory(self,parent):
        rows=self.app.master.products(); tree=self._tree(parent,["الاسم","الباركود","سعر البيع","الحد الأدنى"])
        for r in rows: tree.insert("","end",values=(r["name"],r["barcode"],r["sale_price"],r["min_stock"]))

    def _master(self,parent,kind):
        rows=getattr(self.app.master,kind)(); labels=["الاسم","الهاتف"]
        tree=self._tree(parent,labels)
        for r in rows: tree.insert("","end",values=(r["name"],r.get("phone","") if hasattr(r,"get") else ""))

    def _reports(self,parent):
        ttk.Button(parent,text="ميزان المراجعة",command=lambda:self._show_rows(self.app.trial_balance())).pack(fill="x",pady=5)
        ttk.Button(parent,text="قائمة الدخل",command=lambda:self._show_dict(self.app.income_statement())).pack(fill="x",pady=5)
        ttk.Button(parent,text="الميزانية",command=lambda:self._show_dict(self.app.balance_sheet())).pack(fill="x",pady=5)

    def _tree(self,parent,columns):
        tree=ttk.Treeview(parent,columns=columns,show="headings")
        for c in columns: tree.heading(c,text=c); tree.column(c,width=180)
        tree.pack(fill="both",expand=True); return tree

    def _show_rows(self,rows):
        win=tk.Toplevel(self); win.title("التقرير"); win.geometry("900x500"); tree=self._tree(win,list(rows[0].keys()) if rows else ["نتيجة"])
        for r in rows: tree.insert("","end",values=tuple(r[k] for k in tree["columns"]))

    def _show_dict(self,data): messagebox.showinfo("التقرير","\n".join(f"{k}: {v}" for k,v in data.items()))


def main(): HassedPOSApp().mainloop()

if __name__=="__main__": main()
