from __future__ import annotations

from pathlib import Path
from decimal import Decimal

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas


class InvoicePDF:
    def __init__(self, output: str | Path):
        self.output = Path(output)

    def generate(self, invoice_number: str, customer: str, lines: list[tuple[str, Decimal, Decimal]], total: Decimal) -> Path:
        self.output.parent.mkdir(parents=True, exist_ok=True)
        pdf = canvas.Canvas(str(self.output), pagesize=A4)
        width, height = A4
        pdf.setTitle(f"Invoice {invoice_number}")
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(40, height - 50, "HASSED ERP")
        pdf.setFont("Helvetica", 10)
        pdf.drawString(40, height - 70, f"Invoice: {invoice_number}")
        pdf.drawString(40, height - 85, f"Customer: {customer}")
        y = height - 125
        pdf.setFont("Helvetica-Bold", 10)
        for x, title in [(40, "Item"), (300, "Qty"), (370, "Price"), (450, "Total")]:
            pdf.drawString(x, y, title)
        y -= 20
        pdf.setFont("Helvetica", 9)
        for name, quantity, price in lines:
            line_total = Decimal(str(quantity)) * Decimal(str(price))
            pdf.drawString(40, y, str(name)[:38])
            pdf.drawRightString(340, y, f"{quantity}")
            pdf.drawRightString(420, y, f"{price:.2f}")
            pdf.drawRightString(520, y, f"{line_total:.2f}")
            y -= 18
            if y < 60:
                pdf.showPage()
                y = height - 50
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawRightString(520, y - 10, f"Total: {Decimal(str(total)):.2f}")
        pdf.save()
        return self.output
