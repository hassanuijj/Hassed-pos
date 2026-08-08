from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from sqlalchemy.orm import Session


T = TypeVar("T")


def run_atomic(session: Session, operation: Callable[[], T]) -> T:
    """Run an ERP operation atomically; exceptions force rollback."""
    try:
        with session.begin():
            return operation()
    except Exception:
        session.rollback()
        raise
