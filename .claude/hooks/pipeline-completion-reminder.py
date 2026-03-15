#!/usr/bin/env python3
"""Pipeline Completion Reminder Hook.

PreToolUse hook on Bash that emits a non-blocking reminder before
`git commit` or `git push` when an OBPI pipeline is still active
and the corresponding brief has not been completed.

Exit codes:
  0 - Always (advisory only)
"""

import json
import os
import sys
from pathlib import Path

from gzkit.pipeline_runtime import (
    PIPELINE_LEGACY_MARKER,
    _load_pipeline_json,
    _pipeline_plans_dir,
    pipeline_completion_reminder_message,
    pipeline_stale_marker_message,
)


def find_active_marker(plans_dir: Path) -> dict | None:
    """Return the first readable active pipeline marker payload."""
    marker_paths = sorted(plans_dir.glob(".pipeline-active-*.json"))
    marker_paths.append(plans_dir / PIPELINE_LEGACY_MARKER)

    for marker_path in marker_paths:
        if not marker_path.exists():
            continue
        marker = _load_pipeline_json(marker_path)
        if marker is not None:
            return marker
        return None
    return None


def find_brief_path(docs_root: Path, obpi_id: str) -> Path | None:
    """Find the OBPI brief that corresponds to the active marker."""
    if not docs_root.is_dir():
        return None

    pattern = f"{obpi_id}*.md"
    matches = sorted(docs_root.rglob(pattern))
    return matches[0] if matches else None


def brief_status(brief_path: Path) -> str | None:
    """Extract the brief status from a brief file."""
    try:
        lines = brief_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("status:"):
            return stripped.split(":", 1)[1].strip()
        if stripped.startswith("**Status:**"):
            return stripped.split("**Status:**", 1)[1].strip()
        if stripped.startswith("**Brief Status:**"):
            return stripped.split("**Brief Status:**", 1)[1].strip()
    return None


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

    cwd_path = Path(input_data.get("cwd", os.getcwd())).resolve()
    plans_dir = _pipeline_plans_dir(cwd_path)
    if not plans_dir.is_dir():
        sys.exit(0)

    marker = find_active_marker(plans_dir)
    if not marker:
        sys.exit(0)

    obpi_id = marker.get("obpi_id", "")
    if not obpi_id:
        sys.exit(0)

    brief_path = find_brief_path(cwd_path / "docs" / "design" / "adr", obpi_id)
    if brief_path is None:
        sys.exit(0)

    status = brief_status(brief_path)
    if status == "Completed":
        print(pipeline_stale_marker_message(obpi_id), file=sys.stderr)
        sys.exit(0)

    print(
        pipeline_completion_reminder_message(
            obpi_id,
            status=status,
            next_command=marker.get("next_command"),
        ),
        file=sys.stderr,
    )
    sys.exit(0)


if __name__ == "__main__":
    main()

