#!/usr/bin/env python3
"""Settings-Local Backup Hook.

`.claude/settings.local.json` is gitignored, so a repo deletion or a fresh
clone loses it with no recovery from origin — measured 2026-08-29, when the
file was lost and neither `git` nor Claude's own `~/.claude.json` backups
held its contents (`allowedTools` is empty there; this project's permissions
lived only in the local file).

Keeps timestamped copies OUTSIDE the repository, under
`~/.claude/backups/<project-slug>/settings.local/`, so the vault survives
whatever happens to the working tree. Writes only when the content changed,
prunes to the most recent `_KEEP` snapshots, and reports a restore command
when the live file is missing but snapshots exist.

Stdlib only, per AGENTS.md § STDLIB-FIRST DOCTRINE.

Books, never refuses: a backup failure must not cost the operator a session.

Exit codes:
  0 - always
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

_KEEP = 20
_REL = Path(".claude") / "settings.local.json"


def _find_project_root(start: Path) -> Path:
    current = start
    while current != current.parent:
        if (current / ".gzkit").is_dir():
            return current
        current = current.parent
    return start


def _vault(root: Path) -> Path:
    slug = str(root).replace("/", "-")
    return Path.home() / ".claude" / "backups" / slug / "settings.local"


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _snapshots(vault: Path) -> list[Path]:
    if not vault.is_dir():
        return []
    return sorted(vault.glob("settings.local.*.json"))


def _prune(vault: Path) -> None:
    for stale in _snapshots(vault)[:-_KEEP]:
        stale.unlink(missing_ok=True)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        sys.exit(0)

    cwd = payload.get("cwd") or ""
    if not cwd:
        sys.exit(0)

    root = _find_project_root(Path(cwd).resolve())
    live = root / _REL
    vault = _vault(root)
    existing = _snapshots(vault)

    if not live.is_file():
        if existing:
            print(
                f"settings.local.json is MISSING. Newest snapshot: {existing[-1]}\n"
                f"  restore: cp '{existing[-1]}' '{live}'",
                file=sys.stderr,
            )
        sys.exit(0)

    try:
        if existing and _digest(existing[-1]) == _digest(live):
            sys.exit(0)
        vault.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        shutil.copy2(live, vault / f"settings.local.{stamp}.json")
        _prune(vault)
    except OSError as exc:
        print(f"settings.local.json backup skipped: {exc}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
