"""REQ-coverage discovery for the OBPI completion gate.

Composes two pure functions used by ``gz obpi complete``'s pre-emission
REQ-coverage gate (ADR-0.0.25, OBPI-01):

* ``parse_brief_reqs(Path) -> list[str]`` — extract REQ-IDs from a
  brief's ``## Acceptance Criteria`` section, tolerating the canonical
  ``- [ ] REQ-X.Y.Z-NN-MM: <text>`` shape and skipping malformed rows.
* ``discover_covers(req_id, Path, *, features_root) -> list[TestRef]`` —
  return every covering reference for the given REQ: ``@covers``-decorated
  unit tests under ``tests_root`` unioned with ``@REQ-*`` BDD scenario
  tags under ``features_root`` (when supplied). AST-based for Python
  tests; feature-file scan for BDD. Never imports test modules under
  audit (REQ-0.0.25-01-05; underwrites ``.claude/rules/pythonic.md``
  imports rule and the ``@covers`` discovery contract from #120).

The implementation reuses existing primitives:

* ``gzkit.triangle.extract_reqs_from_brief`` — single-source REQ parser
  (also fed by ``scan_briefs``); avoids duplicating the canonical
  ``_AC_LINE_PATTERN`` regex.
* ``gzkit.traceability.scan_test_tree`` — single-source ``@covers``
  scanner walking ``tests/**`` once; the per-REQ filter here is just a
  projection over its output (#120).

@covers OBPI-0.0.25-01-implement-coverage-gate
"""

from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.traceability import scan_feature_tree, scan_test_tree
from gzkit.triangle import extract_reqs_from_brief

# ADR-0.0.59 inline kind tag: ``REQ-X.Y.Z-NN-MM [BEHAVIOR|SUPPORT|STRUCTURAL-FENCE]:``.
# The trailing colon scopes the match to the declaration line, not prose references.
# Emphasis is tolerated around the tag for the reason ``gzkit.triangle`` states —
# ADR-0.0.59 mandates the tag, not its typographic weight. This reader was the
# third of three and had the tolerance in neither position; an emphasised brief
# resolved to an empty kind map, so its REQs lost their declared kind and fell
# back to the BEHAVIOR default (GHI #809, sibling of GHI #700).
_REQ_KIND_TAG_RE = re.compile(
    r"(REQ-[\d.]+(?:-\d+)+)\s+\*{0,2}\[(BEHAVIOR|SUPPORT|STRUCTURAL-FENCE)\]\*{0,2}:",
    re.IGNORECASE,
)


class TestRef(BaseModel):
    """Reference to a single ``@covers``-decorated test function."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    qualified_name: str = Field(
        ...,
        description="Function or class.method name as parsed from AST",
    )
    file_path: str = Field(
        ...,
        description="POSIX-rendered path to the .py file (cross-platform-safe)",
    )
    line: int = Field(..., description="Decorator line number in the source file")


def parse_brief_reqs(brief_path: Path) -> list[str]:
    """Return REQ-IDs declared in the brief's ``## Acceptance Criteria`` section.

    Tolerates the canonical brief shape ``- [ ] REQ-X.Y.Z-NN-MM: <description>``
    and ``- [x] REQ-...`` (checked variant); skips checklist rows that do not
    match the REQ-ID pattern. Returns IDs sorted by canonical REQ ordering
    (semantic version), deduplicated. Returns ``[]`` when the section is
    missing, empty, or the file does not exist.
    """
    if not brief_path.is_file():
        return []
    content = brief_path.read_text(encoding="utf-8")
    # parent_obpi is unused by this consumer — we only need the REQ-IDs.
    reqs = extract_reqs_from_brief(content, parent_obpi="")
    return [str(r.id) for r in reqs]


def parse_brief_req_kinds(brief_path: Path) -> dict[str, str]:
    """Map REQ-ID -> declared ADR-0.0.59 ``[kind]`` tag (uppercased) from the brief.

    Only REQs carrying an explicit ``[BEHAVIOR|SUPPORT|STRUCTURAL-FENCE]`` inline
    tag appear in the map; untagged (legacy) REQs are absent and treated as
    BEHAVIOR by callers. Used by the ``gz obpi complete`` REQ-coverage gate to
    exempt SUPPORT / STRUCTURAL-FENCE REQs from the ``@covers`` requirement —
    those kinds are proven by a ledger event + structural validator and a
    parent-ADR ``## Boundary Invariants`` entry respectively, not by a test
    (``.gzkit/rules/tests.md`` § REQ Scope Discipline). Returns ``{}`` when the
    file is absent.
    """
    if not brief_path.is_file():
        return {}
    content = brief_path.read_text(encoding="utf-8")
    return {req_id: kind.upper() for req_id, kind in _REQ_KIND_TAG_RE.findall(content)}


def discover_covers(
    req_id: str,
    tests_root: Path,
    *,
    features_root: Path | None = None,
) -> list[TestRef]:
    """Return every covering reference for ``req_id`` under the given roots.

    Walks ``tests_root`` and optionally ``features_root``.
    Unions ``scan_test_tree(tests_root)`` (``@covers``-decorated unit tests)
    with ``scan_feature_tree(features_root)`` (``@REQ-*`` BDD scenario tags)
    when ``features_root`` is supplied — matching the ``gz covers`` behaviour
    (covers.py:174). No test modules are imported during discovery —
    REQ-0.0.25-01-05.

    File paths are rendered with ``Path.as_posix()`` so cross-platform
    consumers (ledger artifacts, JSON, downstream string comparisons) see
    forward-slash separators on every platform per
    ``.claude/rules/cross-platform.md``.
    """
    records = []
    if tests_root.is_dir():
        records.extend(scan_test_tree(tests_root))
    if features_root is not None and features_root.is_dir():
        records.extend(scan_feature_tree(features_root))
    refs: list[TestRef] = []
    for record in records:
        if record.target.identifier != req_id:
            continue
        evidence_path = record.evidence_path or ""
        evidence_line = record.evidence_line or 0
        refs.append(
            TestRef(
                qualified_name=record.source.identifier,
                file_path=Path(evidence_path).as_posix(),
                line=evidence_line,
            )
        )
    return refs


class UncoveredAcceptanceRecord(BaseModel):
    """One accepted-uncovered REQ waiver, before writing to the ledger (ADR-0.0.25-02)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    obpi_id: str = Field(..., description="OBPI brief identifier")
    req_id: str = Field(..., description="REQ-ID being waived")
    operator: str = Field(..., description="Operator identity (name only, no email)")
    rationale: str = Field(..., description="Mandatory waiver rationale")
    acceptance_type: str = Field(..., description="human or agent-relayed-operator-attestation")
