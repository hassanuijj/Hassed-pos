from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from core.exceptions import UnbalancedEntryError, ValidationError


class JournalEntry(Base):
    __tablename__ = "journal_entries"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    fiscal_year_id: Mapped[int] = mapped_column(ForeignKey("fiscal_years.id", ondelete="RESTRICT"), nullable=False, index=True)
    entry_number: Mapped[str] = mapped_column(String(60), nullable=False)
    entry_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="DRAFT", index=True)
    description: Mapped[str | None] = mapped_column(Text)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime)
    posted_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    __table_args__ = (Index("ix_journal_company_date", "company_id", "entry_date"),)


class JournalLine(Base):
    __tablename__ = "journal_lines"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    journal_entry_id: Mapped[int] = mapped_column(ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False, index=True)
    currency_id: Mapped[int] = mapped_column(ForeignKey("currencies.id", ondelete="RESTRICT"), nullable=False)
    debit: Mapped[Decimal] = mapped_column(Numeric(28, 8), nullable=False, default=0)
    credit: Mapped[Decimal] = mapped_column(Numeric(28, 8), nullable=False, default=0)
    exchange_rate: Mapped[Decimal] = mapped_column(Numeric(28, 12), nullable=False, default=1)
    debit_base: Mapped[Decimal] = mapped_column(Numeric(28, 8), nullable=False, default=0)
    credit_base: Mapped[Decimal] = mapped_column(Numeric(28, 8), nullable=False, default=0)
    description: Mapped[str | None] = mapped_column(Text)


def validate_lines(lines: list[dict]) -> None:
    if not lines:
        raise ValidationError("القيد لا يحتوي على أسطر")
    debit = sum((Decimal(str(x.get("debit", 0))) for x in lines), Decimal("0"))
    credit = sum((Decimal(str(x.get("credit", 0))) for x in lines), Decimal("0"))
    if debit != credit:
        raise UnbalancedEntryError(f"القيد غير متوازن: مدين={debit} دائن={credit}")
    for line in lines:
        d = Decimal(str(line.get("debit", 0)))
        c = Decimal(str(line.get("credit", 0)))
        if d < 0 or c < 0 or (d > 0 and c > 0):
            raise ValidationError("كل سطر يجب أن يكون مدينًا أو دائنًا فقط وبقيمة غير سالبة")
