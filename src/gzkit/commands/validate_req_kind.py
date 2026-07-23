"""REQ-kind discipline validator (ADR-0.0.59-02).

Extracted from ``validate_cmd.py`` (A3 module split). Checks that each REQ in an
OBPI brief's ``## Acceptance Criteria`` carries a ``[kind]`` tag and that each
tagged REQ cites the proof channel its kind requires. Shares
``_find_obpi_briefs`` with the briefs and task-envelope validator modules.
"""

import re
from pathlib import Path

from gzkit.commands.validate_briefs import _find_obpi_briefs
from gzkit.req_kind_fence import (
    _boundary_invariants_section,
    _fence_obpi_anchored,
    _is_enforcement_asserting,
)
from gzkit.req_kind_support import parse_support_citation
from gzkit.validate import ValidationError

_REQ_KIND_TAG_RE = re.compile(
    r"-\s+\[[ xX]\]\s+\*{0,2}(REQ-[\d.]+[-\d]+)\s+\[(BEHAVIOR|SUPPORT|STRUCTURAL-FENCE)\]:",
    re.IGNORECASE,
)
_REQ_ANY_ID_RE = re.compile(r"(REQ-[\d.]+[-\d]+)")
_ALLOWED_PATHS_HEADING_RE = re.compile(r"^##\s+Allowed Paths", re.MULTILINE)
_ACCEPTANCE_CRITERIA_HEADING_RE = re.compile(r"^##\s+Acceptance Criteria", re.MULTILINE)
_BOUNDARY_INVARIANTS_HEADING_RE = re.compile(r"^##\s+Boundary Invariants", re.MULTILINE)
_PARENT_FRONTMATTER_RE = re.compile(r"^parent:\s*(.+)$", re.MULTILINE)
_NEXT_H2_RE = re.compile(r"^##\s", re.MULTILINE)
_LEDGER_EVENT_KEYWORDS: frozenset[str] = frozenset(
    {"artifact_edited", "obpi_created", "obpi_completed", "adr_created", "ledger", "event"}
)


def _extract_md_section(content: str, heading_re: re.Pattern[str]) -> str:
    """Extract content from a `##` heading match through the next `##` boundary."""
    m = heading_re.search(content)
    if m is None:
        return ""
    start = m.end()
    next_h2 = _NEXT_H2_RE.search(content[start:])
    end = start + next_h2.start() if next_h2 else len(content)
    return content[start:end]


def _find_parent_adr_path(brief_path: Path, project_root: Path) -> Path | None:
    """Resolve the parent ADR file from a brief's `parent:` frontmatter field."""
    content = brief_path.read_text(encoding="utf-8")
    m = _PARENT_FRONTMATTER_RE.search(content)
    if m is None:
        return None
    parent_id = m.group(1).strip()
    adr_root = project_root / "docs" / "design" / "adr"
    for adr_file in adr_root.rglob(f"{parent_id}.md"):
        return adr_file
    return None


def _req_kind_error(artifact: str, message: str) -> ValidationError:
    return ValidationError(type="req_kind_discipline", artifact=artifact, message=message)


def _check_behavior_req(req_id: str, allowed_section: str, artifact: str) -> list[ValidationError]:
    if "tests/" in allowed_section:
        return []
    return [
        _req_kind_error(
            artifact,
            f"BEHAVIOR REQ {req_id!r}: requires tests/** in Allowed Paths "
            "but no 'tests/' path found.",
        )
    ]


def _check_support_req(req_id: str, ac_section: str, artifact: str) -> list[ValidationError]:
    req_line_re = re.compile(
        rf"-\s+\[[ xX]\]\s+\*{{0,2}}{re.escape(req_id)}\s+\[SUPPORT\]:[^\n]*",
        re.IGNORECASE,
    )
    m = req_line_re.search(ac_section)
    req_line = m.group(0) if m else ""
    if parse_support_citation(req_line) is not None:
        return []
    # Legacy fallback: keyword-presence citations that predate the strict
    # parser stay green at authoring time; their proof resolves unproven at
    # closeout until the citation names a recognized event type.
    has_validator = "gz validate --" in req_line
    has_ledger = any(kw in req_line for kw in _LEDGER_EVENT_KEYWORDS)
    if has_validator and has_ledger:
        return []
    return [
        _req_kind_error(
            artifact,
            f"SUPPORT REQ {req_id!r}: missing or unparseable citation — "
            "add 'gz validate --<scope>' and a recognized ledger event type "
            "(e.g. artifact_edited) to the REQ text.",
        )
    ]


