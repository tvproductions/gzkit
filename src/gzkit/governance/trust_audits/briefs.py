"""OBPI brief trust audits — heading shape, BDD coverage, cross-references.

* ``audit_brief_headings`` — evidence sections must use H3, not H2 (GHI #238).
* ``audit_behave_req_tags`` — heavy-lane OBPIs whose REQs lack ``@REQ-*``
  scenario tags under ``features/**`` fail closed (GHI #211 / GHI #276).
* ``audit_brief_cross_references`` — bare ``OBPI-X.Y.Z-NN`` / ``ADR-X.Y.Z``
  identifiers in briefs must resolve to on-disk artifacts (GHI #436).
* ``audit_brief_demo_section`` — heavy-lane CLI-shipping briefs must carry a
  ``## Demo`` H2 section so the closeout walkthrough does not fall back to
  ``--help`` (GHI #431).
* ``audit_brief_command_shape`` — brief Verification blocks must contain only
  single-program shell-less commands; compound forms exit 3 (GHI #550, OBPI-0.0.63-07).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from gzkit.brief_commands import extract_fenced_commands, is_shell_less_executable
from gzkit.decomposition import extract_markdown_section
from gzkit.validate import ValidationError

_REQ_ID_IN_BRIEF = re.compile(r"\bREQ-\d+\.\d+\.\d+-\d+-\d+\b")
_SCENARIO_REQ_TAG = re.compile(r"^\s*@(REQ-\d+\.\d+\.\d+-\d+-\d+)\b", re.MULTILINE)

_OBPI_ID_IN_FRONTMATTER = re.compile(
    r"^id:\s*(OBPI-[0-9]+\.[0-9]+\.[0-9]+-[0-9]+[A-Za-z0-9\-.]*)\s*$",
    re.MULTILINE,
)
_LANE_IN_FRONTMATTER = re.compile(r"^lane:\s*([A-Za-z]+)\s*$", re.MULTILINE)
_STATUS_IN_FRONTMATTER = re.compile(r"^status:\s*([A-Za-z][A-Za-z_]*)\s*$", re.MULTILINE)
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


_BRIEF_CROSS_REF_SKIP_MARKER = "<!-- gz-validate-skip: brief-cross-references -->"

_BRIEF_CROSS_REF_PATTERN = re.compile(
    r"\b(?P<kind>OBPI|ADR)-(?P<ver>\d+\.\d+\.\d+)(?:-(?P<seq>\d+)(?:-(?P<slug>[a-z0-9][a-z0-9-]*))?)?\b"
)

_ADR_DIR_PATTERN = re.compile(r"^ADR-(\d+\.\d+\.\d+)(?:-[a-z0-9][a-z0-9-]*)?$")
_OBPI_FILE_PATTERN = re.compile(r"^OBPI-(\d+\.\d+\.\d+)-(\d+)(?:-[a-z0-9][a-z0-9-]*)?\.md$")
_ADR_NAMESPACES: tuple[str, ...] = ("foundation", "pre-release")


def _build_cross_reference_index(adr_root: Path) -> tuple[set[str], set[str]]:
    """Walk ADR canon and index resolvable ``X.Y.Z`` and ``X.Y.Z-NN`` keys."""
    adr_versions: set[str] = set()
    obpi_keys: set[str] = set()
    for namespace in _ADR_NAMESPACES:
        ns_dir = adr_root / namespace
        if not ns_dir.is_dir():
            continue
        for adr_dir in ns_dir.iterdir():
            if not adr_dir.is_dir():
                continue
            match = _ADR_DIR_PATTERN.match(adr_dir.name)
            if match is None:
                continue
            adr_versions.add(match.group(1))
            obpi_dir = adr_dir / "obpis"
            if not obpi_dir.is_dir():
                continue
            for brief in obpi_dir.glob("OBPI-*.md"):
                fm = _OBPI_FILE_PATTERN.match(brief.name)
                if fm is not None:
                    obpi_keys.add(f"{fm.group(1)}-{fm.group(2)}")
    return adr_versions, obpi_keys


def _resolves(
    kind: str, version: str, seq: str | None, adr_versions: set[str], obpi_keys: set[str]
) -> bool:
    """Return True if the identifier resolves to an on-disk artifact.

    Bare ``OBPI-X.Y.Z`` (without ``-NN``) is a prose group-reference to the
    ADR family and resolves when the ADR version exists. Drift cases the
    GHI #436 body targets all carry a sequence number; bare-prefix prose is
    not a drift signal.
    """
    if kind == "ADR" or seq is None:
        return version in adr_versions
    return f"{version}-{seq}" in obpi_keys


def _scan_brief_cross_references(
    brief: Path,
    adr_versions: set[str],
    obpi_keys: set[str],
    project_root: Path,
) -> list[ValidationError]:
    """Extract identifiers from one brief and emit one error per unresolvable hit."""
    try:
        lines = brief.read_text(encoding="utf-8").splitlines()
    except (UnicodeDecodeError, OSError):
        return []
    rel = brief.relative_to(project_root).as_posix()
    errors: list[ValidationError] = []
    self_id = brief.stem  # e.g. "OBPI-0.0.31-02-register-t0-scorecard"
    self_match = _OBPI_FILE_PATTERN.match(brief.name)
    self_obpi_key = f"{self_match.group(1)}-{self_match.group(2)}" if self_match else None
    seen_on_line: set[tuple[int, str]] = set()
    in_fenced_block = False
    for idx, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            in_fenced_block = not in_fenced_block
            continue
        if in_fenced_block:
            continue
        if idx > 0 and lines[idx - 1].strip() == _BRIEF_CROSS_REF_SKIP_MARKER:
            continue
        for match in _BRIEF_CROSS_REF_PATTERN.finditer(line):
            kind = match.group("kind")
            version = match.group("ver")
            seq = match.group("seq")
            identifier = match.group(0)
            # A brief naturally references its own ID (frontmatter, headings,
            # Verification commands); self-reference is always resolvable.
            if kind == "OBPI" and seq is not None:
                if f"{version}-{seq}" == self_obpi_key:
                    continue
                if identifier == self_id:
                    continue
            key = (idx + 1, identifier)
            if key in seen_on_line:
                continue
            if _resolves(kind, version, seq, adr_versions, obpi_keys):
                continue
            seen_on_line.add(key)
            errors.append(
                ValidationError(
                    type="brief_cross_references",
                    artifact=f"{rel}:{idx + 1}",
                    message=(
                        f"Brief references `{identifier}` but no matching "
                        "on-disk artifact exists under "
                        "`docs/design/adr/{foundation,pre-release}/`. "
                        "Update the reference to a registered identifier, "
                        "or prefix the line with "
                        f"`{_BRIEF_CROSS_REF_SKIP_MARKER}` "
                        "to mark it as speculative (GHI #436)."
                    ),
                )
            )
    return errors


def audit_brief_cross_references(project_root: Path) -> list[ValidationError]:
    """Brief identifier references must resolve to on-disk artifacts (GHI #436).

    OBPI briefs cite sibling OBPIs and parent/peer ADRs by bare identifier
    throughout. When the referenced sibling is renamed or renumbered after
    the brief is authored, the brief silently drifts; ``gz validate
    --documents`` and ``mkdocs build --strict`` do not catch bare-identifier
    drift because the references are not markdown links.

    Scope: every brief under
    ``docs/design/adr/{foundation,pre-release}/*/obpis/*.md``. Each
    identifier matching ``(OBPI|ADR)-X.Y.Z[-NN[-slug]]`` must resolve to:

    * An ADR directory (for ``ADR-X.Y.Z``) under
      ``docs/design/adr/{foundation,pre-release}/ADR-X.Y.Z-*/``, OR
    * An OBPI brief file (for ``OBPI-X.Y.Z-NN``) at
      ``docs/design/adr/{foundation,pre-release}/ADR-X.Y.Z-*/obpis/OBPI-X.Y.Z-NN*.md``.

    Bare-prefix references (``OBPI-0.0.32-05`` resolving to on-disk
    ``OBPI-0.0.32-05-init-update-flag.md``) are accepted — the GHI #436
    body explicitly classifies the prefix-match shape as ``fine``. Drift
    where the surrounding description contradicts the resolved surface is
    a semantic check beyond the mechanical scope; the operator catches
    that during reconcile.

    Recovery: update the reference, or prefix the line with
    ``<!-- gz-validate-skip: brief-cross-references -->`` to mark it as
    a forward-reference to an unlanded artifact.
    """
    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return []
    adr_versions, obpi_keys = _build_cross_reference_index(adr_root)
    brief_paths: list[Path] = []
    for namespace in _ADR_NAMESPACES:
        ns_dir = adr_root / namespace
        if not ns_dir.is_dir():
            continue
        brief_paths.extend(ns_dir.glob("*/obpis/OBPI-*.md"))
    errors: list[ValidationError] = []
    for brief in sorted(brief_paths):
        errors.extend(_scan_brief_cross_references(brief, adr_versions, obpi_keys, project_root))
    return errors


_BRIEF_DEMO_SKIP_MARKER = "<!-- gz-validate-skip: brief-demo-section -->"

_BRIEF_DEMO_HEADING_RE = re.compile(r"^##\s+Demo\s*$", re.MULTILINE)
# Audit fires only on briefs actively being authored or implemented. Backlog
# briefs (`pending`) carry queued scope that may never be implemented, so
# flagging them adds friction without value. Terminal briefs predate the rule
# and are grandfathered.
_DEMO_ACTIVE_STATUSES = frozenset({"draft", "in_progress"})
_DEMO_CLI_SURFACE_RE = re.compile(
    r"src/gzkit/cli/parser_artifacts\.py|src/gzkit/commands/[A-Za-z0-9_./*\-]+\.py"
)


def _brief_lane(text: str) -> str | None:
    """Return lowercase lane value from frontmatter, or None when absent."""
    match = _LANE_IN_FRONTMATTER.search(text)
    return match.group(1).lower() if match else None


def _brief_status(text: str) -> str | None:
    """Return lowercase status value from frontmatter, or None when absent."""
    match = _STATUS_IN_FRONTMATTER.search(text)
    return match.group(1).lower() if match else None


def _brief_allowed_paths_section(text: str) -> str:
    """Return the text of the brief's ``## Allowed Paths`` section, or ``""``."""
    lines = text.splitlines()
    start: int | None = None
    for idx, line in enumerate(lines):
        if line.strip().lower().startswith("## allowed paths"):
            start = idx + 1
            break
    if start is None:
        return ""
    end = len(lines)
    for idx in range(start, len(lines)):
        if lines[idx].startswith("## "):
            end = idx
            break
    return "\n".join(lines[start:end])


def _brief_touches_cli_surface(text: str) -> bool:
    """Return True when Allowed Paths intersect a CLI verb / commands module."""
    section = _brief_allowed_paths_section(text)
    if not section:
        return False
    return _DEMO_CLI_SURFACE_RE.search(section) is not None


def audit_brief_demo_section(project_root: Path) -> list[ValidationError]:
    """Heavy-lane CLI-shipping briefs must carry a ``## Demo`` H2 section (GHI #431).

    The closeout walkthrough discovery (``src/gzkit/commands/ceremony_data.py``)
    harvests concrete invocations from a brief's ``## Demo`` section. When a
    heavy-lane brief that ships a new or amended CLI verb omits the section,
    walkthrough falls back to synthesized ``--help`` invocations — the
    weakest possible product demonstration — and the operator only discovers
    the deficit mid-attestation. The retroactive fix on ADR-0.0.30 (five
    briefs, ``## Demo`` sections appended at closeout) is the canonical
    failure exemplar.

    Scope: brief under
    ``docs/design/adr/{foundation,pre-release}/*/obpis/*.md`` fails closed
    when **all** of the following hold:

    * frontmatter ``lane: Heavy`` (case-insensitive)
    * frontmatter ``status`` is in ``{draft, in_progress}`` — the active
      authoring/implementation states. Terminal briefs
      (``completed``/``attested_completed``/``validated``/``withdrawn``/
      ``superseded``) predate the rule and are grandfathered; ``pending``
      backlog briefs carry queued scope and are not gated until activated
    * ``## Allowed Paths`` section names ``src/gzkit/cli/parser_artifacts.py``
      OR any ``src/gzkit/commands/*.py`` path (the new/amended CLI verb signal)
    * brief body contains no ``^## Demo\\s*$`` H2 heading

    Recovery: author the ``## Demo`` H2 section with concrete invocations
    exercising the delivered surface (not ``--help``), or — when the brief
    is intentionally exempted (e.g. CLI surface added for housekeeping in a
    larger non-CLI brief) — place
    ``<!-- gz-validate-skip: brief-demo-section -->`` anywhere in the brief
    body to mark it grandfathered.
    """
    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return []
    brief_paths: list[Path] = []
    for namespace in _ADR_NAMESPACES:
        ns_dir = adr_root / namespace
        if not ns_dir.is_dir():
            continue
        brief_paths.extend(ns_dir.glob("*/obpis/OBPI-*.md"))
    errors: list[ValidationError] = []
    for brief in sorted(brief_paths):
        try:
            text = brief.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if _BRIEF_DEMO_SKIP_MARKER in text:
            continue
        if _brief_lane(text) != "heavy":
            continue
        status = _brief_status(text) or ""
        if status not in _DEMO_ACTIVE_STATUSES:
            continue
        if not _brief_touches_cli_surface(text):
            continue
        if _BRIEF_DEMO_HEADING_RE.search(text):
            continue
        rel = brief.relative_to(project_root).as_posix()
        errors.append(
            ValidationError(
                type="brief_demo_section",
                artifact=rel,
                message=(
                    "Heavy-lane CLI-shipping brief is missing a `## Demo` "
                    "H2 section. The closeout walkthrough harvests this "
                    "section for concrete invocations; without it, the "
                    "discovery falls back to synthesized `--help` runs "
                    "(the weakest product demonstration). Author the "
                    "section with real invocations exercising the "
                    "delivered surface, or place "
                    f"`{_BRIEF_DEMO_SKIP_MARKER}` in the body to mark "
                    "the brief grandfathered (GHI #431)."
                ),
            )
        )
    return errors


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


_BRIEF_STATUS_IN_FRONTMATTER = re.compile(r"^status:\s*(\S+)", re.MULTILINE)

# Terminal statuses: briefs in these states are historical records, not active
# authoring surfaces. The --brief-command-shape validator only gates at
# authoring time (GHI #550 objective: "fails closed at authoring time"), so
# pre-existing compound commands in completed/superseded briefs are not flagged.
_BRIEF_TERMINAL_STATUSES: frozenset[str] = frozenset(
    {
        "Completed",
        "attested_completed",
        "Validated",
        "Superseded",
        "archived",
        "Promoted",
    }
)


def audit_brief_command_shape(project_root: Path) -> list[ValidationError]:
    """Fail closed (exit 3) when a brief Verification block contains a
    non-shell-less command (GHI #550, OBPI-0.0.63-07).

    Walks active (non-terminal-status) OBPI-*.md briefs, extracts
    ``## Verification`` fenced commands via ``extract_fenced_commands``,
    and flags any command that fails ``is_shell_less_executable``
    (the BI-1 shared classifier from OBPI-02).

    Terminal-status briefs (Completed, attested_completed, Validated,
    Superseded, archived, Promoted) are skipped — they are historical
    records, not active authoring surfaces.
    """
    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return []
    errors: list[ValidationError] = []
    for brief in sorted(adr_root.rglob("OBPI-*.md")):
        text = brief.read_text(encoding="utf-8")
        status_match = _BRIEF_STATUS_IN_FRONTMATTER.search(text)
        if status_match and status_match.group(1) in _BRIEF_TERMINAL_STATUSES:
            continue
        section = extract_markdown_section(text, "Verification") or ""
        for cmd in extract_fenced_commands(section):
            if not is_shell_less_executable(cmd):
                rel = brief.relative_to(project_root).as_posix()
                errors.append(
                    ValidationError(
                        type="brief_command_shape",
                        artifact=rel,
                        message=(
                            f"Non-shell-less Verification command in {rel!r}: {cmd!r}. "
                            "Rewrite as separate single-program lines "
                            "(no &&, ||, |, ;, $(...), or redirects)."
                        ),
                    )
                )
    return errors
