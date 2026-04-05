#!/usr/bin/env python3
"""Pipeline Gate Hook.

PreToolUse hook on Write|Edit that blocks implementation file writes
under `src/` and `tests/` when an OBPI plan-audit receipt exists but
the governance pipeline has not been activated.

Exit codes:
  0 - Allow operation
  2 - Block operation (pipeline not invoked)
"""

import json
import os
import sys
from pathlib import Path


def resolve_repo_path(cwd: str, file_path: str) -> str | None:
    """Resolve a tool file path into a repo-relative POSIX path."""
    if not cwd or not file_path:
        return None

    try:
        cwd_path = Path(cwd).resolve()
        target = Path(file_path)
        if not target.is_absolute():
            target = cwd_path / target
        rel_path = target.resolve().relative_to(cwd_path)
    except (OSError, TypeError, ValueError):
        return None

    return rel_path.as_posix()


def find_project_root(start: Path) -> Path:
    """Find the project root by looking for .gzkit or src/gzkit."""
    current = start
    while current != current.parent:
        if (current / ".gzkit").is_dir() or (current / "src" / "gzkit").is_dir():
            return current
        current = current.parent
    return start


def main() -> None:
    """Gate implementation writes until the pipeline is active."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    rel_path = resolve_repo_path(
        input_data.get("cwd", os.getcwd()),
        tool_input.get("file_path", ""),
    )
    if rel_path is None or not rel_path.startswith(("src/", "tests/")):
        sys.exit(0)

    project_root = find_project_root(Path(input_data.get("cwd", os.getcwd())).resolve())
    sys.path.insert(0, str(project_root / "src"))

    try:
        from gzkit.pipeline_runtime import (
            load_plan_audit_receipt,
            marker_matches,
            pipeline_gate_message,
            pipeline_marker_paths,
            pipeline_plans_dir,
        )
    except Exception:
        sys.exit(0)

    plans_dir = pipeline_plans_dir(project_root)
    receipt_path = plans_dir / ".plan-audit-receipt.json"
    if not receipt_path.exists():
        sys.exit(0)

    receipt_state, _warnings, receipt = load_plan_audit_receipt(plans_dir, "")
    if receipt is None or receipt_state != "pass":
        sys.exit(0)

    obpi_id = str(receipt.get("obpi_id") or "")
    if not obpi_id:
        sys.exit(0)

    obpi_marker, legacy_marker = pipeline_marker_paths(plans_dir, obpi_id)
    if marker_matches(obpi_marker, obpi_id):
        sys.exit(0)

    if marker_matches(legacy_marker, obpi_id):
        sys.exit(0)

    print(pipeline_gate_message(obpi_id), file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()

