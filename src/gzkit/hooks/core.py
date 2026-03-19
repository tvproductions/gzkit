"""Core hook logic shared across agent implementations.

This module contains the governance enforcement logic that all agent hooks use.
"""

import re
import sys
from pathlib import Path
from typing import Any

from gzkit.config import GzkitConfig
from gzkit.git_sync import assess_git_sync_readiness
from gzkit.hooks.obpi import (
    ObpiValidator,
    build_scope_audit,
    normalize_git_sync_state,
)
from gzkit.ledger import (
    Ledger,
    artifact_edited_event,
    normalize_req_proof_inputs,
    obpi_receipt_emitted_event,
    parse_frontmatter_value,
    resolve_adr_lane,
)
from gzkit.utils import capture_validation_anchor_with_warnings

# Governance artifact patterns
GOVERNANCE_PATTERNS = [
    r"^design/prd/.*\.md$",
    r"^design/constitutions/.*\.md$",
    r"^design/obpis/.*\.md$",
    r"^design/adr/.*\.md$",
    r"^docs/prd/.*\.md$",
    r"^docs/adr/.*\.md$",
    r"^docs/design/obpis/.*\.md$",
    r"^docs/design/adr/.*\.md$",
    r"^AGENTS\.md$",
    r"^CLAUDE\.md$",
]


def is_governance_artifact(path: str) -> bool:
    """Check if a path is a governance artifact.

    Args:
        path: Relative path to check.

    Returns:
        True if the path matches a governance pattern.

    """
    # Normalize path separators
    normalized = path.replace("\\", "/")
    return any(re.match(pattern, normalized) for pattern in GOVERNANCE_PATTERNS)


def validate_obpi_transition(project_root: Path, path: str) -> None:
    """Run the OBPI validator gate for completion readiness.

    Args:
        project_root: Project root directory.
        path: Relative path to the edited artifact.

    Raises:
        GzCliError: If validation fails.

    """
    validator = ObpiValidator(project_root)
    obpi_path = project_root / path
    errors = validator.validate_file(obpi_path)

    if errors:
        print(f"\nOBPI Validation Failed: {path}")
        print("BLOCKERS:")
        for error in errors:
            print(f"- {error}")
        print("\nFix these blockers or revert status to 'Draft' to continue.\n")
        # In a hook context, we want to exit non-zero to block the tool use
        # However, record_artifact_edit is called by the hook script which might
        # ignore the return value or exception.
        # The hook script itself needs to handle this.
        raise RuntimeError("OBPI completion validation failed.")


def _section_body(content: str, heading: str) -> str | None:
    for marker in ("##", "###"):
        pattern = rf"^{re.escape(marker)} {re.escape(heading)}\s*$([\s\S]*?)(?:^{marker} |\n---|\Z)"
        match = re.search(pattern, content, flags=re.MULTILINE)
        if match:
            body = match.group(1).strip()
            if body:
                return body
    return None


def _implementation_summary_value(content: str) -> str | None:
    section = _section_body(content, "Implementation Summary")
    if not section:
        return None
    bullet_matches = re.findall(r"^- [^:\n]+:[ \t]*(.+)$", section, flags=re.MULTILINE)
    for value in bullet_matches:
        cleaned = value.strip()
        if cleaned:
            return cleaned
    plain_bullets = re.findall(r"^- \s*(.+)$", section, flags=re.MULTILINE)
    for value in plain_bullets:
        cleaned = value.strip()
        if cleaned:
            return cleaned
    return None


def _extract_human_attestation(content: str) -> dict[str, str] | None:
    body = _section_body(content, "Human Attestation")
    if not body:
        return None
    attestor_match = re.search(r"^- Attestor:\s*(.+)$", body, flags=re.MULTILINE)
    attestation_match = re.search(r"^- Attestation:\s*(.+)$", body, flags=re.MULTILINE)
    date_match = re.search(r"^- Date:\s*(\d{4}-\d{2}-\d{2})$", body, flags=re.MULTILINE)
    if not attestor_match or not attestation_match or not date_match:
        return None
    return {
        "attestor": attestor_match.group(1).strip(),
        "attestation_text": attestation_match.group(1).strip(),
        "attestation_date": date_match.group(1).strip(),
    }


def _dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


