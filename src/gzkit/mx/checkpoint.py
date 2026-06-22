"""MX shared checkpoint — the single place code reads the marker and resolves guard severity.

ADR-0.0.74 Decision item #2: one place code reads the marker and drops guards to
advisory — everything except the gate5_invariants. A new guard inherits the
checkpoint for free; nobody can forget to wire it, and the never-relax list lives
in exactly one place.
"""

from __future__ import annotations

from pathlib import Path

from gzkit.mx import disposition as _disposition
from gzkit.mx import levels as _levels
from gzkit.mx import marker

# The never-relax set: members stay fail-closed regardless of MX mode.
# Lives in exactly one place — here — so no per-gate duplication.
# OBPI-03 will formally author the full canonical set; OBPI-02 seeds it.
GATE5_INVARIANTS: frozenset[str] = frozenset(
    {
        "ledger",  # ledger integrity (validate_cmd scope)
        "gate5-attestation",  # faked Gate-5 attestation
        "operator-pii",  # operator-PII protection
        "secrets",  # secrets leakage guard
    }
)


def resolve(
    guard_name: str,
    emitted_level: int,
    project_root: Path | None = None,
) -> _disposition.Route:
    """Route guard_name's emitted_level through the disposition handler.

    Under-marker demotion: non-floor guards demote to ADVISORY (visible ledger debt).
    gate5_invariants pin to CRITICAL regardless of emitted level or marker state.
    """
    if guard_name in GATE5_INVARIANTS:
        return _disposition.route(_levels.CRITICAL)
    if marker.is_active(project_root) and emitted_level != _levels.CRITICAL:
        return _disposition.Route.ADVISORY
    return _disposition.route(emitted_level)


def is_advisory(guard_name: str, project_root: Path | None = None) -> bool:
    """Return True when *guard_name* should be advisory (not fail-closed) in context.

    Decision rules (in order):
    - gate5_invariants are never advisory regardless of MX state.
    - Outside the hangar (no marker): always False — strict no-op; guard severity unchanged.
    - Inside the hangar (marker present): True for all non-gate5_invariant guards.
    """
    if guard_name in GATE5_INVARIANTS:
        return False
    return marker.is_active(project_root)
