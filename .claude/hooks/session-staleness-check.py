#!/usr/bin/env python3
"""Session Staleness Check Hook (gzkit adaptation).

PreToolUse hook on Write|Edit that detects stale pipeline artifacts
left from previous sessions and emits warnings so the agent can
clean up before hitting gate blocks.

Adapted from airlineops canonical session-staleness-check.py.
Uses gzkit's OBPI path structure (design/adr/.../obpis/) instead of
airlineops briefs layout.

Checks for:
  1. .pipeline-active.json referencing a completed OBPI
  2. .plan-audit-receipt.json referencing a completed OBPI

Non-blocking — emits warnings only (exit 0 always).
"""

import json
import sys
from pathlib import Path


def _read_json(path: Path) -> dict | None:
    """Read a JSON file, returning None on any error."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_bytes())
    except (json.JSONDecodeError, OSError):
        return None


def _brief_is_completed(cwd: Path, obpi_id: str) -> bool:
    """Check if the referenced OBPI brief has status Completed.

    gzkit stores briefs under design/adr/pre-release/ADR-X.Y.Z-.../obpis/OBPI-*.md
    """
    # Extract numeric prefix (e.g., OBPI-0.14.0-02-... -> 0.14.0)
    stripped = obpi_id.replace("OBPI-", "")
    parts = stripped.rsplit("-", 1)
    if len(parts) < 2:
        return False

    # Search design/adr for matching OBPI files
    adr_root = cwd / "docs" / "design" / "adr"
    if not adr_root.exists():
        return False

    # gzkit uses pre-release/ADR-X.Y.Z-.../obpis/ structure
    for brief_path in adr_root.rglob(f"OBPI-{stripped}*.md"):
        try:
            text = brief_path.read_text(encoding="utf-8")
            for line in text.splitlines()[:15]:
                if "Status:" in line and "Completed" in line:
                    return True
        except OSError:
            continue

    return False


def main():
    """Check for stale pipeline artifacts and warn."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    cwd = input_data.get("cwd", "")
    if not cwd:
        sys.exit(0)

    cwd_path = Path(cwd).resolve()
    plans_dir = cwd_path / ".claude" / "plans"

    marker_path = plans_dir / ".pipeline-active.json"
    receipt_path = plans_dir / ".plan-audit-receipt.json"

    marker = _read_json(marker_path)
    receipt = _read_json(receipt_path)

    warnings = []

    if marker:
        obpi_id = marker.get("obpi_id", "")
        if obpi_id and _brief_is_completed(cwd_path, obpi_id):
            warnings.append(
                f"Stale .pipeline-active.json: references {obpi_id} "
                f"which is already Completed. "
                f"Clean up: delete {marker_path.relative_to(cwd_path)}"
            )

    if receipt:
        obpi_id = receipt.get("obpi_id", "")
        if obpi_id and _brief_is_completed(cwd_path, obpi_id):
            warnings.append(
                f"Stale .plan-audit-receipt.json: references {obpi_id} "
                f"which is already Completed. "
                f"Clean up: delete {receipt_path.relative_to(cwd_path)}"
            )

    if warnings:
        print(
            "SESSION STALENESS WARNING\n"
            + "\n".join(f"  - {w}" for w in warnings)
            + "\n\nClean up stale artifacts to avoid gate blocks.",
            file=sys.stderr,
        )

    # Always non-blocking
    sys.exit(0)


if __name__ == "__main__":
    main()
