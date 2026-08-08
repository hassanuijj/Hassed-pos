from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CheckoutFailure:
    code: str
    message: str
    rolled_back: bool = True
