"""@enforces decorator, EnforcementClaimRecord, and import-time registry.

Provides the ``@enforces(claim, fixture, entrypoint)`` decorator (OBPI-0.0.74-15)
and the claim-type-agnostic registry the runner (OBPI-16) discovers.

Mirrors the ``@covers`` / ``@advances`` decoration-time fail-close precedent:
a malformed or unknown claim id raises ``ValueError`` at import — typos cannot
ship to runtime.

The ``entrypoint`` MUST be a direct, resolvable reference to a production
callable — never a ``functools.partial`` or ``lambda`` pre-binding a forcing
kwarg (§ Boundary Invariants #7; the runner in OBPI-16 invokes it).
"""

from __future__ import annotations

import re
import types
from collections.abc import Callable
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field

_EF = TypeVar("_EF")

# Claim id must be a lowercase slug: starts with a letter, contains only
# lowercase letters, digits, and hyphens.
_CLAIM_ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")

_ENFORCEMENT_REGISTRY: list[EnforcementClaimRecord] = []
_KNOWN_CLAIMS: frozenset[str] | None = None


class EnforcementClaimRecord(BaseModel):
    """A registered ``@enforces`` decoration linking a claim to its NC and entrypoint.

    Captured at decoration time. The runner (OBPI-16) discovers every record in
    ``_ENFORCEMENT_REGISTRY`` and invokes ``entrypoint(fixture())`` to verify the
    claim is genuinely enforced.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)

    claim_id: str = Field(..., description="Enforcement claim identifier slug")
    fixture: Callable[[], Any] = Field(
        ..., description="Violation-builder callable; runner calls fixture()"
    )
    entrypoint: Callable[..., Any] = Field(
        ..., description="Production callable; runner calls entrypoint(fixture())"
    )
    source_fn: str = Field(
        ..., description="Qualified name of the entrypoint for discovery/logging"
    )
    source_file: str | None = Field(None, description="Source file path of the entrypoint")
    source_line: int | None = Field(
        None, description="First source line of the entrypoint (1-indexed)"
    )


def _qualified_fn_name(fn: object) -> str:
    """Return the fully qualified name of a callable."""
    module = getattr(fn, "__module__", None) or "<unknown>"
    qualname = getattr(fn, "__qualname__", None) or getattr(fn, "__name__", "<unknown>")
    return f"{module}.{qualname}"


def _load_known_claims() -> frozenset[str]:
    """Load and cache the set of known enforcement claim ids.

    Production source: ``_PRODUCTION_NEGATIVE_CONTROLS.keys()`` from the
    qc_binding negative-control module. Tests inject via ``set_known_claims()``.
    Mirrors the lazy-load pattern of ``_load_known_reqs()`` in traceability and
    ``_load_known_task_reqs()`` in tasks.
    """
    global _KNOWN_CLAIMS
    if _KNOWN_CLAIMS is not None:
        return _KNOWN_CLAIMS

    from gzkit.governance.trust_audits._qc_negative_controls import (  # noqa: PLC0415
        _PRODUCTION_NEGATIVE_CONTROLS,
    )

    _KNOWN_CLAIMS = frozenset(_PRODUCTION_NEGATIVE_CONTROLS.keys())
    return _KNOWN_CLAIMS


def set_known_claims(claims: frozenset[str]) -> None:
    """Inject known claim identifiers for testing."""
    global _KNOWN_CLAIMS
    _KNOWN_CLAIMS = claims


def enforces(
    claim: str,
    fixture: Callable[[], Any],
    entrypoint: Callable[..., Any],
) -> Callable[[_EF], _EF]:
    """Declare that a production callable enforces an enforcement claim.

    Validates the claim identifier format and known-claims membership at
    decoration time, then registers an :class:`EnforcementClaimRecord` into
    the module-level registry. Returns the decorated callable unchanged —
    registration is metadata-only.

    Raises:
        ValueError: If ``claim`` has an invalid format or is not in the
            registered known-claims set.
    """
    if not _CLAIM_ID_RE.match(claim):
        msg = (
            f"Malformed enforcement claim id: {claim!r} — "
            f"must match {_CLAIM_ID_RE.pattern!r} (lowercase slug)"
        )
        raise ValueError(msg)

    known = _load_known_claims()
    if claim not in known:
        msg = f"Unknown enforcement claim id: {claim!r} — not in the registered known-claims set"
        raise ValueError(msg)

    source_file: str | None = None
    source_line: int | None = None
    code = getattr(entrypoint, "__code__", None)
    if isinstance(code, types.CodeType):
        source_file = code.co_filename
        source_line = code.co_firstlineno

    source_fn = _qualified_fn_name(entrypoint)

    def decorator(fn: _EF) -> _EF:
        record = EnforcementClaimRecord(
            claim_id=claim,
            fixture=fixture,
            entrypoint=entrypoint,
            source_fn=source_fn,
            source_file=source_file,
            source_line=source_line,
        )
        _ENFORCEMENT_REGISTRY.append(record)
        return fn

    return decorator


def registered_claims() -> list[str]:
    """Return the list of registered enforcement claim ids."""
    return [r.claim_id for r in _ENFORCEMENT_REGISTRY]


def get_enforcement_registry() -> list[EnforcementClaimRecord]:
    """Return a copy of the global enforcement registry."""
    return list(_ENFORCEMENT_REGISTRY)


def reset_enforcement_registry() -> None:
    """Clear the global enforcement registry. For testing only."""
    _ENFORCEMENT_REGISTRY.clear()
