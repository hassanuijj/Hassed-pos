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
    __table_args__ = (
        Index("ix_journal_company_date", "company_id", "entry_date"),
        Index("ix_journal_company_number", "company_id", "entry_number", unique=True),
    )


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


_EPS = Decimal("0.00000001")


def validate_lines(lines: list[dict]) -> None:
    if not lines:
        raise ValidationError("القيد لا يحتوي على أسطر")

    debit = Decimal("0")
    credit = Decimal("0")
    debit_base = Decimal("0")
    credit_base = Decimal("0")
    by_currency: dict[int, tuple[Decimal, Decimal]] = {}

    for line in lines:
        d = Decimal(str(line.get("debit", 0)))
        c = Decimal(str(line.get("credit", 0)))
        db = Decimal(str(line.get("debit_base", 0)))
        cb = Decimal(str(line.get("credit_base", 0)))
        rate = Decimal(str(line.get("exchange_rate", 1)))
        currency_id = line.get("currency_id")

        if currency_id is None:
            raise ValidationError("يجب تحديد العملة لكل سطر محاسبي")
        if any(value.is_nan() or value.is_infinite() for value in (d, c, db, cb, rate)):
            raise ValidationError("القيم المحاسبية يجب أن تكون أرقامًا صحيحة")
        if d < 0 or c < 0 or db < 0 or cb < 0:
            raise ValidationError("القيم المدينة والدائنة لا يمكن أن تكون سالبة")
        if d > 0 and c > 0:
            raise ValidationError("كل سطر يجب أن يكون مدينًا أو دائنًا فقط")
        if d == 0 and c == 0:
            raise ValidationError("لا يمكن أن يكون السطر المحاسبي بدون مدين أو دائن")
        if rate <= 0:
            raise ValidationError("سعر الصرف يجب أن يكون أكبر من صفر")

        if d == 0 and db != 0:
            raise ValidationError("لا يجوز وجود مكافئ محلي مدين بدون مبلغ مدين")
        if c == 0 and cb != 0:
            raise ValidationError("لا يجوز وجود مكافئ محلي دائن بدون مبلغ دائن")
        if d and abs(db - d * rate) > _EPS:
            raise ValidationError("المكافئ المحلي للمدين غير مطابق لسعر الصرف")
        if c and abs(cb - c * rate) > _EPS:
            raise ValidationError("المكافئ المحلي للدائن غير مطابق لسعر الصرف")

        debit += d
        credit += c
        debit_base += db
        credit_base += cb
        key = int(currency_id)
        old_d, old_c = by_currency.get(key, (Decimal("0"), Decimal("0")))
        by_currency[key] = (old_d + d, old_c + c)

    if abs(debit - credit) > _EPS:
        raise UnbalancedEntryError(f"القيد غير متوازن: مدين={debit} دائن={credit}")
    if abs(debit_base - credit_base) > _EPS:
        raise UnbalancedEntryError(f"المكافئ المحلي غير متوازن: مدين={debit_base} دائن={credit_base}")
    if any(abs(d - c) > _EPS for d, c in by_currency.values()):
        raise UnbalancedEntryError("القيد غير متوازن حسب العملة")
