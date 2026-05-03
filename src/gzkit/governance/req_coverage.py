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

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.traceability import scan_feature_tree, scan_test_tree
from gzkit.triangle import extract_reqs_from_brief


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


def discover_covers(
    req_id: str,
    tests_root: Path,
    *,
    features_root: Path | None = None,
) -> list[TestRef]:
    """Return every covering reference for ``req_id`` under ``tests_root`` and
    optionally ``features_root``.

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
