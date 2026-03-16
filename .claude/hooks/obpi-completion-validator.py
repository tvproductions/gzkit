#!/usr/bin/env python3
"""OBPI Completion Validator Hook.

PreToolUse hook that gates OBPI brief completion by checking ledger evidence
before allowing status changes to 'Completed'.

Aligned with airlineops canonical obpi-completion-validator.py.
Uses ADR-local audit ledger ({adr-dir}/logs/obpi-audit.jsonl) as evidence source.

Adaptations from canonical:
  - Path check: /obpis/OBPI- (gzkit) instead of /briefs/OBPI- (airlineops)
  - Lane resolution: checks both ADR markdown and frontmatter for Heavy lane

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


def find_parent_adr_dir(brief_path: Path) -> Path | None:
    """Find the parent ADR directory from a brief path.

    gzkit stores briefs in /obpis/ (airlineops uses /briefs/).
    """
    parent_dir = brief_path.parent
    if parent_dir.name not in ("obpis", "briefs"):
        return None
    return parent_dir.parent


def find_parent_adr_file(adr_dir: Path) -> Path | None:
    """Find the parent ADR markdown file."""
    for f in adr_dir.iterdir():
        if (
            f.name.startswith("ADR-")
            and f.name.endswith(".md")
            and re.match(r"ADR-[\d.]+-", f.name)
        ):
            return f
    return None


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
    """Extract OBPI short ID (e.g. OBPI-0.14.0-04) from file path."""
    match = re.search(r"(OBPI-[\d.]+-\d+)", file_path)
    return match.group(1) if match else None


def extract_adr_id(obpi_id: str) -> str | None:
    """Extract parent ADR ID from OBPI ID.

    e.g. OBPI-0.14.0-04 -> ADR-0.14.0
    """
    match = re.match(r"OBPI-([\d.]+)-\d+", obpi_id)
    return f"ADR-{match.group(1)}" if match else None


def is_foundation_adr(adr_id: str) -> bool:
    """Check if ADR is foundation series (0.0.x)."""
    return adr_id.startswith("ADR-0.0.")


def get_parent_adr_lane(adr_file: Path | None) -> str:
    """Determine parent ADR's lane (Heavy or Lite)."""
    if adr_file is None:
        return "unknown"
    try:
        content = adr_file.read_text(encoding="utf-8")
    except OSError:
        return "unknown"

    heavy_patterns = [
        r"##\s*Lane[\s\S]{0,50}Heavy",
        r"\*\*Lane:\*\*\s*Heavy",
        r"Lane:\s*Heavy",
        r"\|\s*Lane\s*\|\s*Heavy\s*\|",
    ]
    for pattern in heavy_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return "Heavy"

    return "Lite"


def get_execution_mode(adr_file: Path | None) -> str:
    """Read execution mode from ADR's ## Execution Mode section."""
    if adr_file is None:
        return "normal"
    try:
        content = adr_file.read_text(encoding="utf-8")
    except OSError:
        return "normal"

    exception_patterns = [
        r"\*\*Mode:\*\*\s*Exception",
        r"Mode:\s*Exception",
    ]
    for pattern in exception_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return "exception"

    return "normal"


def has_audit_evidence(adr_dir: Path, obpi_id: str) -> bool:
    """Check if audit ledger entry exists for this OBPI in ADR-local ledger."""
    ledger_file = adr_dir / "logs" / "obpi-audit.jsonl"

    if not ledger_file.exists():
        return False

    try:
        with ledger_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    entry_type = entry.get("type", "")
                    entry_obpi = entry.get("obpi_id", "")
                    if entry_obpi == obpi_id and entry_type in (
                        "obpi-audit",
                        "obpi-completion",
                    ):
                        return True
                except json.JSONDecodeError:
                    continue
    except OSError:
        return False

    return False


def has_human_attestation(adr_dir: Path, obpi_id: str) -> bool:
    """Check if human attestation exists in ADR-local ledger for this OBPI."""
    ledger_file = adr_dir / "logs" / "obpi-audit.jsonl"

    if not ledger_file.exists():
        return False

    try:
        with ledger_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    entry_obpi = entry.get("obpi_id", "")
                    if entry_obpi == obpi_id:
                        evidence = entry.get("evidence", {})
                        if evidence.get("human_attestation"):
                            return True
                        if entry.get("attestation_type") == "human":
                            return True
                except json.JSONDecodeError:
                    continue
    except OSError:
        return False

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

    # 1. Is this an OBPI brief file? (gzkit uses /obpis/, airlineops uses /briefs/)
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

    # 4. Find parent ADR directory and file
    adr_dir = find_parent_adr_dir(abs_path)
    if not adr_dir or not adr_dir.exists():
        sys.exit(0)

    adr_file = find_parent_adr_file(adr_dir)

    # 5. Check for audit evidence in ADR-local ledger
    if not has_audit_evidence(adr_dir, obpi_id):
        print(
            f"\n\u26d4 BLOCKED: Cannot mark {obpi_id} as Completed.\n"
            f"\n"
            f"No audit evidence found in {adr_dir.name}/logs/obpi-audit.jsonl\n"
            f"\n"
            f"REQUIRED: Run gz-obpi-audit first to verify and record evidence:\n"
            f"  /gz-obpi-audit {obpi_id}\n",
            file=sys.stderr,
        )
        sys.exit(2)

    # 6. Check attestation requirements
    execution_mode = get_execution_mode(adr_file)

    if execution_mode == "exception":
        # Exception mode: self-close allowed. Audit evidence already
        # validated above. Human reviews at ADR closeout.
        sys.exit(0)

    # Normal mode: check lane for attestation rigor
    is_foundation = is_foundation_adr(adr_id)
    parent_lane = get_parent_adr_lane(adr_file)
    requires_human = is_foundation or parent_lane == "Heavy"

    if requires_human and not has_human_attestation(adr_dir, obpi_id):
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
