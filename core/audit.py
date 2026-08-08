from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from core.exceptions import ValidationError
from models import AuditLog


class AuditService:
    def __init__(self, session: Session):
        self.session = session

    def record(self, *, company_id: int, user_id: int | None, action: str, entity_type: str, entity_id: int | None = None, details: dict[str, Any] | None = None) -> AuditLog:
        if not company_id:
            raise ValidationError("معرّف الشركة مطلوب لسجل المراجعة.")
        if not action or not entity_type:
            raise ValidationError("نوع العملية والكيان مطلوبان لسجل المراجعة.")
        entry = AuditLog(company_id=company_id, user_id=user_id, action=action.upper(), entity_type=entity_type, entity_id=entity_id, details=json.dumps(details or {}, ensure_ascii=False, default=str))
        self.session.add(entry)
        self.session.flush()
        return entry
