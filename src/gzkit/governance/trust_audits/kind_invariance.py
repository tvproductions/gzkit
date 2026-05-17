"""Kind-invariance trust audit for foundation-tier ADRs (OBPI-0.0.35-04).

Enforces the ## Why foundation tier? section convention: every ``kind: foundation``
ADR under ``docs/design/adr/foundation/`` must carry a substantive, non-placeholder
section under that exact heading (byte-identical match per OBPI-03 REQ-01).
"""

from __future__ import annotations

import re
from pathlib import Path

from gzkit.governance.trust_audits.taxonomy import _parse_adr_frontmatter
from gzkit.hooks.obpi import STRICT_PLACEHOLDERS
from gzkit.validate import ValidationError

_SECTION_HEADING = "## Why foundation tier?"
_BRACKETED_PROMPT_RE = re.compile(r"_\[.*?\]_", re.DOTALL)


def _is_placeholder_body(text: str) -> bool:
    """Return True if the section body is empty or only placeholder content."""
    clean = text.strip().lower()
    if not clean:
        return True
    if clean in STRICT_PLACEHOLDERS:
        return True
    if any(p in clean for p in ["paste", "one-sentence"]):
        return True
    # Remove _[...]_ bracketed author-prompts; if nothing substantive remains, fail.
    stripped = _BRACKETED_PROMPT_RE.sub("", clean).strip()
    return not stripped


def _extract_section_body(content: str, heading: str) -> str | None:
    """Return the body text between *heading* and the next ## heading, or None if absent.

    Returns an empty string if the heading is present but has no body lines.
    """
    lines = content.splitlines()
    in_section = False
    body_lines: list[str] = []
    for line in lines:
        if line.rstrip() == heading:
            in_section = True
            continue
        if in_section:
            if line.startswith("## "):
                break
            body_lines.append(line)
    if not in_section:
        return None
    return "\n".join(body_lines)


def _strip_frontmatter(content: str) -> str:
    """Return *content* with the leading YAML frontmatter block removed."""
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return content
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[i + 1 :])
    return content


def _check_foundation_adr(adr_file: Path, project_root: Path) -> ValidationError | None:
    """Return a ValidationError if *adr_file* fails the kind-invariance check, else None."""
    frontmatter = _parse_adr_frontmatter(adr_file)
    if frontmatter is None:
        return None
    if frontmatter.get("kind") != "foundation":
        return None

    try:
        raw = adr_file.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None

    body = _strip_frontmatter(raw)
    rel = adr_file.relative_to(project_root).as_posix()

    section_body = _extract_section_body(body, _SECTION_HEADING)
    if section_body is None:
        return ValidationError(
            type="kind_invariance",
            artifact=rel,
            message=(
                f"Foundation ADR is missing the `{_SECTION_HEADING}` section. "
                "Add a substantive one-sentence answer to the invariance test "
                "('Without this ADR, the project would not be the project because ...') "
                "under that exact heading. "
                "Recovery: add `## Why foundation tier?` followed by a non-placeholder answer."
            ),
        )

    if _is_placeholder_body(section_body):
        return ValidationError(
            type="kind_invariance",
            artifact=rel,
            message=(
                f"Foundation ADR has a `{_SECTION_HEADING}` section but its body "
                "is empty or contains only placeholder text (TBD, TODO, unfilled "
                "_[Author: ...]_ prompts, etc.). "
                "Recovery: replace the placeholder with a one-sentence substantive "
                "answer to the invariance test."
            ),
        )

    return None


def audit_kind_invariance(project_root: Path) -> list[ValidationError]:
    """Validate every foundation-kind ADR carries a substantive ## Why foundation tier? section.

    Globs ``docs/design/adr/foundation/ADR-*/ADR-*.md``, parses frontmatter,
    selects only those with ``kind: foundation``, then asserts each carries the
    section heading (byte-identical) with non-empty, non-placeholder body content.

    Exit semantics (per ValidationError aggregation):
        * 0 — all foundation ADRs pass
        * 3 — one or more foundation ADRs fail (policy breach)
    """
    foundation_dir = project_root / "docs" / "design" / "adr" / "foundation"
    if not foundation_dir.is_dir():
        return []

    errors: list[ValidationError] = []
    for adr_file in sorted(foundation_dir.glob("ADR-*/ADR-*.md")):
        error = _check_foundation_adr(adr_file, project_root)
        if error is not None:
            errors.append(error)
    return errors
