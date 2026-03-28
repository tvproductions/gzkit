#!/usr/bin/env python3
"""Pipeline Router Hook.

PostToolUse hook on ExitPlanMode that routes the agent to
`uv run gz obpi pipeline` after plan approval for OBPI work.

How it works:
  1. Reads `.claude/plans/.plan-audit-receipt.json`
  2. If the receipt exists, names an OBPI, and has verdict `PASS`,
     emit a routing instruction on stdout directing the agent to
     invoke the canonical runtime command
  3. If the receipt is absent, invalid, or not `PASS`, exit silently

Exit codes:
  0 - Always (PostToolUse hooks should not block)
"""

import json
import os
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
    """Route approved OBPI plans into the pipeline."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    project_root = find_project_root(Path(input_data.get("cwd", os.getcwd())).resolve())
    sys.path.insert(0, str(project_root / "src"))

    try:
        from gzkit.pipeline_runtime import (
            load_plan_audit_receipt,
            pipeline_plans_dir,
            pipeline_router_message,
        )
    except ImportError:
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

    print(pipeline_router_message(obpi_id))
    sys.exit(0)


if __name__ == "__main__":
    main()
