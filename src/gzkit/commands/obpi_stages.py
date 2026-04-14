"""OBPI pipeline stage execution functions.

Extracted from obpi_cmd.py to stay under the 600-line module cap.
Covers: verification command parsing, pipeline output helpers, and
stage runners (verify, ceremony, sync).
"""

from __future__ import annotations

import json
import re
import shlex
from pathlib import Path
from typing import Any

from gzkit.commands.common import _cli_main, console
from gzkit.decomposition import extract_markdown_section
from gzkit.pipeline_runtime import (
    pipeline_command,
    pipeline_git_sync_command,
    refresh_pipeline_markers,
    remove_pipeline_artifacts,
)

BASELINE_VERIFICATION = [
    "uv run gz lint",
    "uv run gz typecheck",
    "uv run gz test",
]


def _pipeline_verification_commands(obpi_content: str, lane: str) -> list[str]:
    """Parse the Verification block into executable shell commands."""
    commands: list[str] = list(BASELINE_VERIFICATION)
    section = extract_markdown_section(obpi_content, "Verification") or ""
    matches = re.findall(r"```bash\n(.*?)```", section, flags=re.DOTALL)
    for block in matches:
        for raw_line in block.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or line == "command --to --verify":
                continue
            commands.append(line)
    if lane == "heavy":
        commands.extend(["uv run mkdocs build --strict", "uv run -m behave features/"])

    deduped: list[str] = []
    seen: set[str] = set()
    for command in commands:
        if command in seen:
            continue
        seen.add(command)
        deduped.append(command)
    return deduped


# ---------------------------------------------------------------------------
# Pipeline output helpers
# ---------------------------------------------------------------------------


def _print_pipeline_blockers(obpi_id: str, blockers: list[str]) -> None:
    """Render standard pipeline blocker output for one OBPI."""
    console.print(f"[bold]OBPI pipeline:[/bold] {obpi_id}")
    console.print("BLOCKERS:")
    for blocker in blockers:
        console.print(f"- {blocker}")


def _print_pipeline_header(
    *,
    obpi_id: str,
    resolved_parent: str,
    obpi_file: Path,
    project_root: Path,
    lane: str,
    start_from: str | None,
    receipt_state: str,
    stage_labels: list[str],
    per_obpi_marker: Path,
    legacy_marker: Path,
    warnings: list[str],
    receipt: dict[str, Any] | None,
) -> None:
    """Render the shared pipeline header."""
    console.print(f"[bold]OBPI pipeline:[/bold] {obpi_id}")
    console.print(f"  Parent ADR: {resolved_parent}")
    console.print(f"  Brief: {obpi_file.relative_to(project_root)}")
    console.print(f"  Lane: {lane}")
    console.print(f"  Entry: {start_from or 'full'}")
    console.print(f"  Receipt: {receipt_state.upper()}")
    console.print("  Stages: " + " -> ".join(stage_labels))
    console.print(f"  Marker: {per_obpi_marker.relative_to(project_root)}")
    console.print(f"  Legacy Marker: {legacy_marker.relative_to(project_root)}")
    if receipt and receipt.get("plan_file"):
        console.print(f"  Plan File: {receipt['plan_file']}")
    for warning in warnings:
        console.print(f"  Warning: {warning}")


def _print_pipeline_implementation_next_steps(obpi_id: str) -> None:
    """Render Stage 2 guidance after a full launch."""
    console.print("")
    console.print("Next:")
    console.print("- Implement the approved OBPI within the brief allowlist.")
    console.print(f"- When implementation is ready, run: {pipeline_command(obpi_id, 'verify')}")
    console.print("- Keep the active pipeline markers in place during implementation.")


# ---------------------------------------------------------------------------
# Stage runners
# ---------------------------------------------------------------------------


def _run_pipeline_verify_stage(
    *,
    project_root: Path,
    plans_dir: Path,
    obpi_id: str,
    obpi_content: str,
    lane: str,
    resolved_parent: str,
    requires_human_attestation: bool,
    attestor: str | None,
    evidence_json: str | None,
) -> None:
    """Run the verify stage, then chain into ceremony and sync."""
    commands = _pipeline_verification_commands(obpi_content, lane)
    verification_results: list[tuple[str, bool, str]] = []
    failures: list[tuple[str, str]] = []
    console.print("")
    console.print("[bold]Stage 3: Verification[/bold]")
    for command in commands:
        result = _cli_main().run_command(command, cwd=project_root)
        if result.success:
            console.print(f"[green]PASS[/green] {command}")
            verification_results.append((command, True, "pass"))
            continue
        detail = (result.stderr or result.stdout or f"exit code {result.returncode}").strip()
        failures.append((command, detail))
        verification_results.append((command, False, detail))
        console.print(f"[red]FAIL[/red] {command}")
    if failures:
        refresh_pipeline_markers(
            plans_dir,
            obpi_id,
            blockers=[f"{command}: {detail}" for command, detail in failures],
        )
        console.print("BLOCKERS:")
        for command, detail in failures:
            console.print(f"- {command}: {detail}")
        raise SystemExit(1)

    console.print("")
    console.print("Verification passed. Chaining into ceremony.")

    _run_pipeline_ceremony_stage(
        project_root=project_root,
        plans_dir=plans_dir,
        obpi_id=obpi_id,
        obpi_content=obpi_content,
        resolved_parent=resolved_parent,
        requires_human_attestation=requires_human_attestation,
        attestor=attestor,
        evidence_json=evidence_json,
        verification_results=verification_results,
    )


