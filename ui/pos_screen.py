from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox

class POSScreen(ttk.Frame):
    def __init__(self, master, pos_service, on_done=None):
        super().__init__(master, padding=12); self.pos=pos_service; self.on_done=on_done; self.cart={}; self._build()

    def _build(self):
        self.columnconfigure(0,weight=1); self.rowconfigure(1,weight=1)
        top=ttk.Frame(self); top.grid(row=0,column=0,sticky='ew'); top.columnconfigure(0,weight=1)
        self.entry=ttk.Entry(top,font=('Arial',18)); self.entry.grid(row=0,column=0,sticky='ew',padx=5); self.entry.bind('<Return>',self.scan); self.entry.focus_set()
        ttk.Button(top,text='مسح',command=self.scan).grid(row=0,column=1,padx=5)
        self.tree=ttk.Treeview(self,columns=('name','qty','price','total'),show='headings'); self.tree.grid(row=1,column=0,sticky='nsew',pady=10)
        for c,t in zip(('name','qty','price','total'),('الصنف','الكمية','السعر','الإجمالي')): self.tree.heading(c,text=t)
        bottom=ttk.Frame(self); bottom.grid(row=2,column=0,sticky='ew'); self.total=ttk.Label(bottom,text='الإجمالي: 0',font=('Arial',18,'bold')); self.total.pack(side='left')
        ttk.Button(bottom,text='مسح السلة',command=self.clear).pack(side='right',padx=5); ttk.Button(bottom,text='إتمام البيع',command=self.checkout).pack(side='right',padx=5)

    def scan(self,event=None):
        code=self.entry.get().strip(); self.entry.delete(0,'end')
        if not code:return
        try: product=self.pos.product_by_barcode(code)
        except Exception as exc: messagebox.showerror('الباركود',str(exc)); return
        pid=product['id']; row=self.cart.get(pid)
        if row: row['quantity']+=1
        else: self.cart[pid]={'product':product,'quantity':1}
        if row and row['quantity']>float(product['quantity']): row['quantity']-=1; messagebox.showwarning('المخزون','الكمية المطلوبة غير متوفرة'); return
        self.refresh()

    def refresh(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        total=0
        for row in self.cart.values():
            p=row['product']; qty=row['quantity']; line=qty*float(p['sale_price']); total+=line
            self.tree.insert('','end',values=(p['name'],qty,p['sale_price'],line))
        self.total.config(text=f'الإجمالي: {total:.2f}')

    def clear(self): self.cart.clear(); self.refresh(); self.entry.focus_set()

    def checkout(self):
        if not self.cart: return
        try:
            result=self.pos.checkout(list(self.cart.values()))
            messagebox.showinfo('البيع',f"تم حفظ الفاتورة {result['reference']}\nالإجمالي: {result['total']}")
            self.clear()
            if self.on_done:self.on_done(result)
        except Exception as exc: messagebox.showerror('البيع',str(exc))
