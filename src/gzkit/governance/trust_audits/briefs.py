"""OBPI brief trust audits — heading shape and BDD coverage.

* ``audit_brief_headings`` — evidence sections must use H3, not H2 (GHI #238).
* ``audit_behave_req_tags`` — heavy-lane OBPIs whose REQs lack ``@REQ-*``
  scenario tags under ``features/**`` fail closed (GHI #211 / GHI #276).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from gzkit.validate import ValidationError

_REQ_ID_IN_BRIEF = re.compile(r"\bREQ-\d+\.\d+\.\d+-\d+-\d+\b")
_SCENARIO_REQ_TAG = re.compile(r"^\s*@(REQ-\d+\.\d+\.\d+-\d+-\d+)\b", re.MULTILINE)

_OBPI_ID_IN_FRONTMATTER = re.compile(
    r"^id:\s*(OBPI-[0-9]+\.[0-9]+\.[0-9]+-[0-9]+[A-Za-z0-9\-.]*)\s*$",
    re.MULTILINE,
)
_LANE_IN_FRONTMATTER = re.compile(r"^lane:\s*([A-Za-z]+)\s*$", re.MULTILINE)
_STATUS_IN_FRONTMATTER = re.compile(r"^status:\s*([A-Za-z]+)\s*$", re.MULTILINE)
_ACCEPTANCE_SECTION = re.compile(
    r"^##\s+Acceptance Criteria\s*$(.*?)(?=^##\s+|\Z)",
    re.MULTILINE | re.DOTALL,
)

# Brief lifecycle states whose BDD coverage gate is in scope for the
# `behave_req_tags` validator. BDD coverage is an implementation-time gate
# per `.gzkit/rules/tests.md` § Red-Green-Refactor; only briefs in a post-
# implementation state can have BDD coverage to validate. Pre-implementation
# states (Draft, Pending, Proposed, etc.) and terminal-but-not-implemented
# states (Withdrawn, Superseded) are excluded by inverse filter — defaulting
# to skip means future-added statuses do not silently re-introduce the
# pre-implementation flagging defect (GHI #323).
_BDD_GATED_BRIEF_STATUSES = frozenset({"completed", "validated"})

_BRIEF_EVIDENCE_H3_HEADINGS = (
    "Implementation Summary",
    "Key Proof",
    "Closing Argument",
)


def _canonical_h3_heading(line: str, canonical_forms: dict[str, str]) -> str | None:
    """Return the canonical H3 form if ``line`` is a drifted ``## Heading`` match."""
    if not line.startswith("## "):
        return None
    folded = line[3:].split("(")[0].strip().casefold()
    return canonical_forms.get(folded)


def _scan_one_brief_headings(
    brief: Path, canonical_forms: dict[str, str], project_root: Path
) -> list[ValidationError]:
    try:
        lines = brief.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return []
    rel = brief.relative_to(project_root).as_posix()
    errors: list[ValidationError] = []
    for lineno, raw in enumerate(lines, start=1):
        canonical = _canonical_h3_heading(raw, canonical_forms)
        if canonical is None:
            continue
        errors.append(
            ValidationError(
                type="brief_headings",
                artifact=f"{rel}:{lineno}",
                message=(
                    f"Evidence section `{canonical}` must use H3 "
                    f"(`### {canonical}`), not H2. Ceremony renderers "
                    "and completion hooks look for H3 level."
                ),
            )
        )
    return errors


def audit_brief_headings(project_root: Path) -> list[ValidationError]:
    """Brief evidence sections must use H3, not H2 (GHI #238).

    OBPI briefs standardise per-completion evidence headings at H3 level.
    ``gz obpi complete`` and the completion hooks extract
    ``### Implementation Summary`` and ``### Key Proof`` by exact H3 match;
    the defense-brief renderer extracts ``### Closing Argument``. A brief
    that drifts one of these to ``##`` passes schema validation (the section
    exists) but the extractor stops at the next H2 boundary and yields an
    empty body — triggering mid-ceremony failures.
    """
    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return []
    canonical_forms: dict[str, str] = {h.casefold(): h for h in _BRIEF_EVIDENCE_H3_HEADINGS}
    errors: list[ValidationError] = []
    for brief in sorted(adr_root.rglob("OBPI-*.md")):
        errors.extend(_scan_one_brief_headings(brief, canonical_forms, project_root))
    return errors


def _waiver_rationale_code(entry: Any) -> str:
    if isinstance(entry, dict):
        rationale = entry.get("rationale")
        return str(rationale) if rationale is not None else ""
    if isinstance(entry, str):
        return entry
    return ""


