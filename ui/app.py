from __future__ import annotations
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from core.system import SystemBootstrap
from core.security import SecurityError
from core.workday import WorkdayService
from core.backup import BackupService
from core.closing import ClosingService

class HassedPOSApp(tk.Tk):
    def __init__(self):
        super().__init__(); self.title("Hassed POS - ERP"); self.geometry("1200x760"); self.minsize(1000,650)
        self.bootstrap=SystemBootstrap(); self.app=self.bootstrap.initialize(); self.workday=WorkdayService(self.app.db); self.closing=ClosingService(self.app.db,self.app.finance); self._build_login()
    def _clear(self):
        for w in self.winfo_children(): w.destroy()
    def _build_login(self):
        self._clear(); f=ttk.Frame(self,padding=40); f.place(relx=.5,rely=.5,anchor="center")
        ttk.Label(f,text="Hassed POS",font=("Arial",28,"bold")).grid(row=0,column=0,columnspan=2,pady=15)
        ttk.Label(f,text="اسم المستخدم").grid(row=1,column=0,sticky="w",pady=6); u=ttk.Entry(f,width=32); u.grid(row=1,column=1,pady=6)
        ttk.Label(f,text="كلمة المرور").grid(row=2,column=0,sticky="w",pady=6); p=ttk.Entry(f,width=32,show="*"); p.grid(row=2,column=1,pady=6)
        ttk.Button(f,text="دخول",command=lambda:self._login(u.get(),p.get())).grid(row=3,column=0,columnspan=2,pady=18,sticky="ew")
    def _login(self,u,p):
        try: self.app.login(u,p); self._build_dashboard()
        except SecurityError as e: messagebox.showerror("تسجيل الدخول",str(e))
    def _build_dashboard(self):
        self._clear(); self.bind_all("<Control-f>",lambda e:self._quick_search()); self.bind_all("<F5>",lambda e:self._build_dashboard()); self.bind_all("<Control-b>",lambda e:self._backup()); self.bind_all("<Control-k>",lambda e:self._closing())
        top=ttk.Frame(self,padding=12); top.pack(fill="x"); ttk.Label(top,text="Hassed POS",font=("Arial",22,"bold")).pack(side="left")
        for text,cmd in [("بحث Ctrl+F",self._quick_search),("نسخ Ctrl+B",self._backup),("إغلاق اليوم Ctrl+K",self._closing)]: ttk.Button(top,text=text,command=cmd).pack(side="left",padx=5)
        ttk.Button(top,text="تسجيل الخروج",command=self._build_login).pack(side="right")
        body=ttk.Frame(self,padding=15); body.pack(fill="both",expand=True); daily=self.workday.today(); d=self.app.dashboard(); vals=[("مبيعات اليوم",daily["sales"]),("مشتريات اليوم",daily["purchases"]),("مصروفات اليوم",daily["expenses"]),("الصندوق",d["cash"])]
        cards=ttk.Frame(body); cards.pack(fill="x")
        for i,(t,v) in enumerate(vals): c=ttk.LabelFrame(cards,text=t,padding=18); c.grid(row=0,column=i,padx=6,sticky="nsew"); ttk.Label(c,text=str(v),font=("Arial",18,"bold")).pack(); cards.columnconfigure(i,weight=1)
        alerts=ttk.LabelFrame(body,text=f"تنبيهات ({len(daily['alerts'])})",padding=10); alerts.pack(fill="x",pady=12)
        for a in daily["alerts"]: ttk.Label(alerts,text=f"• {a['title']}: {a['message']}").pack(anchor="w")
        if not daily["alerts"]: ttk.Label(alerts,text="لا توجد تنبيهات حالية").pack(anchor="w")
        modules=ttk.LabelFrame(body,text="الوحدات",padding=15); modules.pack(fill="both",expand=True,pady=10); names=["المبيعات","المشتريات","المخزون","العملاء","الموردون","الصندوق","المحاسبة","التقارير"]
        for i,n in enumerate(names): ttk.Button(modules,text=n,command=lambda x=n:self._module(x)).grid(row=i//4,column=i%4,padx=8,pady=8,sticky="nsew",ipadx=25,ipady=18)
        for i in range(4): modules.columnconfigure(i,weight=1)
    def _quick_search(self):
        q=simpledialog.askstring("بحث سريع","اسم أو باركود أو هاتف",parent=self)
        if q:self._show_rows(self.workday.search(q))
    def _backup(self):
        try:messagebox.showinfo("النسخ الاحتياطي",f"تم إنشاء النسخة:\n{BackupService(self.app.db.path).create()}")
        except Exception as e:messagebox.showerror("النسخ الاحتياطي",str(e))
    def _closing(self):
        result=self.closing.can_close(); self._show_dict(result["summary"])
        if result["ok"]: messagebox.showinfo("إغلاق اليوم","تمت مراجعة ملخص اليوم بنجاح.")
    def _module(self,name):
        self._clear(); top=ttk.Frame(self,padding=12); top.pack(fill="x"); ttk.Button(top,text="← الرئيسية",command=self._build_dashboard).pack(side="left"); ttk.Label(top,text=name,font=("Arial",20,"bold")).pack(side="right"); f=ttk.Frame(self,padding=20); f.pack(fill="both",expand=True)
        if name=="المخزون":self._inventory(f)
        elif name in ("العملاء","الموردون"):self._master(f,name)
        elif name=="التقارير":self._reports(f)
        elif name in ("المبيعات","المشتريات"):self._transaction(f,"sale" if name=="المبيعات" else "purchase")
        elif name=="الصندوق":self._cash(f)
        elif name=="المحاسبة":self._accounting(f)
        if name=="العملاء":ttk.Button(f,text="الذمم المستحقة",command=lambda:self._show_rows(self.closing.receivables())).pack(fill="x",pady=8)
    def _inventory(self,p):
        tree=self._tree(p,["الاسم","الباركود","سعر البيع","الحد الأدنى"])
        for r in self.app.master.products():tree.insert("","end",values=(r["name"],r["barcode"],r["sale_price"],r["min_stock"]))
    def _master(self,p,name):
        kind="customers" if name=="العملاء" else "suppliers";tree=self._tree(p,["الاسم","الهاتف"])
        for r in getattr(self.app.master,kind)():tree.insert("","end",values=(r["name"],r["phone"] if "phone" in r.keys() else ""))
    def _transaction(self,p,kind):
        box=ttk.LabelFrame(p,text="عملية جديدة",padding=15);box.pack(fill="x",pady=10);ttk.Label(box,text="مرجع الفاتورة").grid(row=0,column=0);ttk.Entry(box).grid(row=0,column=1);ttk.Label(box,text="معرّف العميل/المورد").grid(row=1,column=0);ttk.Entry(box).grid(row=1,column=1);ttk.Button(box,text="عرض السجل",command=lambda:self._document_list(kind)).grid(row=2,column=0,columnspan=2,sticky="ew",pady=8)
    def _document_list(self,kind):self._show_rows(self.app.db.fetchall("SELECT reference,total,paid,created_at FROM documents WHERE document_type=? ORDER BY created_at DESC",(kind,)))
    def _cash(self,p):ttk.Label(p,text=f"رصيد الصندوق: {self.app.finance.cash_balance()}",font=("Arial",20,"bold")).pack(pady=20);self._show_rows(self.app.db.fetchall("SELECT reference,transaction_type,amount,description,created_at FROM cash_transactions ORDER BY created_at DESC"))
    def _accounting(self,p):ttk.Button(p,text="ميزان المراجعة",command=lambda:self._show_rows(self.app.trial_balance())).pack(fill="x",pady=5);ttk.Button(p,text="دفتر الأستاذ",command=self._ledger_prompt).pack(fill="x",pady=5)
    def _ledger_prompt(self):
        code=simpledialog.askstring("دفتر الأستاذ","رمز الحساب",parent=self)
        if code:
            try:self._show_rows(self.app.finance.ledger(code))
            except Exception as e:messagebox.showerror("المحاسبة",str(e))
    def _reports(self,p):
        for text,cmd in [("ميزان المراجعة",lambda:self._show_rows(self.app.trial_balance())),("قائمة الدخل",lambda:self._show_dict(self.app.income_statement())),("الميزانية",lambda:self._show_dict(self.app.balance_sheet()))]:ttk.Button(p,text=text,command=cmd).pack(fill="x",pady=5)
    def _tree(self,p,columns):
        t=ttk.Treeview(p,columns=columns,show="headings")
        for c in columns:t.heading(c,text=c);t.column(c,width=180)
        t.pack(fill="both",expand=True);return t
    def _show_rows(self,rows):
        win=tk.Toplevel(self);win.title("النتائج");win.geometry("950x550");cols=list(rows[0].keys()) if rows else ["نتيجة"];t=self._tree(win,cols)
        for r in rows:t.insert("","end",values=tuple(r[k] for k in cols))
    def _show_dict(self,d):messagebox.showinfo("التقرير","\n".join(f"{k}: {v}" for k,v in d.items()))

def main(): HassedPOSApp().mainloop()
if __name__=="__main__": main()
