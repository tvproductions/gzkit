#!/usr/bin/env python3
"""Session-Exit Bookmark Hook (GHI #756).

SessionEnd hook. Writes a CHECKPOINT handoff recording where the
session stopped, so continuity does not depend on an agent
remembering to author one — the trigger ADR-0.0.65 never specified.

Books, never refuses (operator ruling: "DO NOT BLOCK HERE ... write
them all to the handoff bookmark, and leave"). Runs synchronously so
the write completes before the process exits; `async` is unsupported
on the Codex side and unverified here.

Thin adapter only: the decision is `gzkit.session_exit.book_exit_bookmark`.

Exit codes:
  0 - always (SessionEnd cannot block; there is no verdict to report)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def _find_project_root(start: Path) -> Path:
    current = start
    while current != current.parent:
        if (current / ".gzkit").is_dir():
            return current
        current = current.parent
    return start


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        sys.exit(0)

    cwd = payload.get("cwd") or ""
    if not cwd:
        sys.exit(0)

    try:
        from gzkit.session_exit import book_exit_bookmark
    except ImportError:
        # gzkit unavailable is a plumbing failure, not a governance
        # signal. Nothing to book and nowhere to report it.
        sys.exit(0)

    root = _find_project_root(Path(cwd).resolve())
    book_exit_bookmark(
        root,
        session_id=str(payload.get("session_id") or ""),
        exit_reason=str(payload.get("reason") or "unknown"),
        transcript_path=payload.get("transcript_path") or None,
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
