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
from gzkit.mx.invariants import GATE5_INVARIANTS


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

    Thin convenience predicate over :func:`resolve` — the single leveled severity
    authority (parent ADR Boundary Invariant #2). A guard is advisory exactly when
    its resolved route is the under-marker demotion sentinel, which reproduces the
    prior decision rules: gate5_invariants pin (never advisory), outside the hangar
    nothing demotes, inside the hangar non-invariant guards demote to ADVISORY.
    """
    return resolve(guard_name, _levels.ERROR, project_root) == _disposition.Route.ADVISORY


def blocks(
    guard_name: str,
    emitted_level: int,
    project_root: Path | None = None,
) -> bool:
    """Return True when a finding from *guard_name* must block (ground).

    The consumer-facing composition of :func:`resolve` and
    :func:`gzkit.mx.disposition.grounds`, so a guard asks one question instead of
    re-deriving the level->route->grounds chain at its own call site. Added for
    the pre-commit enforcement surface (GHI #843), which has three separate
    entrypoints and would otherwise carry three copies of the composition --
    the N-inline-substitutions shape parent ADR-0.0.74 BI#2 exists to prevent.
    """
    return _disposition.grounds(resolve(guard_name, emitted_level, project_root))


def demote_notice(guard_name: str) -> str:
    """Return the operator-facing line a consumer prints when a guard is demoted.

    Demotion is announced, never silent: advisory means non-grounding, not
    discarded. One authority for the wording so every consuming surface says the
    same thing about what did and did not just happen (GHI #843).
    """
    return (
        f"[MX advisory] guard '{guard_name}' reported a violation and was demoted "
        "to advisory by the open Maintenance Hangar marker (.gzkit/mx.json). "
        "It is NOT waived -- `gz mx exit` re-runs every guard at full strength."
    )
