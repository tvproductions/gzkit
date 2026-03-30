"""Step renderers and walkthrough discovery for the closeout ceremony.

Each renderer returns a text block for exactly one ceremony step.
Split from ``closeout_ceremony.py`` to keep both modules under 600 lines.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from gzkit.commands.closeout_ceremony import CeremonyState


# ---------------------------------------------------------------------------
# Step renderers — each returns a text block for exactly one step
# ---------------------------------------------------------------------------


def render_step_2_summary(
    adr_id: str,
    adr_file: Path,
    obpi_files: list[Path],
    manifest: dict[str, Any],
    lane: str,
    project_root: Path,
) -> str:
    """Paths/commands-only summary."""
    obpi_list = "\n".join(f"  - {f.relative_to(project_root)}" for f in obpi_files)
    verification = manifest.get("verification", {})
    test_cmd = verification.get("test", "uv run gz test")
    lint_cmd = verification.get("lint", "uv run gz lint")
    tc_cmd = verification.get("typecheck", "uv run gz typecheck")
    docs_cmd = verification.get("docs", "uv run mkdocs build --strict")

    lines = [
        "ADR CLOSEOUT CEREMONY — MODE TRANSITION",
        "",
        "I am now in PASSIVE PRESENTER mode. I will not interpret evidence.",
        "",
        "Summary (paths/commands only; no outcomes):",
        f"- ADR under review: {adr_file.relative_to(project_root)}",
        f"- Related briefs:\n{obpi_list}",
        "",
        "Artifacts for your direct observation:",
        f"- Tests: Run `{test_cmd}`",
        f"- Lint: Run `{lint_cmd}`",
        f"- Typecheck: Run `{tc_cmd}`",
        f"- Docs build: Run `{docs_cmd}`",
    ]
    if lane == "heavy":
        bdd_cmd = verification.get("bdd", "uv run -m behave features/")
        lines.append(f"- BDD (Heavy): Run `{bdd_cmd}`")
    lines.append("")
    lines.append(f"Step 2 complete. Run `gz closeout {adr_id} --ceremony --next`")
    lines.append("to proceed to docs alignment check.")
    return "\n".join(lines)


def render_step_3_docs_check(adr_id: str) -> str:
    """Docs alignment checklist."""
    return "\n".join(
        [
            "Docs alignment check (human-confirmed):",
            "",
            "- [ ] Manpage exists and reflects current CLI behavior",
            "- [ ] Runbook includes relevant commands",
            "- [ ] Dataset documentation updated if applicable",
            "- [ ] CLI --help matches manpage SYNOPSIS",
            "",
            f"Step 3 complete. Run `gz closeout {adr_id} --ceremony --next`",
            "to proceed to runbook walkthrough.",
        ]
    )


def render_step_4_walkthrough(adr_id: str, commands: list[str]) -> str:
    """Runbook walkthrough — command list."""
    cmd_list = "\n".join(f"  {i + 1}. `{c}`" for i, c in enumerate(commands))
    return "\n".join(
        [
            "Runbook Walkthrough — Demonstrating ADR Value",
            "",
            "The following commands demonstrate the ADR's achieved value.",
            "They will be presented one at a time in the next steps.",
            "",
            cmd_list,
            "",
            f"Step 4 complete. Run `gz closeout {adr_id} --ceremony --next`",
            "to begin executing commands one at a time.",
        ]
    )


def render_step_5_execute(adr_id: str, commands: list[str]) -> str:
    """Run all walkthrough commands now."""
    cmd_list = "\n".join(f"  {c}" for c in commands)
    return "\n".join(
        [
            "Run these walkthrough commands now:",
            "",
            cmd_list,
            "",
            "After observing the output,",
            f"run `gz closeout {adr_id} --ceremony --next` to proceed to attestation.",
        ]
    )


def render_step_6_attestation(adr_id: str) -> str:
    """Request attestation."""
    return "\n".join(
        [
            "Runbook walkthrough complete.",
            "",
            "When you are ready, provide your attestation:",
            "",
            f'  gz closeout {adr_id} --ceremony --attest "Completed"',
            f'  gz closeout {adr_id} --ceremony --attest "Completed - Partial: [reason]"',
            f'  gz closeout {adr_id} --ceremony --attest "Dropped - [reason]"',
            "",
            "I await your attestation.",
        ]
    )


def render_step_7_closeout(adr_id: str) -> str:
    """Instruct the agent to run the closeout pipeline."""
    return "\n".join(
        [
            "Attestation recorded. Run the closeout pipeline:",
            "",
            f"  uv run gz closeout {adr_id}",
            "",
            "This runs quality gates, records attestation, bumps version,",
            "and writes the closeout form.",
            "",
            f"After closeout completes, run `gz closeout {adr_id} --ceremony --next`.",
        ]
    )


def render_step_8_issues(adr_id: str) -> str:
    """Instruct the agent to close related GitHub issues."""
    return "\n".join(
        [
            "Close related GitHub issues:",
            "",
            f'  gh issue list --search "{adr_id}" --state open',
            "",
            "Review each issue. Close resolved issues with:",
            "",
            f'  gh issue close <number> --comment "Resolved by {adr_id} closeout."',
            "",
            f"After reviewing issues, run `gz closeout {adr_id} --ceremony --next`.",
        ]
    )


def render_step_9_release_notes(adr_id: str) -> str:
    """Instruct the agent to update RELEASE_NOTES.md."""
    return "\n".join(
        [
            "Update RELEASE_NOTES.md with a new release entry for this ADR.",
            "",
            "Template:",
            "  ## vX.Y.Z (YYYY-MM-DD)",
            f"  **ADR:** {adr_id}",
            "  [Brief description]",
            "  ### Delivered",
            "  - [Key deliverables]",
            "  ### Gate Evidence",
            "  All 5 GovZero gates satisfied.",
            "",
            f"After updating, run `gz closeout {adr_id} --ceremony --next`.",
        ]
    )


def render_step_10_release(adr_id: str) -> str:
    """Instruct the agent to create a GitHub release."""
    return "\n".join(
        [
            "Create GitHub release:",
            "",
            "  # MANDATORY: sync before release",
            "  uv run gz git-sync --apply --lint --test",
            "",
            '  gh release create vX.Y.Z --title "vX.Y.Z" --notes "..."',
            "",
            f"After creating the release, run `gz closeout {adr_id} --ceremony --next`.",
        ]
    )


def render_step_11_complete(state: CeremonyState) -> str:
    """Ceremony completion summary."""
    step_names = {
        1: "Trigger recognized",
        2: "Paths/commands summary presented",
        3: "Docs alignment verified",
        4: "Runbook walkthrough presented",
        5: "Commands executed (one at a time)",
        6: "Attestation recorded",
        7: "Closeout pipeline executed",
        8: "GitHub Issues reviewed",
        9: "RELEASE_NOTES.md updated",
        10: "GitHub Release created",
        11: "Ceremony complete",
    }
    lines = [f"ADR {state.adr_id} CLOSEOUT CEREMONY — COMPLETE", ""]
    for record in state.step_history:
        name = step_names.get(record.step, f"Step {record.step}")
        lines.append(f"  Step {record.step:2d}: {name}")
    if state.attestation:
        lines.append(f"\n  Attestation: {state.attestation}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Walkthrough command discovery
# ---------------------------------------------------------------------------


def _commands_from_command_docs(project_root: Path, obpi_files: list[Path]) -> list[str]:
    """Extract CLI commands by resolving command-doc links in OBPI briefs."""
    cmd_dir = project_root / "docs" / "user" / "commands"
    if not cmd_dir.is_dir():
        return []
    commands: list[str] = []
    for obpi_file in obpi_files:
        content = obpi_file.read_text(encoding="utf-8")
        for line in content.splitlines():
            m = re.match(r"^- `(docs/user/commands/\S+\.md)`", line)
            if not m:
                continue
            cmd_path = project_root / m.group(1)
            if not cmd_path.exists():
                continue
            first_line = cmd_path.read_text(encoding="utf-8").split("\n", 1)[0]
            if first_line.startswith("# "):
                commands.append(f"uv run {first_line[2:].strip()} --help")
    return commands


def _commands_from_verification_sections(obpi_files: list[Path]) -> list[str]:
    """Extract bash commands from ``## Verification Commands`` fenced blocks."""
    commands: list[str] = []
    for obpi_file in obpi_files:
        content = obpi_file.read_text(encoding="utf-8")
        in_verification = False
        in_code = False
        for line in content.splitlines():
            if line.startswith("## Verification Commands"):
                in_verification = True
                continue
            if in_verification and line.startswith("## "):
                break
            if in_verification and line.strip() == "```bash":
                in_code = True
                continue
            if in_verification and line.strip() == "```":
                in_code = False
                continue
            if in_code and line.strip() and not line.strip().startswith("#"):
                commands.append(line.strip())
    return commands


def discover_walkthrough_commands(
    project_root: Path,
    adr_id: str,
    obpi_files: list[Path],
) -> list[str]:
    """Extract relevant CLI commands for the runbook walkthrough."""
    commands = _commands_from_command_docs(project_root, obpi_files)
    if not commands:
        commands = _commands_from_verification_sections(obpi_files)
    return commands or [f"uv run gz adr status {adr_id} --json"]
