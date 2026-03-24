"""Audit command implementation."""

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, cast

from gzkit.commands.closeout import _manifest_verification_commands
from gzkit.commands.common import (
    GzCliError,
    _cli_main,
    _reject_pool_adr_for_lifecycle,
    aggregate_audit_evidence,
    console,
    ensure_initialized,
    get_git_user,
    get_project_root,
    load_manifest,
    resolve_adr_file,
    resolve_adr_ledger_id,
)
from gzkit.ledger import Ledger, audit_generated_event, audit_receipt_emitted_event
from gzkit.lifecycle import InvalidTransitionError, LifecycleStateMachine
from gzkit.templates import render_template


def _run_audit_verifications(
    commands: list[tuple[str, str]],
    proofs_dir: Path,
    project_root: Path,
) -> tuple[list[dict[str, Any]], int]:
    """Execute verification commands, write proof files, return results and failure count."""
    result_rows: list[dict[str, Any]] = []
    failures = 0
    for label, command in commands:
        result = _cli_main().run_command(command, cwd=project_root)
        proof_file = proofs_dir / f"{label}.txt"
        proof_file.write_text(
            f"$ {command}\n\n[returncode] {result.returncode}\n\n"
            f"[stdout]\n{result.stdout}\n\n[stderr]\n{result.stderr}\n",
            encoding="utf-8",
        )
        result_rows.append(
            {
                "label": label,
                "command": command,
                "returncode": result.returncode,
                "success": result.success,
                "proof_file": str(proof_file.relative_to(project_root)),
            }
        )
        if not result.success:
            failures += 1
    return result_rows, failures


def _format_attestation_content(attestation: dict[str, Any] | None) -> str:
    """Format attestation data as markdown content for the audit template."""
    if attestation:
        return "\n".join(
            [
                f"- Attestor: {attestation['by']}",
                f"- Status: {attestation['status']}",
                f"- Timestamp: {attestation['ts']}",
            ]
        )
    return "No attestation record found."


def _format_gate_results_content(gate_results: list[dict[str, Any]]) -> str:
    """Format gate results as markdown content for the audit template."""
    if gate_results:
        lines = [
            "| Gate | Status | Command | Return Code |",
            "|------|--------|---------|-------------|",
        ]
        for gr in gate_results:
            lines.append(
                f"| {gr['gate']} | {gr['status']} | `{gr['command']}` | {gr['returncode']} |"
            )
        return "\n".join(lines)
    return "No prior gate results recorded."


def _format_obpi_summary_content(obpi_completions: list[dict[str, Any]]) -> str:
    """Format OBPI completion data as markdown content for the audit template."""
    if obpi_completions:
        lines = [
            "| OBPI | Receipt Event | Completed |",
            "|------|---------------|-----------|",
        ]
        for obpi in obpi_completions:
            completed = "Yes" if obpi["ledger_completed"] else "No"
            receipt = obpi.get("receipt_event") or "\u2014"
            lines.append(f"| {obpi['obpi_id']} | {receipt} | {completed} |")
        return "\n".join(lines)
    return "No OBPI completion records found."


def _format_evidence_links_content(evidence_links: list[str]) -> str:
    """Format evidence links as markdown content for the audit template."""
    if evidence_links:
        lines: list[str] = []
        for link in evidence_links:
            if link.endswith("CLOSEOUT.md"):
                lines.append(f"- Closeout: `{link}`")
            else:
                lines.append(f"- `{link}`")
        return "\n".join(lines)
    return "No evidence links found."


def _collect_evidence_links(
    adr_file: Path,
    project_root: Path,
) -> list[str]:
    """Collect filesystem-based evidence links for the audit report."""
    obpi_dir = adr_file.parent / "obpis"
    obpi_files = sorted(obpi_dir.glob("OBPI-*.md")) if obpi_dir.exists() else []
    closeout_form = adr_file.parent / "closeout" / "CLOSEOUT.md"

    evidence_links: list[str] = [f.relative_to(project_root).as_posix() for f in obpi_files]
    if closeout_form.exists():
        evidence_links.append(closeout_form.relative_to(project_root).as_posix())
    return evidence_links


