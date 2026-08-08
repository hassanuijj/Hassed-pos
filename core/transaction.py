from __future__ import annotations

from contextlib import contextmanager
from collections.abc import Iterator

from sqlalchemy.orm import Session


@contextmanager
def transaction(session: Session) -> Iterator[Session]:
    """Run one business operation atomically.

    The caller owns the session lifecycle; this context owns commit/rollback.
    Nested calls use the existing transaction instead of committing midway.
    """
    if session.in_transaction():
        yield session
        return

    try:
        with session.begin():
            yield session
    except Exception:
        # session.begin() already rolls back; this explicit rollback also
        # clears any driver-level failed transaction state.
        session.rollback()
        raise