def _load_behave_coverage_waivers(project_root: Path) -> dict[str, str]:
    """Return ``{OBPI-id: rationale}`` from the sidecar waiver file.

    The sidecar stores rationale codes keyed to a ``default_rationale`` map
    so the 370+ historical entries compress to one-liners plus one shared
    message. Keys without a resolvable rationale code still load as waived
    (rationale falls through to the raw code string) so the audit never
    blocks on a malformed entry.
    """
    waiver_path = project_root / "data" / "behave_coverage_waivers.json"
    if not waiver_path.is_file():
        return {}
    try:
        payload = json.loads(waiver_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return {}
    default_rationale = payload.get("default_rationale", {}) or {}
    waivers = payload.get("waivers", {}) or {}
    out: dict[str, str] = {}
    for obpi_id, entry in waivers.items():
        if not isinstance(obpi_id, str) or not obpi_id.startswith("OBPI-"):
            continue
        code = _waiver_rationale_code(entry)
        out[obpi_id] = default_rationale.get(code, code)
    return out


def _extract_one_heavy_brief(brief: Path) -> tuple[Path, str, list[str]] | None:
    """Return ``(brief, obpi_id, req_ids)`` if the brief is BDD-gated heavy, else None."""
    try:
        text = brief.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None
    lane_match = _LANE_IN_FRONTMATTER.search(text)
    if not lane_match or lane_match.group(1).lower() != "heavy":
        return None
    status_match = _STATUS_IN_FRONTMATTER.search(text)
    status_value = status_match.group(1).lower() if status_match else ""
    if status_value not in _BDD_GATED_BRIEF_STATUSES:
        return None
    id_match = _OBPI_ID_IN_FRONTMATTER.search(text)
    if not id_match:
        return None
    accept_match = _ACCEPTANCE_SECTION.search(text)
    if not accept_match:
        return None
    req_ids = sorted(set(_REQ_ID_IN_BRIEF.findall(accept_match.group(1))))
    if not req_ids:
        return None
    return brief, id_match.group(1), req_ids


def _extract_heavy_obpi_briefs(project_root: Path) -> list[tuple[Path, str, list[str]]]:
    """Enumerate heavy-lane OBPI briefs under ``docs/design/adr/``.

    Returns tuples of ``(brief_path, obpi_id, req_ids)``. Pool-ADR briefs
    (``docs/design/adr/pool/**``) are excluded per the ``--pool-adr-isolation``
    contract. REQ-IDs are extracted from the ``## Acceptance Criteria``
    section only — the REQ Coverage and Requirements sections restate the
    same IDs, and anchoring on Acceptance Criteria matches the brief template
    and the ``gz adr audit-check`` derivation.
    """
    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return []
    briefs: list[tuple[Path, str, list[str]]] = []
    for brief in sorted(adr_root.rglob("OBPI-*.md")):
        if "pool" in brief.parts:
            continue
        record = _extract_one_heavy_brief(brief)
        if record is not None:
            briefs.append(record)
    return briefs


def _collect_scenario_req_tags(project_root: Path) -> set[str]:
    """Return the set of REQ-IDs carried by scenario-level ``@REQ-*`` tags."""
    features_root = project_root / "features"
    if not features_root.is_dir():
        return set()
    tagged: set[str] = set()
    for feat in features_root.rglob("*.feature"):
        try:
            text = feat.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        tagged.update(m.group(1) for m in _SCENARIO_REQ_TAG.finditer(text))
    return tagged


def audit_behave_req_tags(project_root: Path) -> list[ValidationError]:
    """Fail on heavy-lane OBPIs whose REQs lack ``@REQ-*`` scenario tags.

    Rule 39 (``.gzkit/rules/tests.md`` § Behave scenario tagging) and the
    advisory scorecard row 39 both assert that heavy-lane and foundation-kind
    OBPIs carry scenario-level ``@REQ-X.Y.Z-NN-MM`` tags for every REQ in
    their Acceptance Criteria. The enforcement direction is OBPI → feature:
    enumerate heavy OBPI briefs, assert each REQ is tagged somewhere under
    ``features/**``. Missing coverage → policy breach (exit 3) unless the
    OBPI ID is present in ``data/behave_coverage_waivers.json``.

    Pool-ADR briefs are excluded per the ``--pool-adr-isolation`` contract;
    pool ADRs do not carry gate obligations and cannot fire Gate 4.
    """
    briefs = _extract_heavy_obpi_briefs(project_root)
    if not briefs:
        return []
    tagged_reqs = _collect_scenario_req_tags(project_root)
    waivers = _load_behave_coverage_waivers(project_root)
    errors: list[ValidationError] = []
    for brief_path, obpi_id, req_ids in briefs:
        if obpi_id in waivers:
            continue
        missing = [r for r in req_ids if r not in tagged_reqs]
        if not missing:
            continue
        rel = brief_path.relative_to(project_root).as_posix()
        errors.append(
            ValidationError(
                type="behave_req_tags",
                artifact=rel,
                message=(
                    f"Heavy-lane OBPI `{obpi_id}` has REQ-IDs without "
                    "matching scenario-level `@REQ-X.Y.Z-NN-MM` tags under "
                    "`features/**`. Missing: "
                    + ", ".join(missing[:5])
                    + (f" (+{len(missing) - 5} more)" if len(missing) > 5 else "")
                    + ". Add scenario tags or waive in "
                    "`data/behave_coverage_waivers.json` with rationale."
                ),
            )
        )
    return errors
