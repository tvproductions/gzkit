"""Pointer-integrity validator — ADR-0.0.33 Invariant 3.

Two arms, one contract (``docs/governance/agent-control-surface-fidelity-doctrine.md``
§ Invariant 3; ADR-0.0.33 Anti-Pattern 5 names the comment *"the reverse half of
the pointer-integrity contract"*).

**Forward arm.** Walks the per-turn surface corpus (``AGENTS.md``, ``CLAUDE.md``,
``.claude/rules/**``), extracts every ``> See [...](path#anchor)`` blockquote
pointer, and asserts:

1. The referenced ``path`` exists on disk, resolved RELATIVE TO THE SOURCE
   FILE's directory — the same resolution a reader's markdown viewer performs
   (GHI #931).
2. The ``#anchor`` resolves to a heading in the destination file (using
   mkdocs-compatible slugification).
3. The destination file carries a back-pointer that MATCHES this pointer:
   ``<!-- lifted-from: <source-path>#<anchor> -->`` naming this source and this
   anchor. A comment naming some other source does not discharge it (GHI #932).

Forward scope is ``> See [...]`` blockquotes only — REQ-0.0.33-03-04, attested:
inline markdown links and unrelated blockquotes are not checked.

**Reverse arm (GHI #933).** Walks every ``<!-- lifted-from: <origin>#<anchor> -->``
declaration under ``docs/governance/**`` and asserts:

4. The named origin file exists.
5. ``#anchor`` resolves to a heading in the declaring (destination) page.
6. The origin carries a link to this destination with this anchor — resolved
   relative to the origin's directory, as in (1). ANY ``[...](path#anchor)`` link
   satisfies it, prose or blockquote: the reverse arm asks whether the lift is
   still pointed at; the pointer's shape is the forward arm's scope question.

The doctrine's own format example, the literal ``<path>#<anchor>``, is not a
declaration and is excluded exactly — a real declaration naming a missing origin
still produces a finding.

Returns a ``ValidationError(type="pointer_anchors")`` for every finding. An
empty list means the surface is clean in both directions.
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
#: Any markdown link target, anchored or not — the reverse arm's notion of "points at".
_ANY_LINK_RE = re.compile(r"\[[^\]]*\]\(([^()\s]+)\)")
#: The doctrine's literal format example. Excluded exactly, never by shape.
_PLACEHOLDER_DECLARATION = "<path>#<anchor>"
_REVERSE_SCOPE = Path("docs") / "governance"
#: Recovery prose for reverse-arm findings (guardrail-feedback-prose: what / why / next).
_REVERSE_RECOVERY = (
    " Invariant 3 (docs/governance/agent-control-surface-fidelity-doctrine.md) requires the"
    " origin to carry the forward pointer for every lift it declares. Restore the pointer at"
    " the origin's canonical source (for AGENTS.md: the committed rendition via"
    " `gz content compose` -> `gz content commit`), or retire the declaration if the lift"
    " was undone, then re-run `uv run gz validate --pointer-anchors`."
)


def validate_pointer_integrity(project_root: Path) -> list[ValidationError]:
    """Return ValidationErrors for unresolved pointers, missing or orphaned back-pointers."""
    errors: list[ValidationError] = []
    for source_rel, content in _iter_surface_files(project_root):
        errors.extend(_check_source_file(project_root, source_rel, content))
    errors.extend(_check_back_pointers(project_root))
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


# ---------------------------------------------------------------------------
# Reverse arm (GHI #933)
# ---------------------------------------------------------------------------


def _check_back_pointers(project_root: Path) -> list[ValidationError]:
    """Check every `lifted-from` declaration under docs/governance/** against its origin."""
    errors: list[ValidationError] = []
    scope_root = project_root / _REVERSE_SCOPE
    if not scope_root.exists():
        return errors
    for dest_path in sorted(scope_root.rglob("*.md")):
        try:
            content = dest_path.read_text(encoding="utf-8")
        except OSError:
            continue
        dest_rel = dest_path.relative_to(project_root).as_posix()
        dest_slugs = _heading_slugs(content)
        for lineno, line in enumerate(content.splitlines(), start=1):
            for declaration in _LIFTED_FROM_RE.findall(line):
                if declaration == _PLACEHOLDER_DECLARATION:
                    continue
                errors.extend(
                    _validate_back_pointer(
                        project_root, dest_path, dest_rel, lineno, declaration, dest_slugs
                    )
                )
    return errors


def _validate_back_pointer(
    project_root: Path,
    dest_path: Path,
    dest_rel: str,
    lineno: int,
    declaration: str,
    dest_slugs: set[str],
) -> list[ValidationError]:
    """Return errors for one `<!-- lifted-from: origin#anchor -->` declaration."""
    finding = _check_one_back_pointer(
        project_root, dest_path, dest_rel, lineno, declaration, dest_slugs
    )
    if finding is None:
        return []
    return [_make_error(finding + _REVERSE_RECOVERY, dest_rel)]


def _check_one_back_pointer(
    project_root: Path,
    dest_path: Path,
    dest_rel: str,
    lineno: int,
    declaration: str,
    dest_slugs: set[str],
) -> str | None:
    """Return the what-failed clause for one declaration, or None when it is satisfied."""
    origin_rel, _, anchor = declaration.partition("#")
    where = f"{dest_rel}:{lineno} names {declaration}"
    origin_path = project_root / origin_rel
    if not origin_path.is_file():
        return f"Orphaned back-pointer: {where} but {origin_rel} does not exist."

    if anchor not in dest_slugs:
        return (
            f"Orphaned back-pointer: {where} but no heading slugifies to '{anchor}' in {dest_rel}."
        )

    try:
        origin_content = origin_path.read_text(encoding="utf-8")
    except OSError:
        return f"Orphaned back-pointer: {where} but {origin_rel} is unreadable."

    if not _origin_points_at(origin_path, origin_content, dest_path, anchor):
        return (
            f"Orphaned back-pointer: {where} but {origin_rel} carries no link to "
            f"{dest_rel}#{anchor}."
        )
    return None


def _origin_points_at(origin_path: Path, origin_content: str, dest_path: Path, anchor: str) -> bool:
    """Return True when any link in the origin resolves to dest_path with exactly this anchor."""
    for target in _ANY_LINK_RE.findall(origin_content):
        path_part, _, link_anchor = target.partition("#")
        if link_anchor != anchor:
            continue
        resolved = Path(os.path.normpath(origin_path.parent / path_part))
        if resolved == Path(os.path.normpath(dest_path)):
            return True
    return False


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
