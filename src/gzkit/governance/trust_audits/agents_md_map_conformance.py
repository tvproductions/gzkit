"""Map-not-encyclopedia conformance audit for AGENTS.md template and rendered file (ADR-0.0.54).

Asserts four shape criteria from ADR-0.0.54 § Decision item 3:
(a) every paragraph in AGENTS.md is either <= 5 lines OR begins with a
    binding-bullet marker ('- ', '* ', '1.'/'2.'/..., '**')
(b) no subsection title matches the prohibited set
    ({'Worked example', 'Anti-patterns', 'Rationale', 'Why this is canon',
      'Why X is canon (any regex)'}, case-insensitive)
(c) every '[text](path)' link resolves to an existing file under
    project_root; when '#anchor' is present, the anchor must match a
    slugified heading in the target file
(d) the file size is within the budget declared in
    data/instructions_files_budget.json

Two-layer audit (state-doctrine Layer-1 + Layer-3):
- Template (src/gzkit/templates/agents.md): shape criteria (a)/(b)/(c) — the
  operator-edit surface where violations are authored. Per ADR-0.0.54, this
  is the canonical surface; ADR-0.0.37's invariant registry will absorb
  portions of this content via projection in future OBPIs.
- Rendered AGENTS.md (project root): budget criterion (d) — the projected
  property that determines context-load cost.

Registry entries (.gzkit/invariants/*.json) are NOT audited in this version.
The registry is ADR-0.0.37's edit surface; registry-specific validation
will land in a future OBPI under that ADR. Today's registry has 3 entries
(CIC-1, CIC-2, foundation-adr-registers) — the rule corpus has not yet
migrated to the registry.

Failures embed '/gz-context-diet' in the message field as a forward-compat
recovery pointer. ADR-0.0.53-02 will migrate this to a structured
RemediationPayload.recovery field once ADR-0.0.53 lands.

Additionally, the per-bullet 3-line heuristic in binding-rule sections
(PRIME DIRECTIVE, DO IT RIGHT, Behavior Rules) emits a non-policy
'agents_md_map_conformance_advisory' finding per ADR-0.0.54
Sec. Consequences Negative #7 — a warning, not a hard rejection.

Design decision (case-insensitive prohibited titles): the ADR enumerates
title strings with sentence case ('Worked example'), but operators may
plausibly author Title Case ('Worked Example'). The validator matches
case-insensitively so that authoring case does not provide an escape
hatch from the doctrine.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from gzkit.validate import ValidationError

_BUDGET_DATA_PATH = Path("data") / "instructions_files_budget.json"
_REMEDIATION = (
    "Run /gz-context-diet (or `uv run gz chores show instructions-files-diet`) "
    "to lift inline rationale to docs/governance/ behind one-line pointers."
)
_PACKAGED_DEFAULTS: dict[str, Any] = {
    "files": {"AGENTS.md": 40000, "CLAUDE.md": 40000},
    "globs": [{"pattern": ".claude/rules/*.md", "max_chars_per_file": 16000}],
}

# Case-insensitive match; tests use "Worked example" and "Worked Example"
_PROHIBITED_TITLES: frozenset[str] = frozenset(
    {
        "worked example",
        "anti-patterns",
        "rationale",
        "why this is canon",
    }
)

# "Why X is canon" pattern: matches "Why <anything> is canon", case-insensitive
_PROHIBITED_TITLE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^why\s+.+\s+is\s+canon$", re.IGNORECASE),
)

_BINDING_MARKER_PREFIXES: tuple[str, ...] = ("- ", "* ", "**")
# Numbered list patterns: "1.", "2.", "10." etc.
_NUMBERED_BULLET_PATTERN = re.compile(r"^\d+\.\s")

_BINDING_RULE_SECTION_TITLES: frozenset[str] = frozenset(
    {
        "prime directive (ownership)",
        "do it right (craftsmanship maxim)",
        "behavior rules",
    }
)

_TEMPLATE_REL_PATH = Path("src") / "gzkit" / "templates" / "agents.md"
_RENDERED_REL_PATH = Path("AGENTS.md")


def audit_agents_md_map_conformance(project_root: Path) -> list[ValidationError]:
    """Audit the AGENTS.md template + rendered file against map-not-encyclopedia doctrine.

    Two-layer audit (state-doctrine Layer-1 + Layer-3):
    - Template (src/gzkit/templates/agents.md): shape criteria (a)/(b)/(c) — the
      operator-edit surface where violations are authored. Per ADR-0.0.54, this
      is the canonical surface; ADR-0.0.37's invariant registry will absorb
      portions of this content via projection in future OBPIs.
    - Rendered AGENTS.md (project root): budget criterion (d) — the projected
      property that determines context-load cost.

    Registry entries (.gzkit/invariants/*.json) are NOT audited in this version.
    The registry is ADR-0.0.37's edit surface; registry-specific validation
    will land in a future OBPI under that ADR. Today's registry has 3 entries
    (CIC-1, CIC-2, foundation-adr-registers) — the rule corpus has not yet
    migrated to the registry.

    Returns hard-rejection ValidationErrors (type 'agents_md_map_conformance')
    for criteria a/b/c/d, and advisory findings (type
    'agents_md_map_conformance_advisory') for the per-bullet 3-line heuristic
    in binding-rule sections of the template.
    """
    config = _load_budget_config(project_root)
    errors: list[ValidationError] = []

    # Layer 1: template shape audit (a, b, c) + advisory bullet check
    template = project_root / _TEMPLATE_REL_PATH
    if template.is_file():
        template_text = template.read_text(encoding="utf-8")
        template_artifact = _TEMPLATE_REL_PATH.as_posix()
        errors.extend(_check_prohibited_titles(template_text, template_artifact))
        errors.extend(_check_paragraph_shape(template_text, template_artifact))
        errors.extend(
            _check_link_resolution(template_text, template_artifact, template, project_root)
        )
        errors.extend(_check_per_bullet_advisory(template_text, template_artifact))

    # Layer 3: rendered budget audit (d) only
    rendered = project_root / _RENDERED_REL_PATH
    if rendered.is_file():
        rendered_text = rendered.read_text(encoding="utf-8")
        rendered_artifact = _RENDERED_REL_PATH.as_posix()
        default_budget = _PACKAGED_DEFAULTS["files"].get(rendered_artifact, 40000)
        budget = int(config.get("files", {}).get(rendered_artifact, default_budget))
        errors.extend(_check_budget(rendered_text, rendered_artifact, budget))

    return errors


def _load_budget_config(project_root: Path) -> dict[str, Any]:
    """Resolve project overlay; fall back to packaged defaults."""
    overlay = project_root / _BUDGET_DATA_PATH
    if overlay.is_file():
        return json.loads(overlay.read_text(encoding="utf-8"))
    return _PACKAGED_DEFAULTS


def _check_budget(text: str, relpath: str, budget: int) -> list[ValidationError]:
    """Criterion (d): file size within budget."""
    actual = len(text)
    if actual <= budget:
        return []
    return [
        ValidationError(
            type="agents_md_map_conformance",
            artifact=relpath,
            message=(
                f"file is {actual} chars, exceeds {budget}-char budget by "
                f"{actual - budget}. {_REMEDIATION}"
            ),
        )
    ]


def _check_prohibited_titles(text: str, relpath: str) -> list[ValidationError]:
    """Criterion (b): no subsection title in the prohibited set (case-insensitive)."""
    errors: list[ValidationError] = []
    heading_pattern = re.compile(r"^(#{2,})\s+(.+?)\s*$")
    for lineno, line in enumerate(text.splitlines(), start=1):
        match = heading_pattern.match(line)
        if match is None:
            continue
        title = match.group(2).strip().lower()
        is_prohibited = title in _PROHIBITED_TITLES or any(
            p.match(title) for p in _PROHIBITED_TITLE_PATTERNS
        )
        if is_prohibited:
            errors.append(
                ValidationError(
                    type="agents_md_map_conformance",
                    artifact=relpath,
                    message=(
                        f"line {lineno}: prohibited subsection title "
                        f"{match.group(2)!r} (map-not-encyclopedia doctrine). "
                        f"{_REMEDIATION}"
                    ),
                )
            )
    return errors


def _check_paragraph_shape(text: str, relpath: str) -> list[ValidationError]:
    """Criterion (a): paragraph <= 5 lines OR starts with binding marker.

    Paragraph = consecutive non-blank lines. Headings (lines starting with #)
    and code-block delimiters are excluded from paragraph counting. Lines
    inside fenced code blocks are skipped (they may legitimately exceed
    5 lines without doctrine violation).
    """
    errors: list[ValidationError] = []
    paragraphs = _parse_paragraphs(text)
    for para in paragraphs:
        lines: list[str] = para["lines"]
        if len(lines) <= 5:
            continue
        if _starts_with_binding_marker(lines[0]):
            continue
        errors.append(
            ValidationError(
                type="agents_md_map_conformance",
                artifact=relpath,
                message=(
                    f"line {para['start_line']}: paragraph spans {len(lines)} "
                    f"lines without a binding-bullet marker (map-not-encyclopedia "
                    f"doctrine). {_REMEDIATION}"
                ),
            )
        )
    return errors


def _starts_with_binding_marker(line: str) -> bool:
    """True if line begins with a binding-bullet marker."""
    stripped = line.lstrip()
    if stripped.startswith(_BINDING_MARKER_PREFIXES):
        return True
    return bool(_NUMBERED_BULLET_PATTERN.match(stripped))


def _parse_paragraphs(text: str) -> list[dict[str, Any]]:
    """Group consecutive non-blank non-heading lines into paragraphs.

    Returns: list of {"lines": [str], "start_line": int}.
    Skips: blank lines, heading lines (starts with #), fenced code blocks
    (between ``` delimiters), markdown table rows (lines starting with '|'),
    and any line containing only whitespace.

    Table rows are skipped because tables are allowed shape (b) under
    `.gzkit/rules/agents-md-map-doctrine.md` § Invariant — distinct from
    prose paragraphs (shape a/c) and exempt from criterion (a)'s length limit.
    """
    paragraphs: list[dict[str, Any]] = []
    current_lines: list[str] = []
    current_start: int = 0
    in_code_fence = False
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.rstrip()
        if line.lstrip().startswith("```"):
            in_code_fence = not in_code_fence
            if current_lines:
                paragraphs.append({"lines": current_lines, "start_line": current_start})
                current_lines = []
            continue
        if in_code_fence:
            continue
        if line.lstrip().startswith("|"):
            if current_lines:
                paragraphs.append({"lines": current_lines, "start_line": current_start})
                current_lines = []
            continue
        if line.startswith("#") or not line.strip():
            if current_lines:
                paragraphs.append({"lines": current_lines, "start_line": current_start})
                current_lines = []
            continue
        if not current_lines:
            current_start = lineno
        current_lines.append(line)
    if current_lines:
        paragraphs.append({"lines": current_lines, "start_line": current_start})
    return paragraphs


def _check_link_resolution(
    text: str,
    relpath: str,
    target: Path,
    project_root: Path,
) -> list[ValidationError]:
    """Criterion (c): every '[...](path)' link resolves to existing file + anchor.

    Skips absolute URLs (http://, https://, mailto:, etc.) and pure '#anchor'
    intra-document links. For relative paths, the file MUST exist under
    project_root. When '#anchor' is present, the anchor MUST match a
    slugified heading in the target file (GitHub-style slugification).
    """
    errors: list[ValidationError] = []
    # Match [text](path) — non-greedy on text; path stops at ')' or whitespace
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
    in_code_fence = False
    for lineno, raw in enumerate(text.splitlines(), start=1):
        if raw.lstrip().startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue
        for match in link_pattern.finditer(raw):
            path_str = match.group(2)
            error = _resolve_one_link(path_str, lineno, relpath, target, project_root)
            if error is not None:
                errors.append(error)
    return errors


def _resolve_one_link(
    path_str: str,
    lineno: int,
    relpath: str,
    target: Path,
    project_root: Path,
) -> ValidationError | None:
    """Resolve a single link; return ValidationError or None."""
    # Skip absolute URLs and pure anchors
    if path_str.startswith(("http://", "https://", "mailto:", "#")):
        return None
    if "#" in path_str:
        file_part, anchor = path_str.split("#", 1)
    else:
        file_part, anchor = path_str, None
    if not file_part:
        return None
    # Resolve relative to the target file's directory first; fall back to project root
    candidates = [target.parent / file_part, project_root / file_part]
    resolved: Path | None = None
    for candidate in candidates:
        try:
            if candidate.is_file():
                resolved = candidate
                break
        except (OSError, ValueError):
            continue
    if resolved is None:
        return ValidationError(
            type="agents_md_map_conformance",
            artifact=relpath,
            message=(
                f"line {lineno}: link {path_str!r} does not resolve to "
                f"an existing file. {_REMEDIATION}"
            ),
        )
    if anchor is not None and not _anchor_resolves(resolved, anchor):
        return ValidationError(
            type="agents_md_map_conformance",
            artifact=relpath,
            message=(
                f"line {lineno}: link {path_str!r} resolves to a file "
                f"but anchor {anchor!r} does not match any heading. "
                f"{_REMEDIATION}"
            ),
        )
    return None


def _anchor_resolves(target: Path, anchor: str) -> bool:
    """True if `anchor` matches a slugified heading in `target`.

    Slugification: GitHub-style — lowercase, replace whitespace with '-',
    drop non-alphanumeric except '-' and '_'.
    """
    try:
        text = target.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    expected = anchor.lower().strip()
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
    in_code_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue
        match = heading_pattern.match(line)
        if match is None:
            continue
        heading = match.group(2)
        slug = _slugify(heading)
        if slug == expected:
            return True
    return False


def _slugify(heading: str) -> str:
    """GitHub-style slug: lowercase, spaces -> '-', drop non-alphanumeric/-/_."""
    text = heading.lower().strip()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^a-z0-9_-]", "", text)
    return text


def _check_per_bullet_advisory(text: str, relpath: str) -> list[ValidationError]:
    """REQ-05: per-bullet 3-line heuristic in binding-rule sections.

    Soft warning (type 'agents_md_map_conformance_advisory') — not in the
    policy-breach set, does not change exit code. Operator-informational only.
    Per ADR-0.0.54 Sec. Consequences Negative #7, hard rejection is reserved
    for the prohibited-subsection-title set; the per-bullet check is heuristic.
    """
    errors: list[ValidationError] = []
    current_section: str | None = None
    in_code_fence = False
    bullet_lines: list[str] = []
    bullet_start = 0
    section_pattern = re.compile(r"^##\s+(.+?)\s*$")
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.rstrip()
        if line.lstrip().startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue
        section_match = section_pattern.match(line)
        if section_match:
            if bullet_lines:
                _maybe_advisory(bullet_lines, bullet_start, current_section, relpath, errors)
                bullet_lines = []
            current_section = section_match.group(1).strip().lower()
            continue
        if current_section not in _BINDING_RULE_SECTION_TITLES:
            continue
        if _starts_with_binding_marker(line):
            if bullet_lines:
                _maybe_advisory(bullet_lines, bullet_start, current_section, relpath, errors)
            bullet_lines = [line]
            bullet_start = lineno
        elif bullet_lines and line.strip():
            bullet_lines.append(line)
        elif bullet_lines and not line.strip():
            _maybe_advisory(bullet_lines, bullet_start, current_section, relpath, errors)
            bullet_lines = []
    if bullet_lines:
        _maybe_advisory(bullet_lines, bullet_start, current_section, relpath, errors)
    return errors


def _maybe_advisory(
    bullet_lines: list[str],
    bullet_start: int,
    section: str | None,
    relpath: str,
    errors: list[ValidationError],
) -> None:
    """Emit advisory if bullet exceeds 3 lines."""
    if len(bullet_lines) > 3:
        errors.append(
            ValidationError(
                type="agents_md_map_conformance_advisory",
                artifact=relpath,
                message=(
                    f"line {bullet_start}: bullet in section {section!r} spans "
                    f"{len(bullet_lines)} lines (>3 advisory threshold). "
                    f"Consider lifting prose to docs/governance/ if it's rationale. "
                    f"{_REMEDIATION}"
                ),
            )
        )
