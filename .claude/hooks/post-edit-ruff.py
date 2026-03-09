#!/usr/bin/env python3
"""Post-Edit Ruff Hook.

PostToolUse hook that runs ruff check --fix and ruff format on edited
Python files immediately after each Write/Edit operation.

Shifts lint enforcement left: from pre-commit (batch) to post-edit
(immediate), eliminating the "fix lint at the end" friction pattern.

Exit codes:
  0 - Always (non-blocking; lint failures do not prevent edits)
"""

import json
import subprocess
import sys
from contextlib import suppress
from pathlib import Path

TIMEOUT_SECONDS = 8


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
        subprocess.run(
            ["uv", "run", "ruff", "check", "--fix", "--quiet", posix_path],
            capture_output=True,
            timeout=TIMEOUT_SECONDS,
        )

    with suppress(FileNotFoundError, subprocess.TimeoutExpired, OSError):
        subprocess.run(
            ["uv", "run", "ruff", "format", "--quiet", posix_path],
            capture_output=True,
            timeout=TIMEOUT_SECONDS,
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
