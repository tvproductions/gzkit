"""OBPI emit-receipt, pipeline, and validate command implementations."""

import json
from pathlib import Path
from typing import Any, cast

from gzkit.commands.adr_audit import (
    ATTESTATION_TYPE_OPERATOR_VERBATIM,
    _requires_human_obpi_attestation,
    _validate_explicit_req_proof_inputs,
    _validate_obpi_completion_evidence,
)
from gzkit.commands.common import (
    GzCliError,
    _is_pool_adr_id,
    console,
    ensure_initialized,
    get_project_root,
    resolve_adr_file,
    resolve_obpi_file,
)
from gzkit.commands.obpi_stages import (  # noqa: F401
    BASELINE_VERIFICATION,
    _pipeline_verification_commands,
    _print_pipeline_blockers,
    _print_pipeline_header,
    _print_pipeline_implementation_next_steps,
    _run_pipeline_ceremony_stage,
    _run_pipeline_sync_stage,
    _run_pipeline_verify_stage,
)
from gzkit.commands.status import _inspect_obpi_brief
from gzkit.events import EventAnchor
from gzkit.hooks.obpi import ObpiValidator
from gzkit.ledger import (
    Ledger,
    normalize_req_proof_inputs,
    obpi_receipt_emitted_event,
    obpi_withdrawn_event,
    parse_frontmatter_value,
    pipeline_launched_event,
    pipeline_marker_purged_event,
    resolve_adr_lane,
)
from gzkit.pipeline_runtime import (
    clear_stale_pipeline_markers,
    load_plan_audit_receipt,
    pipeline_concurrency_blockers,
    pipeline_marker_payload,
    pipeline_plans_dir,
    pipeline_stage_labels,
    purge_orphaned_active_markers,
    write_pipeline_markers,
)
from gzkit.utils import capture_validation_anchor


