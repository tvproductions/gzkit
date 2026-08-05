#!/usr/bin/env python3
"""Session-Start Handoff Advisement Hook (GHI #757).

SessionStart hook. Surfaces the newest handoff and its advised steps
so the review happens without the operator retyping the request each
session.

Binds by SEEDING the turn, never by refusing tool calls — the entry
edge already blocks hard, and the advisement's problem was that it
was skippable, not that it was unguarded. A handoff ADVISES; this
hook never authorizes, and says so in the text it injects.

Dual-channel: `additionalContext` is passive and universal (Codex
has only this); `initialUserMessage` seeds a real first turn and is
a Claude-side upgrade, never a correctness dependency.

Thin adapter only: the decision is `gzkit.session_start.build_advisement`.

Exit codes:
  0 - always (advisement never blocks)
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
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
        from gzkit.session_start import build_advisement
    except ImportError:
        sys.exit(0)

    root = _find_project_root(Path(cwd).resolve())
    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    advisement = build_advisement(root, now=now)
    if not advisement.present:
        sys.exit(0)

    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": advisement.text,
                },
                "initialUserMessage": advisement.text,
            }
        )
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
