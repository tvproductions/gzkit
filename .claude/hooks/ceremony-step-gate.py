#!/usr/bin/env python3
"""Ceremony Step Gate Hook.

PreToolUse hook on Bash that blocks ``gz closeout --ceremony --next``
from being called twice in the same agent turn.  Uses a two-file
protocol: the CLI writes a turn-lock with ``presented_step``, and
this hook maintains a ``last_allowed_step`` counter.  When both match,
the step was already presented this turn and the agent must wait.

Exit codes:
  0 - Allow operation
  2 - Block (step already presented, wait for human)
"""

import json
import os
import re
import sys
from pathlib import Path


def find_project_root(start: Path) -> Path:
    current = start
    while current != current.parent:
        if (current / ".gzkit").is_dir() or (current / "src" / "gzkit").is_dir():
            return current
        current = current.parent
    return start


def main() -> None:
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    # Only gate ceremony --next commands
    if not re.search(r"gz\s+closeout\b.*--ceremony\b.*--next\b", command) and not re.search(
        r"gz\s+closeout\b.*--next\b.*--ceremony\b", command
    ):
        sys.exit(0)

    # Extract ADR ID from command
    adr_match = re.search(r"(ADR-[\d.]+(?:-[\w-]+)?)", command)
    if not adr_match:
        sys.exit(0)
    adr_id = adr_match.group(1)

    project_root = find_project_root(Path(input_data.get("cwd", os.getcwd())).resolve())
    ceremonies_dir = project_root / ".gzkit" / "ceremonies"

    lock_path = ceremonies_dir / f"{adr_id}.turn-lock"
    hook_state_path = ceremonies_dir / f"{adr_id}.hook-state.json"

    if not lock_path.exists():
        sys.exit(0)

    try:
        lock_data = json.loads(lock_path.read_text(encoding="utf-8"))
        presented_step = lock_data.get("presented_step")
    except (json.JSONDecodeError, OSError):
        sys.exit(0)

    last_allowed = None
    if hook_state_path.exists():
        try:
            hook_data = json.loads(hook_state_path.read_text(encoding="utf-8"))
            last_allowed = hook_data.get("last_allowed_step")
        except (json.JSONDecodeError, OSError):
            pass

    if presented_step == last_allowed:
        # Step was already presented and allowed this turn — block
        print(
            f"Ceremony step {presented_step} already presented. "
            "Wait for human acknowledgment before calling --next again.",
            file=sys.stderr,
        )
        sys.exit(2)

    # Allow and record
    ceremonies_dir.mkdir(parents=True, exist_ok=True)
    hook_state_path.write_text(
        json.dumps({"last_allowed_step": presented_step}) + "\n",
        encoding="utf-8",
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