def obpi_withdraw_cmd(obpi: str, reason: str, dry_run: bool) -> None:
    """Withdraw a phantom or erroneous OBPI from the ledger."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    canonical_id = ledger.canonicalize_id(obpi)
    graph = ledger.get_artifact_graph()
    info = graph.get(canonical_id, {})
    if info.get("type") != "obpi":
        msg = f"OBPI not found in ledger: {canonical_id}"
        raise GzCliError(msg)  # noqa: TRY003
    if info.get("withdrawn"):
        msg = f"OBPI is already withdrawn: {canonical_id}"
        raise GzCliError(msg)  # noqa: TRY003

    parent = info.get("parent", "")
    event = obpi_withdrawn_event(
        obpi_id=canonical_id,
        parent=parent if isinstance(parent, str) else "",
        reason=reason,
    )

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no ledger event will be written.")
        console.print(json.dumps(event.model_dump(), indent=2))
        return

    ledger.append(event)
    console.print("[green]OBPI withdrawn.[/green]")
    console.print(f"  OBPI: {canonical_id}")
    if parent:
        console.print(f"  Parent ADR: {parent}")
    console.print(f"  Reason: {reason}")


def _gate_completed_receipt_binding(
    *,
    obpi_id: str,
    parent_adr: Any,
    parent_lane: str,
    project_root: Path,
    config: Any,
    evidence: dict[str, Any] | None,
    ledger: Ledger,
    attestor: str,
    dry_run: bool,
) -> None:
    """ADR-0.0.24-02 receipt-binding gate wrapper for the emit-receipt path.

    Mirrors ``_gate_completed_receipt_authenticity`` (the GHI #290 gate
    wrapper) so ``obpi_emit_receipt_cmd`` stays below the xenon C-rank
    complexity ceiling. Resolves the parent ADR's ``kind`` from frontmatter
    and dispatches to the shared helper in ``obpi_complete``.
    """
    if dry_run or not isinstance(parent_adr, str) or not parent_adr:
        return
    from gzkit.commands.obpi_complete import (
        _enforce_attestation_receipt_gate,
        _read_adr_kind,
    )

    adr_file_for_kind, _ = resolve_adr_file(project_root, config, parent_adr)
    attestation_text_value = ""
    if isinstance(evidence, dict):
        value = evidence.get("attestation_text") or evidence.get("scope")
        if isinstance(value, str):
            attestation_text_value = value
    _enforce_attestation_receipt_gate(
        obpi_id=obpi_id,
        parent_adr=parent_adr,
        parent_lane=parent_lane,
        parent_kind=_read_adr_kind(adr_file_for_kind),
        attestation_text=attestation_text_value,
        attestor=attestor,
        ledger=ledger,
        project_root=project_root,
        as_json=False,
        dry_run=dry_run,
    )


def _resolve_emit_receipt_authenticity_context(
    *,
    obpi_content: str,
    parent_adr: Any,
    project_root: Path,
    config: Any,
) -> tuple[str | None, str | None]:
    """Return ``(sensitivity, parent_kind)`` for the emit-receipt authenticity gate.

    Extracted from ``obpi_emit_receipt_cmd`` so that path stays under the
    xenon C-rank complexity ceiling (GHI #412 plumbing added the lookup).
    """
    sensitivity_value = parse_frontmatter_value(obpi_content, "sensitivity")
    parent_kind_value: str | None = None
    if isinstance(parent_adr, str) and parent_adr:
        from gzkit.commands.obpi_complete import _read_adr_kind

        adr_file_for_kind, _ = resolve_adr_file(project_root, config, parent_adr)
        parent_kind_value = _read_adr_kind(adr_file_for_kind)
    return sensitivity_value, parent_kind_value


def _gate_completed_receipt_authenticity(
    *,
    obpi_id: str,
    parent_adr: Any,
    attestor: str,
    evidence: dict[str, Any] | None,
    dry_run: bool,
    attestor_present: bool = False,
    project_root: Path | None = None,
    sensitivity: str | None = None,
    parent_kind: str | None = None,
) -> None:
    """Resolve attestation_type for the emit-receipt path.

    Per the canon-owner declaration (AGENTS.md section "Lane & Kind &
    Sensitivity Attestation Matrix"), the operator's verbatim attestation
    relayed via the receipt evidence IS the Gate-5 attestation for every
    lane / kind / sensitivity. The prior TTY-typed ATTEST authenticity gate
    (GHI #290) is no longer invoked; ``attestor`` / ``attestor_present`` /
    ``project_root`` / ``sensitivity`` / ``parent_kind`` are retained on the
    signature for the call graph and are slated for removal with the gate
    scaffolding under a separate ADR. Skipped for --dry-run.
    """
    if dry_run or not isinstance(evidence, dict):
        return
    if evidence.get("attestation_requirement") != "required":
        return
    attestation_text = cast(str, evidence.get("attestation_text", ""))
    if not attestation_text.strip():
        msg = (
            f"Completed receipt for {obpi_id} requires the operator's verbatim "
            "attestation text in --evidence-json (the 'attestation_text' field)."
        )
        raise GzCliError(msg)  # noqa: TRY003
    evidence["attestation_type"] = ATTESTATION_TYPE_OPERATOR_VERBATIM


def obpi_emit_receipt_cmd(
    obpi: str,
    receipt_event: str,
    attestor: str,
    evidence_json: str | None,
    dry_run: bool,
    attestor_present: bool = False,
) -> None:
    """Emit an OBPI receipt event anchored in the ledger."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    obpi_file, obpi_id = resolve_obpi_file(project_root, config, ledger, obpi)
    graph = ledger.get_artifact_graph()
    obpi_info = graph.get(obpi_id, {})
    if obpi_info.get("type") != "obpi":
        msg = f"OBPI not found in ledger: {obpi_id}"
        raise GzCliError(msg)  # noqa: TRY003
    parent_adr = obpi_info.get("parent")
    if isinstance(parent_adr, str) and _is_pool_adr_id(parent_adr):
        msg = (
            "Pool-linked OBPIs cannot be issued receipts: "
            f"{obpi_id} (parent: {parent_adr}). Promote parent ADR first."
        )
        raise GzCliError(msg)  # noqa: TRY003

    evidence: dict[str, Any] | None = None
    if evidence_json:
        try:
            parsed = json.loads(evidence_json)
        except json.JSONDecodeError as exc:
            msg = f"Invalid --evidence-json: {exc}"
            raise GzCliError(msg) from exc  # noqa: TRY003
        if not isinstance(parsed, dict):
            msg = "--evidence-json must decode to a JSON object"
            raise GzCliError(msg)  # noqa: TRY003
        evidence = parsed

    parent_lane = config.mode
    if isinstance(parent_adr, str) and parent_adr:
        parent_info = graph.get(parent_adr, {})
        parent_lane = resolve_adr_lane(parent_info, config.mode)

    obpi_completion: str | None = None
    anchor: EventAnchor | None = None
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
        # ADR-0.0.24-02 receipt-binding gate: heavy/foundation = fail-closed
        # on unresolvable ARB receipts; lite-non-foundation = warn-only. Runs
        # BEFORE the GHI #290 TTY gate at ``_gate_completed_receipt_authenticity``
        # (REQ-0.0.24-02-07, mechanism for REQ-02). Closes the same-class
        # fabrication vector on the lower-level emit-receipt path.
        _gate_completed_receipt_binding(
            obpi_id=obpi_id,
            parent_adr=parent_adr,
            parent_lane=parent_lane,
            project_root=project_root,
            config=config,
            evidence=evidence,
            ledger=ledger,
            attestor=attestor,
            dry_run=dry_run,
        )
        sensitivity_value, parent_kind_value = _resolve_emit_receipt_authenticity_context(
            obpi_content=obpi_content,
            parent_adr=parent_adr,
            project_root=project_root,
            config=config,
        )
        _gate_completed_receipt_authenticity(
            obpi_id=obpi_id,
            parent_adr=parent_adr,
            attestor=attestor,
            evidence=evidence,
            dry_run=dry_run,
            attestor_present=attestor_present,
            project_root=project_root,
            sensitivity=sensitivity_value,
            parent_kind=parent_kind_value,
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
        msg = f"OBPI not found in ledger: {obpi_id}"
        raise GzCliError(msg)  # noqa: TRY003

    parent_adr = cast(str | None, info.get("parent"))
    if not parent_adr:
        msg = f"OBPI is missing a parent ADR link in the ledger: {obpi_id}"
        raise GzCliError(msg)  # noqa: TRY003
    if _is_pool_adr_id(parent_adr):
        msg = f"Pool-linked OBPI cannot enter the pipeline: {obpi_id}"
        raise GzCliError(msg)  # noqa: TRY003

    _adr_file, resolved_parent = resolve_adr_file(project_root, config, parent_adr)
    obpi_content = obpi_file.read_text(encoding="utf-8")
    inspection = _inspect_obpi_brief(project_root, obpi_file, obpi_id, graph)
    if bool(inspection.get("ledger_completed")):
        _print_pipeline_blockers(
            obpi_id, ["OBPI is already completed in the ledger; pipeline launch is not allowed"]
        )
        raise SystemExit(1)

    plans_dir = pipeline_plans_dir(project_root)
    for purged_path, purged_obpi, purged_parent in purge_orphaned_active_markers(plans_dir, graph):
        relative = purged_path.relative_to(project_root).as_posix()
        ledger.append(
            pipeline_marker_purged_event(
                obpi_id=purged_obpi,
                parent_adr=purged_parent,
                reason="attested_completed",
                marker_path=relative,
            )
        )
        console.print(
            f"Purged stale pipeline marker: {relative} (OBPI {purged_obpi} is "
            f"attested_completed in the ledger)"
        )
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
    ledger.append(
        pipeline_launched_event(
            obpi_id=obpi_id,
            parent_adr=resolved_parent,
            lane=lane,
            nonce=str(marker_payload["nonce"]),
            marker_path=per_obpi_marker.relative_to(project_root).as_posix(),
            entry=str(marker_payload.get("entry") or "full"),
        )
    )
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
            msg = (
                "--attestor is required for --from=sync. "
                "Use --attestor <name> for attested OBPIs "
                "or --attestor agent:<name> for agent-closed OBPIs."
            )
            raise GzCliError(msg)  # noqa: TRY003
        if not evidence_json:
            msg = (
                "--evidence-json is required for --from=sync. "
                "Must include value_narrative and key_proof fields."
            )
            raise GzCliError(msg)  # noqa: TRY003
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


def _validate_brief_path_existence(project_root: Path, brief_path: Path) -> list[str]:
    """Surface allowed-path drift at brief authoring time (GHI #419).

    Mirrors the ``gz plan audit`` allowed-path validity gap (GHI #393 +
    GHI #403) so authoring-time ``gz obpi validate`` rejects briefs whose
    ``## Allowed Paths`` reference files that do not exist on disk —
    closing the cost gap where every implementation paid ~10 minutes
    correcting drift mid-flight at Stage 4 instead of zero cost at
    authoring time.

    Briefs without an ``## Allowed Paths`` section (fresh scaffolds)
    surface no errors. Net-new paths declared via ``**CREATE**`` markers
    or under a ``Creates these files`` heading are exempt from the
    existence gap; vendor-mirror surfaces fail fail-closed regardless.
    """
    from gzkit.governance.brief_path_validity import (  # noqa: PLC0415
        check_brief_path_validity_for_brief,
    )

    return check_brief_path_validity_for_brief(project_root, brief_path)


def obpi_validate_cmd(obpi_path: str | None, adr_id: str | None, authored: bool) -> None:
    """Validate OBPI brief(s) for structural conformance and content readiness."""
    config = ensure_initialized()
    project_root = get_project_root()
    validator = ObpiValidator(project_root)

    if adr_id and not obpi_path:
        _obpi_validate_batch(project_root, config, validator, adr_id, authored=authored)
        return

    if not obpi_path:
        console.print("[red]Error:[/red] Provide an OBPI path or --adr flag.")
        raise SystemExit(1)

    path = Path(obpi_path)
    if not path.is_absolute():
        path = project_root / path

    # Structural conformance check (always runs, regardless of status)
    structure_errors = _validate_brief_structure(project_root, path)

    # Allowed-path validity check (GHI #419) — gated on --authored so early
    # Draft briefs with placeholder paths still pass lenient validation;
    # the authoring-time gate fires before plan authoring incurs the
    # ~10-minute mid-flight drift-correction cost the GHI surfaced.
    path_errors = _validate_brief_path_existence(project_root, path) if authored else []

    # Content readiness check (ObpiValidator)
    completion_errors = validator.validate_file(path, require_authored=authored)

    all_errors = structure_errors + path_errors + completion_errors
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
    *,
    authored: bool,
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
        path_errors = _validate_brief_path_existence(project_root, brief_path) if authored else []
        completion_errors = validator.validate_file(brief_path, require_authored=authored)
        all_errors = structure_errors + path_errors + completion_errors
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
