#!/usr/bin/env python3
"""gzkit ledger writer hook for claude.

This hook records governance artifact edits in the ledger.
"""

import json
import os
import sys
from pathlib import Path


def find_project_root() -> Path:
    """Find the project root by looking for .gzkit directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".gzkit").is_dir():
            return current
        current = current.parent
    return Path.cwd()


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
        rel_path = Path(file_path).relative_to(project_root)
    except ValueError:
        return 0

    # Import gzkit and record edit
    sys.path.insert(0, str(project_root / "src"))
    try:
        from gzkit.hooks.core import record_artifact_edit

        session = os.environ.get("CLAUDE_SESSION_ID") or os.environ.get("COPILOT_SESSION_ID")
        record_artifact_edit(project_root, str(rel_path), session)
    except ImportError:
        pass  # gzkit not installed, skip

    return 0


if __name__ == "__main__":
    sys.exit(main())
