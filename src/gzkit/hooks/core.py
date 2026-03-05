"""Core hook logic shared across agent implementations.

This module contains the governance enforcement logic that all agent hooks use.
"""

import re
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.hooks.obpi import ObpiValidator
from gzkit.ledger import (
    Ledger,
    artifact_edited_event,
    obpi_receipt_emitted_event,
    parse_frontmatter_value,
    resolve_adr_lane,
)
from gzkit.utils import capture_validation_anchor

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
        for error in errors:
            print(f"  - BLOCK: {error}")
        print("\nFix these issues or revert status to 'Draft' to continue.\n")
        # In a hook context, we want to exit non-zero to block the tool use
        # However, record_artifact_edit is called by the hook script which might
        # ignore the return value or exception.
        # The hook script itself needs to handle this.
        raise RuntimeError("OBPI completion validation failed.")


def _record_obpi_completion_if_ready(
    project_root: Path,
    ledger: Ledger,
    config: GzkitConfig,
    path: str,
) -> None:
    """Record an OBPI completion receipt if the file is in 'Completed' status."""
    obpi_path = project_root / path
    if not obpi_path.exists():
        return

    content = obpi_path.read_text()
    status = (parse_frontmatter_value(content, "status") or "").strip().lower()
    if status != "completed":
        return

    # Extract metadata for receipt
    obpi_id = parse_frontmatter_value(content, "id") or obpi_path.stem
    parent_adr = parse_frontmatter_value(content, "parent")

    # Resolve lane for attestation term
    parent_lane = config.mode
    if parent_adr:
        graph = ledger.get_artifact_graph()
        parent_info = graph.get(ledger.canonicalize_id(parent_adr), {})
        parent_lane = resolve_adr_lane(parent_info, config.mode)

    # Use 'human:agent-automated' as fallback if session is not human
    # In AirlineOps, agents can record 'completed' events, but they are 'not_attested'
    # unless evidence is present.
    # The validator ensures evidence is present before we get here.

    # For now, we'll use a fixed attestor token for automated completion
    attestor = "agent:automated-recorder"

    # Capture anchor
    anchor = capture_validation_anchor(project_root, parent_adr)

    # Emit receipt
    event = obpi_receipt_emitted_event(
        obpi_id=obpi_id,
        receipt_event="completed",
        attestor=attestor,
        parent_adr=parent_adr,
        obpi_completion="completed" if parent_lane == "lite" else "attested_completed",
        anchor=anchor,
    )
    ledger.append(event)


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
    if is_obpi:
        validate_obpi_transition(project_root, path)

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
        _record_obpi_completion_if_ready(project_root, ledger, config, path)

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
    script_path.write_text(script_content)

    # Make executable on Unix
    script_path.chmod(0o755)

    return script_path
