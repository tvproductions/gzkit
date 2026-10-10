"""Enforcement claims for the completion scope gate (GHI #1181).

The transaction contract has required since March that completion fail closed on a
changed file outside the brief's Allowed Paths. The brief validator did it on a path
``gz obpi complete`` never takes, and it counted gzkit's own records, so it could not
have passed a real completion. ``hooks.obpi.scope_finding`` is now the one decision
``gz obpi precomplete`` reports and ``gz obpi complete`` refuses on.

Two claims, on the exemption-half precedent (GHI #797).

* ``completion-scope-outside-allowed-paths`` plants, for each kind of product file, a
  changed set holding one file of that kind outside the allowlist beside an allowed
  file and a gzkit record. The decision must name that file.
* ``completion-scope-records-admitted`` is the admit control: a changed set holding an
  allowed file, every kind of gzkit record, the brief itself and its package's audit
  log yields no finding, so an always-refuse gate cannot discharge the first claim.
"""

from __future__ import annotations

from pathlib import Path

REFUSE_CLAIM_ID = "completion-scope-outside-allowed-paths"
ADMIT_CLAIM_ID = "completion-scope-records-admitted"
SCOPE_GATE_CLAIM_IDS: frozenset[str] = frozenset({REFUSE_CLAIM_ID, ADMIT_CLAIM_ID})

_OUTSIDE = "outside this brief's Allowed Paths"
_ROOT = Path("/claim-fixture")
_PACKAGE = "docs/design/adr/pre-release/ADR-0.0.0-claim-fixture"
_BRIEF = f"{_PACKAGE}/obpis/OBPI-0.0.0-01-claim-fixture.md"
_ALLOWLIST = ["src/gzkit/claim_fixture.py", "tests/claim_fixture/**"]
_ALLOWED_FILE = "src/gzkit/claim_fixture.py"

#: One product file of each kind a package can change outside its allowlist. Declared
#: here, not derived from the gate: the last two sit beside paths the gate exempts
#: (canon under `.gzkit/`, and a sibling brief in the package whose own brief is exempt).
_OUTSIDE_FILES: dict[str, str] = {
    "source-file": "src/gzkit/claim_other.py",
    "test-file": "tests/test_claim_other.py",
    "doc-file": "docs/user/runbook.md",
    "gzkit-canon": ".gzkit/skills/gz-claim-fixture/SKILL.md",
    "sibling-brief": f"{_PACKAGE}/obpis/OBPI-0.0.0-02-claim-sibling.md",
}

#: One path of each kind gzkit writes as its own record. Declared from the operator's
#: reading of 2026-10-10, not read from `GZKIT_RECORD_PATHS`.
_RECORD_FILES: tuple[str, ...] = (
    ".gzkit/ledger.jsonl",
    ".gzkit/handoffs/20261010T000000Z-claim-fixture.md",
    ".gzkit/locks/exchange/20261010T000000Z-claim-fixture-complete.md",
    ".gzkit/insights/agent-insights.jsonl",
    ".gzkit/evidence/OBPI-0.0.0-01-claim-fixture.evidence.json",
    ".gzkit/ceremonies/ADR-0.0.0-claim-fixture.ceremony.json",
    ".claude/plans/.pipeline-active.json",
    _BRIEF,
    f"{_PACKAGE}/logs/obpi-audit.jsonl",
)


def outside_file_population() -> list[str]:
    """Return every kind of out-of-scope product file the gate must name."""
    return list(_OUTSIDE_FILES)


def _build_kind(member: str | None = None) -> str | None:
    """Name the kind of file to plant; ``None`` plants only allowed files and records."""
    return member


# Each entrypoint imports the decision itself: the registry derives a claim's
# `gate_targets` from the entrypoint's own imports (GHI #798).


def _ep_outside_file_refused(kind: str) -> list[str]:
    """Return a finding naming *kind* when its file is reported outside Allowed Paths."""
    from gzkit.hooks.obpi import (  # noqa: PLC0415
        brief_record_paths,
        out_of_scope_files,
        scope_finding,
    )

    planted = _OUTSIDE_FILES[kind]
    changed = [_ALLOWED_FILE, ".gzkit/ledger.jsonl", _BRIEF, planted]
    own = brief_record_paths(_ROOT, _ROOT / _BRIEF)
    audit = {
        "allowlist": _ALLOWLIST,
        "changed_files": changed,
        "out_of_scope_files": out_of_scope_files(changed, _ALLOWLIST, own_paths=own),
    }
    finding = scope_finding(audit)
    named = finding is not None and planted in finding and _OUTSIDE in finding
    return [f"{kind}: {finding}"] if named else []


def _ep_records_admitted(_kind: str | None) -> int:
    """Truthy only when allowed files and gzkit's records alone yield no finding."""
    from gzkit.hooks.obpi import (  # noqa: PLC0415
        brief_record_paths,
        out_of_scope_files,
        scope_finding,
    )

    changed = [_ALLOWED_FILE, "tests/claim_fixture/test_claim.py", *_RECORD_FILES]
    own = brief_record_paths(_ROOT, _ROOT / _BRIEF)
    audit = {
        "allowlist": _ALLOWLIST,
        "changed_files": changed,
        "out_of_scope_files": out_of_scope_files(changed, _ALLOWLIST, own_paths=own),
    }
    return 1 if scope_finding(audit) is None else 0


class _ScopeGateMarker:
    """Inert carrier for the completion-scope ``@enforces`` registrations."""


def ensure_scope_gate_claims_registered() -> None:
    """(Re)register the completion-scope claims (idempotent, reset-safe).

    MUST stay wired into ``enforcement._ensure_production_claims_registered``: a
    registration authored but un-wired there is an ORPHAN whose floor membership is a
    facade.
    """
    from gzkit.enforcement import (  # noqa: PLC0415
        EXEMPTS_NONE,
        POPULATION_NONE,
        enforces,
        extend_known_claims,
        get_enforcement_registry,
    )

    extend_known_claims(SCOPE_GATE_CLAIM_IDS)
    existing = {r.claim_id for r in get_enforcement_registry()}
    if REFUSE_CLAIM_ID not in existing:
        enforces(
            REFUSE_CLAIM_ID,
            _build_kind,
            _ep_outside_file_refused,
            expect=_OUTSIDE,
            exempts=ADMIT_CLAIM_ID,
            population=outside_file_population,
        )(_ScopeGateMarker)
    if ADMIT_CLAIM_ID not in existing:
        enforces(
            ADMIT_CLAIM_ID,
            _build_kind,
            _ep_records_admitted,
            exempts=EXEMPTS_NONE,
            population=POPULATION_NONE,
        )(_ScopeGateMarker)
