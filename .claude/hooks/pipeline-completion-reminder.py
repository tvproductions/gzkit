#!/usr/bin/env python3
"""Pipeline Completion Reminder Hook.

PreToolUse hook on Bash that emits a non-blocking reminder before
`git commit` or `git push` when an OBPI pipeline is still active
and the corresponding brief has not been completed.

Exit codes:
  0 - Always (advisory only)
"""

import json
import sys
from pathlib import Path


def find_project_root(start: Path) -> Path:
    """Find the project root by looking for .gzkit or src/gzkit."""
    current = start
    while current != current.parent:
        if (current / ".gzkit").is_dir() or (current / "src" / "gzkit").is_dir():
            return current
        current = current.parent
    return start


def main() -> None:
    """Emit a reminder before commit/push when the pipeline is incomplete."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")
    if not any(git_cmd in command for git_cmd in ("git commit", "git push")):
        sys.exit(0)

    project_root = find_project_root(Path(input_data.get("cwd", str(Path.cwd()))).resolve())
    sys.path.insert(0, str(project_root / "src"))

    try:
        from gzkit.pipeline_runtime import (
            extract_brief_status,
            find_active_pipeline_marker,
            find_obpi_brief,
            pipeline_completion_reminder_message,
            pipeline_plans_dir,
        )
    except ImportError:
        sys.exit(0)

    plans_dir = pipeline_plans_dir(project_root)
    if not plans_dir.is_dir():
        sys.exit(0)

    marker = find_active_pipeline_marker(plans_dir)
    if not marker:
        sys.exit(0)

    obpi_id = marker.get("obpi_id", "")
    if not obpi_id:
        sys.exit(0)

    brief_path = find_obpi_brief(project_root / "docs" / "design" / "adr", obpi_id)
    if brief_path is None:
        sys.exit(0)

    message = pipeline_completion_reminder_message(
        marker,
        brief_status=extract_brief_status(brief_path),
    )
    if not message:
        sys.exit(0)

    print(message, file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
