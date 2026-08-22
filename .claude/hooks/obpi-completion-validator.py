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
    """Find the project root by looking for .gzkit directory.

    Resolved, because callers compare it against a resolved
    target path. On Windows an 8.3 short-name cwd
    (C:/Users/RUNNER~1/...) and its resolved long form share no
    prefix, so relative_to() raises and the caller loses the
    path it was about to gate.
    """
    current = Path.cwd().resolve()
    while current != current.parent:
        if (current / ".gzkit").is_dir():
            return current
        current = current.parent
    return Path.cwd().resolve()


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


def resolve_would_be_content(abs_path: Path, tool_input: dict) -> str:
    """Resolve the file content that would result from the edit/write."""
    content_field = tool_input.get("content")
    if content_field:
        # Write tool: content IS the full new file
        return content_field
    # Edit tool: read current file, apply old_string -> new_string
    old = tool_input.get("old_string", "")
    new = tool_input.get("new_string", "")
    try:
        current = abs_path.read_text(encoding="utf-8")
    except OSError:
        return new
    if old and old in current:
        return current.replace(old, new, 1)
    return current


def _obpi_id_matches(entry_obpi: str, obpi_id: str) -> bool:
    """Match a ledger entry's OBPI id against the short id from the brief path.

    The ADR-local audit ledger records full-slug ids
    (OBPI-0.0.73-06-self-check-facade-regression-corpus), while
    extract_obpi_id yields the short id (OBPI-0.0.73-06). Match the
    short id exactly, or as the stem of a full slug (short id + '-' +
    slug). The trailing '-' boundary keeps OBPI-0.0.73-1 from matching
    OBPI-0.0.73-10 (GHI #629).
    """
    return entry_obpi == obpi_id or entry_obpi.startswith(obpi_id + "-")


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
                    if _obpi_id_matches(entry_obpi, obpi_id) and entry_type in (
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
                    if _obpi_id_matches(entry_obpi, obpi_id):
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
        abs_path = Path(file_path).resolve()
    except (ValueError, TypeError, OSError):
        sys.exit(0)

    # Brief-shape is read from the absolute path so it survives a
    # failure to place the file against the project root. This
    # hook fires on EVERY Edit/Write, so the fail-closed arm below
    # must stay scoped to the surface it guards — blocking every
    # unplaceable path would refuse scratchpad and system edits.
    abs_str = abs_path.as_posix()
    looks_like_brief = "/obpis/OBPI-" in abs_str and abs_str.endswith(".md")

    try:
        project_root = find_project_root()
        rel_str = abs_path.relative_to(project_root).as_posix()
    except (ValueError, TypeError):
        if looks_like_brief:
            print(
                "BLOCKED: OBPI brief edit refused — cannot place "
                f"{abs_str} against project root.\n\n"
                "WHY: this hook gates the Completed transition on "
                "Implementation Summary and Key Proof. A brief it "
                "cannot resolve cannot be checked, and an "
                "unverifiable completion must fail closed, never "
                "open (AGENTS.md Never #8; ADR-0.0.36 makes Gate 5 "
                "universal).\n\n"
                "NEXT STEP: edit the brief from inside its own "
                "project root so the hook can resolve it, then "
                "re-run `uv run gz obpi status <OBPI-ID>` to "
                "confirm the brief the gate sees.",
                file=sys.stderr,
            )
            sys.exit(2)
        sys.exit(0)

    # 1. Is this an OBPI brief file? (gzkit uses /obpis/, airlineops uses /briefs/)
    if "/obpis/OBPI-" not in rel_str or not rel_str.endswith(".md"):
        sys.exit(0)

    # 2. Is this changing status to Completed?
    #    If old_string already contains Completed, the file is already in that state
    #    and this edit is not introducing a status transition — allow it through.
    old_string = tool_input.get("old_string", "")
    if not check_status_change_to_completed(new_string):
        sys.exit(0)
    if old_string and check_status_change_to_completed(old_string):
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

    # 4b. Resolve lane early so content quality checks can gate attestation (#126)
    is_foundation = is_foundation_adr(adr_id)
    parent_lane = get_parent_adr_lane(adr_file)
    execution_mode = get_execution_mode(adr_file)
    requires_human = execution_mode != "exception" and (is_foundation or parent_lane == "Heavy")

    # 5. Check brief content quality (hard block)
    would_be = resolve_would_be_content(abs_path, tool_input)
    # The evidence rule is IMPORTED, never redefined here. This hook
    # is the ADVISORY fast path: it binds Write|Edit|NotebookEdit and
    # keys on tool_input.file_path, so every sed / heredoc /
    # inline-python write bypasses it entirely. The arm that BINDS is
    # gzkit.hooks.guards.forbid_unattested_obpi_completion_commits,
    # reading git diff --cached. A second copy of the rule here could
    # disagree with that guard, and the disagreement would be
    # invisible -- whichever locus the agent reached would rule
    # (GHI #847).
    from gzkit.obpi_completion_fence import completion_blockers

    brief_blocks = [
        f"  - {blocker}" for blocker in completion_blockers(would_be, requires_human=requires_human)
    ]
    if brief_blocks:
        details = "\n".join(brief_blocks)
        print(
            f"\n\u26d4 BLOCKED: Cannot mark {obpi_id} as Completed.\n"
            f"\n"
            f"Brief content quality checks failed:\n"
            f"{details}\n"
            f"\n"
            f"REQUIRED: Add substantive content to these sections before "
            f"marking the OBPI as Completed.\n",
            file=sys.stderr,
        )
        sys.exit(2)

    # 6. Check for audit evidence in ADR-local ledger
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

    # 7. Check attestation requirements (lane resolved in step 4b)
    if execution_mode == "exception":
        # Exception mode: self-close allowed. Audit evidence already
        # validated above. Human reviews at ADR closeout.
        sys.exit(0)

    if requires_human and not has_human_attestation(adr_dir, obpi_id):
        lane_reason = "Foundation (0.0.x)" if is_foundation else "Heavy lane"
        print(
            f"\n\u26d4 BLOCKED: {obpi_id} requires human attestation.\n"
            f"\n"
            f"Parent {adr_id} is {lane_reason}.\n"
            f"Per AGENTS.md, OBPIs under Heavy/Foundation ADRs "
            f"inherit attestation rigor.\n"
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
