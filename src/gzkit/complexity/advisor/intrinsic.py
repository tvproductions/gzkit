"""@intrinsic_complexity decorator and runtime registry (OBPI-0.0.29-07).

REQ-0.0.29-07-01: Decorator registers (file_path, qualname) -> (reason, attestor, date).
REQ-0.0.29-07-02: Decorator is a strict no-op at runtime — returns the function unchanged.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from datetime import date
from typing import TypeVar

_F = TypeVar("_F", bound=Callable[..., object])

_REGISTRY: dict[tuple[str, str], tuple[str, str, str]] = {}


def intrinsic_complexity(*, reason: str, attestor: str) -> Callable[[_F], _F]:
    """Decorator declaring a function as having irreducibly intrinsic complexity.

    No-op at runtime: returns the decorated function unchanged.
    Registers (file_path, qualname) -> (reason, attestor, date) in the module registry.
    """
    decoration_date = date.today().isoformat()

    def decorator(fn: _F) -> _F:
        file_path = inspect.getfile(fn)
        _REGISTRY[(file_path, fn.__qualname__)] = (reason, attestor, decoration_date)
        return fn

    return decorator


def get_attestation(file_path: str, qualname: str) -> tuple[str, str, str] | None:
    """Look up the registry for (file_path, qualname).

    Returns (reason, attestor, decoration_date) or None if not registered.
    """
    return _REGISTRY.get((file_path, qualname))


def clear_registry() -> None:
    """Clear the registry. For testing ONLY — do NOT call in production code."""
    _REGISTRY.clear()
