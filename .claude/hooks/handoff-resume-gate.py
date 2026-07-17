#!/usr/bin/env python3
"""Handoff Resume Gate Hook (GHI #574).

PreToolUse hook on Write|Edit|NotebookEdit|Bash. Refuses execution while
this session has resumed a handoff the operator has not yet ruled on —
the mechanical form of `gz-session-handoff` SKILL.md § RESUME's universal
Operator Authorization Gate ("no file mutation / gz ceremony / migration
until the operator rules"), which was prose plus a banner until now.

Thin adapter only: the decision is `gzkit.handoff_resume_gate.decide`.

Exit codes:
  0 - Allow operation
  2 - Block operation (no operator authorization booked for this session)
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
        from gzkit.handoff_resume_gate import decide
    except ImportError:
        # Fail-open: gzkit unavailable is a plumbing failure, not a
        # governance signal. The gate's evidence read fails CLOSED
        # where it matters (see is_resume_authorized).
        sys.exit(0)

    root = _find_project_root(Path(cwd).resolve())
    verdict = decide(
        root,
        session_id=str(payload.get("session_id") or ""),
        tool_name=str(payload.get("tool_name") or ""),
        tool_input=payload.get("tool_input") or {},
    )
    if verdict.blocked:
        print(verdict.reason, file=sys.stderr)
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