def _write_audit_artifacts(
    adr_id: str,
    adr_file: Path,
    audit_dir: Path,
    proofs_dir: Path,
    result_rows: list[dict[str, Any]],
    project_root: Path,
    ledger: "Ledger | None" = None,
) -> tuple[Path, Path, dict[str, Any]]:
    """Write AUDIT_PLAN.md and AUDIT.md from templates, return paths and enrichment data."""
    adr_path = adr_file.relative_to(project_root).as_posix()
    generated_ts = date.today().isoformat()

    # --- AUDIT_PLAN.md ---
    verification_commands = "\n".join(f"- `{row['command']}`" for row in result_rows)
    plan_content = render_template(
        "audit_plan",
        adr_id=adr_id,
        adr_path=adr_path,
        generated_ts=generated_ts,
        verification_commands_section=verification_commands,
        proofs_dir=proofs_dir.relative_to(project_root).as_posix(),
    )
    plan_file = audit_dir / "AUDIT_PLAN.md"
    plan_file.write_text(plan_content, encoding="utf-8")

    # --- Aggregate evidence from ledger ---
    evidence_links = _collect_evidence_links(adr_file, project_root)
    if ledger is not None:
        graph = ledger.get_artifact_graph()
        aggregated = aggregate_audit_evidence(ledger, adr_id, graph)
    else:
        aggregated = {
            "obpi_completions": [],
            "gate_results": [],
            "attestation": None,
            "closeout": None,
        }

    # --- Extract typed values from aggregated evidence ---
    obpi_completions = cast(list[dict[str, Any]], aggregated["obpi_completions"])
    gate_results = cast(list[dict[str, Any]], aggregated["gate_results"])
    attestation_data = cast(dict[str, Any] | None, aggregated["attestation"])

    # --- Format sections for template ---
    attestation_section = _format_attestation_content(attestation_data)
    gate_results_section = _format_gate_results_content(gate_results)
    obpi_summary_section = _format_obpi_summary_content(obpi_completions)
    evidence_links_section = _format_evidence_links_content(evidence_links)

    verification_lines: list[str] = []
    for row in result_rows:
        row_status = "PASS" if row["success"] else "FAIL"
        verification_lines.append(
            f"- **{row['label']}**: {row_status} (`{row['command']}`) -> `{row['proof_file']}`"
        )
    verification_results_section = "\n".join(verification_lines)

    # --- AUDIT.md ---
    audit_content = render_template(
        "audit",
        adr_id=adr_id,
        adr_path=adr_path,
        generated_ts=generated_ts,
        attestation_section=attestation_section,
        gate_results_section=gate_results_section,
        obpi_summary_section=obpi_summary_section,
        verification_results_section=verification_results_section,
        evidence_links_section=evidence_links_section,
    )
    audit_file = audit_dir / "AUDIT.md"
    audit_file.write_text(audit_content, encoding="utf-8")

    # --- Build enrichment dict for JSON output compatibility ---
    enrichment: dict[str, Any] = {
        "attestation_record": {
            "attestor": attestation_data["by"],
            "status": attestation_data["status"],
            "timestamp": attestation_data["ts"],
        }
        if attestation_data
        else {},
        "gate_results": gate_results,
        "evidence_links": evidence_links,
    }
    return plan_file, audit_file, enrichment


