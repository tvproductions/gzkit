"""Pointer-integrity validator — ADR-0.0.33 Invariant 3.

Walks the per-turn surface corpus (``AGENTS.md``, ``CLAUDE.md``,
``.claude/rules/**``), extracts every ``> See [...](path#anchor)``
blockquote pointer, and asserts:

1. The referenced ``path`` exists on disk, resolved RELATIVE TO THE SOURCE
   FILE's directory — the same resolution a reader's markdown viewer performs
   (GHI #931).
2. The ``#anchor`` resolves to a heading in the destination file (using
   mkdocs-compatible slugification).
3. The destination file carries a back-pointer that MATCHES this pointer:
   ``<!-- lifted-from: <source-path>#<anchor> -->`` naming this source and this
   anchor. A comment naming some other source does not discharge it (GHI #932).

Returns a ``ValidationError(type="pointer_anchors")`` for every unresolved
pointer or missing back-pointer. An empty list means the surface is clean.

Scope: only blockquote lines (``> ...``) that contain the keyword ``See``
are checked. Inline markdown links and unrelated blockquotes are ignored.
"""

from __future__ import annotations

import contextlib
import os
import re
from pathlib import Path

from gzkit.core.validation_rules import ValidationError

_SURFACE_FILES = ("AGENTS.md", "CLAUDE.md")
_HEADING_RE = re.compile(r"^#{1,6}\s+(.+)", re.MULTILINE)
_LINK_RE = re.compile(r"\(([^()\s]+#[^()\s]+)\)")
_LIFTED_FROM_RE = re.compile(r"<!--\s*lifted-from:\s*(\S+?)\s*-->")


def validate_pointer_integrity(project_root: Path) -> list[ValidationError]:
    """Return ValidationErrors for unresolved pointers or missing back-pointers."""
    errors: list[ValidationError] = []
    for source_rel, content in _iter_surface_files(project_root):
        errors.extend(_check_source_file(project_root, source_rel, content))
    return errors


def _iter_surface_files(project_root: Path) -> list[tuple[str, str]]:
    """Yield (relative_path_posix, content) for each per-turn surface file."""
    results: list[tuple[str, str]] = []
    for name in _SURFACE_FILES:
        path = project_root / name
        if path.exists():
            with contextlib.suppress(OSError):
                results.append((name, path.read_text(encoding="utf-8")))

    rules_root = project_root / ".claude" / "rules"
    if rules_root.exists():
        for rule_path in sorted(rules_root.rglob("*.md")):
            with contextlib.suppress(OSError):
                rel = rule_path.relative_to(project_root).as_posix()
                results.append((rel, rule_path.read_text(encoding="utf-8")))
    return results


def _check_source_file(project_root: Path, source_rel: str, content: str) -> list[ValidationError]:
    """Check every blockquote-See pointer in one source file."""
    errors: list[ValidationError] = []
    for lineno, line in enumerate(content.splitlines(), start=1):
        if not _is_blockquote_see(line):
            continue
        for target in _LINK_RE.findall(line):
            path_part, _, anchor = target.partition("#")
            if not anchor:
                continue
            errors.extend(
                _validate_pointer(
                    project_root,
                    source_rel,
                    lineno,
                    path_part,
                    anchor,
                )
            )
    return errors


def _is_blockquote_see(line: str) -> bool:
    """Return True if line is a `> ... See ...` blockquote pointer."""
    stripped = line.lstrip()
    if not stripped.startswith(">"):
        return False
    return " See " in stripped or stripped.startswith("> See ")


def _validate_pointer(
    project_root: Path,
    source_rel: str,
    lineno: int,
    path_part: str,
    anchor: str,
) -> list[ValidationError]:
    """Return errors for one resolved (path#anchor) pointer."""
    source_dir = (project_root / source_rel).parent
    dest_path = Path(os.path.normpath(source_dir / path_part))
    if not dest_path.exists() or not dest_path.is_file():
        return [
            _make_error(
                f"Pointer destination does not exist: "
                f"{source_rel}:{lineno} -> {path_part}#{anchor}",
                source_rel,
            )
        ]

    try:
        dest_content = dest_path.read_text(encoding="utf-8")
    except OSError:
        return [
            _make_error(
                f"Pointer destination unreadable: {source_rel}:{lineno} -> {path_part}#{anchor}",
                source_rel,
            )
        ]

    slugs = _heading_slugs(dest_content)
    if anchor not in slugs:
        return [
            _make_error(
                f"Pointer anchor unresolved: "
                f"{source_rel}:{lineno} -> {path_part}#{anchor} "
                f"(no heading slugifies to '{anchor}' in {path_part})",
                source_rel,
            )
        ]

    back_pointers = _LIFTED_FROM_RE.findall(dest_content)
    if not back_pointers:
        return [
            _make_error(
                f"Missing back-pointer: destination {path_part} (referenced by "
                f"{source_rel}:{lineno}#{anchor}) lacks "
                f"`<!-- lifted-from: -->` comment",
                source_rel,
            )
        ]

    expected = f"{source_rel}#{anchor}"
    if expected not in back_pointers:
        return [
            _make_error(
                f"Unmatched back-pointer: destination {path_part} (referenced by "
                f"{source_rel}:{lineno}#{anchor}) carries "
                f"{sorted(back_pointers)} but none names `{expected}`",
                source_rel,
            )
        ]

    return []


def _slugify(text: str) -> str:
    """Slugify heading text mkdocs-compatibly.

    Mirrors the mkdocs default ``markdown.extensions.toc`` slugifier:
    lowercase, strip non-word/non-space/non-hyphen characters in-place
    (does NOT collapse the surrounding whitespace), then map whitespace and
    underscores to ``-``. Adjacent hyphens (e.g. from stripped ``&``) are
    preserved verbatim — that's how anchors like
    ``anti-vibing-mantra--relationship`` arise.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]", "-", text)
    return text.strip("-")


def _heading_slugs(content: str) -> set[str]:
    """Return the set of slugified headings from markdown content."""
    return {_slugify(m.group(1).strip()) for m in _HEADING_RE.finditer(content)}


def _make_error(message: str, source_rel: str) -> ValidationError:
    """Build a pointer_anchors ValidationError."""
    return ValidationError(
        type="pointer_anchors",
        artifact=source_rel,
        message=message,
    )
