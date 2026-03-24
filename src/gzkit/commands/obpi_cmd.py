"""OBPI emit-receipt, pipeline, and validate command implementations."""

import json
import re
import shlex
from pathlib import Path
from typing import Any, cast

from gzkit.commands.adr_audit import (
    _requires_human_obpi_attestation,
    _validate_explicit_req_proof_inputs,
    _validate_obpi_completion_evidence,
)
from gzkit.commands.common import (
    GzCliError,
    _cli_main,
    _is_pool_adr_id,
    console,
    ensure_initialized,
    get_project_root,
    resolve_adr_file,
    resolve_obpi_file,
)
from gzkit.commands.status import _inspect_obpi_brief
from gzkit.decomposition import extract_markdown_section
from gzkit.hooks.obpi import ObpiValidator
from gzkit.ledger import (
    Ledger,
    normalize_req_proof_inputs,
    obpi_receipt_emitted_event,
    resolve_adr_lane,
)
from gzkit.pipeline_runtime import (
    clear_stale_pipeline_markers,
    load_plan_audit_receipt,
    pipeline_command,
    pipeline_concurrency_blockers,
    pipeline_git_sync_command,
    pipeline_marker_payload,
    pipeline_plans_dir,
    pipeline_stage_labels,
    refresh_pipeline_markers,
    remove_pipeline_markers,
    write_pipeline_markers,
)
from gzkit.utils import capture_validation_anchor