def audit_cmd(adr: str, as_json: bool, dry_run: bool) -> None:
    """Run the end-to-end audit pipeline for an ADR.

    Executes verification commands, creates proof artifacts, emits a
    validation receipt to the ledger, and transitions the ADR to Validated.
    """
    config = ensure_initialized()
    project_root = get_project_root()
    manifest = load_manifest(project_root)
    ledger = Ledger(project_root / config.paths.ledger)

    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)
    adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    adr_id = resolve_adr_ledger_id(adr_file, adr_id, ledger)
    _reject_pool_adr_for_lifecycle(adr_id, "audited")
    graph = ledger.get_artifact_graph()
    adr_info = graph.get(adr_id)
    if not adr_info or adr_info.get("type") != "adr":
        raise GzCliError(f"ADR not found in ledger: {adr_id}")
    if not adr_info.get("attested"):
        blocker = {
            "adr": adr_id,
            "allowed": False,
            "reason": "gz audit requires human attestation first (Gate 5).",
            "next_steps": [
                f"uv run gz closeout {adr_id}",
                f"uv run gz attest {adr_id} --status completed",
            ],
            "dry_run": dry_run,
        }
        if as_json:
            print(json.dumps(blocker, indent=2))
        else:
            console.print("[red]Audit blocked:[/red] human attestation is required first.")
            console.print(f"  - Run: uv run gz closeout {adr_id}")
            console.print(f"  - Run: uv run gz attest {adr_id} --status completed")
        raise SystemExit(1)

    audit_dir = adr_file.parent / "audit"
    proofs_dir = audit_dir / "proofs"
    include_docs = (project_root / "mkdocs.yml").exists()
    commands = _manifest_verification_commands(manifest, include_docs=include_docs)

    if dry_run:
        dry_payload = {
            "adr": adr_id,
            "dry_run": True,
            "audit_dir": str(audit_dir.relative_to(project_root)),
            "proofs_dir": str(proofs_dir.relative_to(project_root)),
            "commands": [command for _label, command in commands],
            "validation_receipt": {"would_emit": True, "event": "validated"},
            "status_transition": {"from": "Completed", "to": "Validated"},
        }
        if as_json:
            print(json.dumps(dry_payload, indent=2))
            return
        console.print("[yellow]Dry run:[/yellow] no files will be written.")
        console.print(f"  Would create: {audit_dir.relative_to(project_root)}")
        console.print(f"  Would create: {proofs_dir.relative_to(project_root)}")
        for _label, command in commands:
            console.print(f"  Would run: {command}")
        console.print("  Would emit validation receipt to ledger")
        console.print("  Would transition ADR status: Completed -> Validated")
        return

    proofs_dir.mkdir(parents=True, exist_ok=True)
    result_rows, failures = _run_audit_verifications(commands, proofs_dir, project_root)
    plan_file, audit_file, enrichment = _write_audit_artifacts(
        adr_id,
        adr_file,
        audit_dir,
        proofs_dir,
        result_rows,
        project_root,
        ledger=ledger,
    )

    # Record audit_generated event in ledger
    ledger.append(
        audit_generated_event(
            adr_id=adr_id,
            audit_file=str(audit_file.relative_to(project_root)),
            audit_plan_file=str(plan_file.relative_to(project_root)),
            passed=failures == 0,
        )
    )

    # Emit validation receipt (always -- even on failure, to record the audit)
    pass_count = sum(1 for r in result_rows if r["success"])
    fail_count = failures
    auditor = get_git_user()
    receipt_evidence = {
        "audit_date": date.today().isoformat(),
        "pass_count": pass_count,
        "fail_count": fail_count,
        "audit_file": str(audit_file.relative_to(project_root)),
        "audit_plan_file": str(plan_file.relative_to(project_root)),
        "proofs_dir": str(proofs_dir.relative_to(project_root)),
    }
    ledger.append(
        audit_receipt_emitted_event(
            adr_id=adr_id,
            receipt_event="validated",
            attestor=auditor,
            evidence=receipt_evidence,
        )
    )

    # Transition ADR to Validated only if all checks passed and ADR is in Completed state.
    status_transition = None
    if failures == 0:
        semantics = Ledger.derive_adr_semantics(adr_info)
        current_state = semantics["lifecycle_status"]
        if current_state != "Completed":
            print(
                f"Warning: ADR {adr_id} is in '{current_state}' state, not 'Completed'. "
                "Skipping lifecycle transition to Validated.",
                file=sys.stderr,
            )
        else:
            try:
                sm = LifecycleStateMachine(ledger)
                sm.transition(adr_id, "ADR", "Completed", "Validated")
                status_transition = {"from": "Completed", "to": "Validated"}
            except InvalidTransitionError:
                print(
                    f"Warning: lifecycle transition Completed -> Validated failed for {adr_id}. "
                    "The ADR state may be inconsistent.",
                    file=sys.stderr,
                )

    output = {
        "adr": adr_id,
        "audit_file": str(audit_file.relative_to(project_root)),
        "audit_plan_file": str(plan_file.relative_to(project_root)),
        "results": result_rows,
        "passed": failures == 0,
        "validation_receipt": {
            "event": "validated",
            "attestor": auditor,
            "evidence": receipt_evidence,
        },
        "status_transition": status_transition,
        "attestation_record": enrichment["attestation_record"],
        "gate_results": enrichment["gate_results"],
        "evidence_links": enrichment["evidence_links"],
    }
    if as_json:
        print(json.dumps(output, indent=2))
    else:
        console.print(f"[bold]Audit results for {adr_id}[/bold]")
        for row in result_rows:
            row_status = "[green]PASS[/green]" if row["success"] else "[red]FAIL[/red]"
            console.print(f"  {row['label']}: {row_status}")
        console.print(f"Audit plan: {plan_file.relative_to(project_root)}")
        console.print(f"Audit report: {audit_file.relative_to(project_root)}")
        console.print(f"Validation receipt: emitted (by {auditor})")
        if status_transition:
            console.print("ADR status: Completed -> Validated")
        else:
            console.print("[yellow]ADR status: NOT transitioned (failures detected)[/yellow]")

    if failures:
        raise SystemExit(1)
