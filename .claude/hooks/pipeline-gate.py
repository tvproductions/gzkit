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

from gzkit.pipeline_runtime import (
    PIPELINE_LEGACY_MARKER,
    PIPELINE_RECEIPT_FILE,
    _load_pipeline_json,
    _pipeline_plans_dir,
    pipeline_gate_block_message,
)


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


def marker_matches(marker_path: Path, obpi_id: str) -> bool:
    """Return whether a marker exists and matches the target OBPI."""
    if not marker_path.exists():
        return False
    marker = _load_pipeline_json(marker_path)
    return bool(marker and marker.get("obpi_id") == obpi_id)


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

    cwd_path = Path(input_data.get("cwd", os.getcwd())).resolve()
    plans_dir = _pipeline_plans_dir(cwd_path)
    receipt = _load_pipeline_json(plans_dir / PIPELINE_RECEIPT_FILE)
    if not receipt:
        sys.exit(0)

    obpi_id = receipt.get("obpi_id", "")
    verdict = receipt.get("verdict", "")
    if not obpi_id or verdict != "PASS":
        sys.exit(0)

    obpi_marker = plans_dir / f".pipeline-active-{obpi_id}.json"
    if marker_matches(obpi_marker, obpi_id):
        sys.exit(0)

    legacy_marker = plans_dir / PIPELINE_LEGACY_MARKER
    if marker_matches(legacy_marker, obpi_id):
        sys.exit(0)

    print(pipeline_gate_block_message(obpi_id), file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()

