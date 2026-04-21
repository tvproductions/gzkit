#!/usr/bin/env python3
"""Post-Edit Ruff Hook.

PostToolUse hook that runs ruff check (lint-only, no fix) on edited
Python files immediately after each Write/Edit operation.

Reports lint issues without modifying files — avoids the import-removal
problem where --fix deletes an import before the next Edit adds usage
(GHI #239). On non-zero exit, the first N lines of ruff output are
written to stderr so the agent sees the warning in the same turn and
can correct course before the import colocation window closes.

Exit codes:
  0 - Always (non-blocking; lint failures do not prevent edits)
"""

import json
import subprocess
import sys
from contextlib import suppress
from pathlib import Path

TIMEOUT_SECONDS = 8
MAX_OUTPUT_LINES = 20


def main():
    """Run ruff on the edited file if it is a Python file."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path.endswith(".py"):
        sys.exit(0)

    cwd = input_data.get("cwd", "")
    try:
        target = Path(file_path)
        if not target.is_absolute() and cwd:
            target = Path(cwd) / target
        target = target.resolve()
    except (ValueError, TypeError, OSError):
        sys.exit(0)

    if not target.is_file():
        sys.exit(0)

    posix_path = target.as_posix()

    with suppress(FileNotFoundError, subprocess.TimeoutExpired, OSError):
        result = subprocess.run(
            ["uv", "run", "ruff", "check", posix_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=TIMEOUT_SECONDS,
        )
        if result.returncode != 0:
            combined = (result.stdout or "") + (result.stderr or "")
            lines = combined.splitlines()[:MAX_OUTPUT_LINES]
            if lines:
                sys.stderr.write(f"post-edit-ruff: lint findings on {target.name}\n")
                sys.stderr.write("\n".join(lines) + "\n")

    sys.exit(0)


if __name__ == "__main__":
    main()