def enrich_completed_receipt_evidence(
    *,
    project_root: Path,
    content: str,
    base_evidence: dict[str, Any],
    parent_adr: str | None,
    recorder_source: str,
    scope_audit: dict[str, list[str]] | None = None,
    git_sync_state: dict[str, Any] | None = None,
    extra_warnings: list[str] | None = None,
) -> tuple[dict[str, Any], dict[str, str] | None]:
    """Attach structured scope/git metadata and warning-aware anchoring."""
    evidence = dict(base_evidence)
    evidence["scope_audit"] = scope_audit or build_scope_audit(project_root, content)

    normalized_git_sync_state = git_sync_state or normalize_git_sync_state(
        assess_git_sync_readiness(project_root)
    )
    if normalized_git_sync_state is None:
        normalized_git_sync_state = {
            "branch": None,
            "remote": None,
            "head": None,
            "remote_head": None,
            "dirty": False,
            "ahead": 0,
            "behind": 0,
            "diverged": False,
            "actions": [],
            "warnings": ["Could not normalize git-sync state for receipt evidence."],
            "blockers": [],
        }
    evidence["git_sync_state"] = normalized_git_sync_state
    evidence["recorder_source"] = recorder_source

    warnings = list(extra_warnings or [])
    if normalized_git_sync_state.get("dirty"):
        warnings.append("Working tree was dirty when the completion receipt was captured.")
    blockers = normalized_git_sync_state.get("blockers", [])
    if isinstance(blockers, list):
        warnings.extend(
            f"Git-sync blocker present at receipt capture time: {blocker}"
            for blocker in blockers
            if isinstance(blocker, str)
        )

    anchor, anchor_warnings = capture_validation_anchor_with_warnings(project_root, parent_adr)
    warnings.extend(anchor_warnings)
    evidence["recorder_warnings"] = _dedupe_preserve_order(warnings)
    return evidence, anchor


def _record_obpi_completion_if_ready(
    project_root: Path,
    ledger: Ledger,
    config: GzkitConfig,
    path: str,
    scope_audit: dict[str, list[str]] | None = None,
) -> None:
    """Record an OBPI completion receipt if the file is in 'Completed' status."""
    obpi_path = project_root / path
    if not obpi_path.exists():
        return

    content = obpi_path.read_text(encoding="utf-8")
    status = (parse_frontmatter_value(content, "status") or "").strip().lower()
    if status != "completed":
        return

    # Extract metadata for receipt
    obpi_id = parse_frontmatter_value(content, "id") or obpi_path.stem
    parent_adr = parse_frontmatter_value(content, "parent")
    value_narrative = _implementation_summary_value(content)
    key_proof = _section_body(content, "Key Proof")
    human_attestation = _extract_human_attestation(content)

    # Resolve lane for attestation term
    parent_lane = config.mode
    if parent_adr:
        graph = ledger.get_artifact_graph()
        parent_info = graph.get(ledger.canonicalize_id(parent_adr), {})
        parent_lane = resolve_adr_lane(parent_info, config.mode)
    requires_human_attestation = parent_lane == "heavy" or (
        isinstance(parent_adr, str) and bool(re.match(r"^ADR-0\.0\.\d+", parent_adr))
    )

    # Use 'human:agent-automated' as fallback if session is not human
    # In AirlineOps, agents can record 'completed' events, but they are 'not_attested'
    # unless evidence is present.
    # The validator ensures evidence is present before we get here.

    # For now, we'll use a fixed attestor token for automated completion
    attestor = "agent:automated-recorder"

    # Emit receipt
    evidence: dict[str, object] = {
        "attestation_requirement": "required" if requires_human_attestation else "optional",
        "parent_lane": parent_lane,
    }
    if parent_adr:
        evidence["parent_adr"] = parent_adr
    if value_narrative:
        evidence["value_narrative"] = value_narrative
    if key_proof:
        evidence["key_proof"] = key_proof
    if human_attestation:
        evidence["human_attestation"] = True
        evidence["attestation_text"] = human_attestation["attestation_text"]
        evidence["attestation_date"] = human_attestation["attestation_date"]
    evidence["req_proof_inputs"] = normalize_req_proof_inputs(
        None,
        fallback_key_proof=key_proof,
        human_attestation={
            "valid": bool(human_attestation),
            "attestor": human_attestation["attestor"] if human_attestation else None,
            "date": human_attestation["attestation_date"] if human_attestation else None,
        }
        if human_attestation
        else None,
    )
    enriched_evidence, anchor = enrich_completed_receipt_evidence(
        project_root=project_root,
        content=content,
        base_evidence=evidence,
        parent_adr=parent_adr,
        recorder_source="hook:auto",
        scope_audit=scope_audit,
    )
    event = obpi_receipt_emitted_event(
        obpi_id=obpi_id,
        receipt_event="completed",
        attestor=attestor,
        evidence=enriched_evidence,
        parent_adr=parent_adr,
        obpi_completion="attested_completed" if requires_human_attestation else "completed",
        anchor=anchor,
    )
    try:
        ledger.append(event)
    except OSError as exc:
        print(
            f"Warning: Could not append OBPI completion receipt for {obpi_id}: {exc}",
            file=sys.stderr,
        )


