"""Fidelity-presence enforcement (ADR-0.0.73 / OBPI-0.0.73-08).

Mechanizes Boundary Invariant #4: every non-pool ADR Decision must carry a
parseable ``## Fidelity Assertions`` block.  ``gz validate --fidelity-presence``
walks non-pool ADR Decision files and fails closed (exit 3) on any whose block
is absent, empty, or malformed (``parse_fidelity_assertions`` raises) — minus an
explicit grandfathered set of pre-existing block-less ADRs.

The OBPI-04 adversarial audit proved an ADR with no block reaches VALIDATED
through both closeout and audit on a stderr warning, so "VALIDATED = thesis
exercised" was false for every block-less ADR.  This scope closes that bypass.

Fail-closed on NEW block-less ADRs only.  The grandfather file enumerates
today's debt (the ``sensitivity_floor_grandfather.json`` cutover precedent), so
the gate goes green now without silently exempting the backlog, while a
newly-authored block-less ADR cannot reach VALIDATED unchecked (Boundary
Invariant #7).

Usage::

    from gzkit.governance.trust_audits.fidelity_presence import (
        audit_fidelity_presence,
    )
    errors = audit_fidelity_presence(project_root)
    # Non-empty → caller exits 3; empty → exit 0
"""

from __future__ import annotations

import json
from pathlib import Path

from gzkit.core.validation_rules import ValidationError
from gzkit.fidelity import parse_fidelity_assertions

_GRANDFATHER_REL = Path("data") / "fidelity_presence_grandfather.json"
_ADR_ROOT_SEGMENTS = ("docs", "design", "adr")
_POOL_DIRNAME = "pool"
_CLOSEOUT_STEM = "ADR-CLOSEOUT-FORM"


def _load_grandfather(project_root: Path) -> frozenset[str]:
    """Return the set of grandfathered (pre-existing) block-less ADR ids.

    A missing or malformed file means *nothing* is grandfathered (empty set):
    absence must never silently widen the waiver, and presence enforcement does
    not depend on the grandfather file existing.
    """
    gf_path = project_root / _GRANDFATHER_REL
    if not gf_path.is_file():
        return frozenset()
    try:
        payload = json.loads(gf_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return frozenset()
    adrs = payload.get("grandfathered_adrs", []) if isinstance(payload, dict) else []
    return frozenset(a for a in adrs if isinstance(a, str))


def _iter_adr_decisions(project_root: Path) -> list[Path]:
    """Return non-pool ADR Decision files, sorted.

    A Decision file is the canonical ``<package-dir>/<package-dir>.md`` (its
    stem matches its parent directory name) — the same identity used across the
    trust audits.  ``ADR-CLOSEOUT-FORM.md`` sidecars and the pool tree are
    excluded (Boundary Invariant #7 scopes to non-pool Decisions).
    """
    adr_root = project_root.joinpath(*_ADR_ROOT_SEGMENTS)
    if not adr_root.is_dir():
        return []
    decisions: list[Path] = []
    for adr_file in adr_root.rglob("ADR-*.md"):
        if adr_file.stem == _CLOSEOUT_STEM:
            continue
        if adr_file.stem != adr_file.parent.name:
            continue
        if adr_file.relative_to(adr_root).parts[0] == _POOL_DIRNAME:
            continue
        decisions.append(adr_file)
    return sorted(decisions)


def audit_fidelity_presence(
    project_root: Path,
    *,
    grandfather: frozenset[str] | set[str] | None = None,
) -> list[ValidationError]:
    """Flag non-pool ADR Decisions lacking a parseable Fidelity Assertions block.

    Returns one ``ValidationError`` per offending ADR (non-empty → caller exits
    3).  ``grandfather`` overrides the on-disk grandfather set (the
    test-isolation path); ``None`` loads
    ``data/fidelity_presence_grandfather.json``.
    """
    gf = frozenset(grandfather) if grandfather is not None else _load_grandfather(project_root)
    errors: list[ValidationError] = []
    for adr_file in _iter_adr_decisions(project_root):
        adr_id = adr_file.stem
        if adr_id in gf:
            continue
        try:
            parse_fidelity_assertions(adr_file)
        except ValueError:
            rel = adr_file.relative_to(project_root).as_posix()
            errors.append(
                ValidationError(
                    type="fidelity-presence",
                    artifact=adr_id,
                    message=(
                        f"ADR Decision {adr_id} ({rel}) has no parseable "
                        "'## Fidelity Assertions' block. ADR-0.0.73 Boundary "
                        "Invariant #4 requires every non-pool ADR Decision to ship "
                        "runnable Fidelity Assertions (claim | command | "
                        "expected-exit) that exercise its thesis against the real "
                        "system; without one, 'VALIDATED = thesis exercised' is "
                        "false (Boundary Invariant #7). Add a '## Fidelity "
                        "Assertions' block with at least one data row (see the stub "
                        "in .gzkit/templates/adr.md), then re-run "
                        "`uv run gz validate --fidelity-presence`."
                    ),
                )
            )
    return errors