def _run_pipeline_ceremony_stage(
    *,
    project_root: Path,
    plans_dir: Path,
    obpi_id: str,
    obpi_content: str,
    resolved_parent: str,
    requires_human_attestation: bool,
    attestor: str | None,
    evidence_json: str | None,
    verification_results: list[tuple[str, bool, str]] | None = None,
) -> None:
    """Render evidence and either pause for human gate or self-close and chain into sync."""
    console.print("")
    console.print("[bold]Stage 4: Ceremony[/bold]")

    if verification_results:
        console.print("")
        console.print("Verification evidence:")
        for command, passed, detail in verification_results:
            tag = "[green]PASS[/green]" if passed else f"[red]FAIL[/red] {detail}"
            console.print(f"  {command}: {tag}")

    if requires_human_attestation:
        console.print("")
        console.print("[bold]Human attestation required.[/bold]")
        console.print("Present verification evidence to the human for attestation.")
        console.print("After receiving attestation, complete the pipeline with:")
        console.print(
            f"  uv run gz obpi pipeline {obpi_id} --from=sync "
            "--attestor <name> --evidence-json '<json>'"
        )
        console.print("")
        console.print(
            "The --evidence-json must include: value_narrative, key_proof, "
            "human_attestation (true), attestation_text, attestation_date."
        )
        return

    console.print("Human attestation not required. Self-closing and chaining into sync.")

    effective_attestor = attestor or "agent:pipeline-autoclose"
    effective_evidence = evidence_json
    if not effective_evidence:
        objective = extract_markdown_section(obpi_content, "Objective") or obpi_id
        passed_commands = [cmd for cmd, passed, _ in (verification_results or []) if passed]
        key_proof = "All verification checks passed: " + ", ".join(passed_commands)
        auto_evidence = {
            "value_narrative": objective.strip()[:500],
            "key_proof": key_proof[:500],
        }
        effective_evidence = json.dumps(auto_evidence)

    _run_pipeline_sync_stage(
        project_root=project_root,
        plans_dir=plans_dir,
        obpi_id=obpi_id,
        resolved_parent=resolved_parent,
        attestor=effective_attestor,
        evidence_json=effective_evidence,
    )


def _run_pipeline_sync_stage(
    *,
    project_root: Path,
    plans_dir: Path,
    obpi_id: str,
    resolved_parent: str,
    attestor: str,
    evidence_json: str,
) -> None:
    """Run Stage 5: sync and account deterministically, then clear markers."""
    console.print("")
    console.print("[bold]Stage 5: Sync And Account[/bold]")

    emit_cmd = (
        f"uv run gz obpi emit-receipt {obpi_id}"
        f" --event completed"
        f" --attestor {shlex.quote(attestor)}"
        f" --evidence-json {shlex.quote(evidence_json)}"
    )
    # GHI #36: Sync first so the receipt captures a clean anchor (commit hash
    # from synced implementation, dirty=false).  Accounting changes (ledger
    # write, frontmatter reconcile) are committed in a lightweight follow-up.
    steps: list[tuple[str, str]] = [
        (pipeline_git_sync_command(), "Guarded repository sync"),
        (emit_cmd, "Emit completion receipt"),
        (f"uv run gz obpi reconcile {obpi_id}", "Reconcile OBPI"),
        (f"uv run gz adr status {resolved_parent} --json", "Refresh parent ADR view"),
    ]

    for command, label in steps:
        console.print(f"  {label}...")
        result = _cli_main().run_command(command, cwd=project_root)
        if result.success:
            console.print(f"  [green]PASS[/green] {label}")
        else:
            detail = (result.stderr or result.stdout or f"exit code {result.returncode}").strip()
            console.print(f"  [red]FAIL[/red] {label}")
            if detail:
                for line in detail.splitlines()[:10]:
                    console.print(f"    {line}")
            console.print(f"Stage 5 failed at: {label}")
            raise SystemExit(1)

    # Lightweight accounting commit — ledger + frontmatter only, no lint/test.
    # Failure is non-fatal: the receipt is sealed and implementation is synced.
    accounting_steps: list[tuple[str, str]] = [
        ("git add -A", "Stage accounting changes"),
        (
            f'git commit -m "chore: record {obpi_id} completion receipt (gz pipeline)"',
            "Commit accounting changes",
        ),
        ("git push", "Push accounting changes"),
    ]
    for command, label in accounting_steps:
        result = _cli_main().run_command(command, cwd=project_root)
        if result.success:
            console.print(f"  [green]PASS[/green] {label}")
        else:
            detail = (result.stderr or result.stdout or "").strip()
            console.print(f"  [yellow]WARN[/yellow] {label}: {detail[:200]}")

    remove_pipeline_artifacts(plans_dir, obpi_id)
    console.print("")
    console.print(f"Pipeline complete. {obpi_id} synced and lock released.")