def record_artifact_edit(
    project_root: Path,
    path: str,
    session: str | None = None,
) -> bool:
    """Record a governance artifact edit in the ledger.

    Args:
        project_root: Project root directory.
        path: Relative path to the edited artifact.
        session: Optional session identifier.

    Returns:
        True if event was recorded, False otherwise.

    """
    if not is_governance_artifact(path):
        return False

    # Perform OBPI completion validation if it's an OBPI
    is_obpi = "obpis/" in path.replace("\\", "/")
    completion_scope_audit: dict[str, list[str]] | None = None
    if is_obpi:
        validate_obpi_transition(project_root, path)
        obpi_path = project_root / path
        if obpi_path.exists():
            content = obpi_path.read_text(encoding="utf-8")
            status = (parse_frontmatter_value(content, "status") or "").strip().lower()
            if status == "completed":
                completion_scope_audit = build_scope_audit(project_root, content)

    config = GzkitConfig.load(project_root / ".gzkit.json")
    ledger_path = project_root / config.paths.ledger

    if not ledger_path.exists():
        return False

    ledger = Ledger(ledger_path)

    # 1. Record the edit itself
    event = artifact_edited_event(path, session)
    ledger.append(event)

    # 2. If it's an OBPI being completed, record the receipt
    if is_obpi:
        _record_obpi_completion_if_ready(
            project_root,
            ledger,
            config,
            path,
            scope_audit=completion_scope_audit,
        )

    return True


def run_light_validation(project_root: Path) -> list[str]:
    """Run quick validation checks (for hooks).

    This is a lighter version of full validation suitable for hooks.
    Returns a list of issues found.

    Args:
        project_root: Project root directory.

    Returns:
        List of validation issues (empty if all checks pass).

    """
    issues = []

    # Check manifest exists
    manifest_path = project_root / ".gzkit" / "manifest.json"
    if not manifest_path.exists():
        issues.append("Missing .gzkit/manifest.json")

    # Check ledger exists
    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.exists():
        issues.append("Missing .gzkit/ledger.jsonl")

    # Check AGENTS.md exists
    agents_path = project_root / "AGENTS.md"
    if not agents_path.exists():
        issues.append("Missing AGENTS.md")

    return issues


def generate_hook_script(hook_type: str, project_root: Path) -> str:
    """Generate a hook script for the specified agent type.

    Args:
        hook_type: Type of hook ("claude" or "copilot").
        project_root: Project root directory.

    Returns:
        Python script content for the hook.

    """
    script = '''#!/usr/bin/env python3
"""gzkit ledger writer and validator hook for {hook_type}.

This hook records governance artifact edits and enforces completion gates.
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
    tool_input = input_data.get("tool_input", {{}})

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

    # Import gzkit and record edit/validate
    sys.path.insert(0, str(project_root / "src"))
    try:
        from gzkit.hooks.core import record_artifact_edit
        session = os.environ.get("CLAUDE_SESSION_ID") or os.environ.get("COPILOT_SESSION_ID")

        # This will trigger validation and raise if it fails
        record_artifact_edit(project_root, str(rel_path), session)

    except ImportError:
        pass  # gzkit not installed, skip
    except Exception as exc:
        print(f"\\n[GOVERNANCE BLOCK] {{exc}}\\n", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

    return script.format(hook_type=hook_type)


def write_hook_script(project_root: Path, hook_type: str, hooks_dir: str) -> Path:
    """Write a hook script to the appropriate location.

    Args:
        project_root: Project root directory.
        hook_type: Type of hook ("claude" or "copilot").
        hooks_dir: Directory for hooks relative to project root.

    Returns:
        Path to the written hook script.

    """
    hooks_path = project_root / hooks_dir
    hooks_path.mkdir(parents=True, exist_ok=True)

    script_path = hooks_path / "ledger-writer.py"
    script_content = generate_hook_script(hook_type, project_root)
    script_path.write_text(script_content, encoding="utf-8")

    # Make executable on Unix
    script_path.chmod(0o755)

    return script_path
