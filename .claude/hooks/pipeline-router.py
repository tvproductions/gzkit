#!/usr/bin/env python3
"""Pipeline Router Hook.

PostToolUse hook on ExitPlanMode that routes the agent into the
canonical OBPI pipeline runtime after plan approval for OBPI work.

How it works:
  1. Reads `.claude/plans/.plan-audit-receipt.json`
  2. If the receipt exists, names an OBPI, and has verdict `PASS`,
     emit a routing instruction on stdout directing the agent to
     invoke `uv run gz obpi pipeline`
  3. If the receipt is absent, invalid, or not `PASS`, exit silently

Exit codes:
  0 - Always (PostToolUse hooks should not block)
"""

import json
import os
import sys
from pathlib import Path

from gzkit.pipeline_runtime import (
    PIPELINE_RECEIPT_FILE,
    _load_pipeline_json,
    _pipeline_plans_dir,
    pipeline_router_message,
)


def main() -> None:
    """Route approved OBPI plans into the pipeline."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    cwd = input_data.get("cwd", os.getcwd())
    receipt_path = _pipeline_plans_dir(Path(cwd)) / PIPELINE_RECEIPT_FILE
    if not receipt_path.exists():
        sys.exit(0)

    receipt = _load_pipeline_json(receipt_path)
    if receipt is None:
        sys.exit(0)

    obpi_id = receipt.get("obpi_id", "")
    verdict = receipt.get("verdict", "")
    if not obpi_id or verdict != "PASS":
        sys.exit(0)

    print(pipeline_router_message(obpi_id))
    sys.exit(0)


if __name__ == "__main__":
    main()

