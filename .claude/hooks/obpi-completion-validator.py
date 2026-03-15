#!/usr/bin/env python3
"""OBPI Completion Validator Hook (gzkit adaptation).

PreToolUse hook that gates OBPI brief completion by checking ledger evidence
before allowing status changes to 'Completed'.

Adapted from airlineops canonical obpi-completion-validator.py.
Uses gzkit's ledger and lane resolution rather than standalone logic.

Adaptations from canonical:
  - Path check: /obpis/OBPI- (gzkit) instead of /briefs/OBPI- (airlineops)
  - Ledger: .gzkit/ledger.jsonl (project-wide) instead of adr_dir/logs/obpi-audit.jsonl
  - Evidence event: 'obpi_receipt_emitted' instead of 'obpi-audit'/'obpi-completion'
  - Lane resolution: resolve_adr_lane() from ledger events instead of ADR markdown parsing

Exit codes:
  0 - Allow operation
  2 - Block operation (evidence missing or attestation required)
"""

import json
import re
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


def check_status_change_to_completed(new_string: str) -> bool:
    """Check if the edit changes status to Completed."""
    status_patterns = [
        r"\*\*(?:Brief\s+)?Status:\*\*\s*Completed",
        r"^(?:Brief\s+)?Status:\s*Completed",
        r"^\|\s*(?:Brief\s+)?Status\s*\|\s*Completed\s*\|",
    ]
    return any(
        re.search(pattern, new_string, re.MULTILINE | re.IGNORECASE) for pattern in status_patterns
    )


def extract_obpi_id(file_path: str) -> str | None:
    """Extract full OBPI ID (slug) from file path.

    The ledger stores full slugs like 'OBPI-0.9.0-02-compatibility-adaptation-blocking-hooks',
    so we extract the filename stem rather than just the numeric prefix.
    """
    path = Path(file_path)
    stem = path.stem  # e.g. OBPI-0.9.0-02-compatibility-adaptation-blocking-hooks
    if re.match(r"OBPI-[\d.]+-\d+", stem):
        return stem
    return None


def extract_adr_id(obpi_id: str) -> str | None:
    """Extract parent ADR ID from OBPI ID.

    e.g. OBPI-0.9.0-02-compatibility-adaptation-blocking-hooks -> ADR-0.9.0
    """
    match = re.match(r"OBPI-([\d.]+)-\d+", obpi_id)
    return f"ADR-{match.group(1)}" if match else None


def is_foundation_adr(adr_id: str) -> bool:
    """Check if ADR is foundation series (0.0.x)."""
    return adr_id.startswith("ADR-0.0.")


def has_receipt_evidence(ledger_events: list, obpi_id: str) -> bool:
    """Check if a completion receipt exists in the ledger for this OBPI.

    Matches both exact ID and prefix (short ID like OBPI-0.9.0-02 matches
    full slug OBPI-0.9.0-02-compatibility-adaptation-blocking-hooks).
    """
    for event in ledger_events:
        data = event if isinstance(event, dict) else event.to_dict()
        if data.get("event") != "obpi_receipt_emitted":
            continue
        event_id = data.get("id", "")
        if event_id == obpi_id or obpi_id == event_id:
            return True
    return False


def has_human_attestation(ledger_events: list, obpi_id: str) -> bool:
    """Check if human attestation exists in the ledger for this OBPI."""
    for event in ledger_events:
        data = event if isinstance(event, dict) else event.to_dict()
        if data.get("id") != obpi_id:
            continue
        if data.get("event") == "obpi_receipt_emitted":
            attestor = data.get("attestor", "")
            if attestor.startswith("human:"):
                return True
        if data.get("event") == "human_attestation":
            return True
    return False


def main():
    """Validate and gate OBPI completion."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    new_string = tool_input.get("new_string", "") or tool_input.get("content", "")

    # Normalize path
    try:
        project_root = find_project_root()
        abs_path = Path(file_path).resolve()
        rel_path = abs_path.relative_to(project_root)
        rel_str = rel_path.as_posix()
    except (ValueError, TypeError):
        sys.exit(0)

    # 1. Is this an OBPI brief file? (gzkit uses /obpis/ not /briefs/)
    if "/obpis/OBPI-" not in rel_str or not rel_str.endswith(".md"):
        sys.exit(0)

    # 2. Is this changing status to Completed?
    if not check_status_change_to_completed(new_string):
        sys.exit(0)

    # 3. Extract identifiers
    obpi_id = extract_obpi_id(rel_str)
    if not obpi_id:
        sys.exit(0)

    adr_id = extract_adr_id(obpi_id)
    if not adr_id:
        sys.exit(0)

    # 4. Load gzkit ledger
    sys.path.insert(0, str(project_root / "src"))
    try:
        from gzkit.config import GzkitConfig
        from gzkit.ledger import Ledger, resolve_adr_lane
        from gzkit.pipeline_runtime import completion_receipt_missing_message

        config = GzkitConfig.load(project_root / ".gzkit.json")
        ledger = Ledger(project_root / config.paths.ledger)
        events = ledger.read_all()
    except (ImportError, Exception) as exc:
        # If gzkit is not importable, allow the operation (fail-open for import errors)
        print(f"Warning: Could not load gzkit ledger: {exc}", file=sys.stderr)
        sys.exit(0)

    # 5. Check for receipt evidence in ledger
    if not has_receipt_evidence(events, obpi_id):
        print(completion_receipt_missing_message(obpi_id), file=sys.stderr)
        sys.exit(2)

    # 6. Check lane for attestation requirements
    is_foundation = is_foundation_adr(adr_id)

    graph = ledger.get_artifact_graph()
    canonical_adr = ledger.canonicalize_id(adr_id)
    parent_info = graph.get(canonical_adr, {})
    parent_lane = resolve_adr_lane(parent_info, config.mode)

    requires_human = is_foundation or parent_lane == "heavy"

    if requires_human and not has_human_attestation(events, obpi_id):
        lane_reason = "Foundation (0.0.x)" if is_foundation else "Heavy lane"
        print(
            f"\n\u26d4 BLOCKED: {obpi_id} requires human attestation.\n"
            f"\n"
            f"Parent {adr_id} is {lane_reason}.\n"
            f"Per AGENTS.md, OBPIs under Heavy/Foundation ADRs inherit attestation rigor.\n"
            f"\n"
            f"REQUIRED: Present evidence and receive human attestation:\n"
            f"  1. Show verification command outputs and test results\n"
            f"  2. Wait for human to respond 'attested' or 'approved'\n"
            f"  3. Record attestation in ledger, then complete\n",
            file=sys.stderr,
        )
        sys.exit(2)

    # All validations passed
    sys.exit(0)


if __name__ == "__main__":
    main()