def obpi_emit_receipt_cmd(
    obpi: str,
    receipt_event: str,
    attestor: str,
    evidence_json: str | None,
    dry_run: bool,
) -> None:
    """Emit an OBPI receipt event anchored in the ledger."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    obpi_file, obpi_id = resolve_obpi_file(project_root, config, ledger, obpi)
    graph = ledger.get_artifact_graph()
    obpi_info = graph.get(obpi_id, {})
    if obpi_info.get("type") != "obpi":
        raise GzCliError(f"OBPI not found in ledger: {obpi_id}")
    parent_adr = obpi_info.get("parent")
    if isinstance(parent_adr, str) and _is_pool_adr_id(parent_adr):
        raise GzCliError(
            "Pool-linked OBPIs cannot be issued receipts: "
            f"{obpi_id} (parent: {parent_adr}). Promote parent ADR first."
        )

    evidence: dict[str, Any] | None = None
    if evidence_json:
        try:
            parsed = json.loads(evidence_json)
        except json.JSONDecodeError as exc:
            raise GzCliError(f"Invalid --evidence-json: {exc}") from exc
        if not isinstance(parsed, dict):
            raise GzCliError("--evidence-json must decode to a JSON object")
        evidence = parsed

    parent_lane = config.mode
    if isinstance(parent_adr, str) and parent_adr:
        parent_info = graph.get(parent_adr, {})
        parent_lane = resolve_adr_lane(parent_info, config.mode)

    obpi_completion: str | None = None
    anchor: dict[str, str] | None = None
    if receipt_event == "completed":
        obpi_content = obpi_file.read_text(encoding="utf-8")
        evidence, obpi_completion, anchor = _validate_obpi_completion_evidence(
            project_root=project_root,
            obpi_content=obpi_content,
            evidence=evidence,
            parent_adr=parent_adr if isinstance(parent_adr, str) else None,
            parent_lane=parent_lane,
            attestor=attestor,
        )
    elif evidence is not None:
        evidence = dict(evidence)
        explicit_req_proof_inputs = _validate_explicit_req_proof_inputs(
            evidence.get("req_proof_inputs")
        )
        evidence["req_proof_inputs"] = explicit_req_proof_inputs or normalize_req_proof_inputs(
            None,
            fallback_key_proof=cast(str | None, evidence.get("key_proof")),
        )
        evidence.setdefault("parent_lane", parent_lane)
        if isinstance(parent_adr, str) and parent_adr:
            evidence.setdefault("parent_adr", parent_adr)
        evidence.setdefault("obpi_completion", "not_completed")
    if receipt_event != "completed":
        anchor = capture_validation_anchor(project_root, parent_adr)
    event = obpi_receipt_emitted_event(
        obpi_id=obpi_id,
        receipt_event=receipt_event,
        attestor=attestor,
        evidence=evidence,
        parent_adr=parent_adr if isinstance(parent_adr, str) else None,
        obpi_completion=obpi_completion,
        anchor=anchor,
    )

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no ledger event will be written.")
        console.print(json.dumps(event.model_dump(), indent=2))
        return

    ledger.append(event)
    console.print("[green]OBPI receipt emitted.[/green]")
    console.print(f"  OBPI: {obpi_id}")
    if isinstance(parent_adr, str) and parent_adr:
        console.print(f"  Parent ADR: {parent_adr}")
    console.print(f"  Event: {receipt_event}")
    console.print(f"  Attestor: {attestor}")


def _pipeline_verification_commands(obpi_content: str, lane: str) -> list[str]:
    """Parse the Verification block into executable shell commands."""
    section = extract_markdown_section(obpi_content, "Verification") or ""
    matches = re.findall(r"```bash\n(.*?)```", section, flags=re.DOTALL)
    commands: list[str] = []
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
            "--attestor human:<name> --evidence-json '<json>'"
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
    steps: list[tuple[str, str]] = [
        (emit_cmd, "Emit completion receipt"),
        (f"uv run gz obpi reconcile {obpi_id}", "Reconcile OBPI"),
        (f"uv run gz adr status {resolved_parent} --json", "Refresh parent ADR view"),
        (pipeline_git_sync_command(), "Guarded repository sync"),
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

    remove_pipeline_markers(plans_dir, obpi_id)
    console.print("")
    console.print(f"Pipeline complete. {obpi_id} synced and lock released.")


def obpi_pipeline_cmd(
    obpi: str,
    start_from: str | None,
    *,
    clear_stale: bool = False,
    attestor: str | None = None,
    evidence_json: str | None = None,
) -> None:
    """Launch the OBPI pipeline runtime surface for one OBPI."""
    config = ensure_initialized()
    project_root = get_project_root()

    if clear_stale:
        plans_dir = pipeline_plans_dir(project_root)
        if plans_dir.is_dir():
            removed = clear_stale_pipeline_markers(plans_dir)
            if removed:
                for marker_path, marker_obpi in removed:
                    console.print(f"Removed stale marker: {marker_path.name} ({marker_obpi})")
            else:
                console.print("No stale markers found.")
        else:
            console.print("No stale markers found.")
        return

    ledger = Ledger(project_root / config.paths.ledger)

    obpi_file, obpi_id = resolve_obpi_file(project_root, config, ledger, obpi)
    graph = ledger.get_artifact_graph()
    info = graph.get(obpi_id, {})
    if info.get("type") != "obpi":
        raise GzCliError(f"OBPI not found in ledger: {obpi_id}")

    parent_adr = cast(str | None, info.get("parent"))
    if not parent_adr:
        raise GzCliError(f"OBPI is missing a parent ADR link in the ledger: {obpi_id}")
    if _is_pool_adr_id(parent_adr):
        raise GzCliError(f"Pool-linked OBPI cannot enter the pipeline: {obpi_id}")

    _adr_file, resolved_parent = resolve_adr_file(project_root, config, parent_adr)
    obpi_content = obpi_file.read_text(encoding="utf-8")
    inspection = _inspect_obpi_brief(project_root, obpi_file, obpi_id, graph)
    if bool(inspection.get("file_completed")):
        _print_pipeline_blockers(
            obpi_id, ["OBPI brief is already completed; pipeline launch is not allowed"]
        )
        raise SystemExit(1)

    plans_dir = pipeline_plans_dir(project_root)
    blockers = pipeline_concurrency_blockers(plans_dir, obpi_id)
    receipt_state, warnings, receipt = load_plan_audit_receipt(plans_dir, obpi_id)
    if receipt_state == "fail":
        _print_pipeline_blockers(
            obpi_id, ["plan-audit receipt verdict is FAIL; correct plan alignment first"]
        )
        raise SystemExit(1)
    if blockers:
        _print_pipeline_blockers(obpi_id, blockers)
        raise SystemExit(1)

    lane = resolve_adr_lane(graph.get(resolved_parent, {}), config.mode)
    requires_human_attestation = _requires_human_obpi_attestation(resolved_parent, lane)
    marker_payload = pipeline_marker_payload(
        obpi_id,
        resolved_parent,
        lane,
        start_from,
        receipt_state,
        requires_human_attestation=requires_human_attestation,
    )
    per_obpi_marker, legacy_marker = write_pipeline_markers(plans_dir, marker_payload)
    stage_labels = pipeline_stage_labels(start_from)

    _print_pipeline_header(
        obpi_id=obpi_id,
        resolved_parent=resolved_parent,
        obpi_file=obpi_file,
        project_root=project_root,
        lane=lane,
        start_from=start_from,
        receipt_state=receipt_state,
        stage_labels=stage_labels,
        per_obpi_marker=per_obpi_marker,
        legacy_marker=legacy_marker,
        warnings=warnings,
        receipt=receipt,
    )

    if start_from is None:
        _print_pipeline_implementation_next_steps(obpi_id)
        return

    if start_from == "verify":
        _run_pipeline_verify_stage(
            project_root=project_root,
            plans_dir=plans_dir,
            obpi_id=obpi_id,
            obpi_content=obpi_content,
            lane=lane,
            resolved_parent=resolved_parent,
            requires_human_attestation=requires_human_attestation,
            attestor=attestor,
            evidence_json=evidence_json,
        )
        return

    if start_from == "ceremony":
        _run_pipeline_ceremony_stage(
            project_root=project_root,
            plans_dir=plans_dir,
            obpi_id=obpi_id,
            obpi_content=obpi_content,
            resolved_parent=resolved_parent,
            requires_human_attestation=requires_human_attestation,
            attestor=attestor,
            evidence_json=evidence_json,
        )
        return

    if start_from == "sync":
        if not attestor:
            raise GzCliError(
                "--attestor is required for --from=sync. "
                "Use --attestor human:<name> for attested OBPIs "
                "or --attestor agent:<name> for self-closed OBPIs."
            )
        if not evidence_json:
            raise GzCliError(
                "--evidence-json is required for --from=sync. "
                "Must include value_narrative and key_proof fields."
            )
        _run_pipeline_sync_stage(
            project_root=project_root,
            plans_dir=plans_dir,
            obpi_id=obpi_id,
            resolved_parent=resolved_parent,
            attestor=attestor,
            evidence_json=evidence_json,
        )
        return


def _validate_brief_structure(project_root: Path, brief_path: Path) -> list[str]:
    """Validate OBPI brief structural conformance against the OBPI schema.

    Checks required frontmatter fields and required section headings,
    independent of completion status.
    """
    from gzkit.validate import validate_document  # noqa: PLC0415

    schema_errors = validate_document(brief_path, "obpi")
    return [
        f"[{e.type}] {e.message}" + (f" (field: {e.field})" if e.field else "")
        for e in schema_errors
    ]


def obpi_validate_cmd(obpi_path: str | None, adr_id: str | None) -> None:
    """Validate OBPI brief(s) for structural conformance and completion readiness."""
    config = ensure_initialized()
    project_root = get_project_root()
    validator = ObpiValidator(project_root)

    if adr_id and not obpi_path:
        _obpi_validate_batch(project_root, config, validator, adr_id)
        return

    if not obpi_path:
        console.print("[red]Error:[/red] Provide an OBPI path or --adr flag.")
        raise SystemExit(1)

    path = Path(obpi_path)
    if not path.is_absolute():
        path = project_root / path

    # Structural conformance check (always runs, regardless of status)
    structure_errors = _validate_brief_structure(project_root, path)

    # Completion readiness check (ObpiValidator)
    completion_errors = validator.validate_file(path)

    all_errors = structure_errors + completion_errors
    if all_errors:
        console.print(f"[red]OBPI Validation Failed:[/red] {path.name}")
        console.print("BLOCKERS:")
        for error in all_errors:
            console.print(f"- {error}")
        raise SystemExit(1)

    console.print(f"[green]OBPI Validation Passed:[/green] {path.name}")


def _obpi_validate_batch(
    project_root: Path,
    config: Any,
    validator: ObpiValidator,
    adr_id: str,
) -> None:
    """Validate all OBPI briefs under an ADR package."""
    from gzkit.ledger import Ledger  # noqa: PLC0415

    ledger = Ledger(project_root / config.paths.ledger)
    adr_input = adr_id if adr_id.startswith("ADR-") else f"ADR-{adr_id}"
    canonical = ledger.canonicalize_id(adr_input)
    adr_file, resolved = resolve_adr_file(project_root, config, canonical)

    obpi_dir = adr_file.parent / "obpis"
    if not obpi_dir.is_dir():
        console.print(f"[red]No obpis/ directory found for {resolved}[/red]")
        raise SystemExit(1)

    briefs = sorted(obpi_dir.glob("OBPI-*.md"))
    if not briefs:
        console.print(f"[red]No OBPI briefs found in {obpi_dir}[/red]")
        raise SystemExit(1)

    total_errors = 0
    for brief_path in briefs:
        structure_errors = _validate_brief_structure(project_root, brief_path)
        completion_errors = validator.validate_file(brief_path)
        all_errors = structure_errors + completion_errors
        if all_errors:
            total_errors += 1
            console.print(f"[red]FAIL[/red] {brief_path.name}")
            for error in all_errors:
                console.print(f"  - {error}")
        else:
            console.print(f"[green]PASS[/green] {brief_path.name}")

    console.print()
    if total_errors:
        console.print(f"[red]{total_errors}/{len(briefs)} briefs failed validation[/red]")
        raise SystemExit(1)
    console.print(f"[green]All {len(briefs)} briefs passed validation[/green]")