def _check_structural_fence_req(
    req_id: str, brief_path: Path, project_root: Path, artifact: str, req_text: str = ""
) -> list[ValidationError]:
    parent_adr = _find_parent_adr_path(brief_path, project_root)
    if parent_adr is None or not parent_adr.exists():
        return [
            _req_kind_error(
                artifact,
                f"STRUCTURAL-FENCE REQ {req_id!r}: parent ADR file not found. "
                "Cannot verify ## Boundary Invariants section.",
            )
        ]
    adr_content = parent_adr.read_text(encoding="utf-8")
    section = _boundary_invariants_section(adr_content)
    if section is None:
        return [
            _req_kind_error(
                artifact,
                f"STRUCTURAL-FENCE REQ {req_id!r}: parent ADR "
                f"{parent_adr.name!r} has no '## Boundary Invariants' "
                "section — add it before completing this OBPI.",
            )
        ]
    # Enforcement-asserting fences prove via their @enforces claim registry at
    # closeout (resolve_fence_proof), not via an OBPI anchor — the brief-time gate
    # stays lenient (heading presence) for them. State-property fences require the
    # OBPI-combination anchor naming this REQ's OBPI (GHI #538).
    if _is_enforcement_asserting(req_text):
        return []
    if _fence_obpi_anchored(section, req_id):
        return []
    return [
        _req_kind_error(
            artifact,
            f"STRUCTURAL-FENCE REQ {req_id!r}: parent ADR "
            f"{parent_adr.name!r} has a '## Boundary Invariants' section but no "
            "invariant anchors this REQ's OBPI — append the '(OBPI-NN)' token to "
            "the invariant that establishes the claim (GHI #538; "
            "docs/governance/req-scope-discipline.md § STRUCTURAL-FENCE).",
        )
    ]


_KIND_CHECKERS: dict[str, str] = {
    "BEHAVIOR": "behavior",
    "SUPPORT": "support",
    "STRUCTURAL-FENCE": "structural_fence",
}


def _check_tagged_req(
    req_id: str,
    kind: str,
    *,
    allowed_section: str,
    ac_section: str,
    brief_path: Path,
    project_root: Path,
    artifact: str,
) -> list[ValidationError]:
    kind_upper = kind.upper()
    if kind_upper == "BEHAVIOR":
        return _check_behavior_req(req_id, allowed_section, artifact)
    if kind_upper == "SUPPORT":
        return _check_support_req(req_id, ac_section, artifact)
    if kind_upper == "STRUCTURAL-FENCE":
        return _check_structural_fence_req(
            req_id, brief_path, project_root, artifact, _req_line_text(ac_section, req_id)
        )
    return []


def _req_line_text(ac_section: str, req_id: str) -> str:
    """Return the acceptance-criteria line text for ``req_id`` (empty if absent).

    Feeds the enforcement/state-property split in ``_check_structural_fence_req``:
    an enforcement-asserting fence proves via its claim registry, a state-property
    fence via the OBPI anchor.
    """
    for line in ac_section.splitlines():
        if req_id in line:
            return line
    return ""


def _validate_req_kind_discipline_for_brief(
    brief_path: Path, project_root: Path
) -> list[ValidationError]:
    """Run per-kind discipline checks for a single OBPI brief."""
    content = brief_path.read_text(encoding="utf-8")
    artifact = brief_path.relative_to(project_root).as_posix()

    ac_section = _extract_md_section(content, _ACCEPTANCE_CRITERIA_HEADING_RE)
    if not ac_section:
        return []

    tagged: list[tuple[str, str]] = _REQ_KIND_TAG_RE.findall(ac_section)
    if not tagged:
        # All-untagged → legacy / grandfathered → pass
        return []

    all_req_ids = _REQ_ANY_ID_RE.findall(ac_section)
    tagged_ids = {req_id for req_id, _ in tagged}
    untagged_ids = [r for r in all_req_ids if r not in tagged_ids]

    errors: list[ValidationError] = [
        _req_kind_error(
            artifact,
            f"REQ {req_id!r} lacks a [kind] tag — add [BEHAVIOR], [SUPPORT], "
            "or [STRUCTURAL-FENCE] between the REQ ID and the colon.",
        )
        for req_id in untagged_ids
    ]

    allowed_section = _extract_md_section(content, _ALLOWED_PATHS_HEADING_RE)
    for req_id, kind in tagged:
        errors.extend(
            _check_tagged_req(
                req_id,
                kind,
                allowed_section=allowed_section,
                ac_section=ac_section,
                brief_path=brief_path,
                project_root=project_root,
                artifact=artifact,
            )
        )
    return errors


def _validate_req_kind_discipline(project_root: Path) -> list[ValidationError]:
    """Validate that OBPI brief acceptance-criteria REQs carry [kind] tags (ADR-0.0.59-02).

    Rules:
    - If ALL REQs in a brief lack [kind] tags → passes (legacy/grandfathered).
    - If SOME REQs have [kind] tags and SOME do not → fails (mixed-state).
    - For each tagged REQ, per-kind proof-citation checks fire (see _check_tagged_req).
    """
    errors: list[ValidationError] = []
    for brief_path in _find_obpi_briefs(project_root):
        errors.extend(_validate_req_kind_discipline_for_brief(brief_path, project_root))
    return errors
