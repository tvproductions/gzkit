#!/usr/bin/env python3
"""Dispatch Stamp Hook (RP-12 rulings 17, 34 and 35).

PreToolUse hook on Bash. On a subagent's call (the payload carries
`agent_id`) whose command names `gz` or `gzkit`, reads the subagent's
dispatch line from its own transcript, the root that dispatch intends
from the ledger, and rewrites the command through `updatedInput` to
carry both in its environment, with no permission decision. `gz` then
refuses the call before any write unless it runs in that root. Every
other call passes untouched; the main session's carry no `agent_id`.

Thin adapter only: the decision is
`gzkit.dispatch_stamp.stamp_hook_output`.

Exit codes:
  0 - Always; the rewrite, when there is one, is on stdout
"""

import json
import os
import sys
from pathlib import Path

STAMP_ROOT_ENV = "GZKIT_DISPATCH_ROOT"
STAMP_ID_ENV = "GZKIT_DISPATCH_ID"


def _no_root(payload: dict) -> dict | None:
    """Stamp no root on any subagent Bash call that mentions gz at all.

    Returns:
        The rewrite, or None for a call it leaves alone.

    """
    tool_input = payload.get("tool_input")
    if payload.get("tool_name") != "Bash" or not payload.get("agent_id"):
        return None
    if not isinstance(tool_input, dict):
        return None
    command = tool_input.get("command")
    if not isinstance(command, str) or "gz" not in command:
        return None
    prefix = f"export {STAMP_ROOT_ENV}='' {STAMP_ID_ENV}=''; "
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "updatedInput": {**tool_input, "command": prefix + command},
        }
    }


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError, OSError:
        sys.exit(0)  # no payload, no command to stamp
    if not isinstance(payload, dict):
        sys.exit(0)

    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or ".")
    try:
        from gzkit.dispatch_stamp import stamp_hook_output  # noqa: PLC0415

        output = stamp_hook_output(payload, root)
    except Exception:  # fail closed: stamp no root
        output = _no_root(payload)

    if output is not None:
        sys.stdout.write(json.dumps(output) + "\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
