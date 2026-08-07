from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class WhatsAppMessageRecord:
    customer_id: int
    phone: str
    template_name: str
    message: str
    reference_type: str | None = None
    reference_id: int | None = None
    created_at: datetime = datetime.now(timezone.utc)
