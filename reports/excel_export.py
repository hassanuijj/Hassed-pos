from __future__ import annotations

from pathlib import Path
from typing import Iterable

from openpyxl import Workbook


class ExcelExporter:
    def export_table(self, output: str | Path, headers: list[str], rows: Iterable[Iterable[object]]) -> Path:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Report"
        sheet.append(headers)
        for row in rows:
            sheet.append(list(row))
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions
        for column in sheet.columns:
            width = max(len(str(cell.value or "")) for cell in column) + 2
            sheet.column_dimensions[column[0].column_letter].width = min(width, 50)
        workbook.save(path)
        return path
