#!/usr/bin/env python3
"""gzkit ledger writer and validator hook for copilot.

This hook records governance artifact edits and enforces completion gates.

COVERAGE LIMIT (GHI #847): this hook binds Edit|Write and keys on
tool_input.file_path, a field a Bash payload does not carry. A governance
artifact written by sed, a heredoc, inline python, git apply, or an editor
outside the session emits nothing here. That channel is recorded instead by
the commit-locus backstop -- gzkit.hooks.commit_ledger, wired as the
post-commit hook in .pre-commit-config.yaml -- which fires only for a path
this hook did not already record. A write that is never committed stays
invisible to both.
"""

import json
import os
import sys
from pathlib import Path


def find_project_root() -> Path:
    """Find the project root by looking for .gzkit directory.

    Resolved, because callers compare it against a resolved target path.
    On Windows an 8.3 short-name cwd and its resolved long form share no
    prefix, so relative_to() raises and the caller silently loses the path.
    """
    current = Path.cwd().resolve()
    while current != current.parent:
        if (current / ".gzkit").is_dir():
            return current
        current = current.parent
    return Path.cwd().resolve()


def main() -> int:
    """Main hook entry point."""
    # Read tool use info from stdin (Claude Code format)
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0  # Silently continue if no valid input

    # Extract file path from tool use
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    if tool_name not in ("Edit", "Write"):
        return 0

    file_path = tool_input.get("file_path", "")
    if not file_path:
        return 0

    # Make path relative to project root
    project_root = find_project_root()
    try:
        rel_path = Path(file_path).resolve().relative_to(project_root)
    except (ValueError, OSError):
        return 0

    # Import gzkit and record edit/validate
    sys.path.insert(0, str(project_root / "src"))
    try:
        from gzkit.hooks.core import record_artifact_edit

        session = os.environ.get("CLAUDE_SESSION_ID") or os.environ.get("COPILOT_SESSION_ID")

        # This will trigger validation and raise if it fails
        record_artifact_edit(project_root, str(rel_path), session)

    except ImportError:
        pass  # gzkit not installed, skip
    except Exception as exc:
        print(f"\n[GOVERNANCE BLOCK] {exc}\n", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
