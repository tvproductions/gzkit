"""@intrinsic_complexity decorator and runtime registry (OBPI-0.0.29-07).

REQ-0.0.29-07-01: Decorator registers (file_path, qualname) -> (reason, attestor, date).
REQ-0.0.29-07-02: Decorator is a strict no-op at runtime — returns the function unchanged.
"""

from __future__ import annotations

import ast
import inspect
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import TypeVar

from gzkit.ledger import Ledger

_F = TypeVar("_F", bound=Callable[..., object])

# (reason, attestor, date)
Attestation = tuple[str, str, str]

_LEDGER_EVENT = "intrinsic-complexity-attestation"

_REGISTRY: dict[tuple[str, str], Attestation] = {}


def intrinsic_complexity(*, reason: str, attestor: str) -> Callable[[_F], _F]:
    """Declare a function as having irreducibly intrinsic complexity.

    No-op at runtime: returns the decorated function unchanged.
    Registers (file_path, qualname) -> (reason, attestor, date) in the module registry.
    """
    decoration_date = date.today().isoformat()

    def decorator(fn: _F) -> _F:
        file_path = inspect.getfile(fn)
        qualname = getattr(fn, "__qualname__", None) or getattr(
            fn, "__name__", type(fn).__qualname__
        )
        _REGISTRY[(file_path, qualname)] = (reason, attestor, decoration_date)
        return fn

    return decorator


def get_attestation(file_path: str, qualname: str) -> tuple[str, str, str] | None:
    """Look up the registry for (file_path, qualname).

    Returns (reason, attestor, decoration_date) or None if not registered.
    """
    return _REGISTRY.get((file_path, qualname))


def decorator_attestation(node: ast.AST) -> Attestation | None:
    """Read a literal ``@intrinsic_complexity(reason=..., attestor=...)`` off *node*.

    The CLI reads source without importing it, so the registry is never filled
    for its targets (GHI #1102); this reads the declaration itself. The date is
    the read date, as the registry's is the decoration (import) date. Arguments
    that are not non-empty string literals are not honoured: they cannot be read
    without executing the file, and an empty one would be a silent escape hatch.
    """
    for decorator in getattr(node, "decorator_list", ()):
        if not isinstance(decorator, ast.Call):
            continue
        func = decorator.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
        if name != "intrinsic_complexity":
            continue
        kwargs = {kw.arg: kw.value for kw in decorator.keywords}
        reason, attestor = _literal(kwargs.get("reason")), _literal(kwargs.get("attestor"))
        if reason and attestor:
            return reason, attestor, date.today().isoformat()
    return None


def _literal(value: ast.expr | None) -> str | None:
    if isinstance(value, ast.Constant) and isinstance(value.value, str) and value.value.strip():
        return value.value
    return None


def ledger_attestations(ledger_path: Path) -> dict[tuple[str, str], Attestation]:
    """Index ``intrinsic-complexity-attestation`` events by (resolved file, qualname).

    A relative ``file_path`` resolves against the working directory, where
    ``--attest-intrinsic`` recorded it; the latest event for a key wins.
    """
    if not ledger_path.exists():
        return {}
    index: dict[tuple[str, str], Attestation] = {}
    for event in Ledger(ledger_path).read_all():
        if event.event != _LEDGER_EVENT:
            continue
        extra = event.extra
        key = (str(Path(extra["file_path"]).resolve()), extra["qualname"])
        index[key] = (extra["reason"], extra["attestor"], extra["attestation_date"])
    return index


def find_attestation(
    node: ast.AST,
    source_file: Path,
    qualname: str,
    ledger_index: dict[tuple[str, str], Attestation],
) -> Attestation | None:
    """Return the attestation for a diagnosed function, from source or ledger."""
    return decorator_attestation(node) or ledger_index.get((str(source_file.resolve()), qualname))


def clear_registry() -> None:
    """Clear the registry. For testing ONLY — do NOT call in production code."""
    _REGISTRY.clear()
