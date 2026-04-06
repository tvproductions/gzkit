"""Step renderers and walkthrough discovery for the closeout ceremony.

Each renderer returns a text block for exactly one ceremony step.
Split from ``closeout_ceremony.py`` to keep both modules under 600 lines.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from rich.console import Group
from rich.markdown import Markdown
from rich.rule import Rule
from rich.text import Text

from gzkit.commands.ceremony_data import (
    _render_to_text,
    check_doc_alignment,
    extract_brief_metadata,
    format_doc_table,
    format_summary_table,
)

if TYPE_CHECKING:
    from gzkit.commands.closeout_ceremony import CeremonyState


# ---------------------------------------------------------------------------
# Step renderers — each returns a text block for exactly one step
# ---------------------------------------------------------------------------


def render_step_1_readiness(
    adr_id: str,
    obpi_rows: list[dict[str, Any]],
    readiness: dict[str, Any],
) -> str:
    """OBPI completion table — the precondition proof."""
    from gzkit.commands.ceremony_data import format_readiness_table

    return format_readiness_table(adr_id, obpi_rows, readiness)


def render_step_2_summary(
    adr_id: str,
    adr_file: Path,
    obpi_files: list[Path],
    manifest: dict[str, Any],
    lane: str,
    project_root: Path,
) -> str:
    """Rich bill of materials — OBPI-by-OBPI with objectives."""
    briefs = [extract_brief_metadata(f) for f in obpi_files]

    lines = [
        "I am now in PASSIVE PRESENTER mode. I will not interpret evidence.",
        "",
        f"ADR: {adr_file.relative_to(project_root)}",
        f"Lane: {lane}",
        "",
        format_summary_table(
            briefs,
            title=f"Bill of Materials — {adr_id}",
        ),
        "",
    ]

    # Verification commands
    verification = manifest.get("verification", {})
    lines.append("Quality gate commands (for your direct observation):")
    lines.append(f"  Tests:     {verification.get('test', 'uv run gz test')}")
    lines.append(f"  Lint:      {verification.get('lint', 'uv run gz lint')}")
    lines.append(f"  Typecheck: {verification.get('typecheck', 'uv run gz typecheck')}")
    lines.append(f"  Docs:      {verification.get('docs', 'uv run mkdocs build --strict')}")
    if lane == "heavy":
        lines.append(f"  BDD:       {verification.get('bdd', 'uv run -m behave features/')}")

    lines.append("")
    lines.append(f"Step 2 complete. Run `gz closeout {adr_id} --ceremony --next`")
    lines.append("to proceed to docs alignment check.")
    return "\n".join(lines)


def render_step_3_docs_check(
    adr_id: str,
    project_root: Path,
    obpi_files: list[Path],
) -> str:
    """Docs alignment findings — agent homework, human reviews."""
    results = check_doc_alignment(project_root, obpi_files)

    lines = [format_doc_table(results)]

    if results:
        missing = [r for r in results if not r["manpage_exists"]]
        if missing:
            lines.append("")
            lines.append(f"GAPS: {len(missing)} command(s) missing manpages.")
        else:
            lines.append("")
            lines.append("All command manpages present.")
    else:
        lines.append("")
        lines.append("Manual review: check that any new/changed commands have documentation.")

    lines.append("")
    lines.append(f"Step 3 complete. Run `gz closeout {adr_id} --ceremony --next`")
    lines.append("to proceed to value walkthrough.")
    return "\n".join(lines)


def render_step_4_walkthrough(
    adr_id: str,
    commands: list[str],
    obpi_files: list[Path],
) -> str:
    """Value narrative — per-OBPI sections, then demo command list."""
    briefs = [extract_brief_metadata(f) for f in obpi_files]
    elements: list[Any] = [Rule("Value Walkthrough")]

    for b in briefs:
        obpi_id = b.get("id", "?")
        title = b.get("title", "?")
        objective = b.get("objective", "(no objective recorded)")
        first_para = objective.split("\n\n")[0].strip()

        md_lines = [f"### {obpi_id}: {title}", "", first_para]
        elements.append(Markdown("\n".join(md_lines)))

        ac = b.get("acceptance_criteria", [])
        if ac:
            elements.append(Text())
            elements.append(Rule(f"Requirements ({len(ac)})", style="dim", align="left"))
            ac_md = "\n".join(f"- {c}" for c in ac)
            elements.append(Markdown(ac_md))

        elements.append(Text())
        elements.append(Text())

    if commands:
        elements.append(Rule("Demo Commands (Step 5)", style="dim"))
        for i, c in enumerate(commands):
            elements.append(Text(f"  {i + 1}. {c}"))
    else:
        elements.append(Text("No demo commands discovered."))

    elements.append(Text())
    elements.append(
        Text(
            f"Step 4 complete. Run `gz closeout {adr_id} --ceremony --next`\n"
            "to begin the live demo."
        )
    )
    return _render_to_text(Group(*elements))


def render_step_5_execute(adr_id: str, commands: list[str]) -> str:
    """Live demo — run commands for direct observation.

    The agent should present these one at a time with light framing,
    waiting for acknowledgment between each command.
    """
    lines = [
        "LIVE DEMO — Test Drive",
        "",
        "Present each command one at a time. For each command:",
        "  1. Explain briefly why this demonstrates value",
        "  2. Run the command (or offer to let the human run it)",
        "  3. Wait for human acknowledgment before proceeding",
        "",
    ]
    if commands:
        lines.append("Commands to demonstrate:")
        for i, c in enumerate(commands):
            lines.append(f"  {i + 1}. `{c}`")
    else:
        lines.append("No demo commands to run.")

    lines.append("")
    lines.append("After all commands have been observed,")
    lines.append(f"run `gz closeout {adr_id} --ceremony --next` to proceed to attestation.")
    return "\n".join(lines)


def render_step_6_attestation(adr_id: str) -> str:
    """Request attestation — supports R&R dialogue."""
    return "\n".join(
        [
            "ATTESTATION — Your Verdict",
            "",
            "The walkthrough is complete. You may now:",
            "",
            "  Ask questions — I will answer factually without interpreting evidence",
            "  Request re-runs — ask to see any command output again",
            "  Direct revisions — identify issues to fix before attesting",
            "",
            "When you are satisfied, provide your attestation:",
            "",
            f'  gz closeout {adr_id} --ceremony --attest "Completed"',
            f'  gz closeout {adr_id} --ceremony --attest "Completed - Partial: [reason]"',
            f'  gz closeout {adr_id} --ceremony --attest "Dropped - [reason]"',
            "",
            "To pause for revisions (revise and resubmit):",
            "",
            f"  gz closeout {adr_id} --ceremony --pause",
            "",
            "I await your decision.",
        ]
    )


def render_step_7_closeout(adr_id: str) -> str:
    """Instruct the agent to run the closeout pipeline."""
    return "\n".join(
        [
            "CLOSEOUT PIPELINE — Agent Executes, Human Observes",
            "",
            "Run the closeout pipeline (quality gates, attestation record,",
            "version bump, closeout form):",
            "",
            f"  uv run gz closeout {adr_id}",
            "",
            "Present each sub-action and its result as it runs.",
            "",
            f"After closeout completes, run `gz closeout {adr_id} --ceremony --next`.",
        ]
    )


def render_step_8_issues(adr_id: str) -> str:
    """Instruct the agent to investigate and close related GitHub issues."""
    return "\n".join(
        [
            "GITHUB ISSUES — Investigate and Close",
            "",
            "Find related issues:",
            "",
            f'  gh issue list --search "{adr_id}" --state open',
            "",
            "For each issue, present: number, title, proposed disposition, reasoning.",
            "Wait for human confirmation before closing.",
            "",
            f'  gh issue close <number> --comment "Resolved by {adr_id} closeout."',
            "",
            "If any issue reveals incomplete work, flag it as a blocker.",
            "",
            f"After reviewing issues, run `gz closeout {adr_id} --ceremony --next`.",
        ]
    )


def render_step_9_release_notes(adr_id: str, is_foundation: bool) -> str:
    """Release notes — foundation-aware."""
    if is_foundation:
        return "\n".join(
            [
                "RELEASE NOTES — Foundation Patch",
                "",
                f"{adr_id} is a foundation ADR (0.0.x).",
                "Foundation patches contribute to the next batch release.",
                "",
                "Note: ADR-0.0.15 (ghi-driven-patch-release-ceremony) will",
                "formalize the foundation patch release flow.",
                "",
                "Ensure this ADR's contributions are noted for the next release.",
                "",
                f"Run `gz closeout {adr_id} --ceremony --next` to proceed.",
            ]
        )
    return "\n".join(
        [
            "RELEASE NOTES — Update RELEASE_NOTES.md",
            "",
            "Add a new release entry for this ADR:",
            "",
            "  ## vX.Y.Z (YYYY-MM-DD)",
            f"  **ADR:** {adr_id}",
            "  [Brief description of delivered value]",
            "  ### Delivered",
            "  - [Key deliverables from each OBPI]",
            "  ### Gate Evidence",
            "  All 5 GovZero gates satisfied.",
            "",
            f"After updating, run `gz closeout {adr_id} --ceremony --next`.",
        ]
    )


def render_step_10_release(adr_id: str, is_foundation: bool) -> str:
    """GitHub release — the certificate."""
    if is_foundation:
        return "\n".join(
            [
                "RELEASE — Foundation (Deferred)",
                "",
                "Foundation ADRs do not create standalone GitHub releases.",
                "The release will be included in the next patch version.",
                "",
                f"Run `gz closeout {adr_id} --ceremony --next` to complete.",
            ]
        )
    return "\n".join(
        [
            "RELEASE — Create GitHub Release",
            "",
            "  # MANDATORY: sync before release",
            "  uv run gz git-sync --apply --lint --test",
            "",
            "  # Verify all version references are in sync",
            "  # (pyproject.toml, README badge, RELEASE_NOTES.md)",
            "",
            '  gh release create vX.Y.Z --title "vX.Y.Z" --notes "..."',
            "",
            f"After creating the release, run `gz closeout {adr_id} --ceremony --next`.",
        ]
    )


def render_step_11_complete(state: CeremonyState) -> str:
    """Ceremony completion — value-landed statement."""
    step_names = {
        1: "Readiness verified",
        2: "Bill of materials presented",
        3: "Docs alignment checked",
        4: "Value walkthrough presented",
        5: "Live demo executed",
        6: "Attestation recorded",
        7: "Closeout pipeline executed",
        8: "GitHub issues reviewed",
        9: "Release notes updated",
        10: "GitHub release created",
        11: "Ceremony complete",
    }
    lines = [
        f"ADR {state.adr_id} CLOSEOUT CEREMONY — COMPLETE",
        "",
        "Steps completed:",
    ]
    for record in state.step_history:
        name = step_names.get(record.step, f"Step {record.step}")
        marker = "  " if record.acknowledged_at else ">>"
        lines.append(f"  {marker} Step {record.step:2d}: {name}")

    if state.attestation:
        lines.append(f"\n  Attestation: {state.attestation}")

    lines.append("")
    lines.append("Value landed. Run `gz git-sync --apply --lint --test` to sync.")
    return "\n".join(lines)
