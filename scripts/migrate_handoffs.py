#!/usr/bin/env python3
"""Migrate per-ADR session handoffs into the canonical ``.gzkit/handoffs/`` store.

WHY: ADR-0.0.65 canonizes ``.gzkit/handoffs/`` as the single handoff write
location (per ADR-0.0.41 / OBPI-0.0.41-03). Historically the ``gz-session-handoff``
skill wrote handoffs into per-ADR package directories
(``docs/design/adr/**/handoffs/``), which the SessionStart orientation reader
could not see. This script relocates those legacy handoffs into
``.gzkit/handoffs/``, rewrites ``continues_from:`` chain pointers that referenced
the old per-ADR paths, and removes the now-empty source directories.

Idempotent: a second run finds no source handoffs and makes no changes.

Collision policy (fail-closed):

- A source handoff whose basename already exists in ``.gzkit/handoffs/`` with
  *byte-identical* content is removed from the source tree as a dedup — the
  canonical copy is authoritative and is never overwritten.
- A source handoff whose basename collides with a *differing* canonical copy is
  a hard error (``RuntimeError``); it is never silently overwritten
  (OBPI-0.0.65-01 REQ #9 STOP-on-BLOCKERS).

Reference: ADR-0.0.65-handoff-system-consolidation, OBPI-0.0.65-01.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

CANONICAL_DIR = Path(".gzkit/handoffs")
SOURCE_ROOT = Path("docs/design/adr")

# A continues_from: line whose value is a per-ADR handoffs path. The basename is
# preserved; only the directory prefix is rewritten to the canonical store.
_CONTINUES_FROM_DOCS_RE = re.compile(
    r"^(continues_from:[ \t]*)docs/design/adr/\S*/handoffs/(\S+\.md)[ \t]*$",
    re.MULTILINE,
)


@dataclass
class MigrationResult:
    """Summary of what a migration run did (or would do, in dry-run)."""

    moved: list[str] = field(default_factory=list)
    deduped: list[str] = field(default_factory=list)
    rewritten: list[str] = field(default_factory=list)
    removed_dirs: list[str] = field(default_factory=list)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(repo_root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo_root, check=True)


def find_source_handoffs(repo_root: Path) -> list[Path]:
    """Return the per-ADR handoff files awaiting migration, sorted for determinism."""
    root = repo_root / SOURCE_ROOT
    if not root.exists():
        return []
    return sorted(p for p in root.rglob("*.md") if p.parent.name == "handoffs")


def rewrite_continues_from(text: str) -> str:
    """Rewrite per-ADR ``continues_from:`` path pointers to the canonical store.

    Bare-filename pointers (already valid in the flat canonical directory) and
    empty pointers are left untouched.
    """
    return _CONTINUES_FROM_DOCS_RE.sub(r"\1.gzkit/handoffs/\2", text)


def migrate(repo_root: Path, *, apply: bool = True) -> MigrationResult:
    """Relocate per-ADR handoffs into ``.gzkit/handoffs/`` and fix chain pointers.

    When ``apply`` is False, the returned result describes the intended actions
    without touching the filesystem or git index.
    """
    result = MigrationResult()
    canonical = repo_root / CANONICAL_DIR
    sources = find_source_handoffs(repo_root)

    for src in sources:
        dst = canonical / src.name
        rel_src = src.relative_to(repo_root).as_posix()
        rel_dst = dst.relative_to(repo_root).as_posix()
        if dst.exists():
            if _sha256(src) != _sha256(dst):
                raise RuntimeError(
                    f"Handoff name collision with differing content: {rel_src} "
                    f"vs canonical {rel_dst}. Resolve manually before migrating "
                    "(STOP-on-BLOCKERS, OBPI-0.0.65-01 REQ #9)."
                )
            result.deduped.append(rel_src)
            if apply:
                _git(repo_root, "rm", "-q", rel_src)
        else:
            result.moved.append(rel_src)
            if apply:
                _git(repo_root, "mv", rel_src, rel_dst)

    # Rewrite continues_from: pointers across the whole canonical store. This
    # covers both freshly-migrated files and pre-existing canonical files whose
    # pointers still reference the per-ADR source tree.
    for path in sorted(canonical.glob("*.md")):
        original = path.read_text(encoding="utf-8")
        rewritten = rewrite_continues_from(original)
        if rewritten != original:
            result.rewritten.append(path.relative_to(repo_root).as_posix())
            if apply:
                path.write_text(rewritten, encoding="utf-8")
                _git(repo_root, "add", path.relative_to(repo_root).as_posix())

    # Remove now-empty per-ADR handoffs/ directories.
    root = repo_root / SOURCE_ROOT
    if root.exists():
        for handoffs_dir in sorted(root.rglob("handoffs")):
            if handoffs_dir.is_dir() and not any(handoffs_dir.iterdir()):
                result.removed_dirs.append(handoffs_dir.relative_to(repo_root).as_posix())
                if apply:
                    handoffs_dir.rmdir()

    return result


def _format(result: MigrationResult) -> str:
    lines = [
        f"moved:        {len(result.moved)}",
        f"deduped:      {len(result.deduped)}",
        f"rewritten:    {len(result.rewritten)}",
        f"removed dirs: {len(result.removed_dirs)}",
    ]
    for rel in result.deduped:
        lines.append(f"  dedup (identical, git rm): {rel}")
    for rel in result.rewritten:
        lines.append(f"  rewrote continues_from:    {rel}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root (defaults to the current working directory).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report intended actions without modifying the filesystem or git index.",
    )
    args = parser.parse_args(argv)
    result = migrate(args.repo_root.resolve(), apply=not args.dry_run)
    print(_format(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
