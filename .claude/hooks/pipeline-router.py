#!/usr/bin/env python3
"""Pipeline Router Hook.

PostToolUse hook on ExitPlanMode that routes the agent to
`/gz-obpi-pipeline` after plan approval for OBPI work.

How it works:
  1. Reads `.claude/plans/.plan-audit-receipt.json`
  2. If the receipt exists, names an OBPI, and has verdict `PASS`,
     emit a routing instruction on stdout directing the agent to
     invoke `/gz-obpi-pipeline`
  3. If the receipt is absent, invalid, or not `PASS`, exit silently

Exit codes:
  0 - Always (PostToolUse hooks should not block)
"""

import json
import os
import sys
from pathlib import Path

RECEIPT_FILE = ".plan-audit-receipt.json"


def main() -> None:
    """Route approved OBPI plans into the pipeline."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    cwd = input_data.get("cwd", os.getcwd())
    receipt_path = Path(cwd) / ".claude" / "plans" / RECEIPT_FILE
    if not receipt_path.exists():
        sys.exit(0)

    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        sys.exit(0)

    obpi_id = receipt.get("obpi_id", "")
    verdict = receipt.get("verdict", "")
    if not obpi_id or verdict != "PASS":
        sys.exit(0)

    print(
        f"OBPI plan approved: {obpi_id}\n"
        f"\n"
        f"REQUIRED: Execute the approved plan via the governance pipeline:\n"
        f"  /gz-obpi-pipeline {obpi_id}\n"
        f"\n"
        f"Do NOT implement directly; the pipeline preserves the required\n"
        f"verification, acceptance ceremony, and sync stages.\n"
        f"\n"
        f"If implementation is already done, use --from=verify or --from=ceremony."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
