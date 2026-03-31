"""Closeout command implementation."""

import json
from datetime import date
from pathlib import Path
from typing import Any, cast

from gzkit.commands.common import (
    GzCliError,
    _canonical_attestation_term,
    _cli_main,
    _closeout_form_attestation_text,
    _closeout_form_timestamp,
    _gate4_na_reason,
    _reject_pool_adr_for_lifecycle,
    _update_adr_attestation_block,
    _write_adr_closeout_form,
    check_version_sync,
    compute_defense_brief,
    console,
    ensure_initialized,
    get_git_user,
    get_project_root,
    load_manifest,
    resolve_adr_file,
    resolve_adr_ledger_id,
    sync_project_version,
)
from gzkit.commands.status import (
    _adr_closeout_readiness,
    _adr_obpi_status_rows,
    _collect_obpi_files_for_adr,
    _summarize_obpi_rows,
)
from gzkit.flags import FlagError, get_decisions
from gzkit.ledger import (
    Ledger,
    attested_event,
    closeout_initiated_event,
    gate_checked_event,
    lifecycle_transition_event,
    resolve_adr_lane,
)
from gzkit.quality import ProductProofResult, check_product_proof


def _manifest_verification_commands(
    manifest: dict[str, Any], include_docs: bool = True
) -> list[tuple[str, str]]:
    verification = manifest.get("verification", {})
    commands: list[tuple[str, str]] = [
        ("test", verification.get("test", "uv run gz test")),
        ("lint", verification.get("lint", "uv run gz lint")),
        ("typecheck", verification.get("typecheck", "uv run gz typecheck")),
    ]
    if include_docs:
        commands.append(("docs", verification.get("docs", "uv run mkdocs build --strict")))
    return commands


def _closeout_verification_steps(
    manifest: dict[str, Any], lane: str, project_root: Path
) -> tuple[list[tuple[str, str]], str | None]:
    verification = manifest.get("verification", {})
    steps: list[tuple[str, str]] = [
        ("Gate 2 (TDD)", verification.get("test", "uv run gz test")),
        ("Quality (Lint)", verification.get("lint", "uv run gz lint")),
        ("Quality (Typecheck)", verification.get("typecheck", "uv run gz typecheck")),
    ]
    if lane != "heavy":
        return steps, None

    steps.append(("Gate 3 (Docs)", verification.get("docs", "uv run mkdocs build --strict")))
    gate4_na_reason = _gate4_na_reason(project_root, lane)
    if gate4_na_reason is None:
        steps.append(("Gate 4 (BDD)", verification.get("bdd", "uv run -m behave features/")))
    return steps, gate4_na_reason


def _closeout_result_payload(
    adr_id: str,
    lane: str,
    dry_run: bool,
    allowed: bool,
    blockers: list[str],
    event: dict[str, Any] | None,
    gate_1_path: str,
    obpi_summary: dict[str, Any],
    obpi_rows: list[dict[str, Any]],
    verification_steps: list[tuple[str, str]],
    gate4_na_reason: str | None,
    attestation_choices: list[str],
    next_steps: list[str],
) -> dict[str, Any]:
    rendered_steps = [{"label": label, "command": command} for label, command in verification_steps]
    return {
        "adr": adr_id,
        "mode": lane,
        "dry_run": dry_run,
        "allowed": allowed,
        "blockers": blockers,
        "event": event,
        "gate_1_path": gate_1_path,
        "obpi_summary": obpi_summary,
        "obpi_rows": obpi_rows,
        "verification_commands": [command for _label, command in verification_steps],
        "verification_steps": rendered_steps,
        "gate4_na_reason": gate4_na_reason,
        "attestation_choices": attestation_choices,
        "next_steps": next_steps,
    }


def _render_closeout_output(result: dict[str, Any], dry_run: bool) -> None:
    adr_id = result["adr"]
    lane = result["mode"]
    gate_1_path = result["gate_1_path"]
    gate4_na_reason = result.get("gate4_na_reason")
    attestation_choices = result.get("attestation_choices", [])
    blockers = cast(list[str], result.get("blockers", []))
    next_steps = cast(list[str], result.get("next_steps", []))
    obpi_summary = cast(dict[str, Any], result.get("obpi_summary", {}))
    steps = result.get("verification_steps", [])
    obpi_total = int(obpi_summary.get("total", 0))
    obpi_completed = int(obpi_summary.get("completed", 0))

    if blockers:
        heading = "[red]Closeout blocked:[/red]" if not dry_run else "[red]Dry run blocked:[/red]"
        console.print(f"{heading} {adr_id}")
        console.print(f"  Gate 1 (ADR): {gate_1_path}")
        console.print(f"  OBPI Completion: {obpi_completed}/{obpi_total} complete")
        console.print("BLOCKERS:")
        for blocker in blockers:
            console.print(f"- {blocker}")
        if next_steps:
            console.print("Next steps:")
            for step in next_steps:
                console.print(f"  - {step}")
        return

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no ledger event will be written.")
        console.print(f"  Would initiate closeout for: {adr_id}")
        console.print(f"  Gate 1 (ADR): {gate_1_path}")
        console.print(f"  OBPI Completion: {obpi_completed}/{obpi_total} complete")
        for step in steps:
            console.print(f"  {step['label']}: {step['command']}")
        if gate4_na_reason is not None and lane == "heavy":
            console.print(f"  Gate 4 (BDD): N/A ({gate4_na_reason})")
        console.print("  Gate 5 (Human): Awaiting explicit attestation")
        for choice in attestation_choices:
            console.print(f"    - {choice}", markup=False)
        return

    console.print(f"[green]Closeout initiated:[/green] {adr_id}")
    console.print(f"Gate 1 (ADR): {gate_1_path}")
    console.print(f"OBPI Completion: {obpi_completed}/{obpi_total} complete")
    for step in steps:
        console.print(f"{step['label']}: {step['command']}")
    if gate4_na_reason is not None and lane == "heavy":
        console.print(f"Gate 4 (BDD): N/A ({gate4_na_reason})")
    console.print("Gate 5 (Human): Awaiting explicit attestation")
    console.print("Attestation choices:")
    for choice in attestation_choices:
        console.print(f"  - {choice}", markup=False)
    console.print(f"Record attestation command: uv run gz attest {adr_id} --status completed")


def _closeout_next_steps(adr_id: str, blocking_ids: list[str]) -> list[str]:
    """Suggest the minimal next commands needed to clear closeout blockers."""
    steps = [f"uv run gz adr status {adr_id}", f"uv run gz adr audit-check {adr_id}"]
    for obpi_id in blocking_ids:
        steps.append(f"uv run gz obpi reconcile {obpi_id}")
    return steps


def _closeout_gate_number(label: str) -> int:
    """Extract gate number from a verification step label."""
    if label.startswith("Gate "):
        try:
            return int(label.split("(")[0].strip().split()[-1])
        except (ValueError, IndexError):
            pass
    return 2  # Quality checks (lint, typecheck) default to gate 2


def _prompt_closeout_attestation(*, quiet: bool = False) -> tuple[str, str | None]:
    """Interactive attestation prompt for the closeout pipeline.

    Returns ``(attest_status, reason)`` tuple.
    """
    if not quiet:
        print("Attestation choices:")  # noqa: T201
        print("  1. Completed")  # noqa: T201
        print("  2. Completed - Partial (requires reason)")  # noqa: T201
        print("  3. Dropped (requires reason)")  # noqa: T201
        selection = input("Select [1/2/3]: ").strip()
    else:
        selection = input().strip()

    if selection == "1":
        return "completed", None
    if selection == "2":
        reason = input("" if quiet else "Reason: ").strip()
        if not reason:
            msg = "Reason required for partial attestation"
        raise GzCliError(msg)  # noqa: TRY003
        return "partial", reason
    if selection == "3":
        reason = input("" if quiet else "Reason: ").strip()
        if not reason:
            msg = "Reason required for dropped attestation"
            raise GzCliError(msg)  # noqa: TRY003
        return "dropped", reason
    msg = f"Invalid selection: {selection}. Expected 1, 2, or 3."
    raise GzCliError(msg)  # noqa: TRY003


def _abort_closeout_with_blockers(
    *,
    adr_id: str,
    lane: str,
    dry_run: bool,
    blockers: list[str],
    gate_1_path: str,
    obpi_summary: dict[str, Any],
    obpi_rows: list[dict[str, Any]],
    verification_steps: list[tuple[str, str]],
    gate4_na_reason: str | None,
    attestation_choices: list[str],
    next_steps: list[str],
    as_json: bool,
) -> None:
    result = _closeout_result_payload(
        adr_id=adr_id,
        lane=lane,
        dry_run=dry_run,
        allowed=False,
        blockers=blockers,
        event=None,
        gate_1_path=gate_1_path,
        obpi_summary=obpi_summary,
        obpi_rows=obpi_rows,
        verification_steps=verification_steps,
        gate4_na_reason=gate4_na_reason,
        attestation_choices=attestation_choices,
        next_steps=next_steps,
    )
    if as_json:
        print(json.dumps(result, indent=2))  # noqa: T201
    else:
        _render_closeout_output(result, dry_run=dry_run)
    raise SystemExit(1)


def _render_closeout_dry_run(
    *,
    adr_id: str,
    lane: str,
    gate_1_path: str,
    obpi_summary: dict[str, Any],
    obpi_rows: list[dict[str, Any]],
    verification_steps: list[tuple[str, str]],
    gate4_na_reason: str | None,
    attestation_choices: list[str],
    current_ver: str | None,
    adr_ver: str | None,
    needs_bump: bool,
    as_json: bool,
    proof_result: ProductProofResult | None = None,
    defense_brief: str | None = None,
) -> None:
    result = _closeout_result_payload(
        adr_id=adr_id,
        lane=lane,
        dry_run=True,
        allowed=True,
        blockers=[],
        event=None,
        gate_1_path=gate_1_path,
        obpi_summary=obpi_summary,
        obpi_rows=obpi_rows,
        verification_steps=verification_steps,
        gate4_na_reason=gate4_na_reason,
        attestation_choices=attestation_choices,
        next_steps=[],
    )
    if as_json:
        result["version_sync"] = {
            "current": current_ver,
            "target": adr_ver,
            "needs_bump": needs_bump,
        }
        if proof_result is not None:
            result["product_proof"] = _product_proof_payload(proof_result)
        if defense_brief is not None:
            result["defense_brief"] = True
        print(json.dumps(result, indent=2))  # noqa: T201
        return
    _render_closeout_output(result, dry_run=True)
    if needs_bump:
        console.print(
            f"  Version sync: would bump {current_ver} -> {adr_ver} "
            f"(pyproject.toml, __init__.py, README.md)"
        )
    if defense_brief:
        console.print("\n  [bold]Defense Brief[/bold] (preview)")
        for line in defense_brief.splitlines():
            console.print(f"  {line}", markup=False)


def _record_closeout_initiation(
    *,
    project_root: Path,
    ledger: Ledger,
    adr_id: str,
    lane: str,
    gate_1_path: str,
    obpi_files: dict[str, Path],
    obpi_summary: dict[str, Any],
    verification_steps: list[tuple[str, str]],
) -> None:
    evidence = {
        "adr_file": gate_1_path,
        "obpi_files": [str(path.relative_to(project_root)) for path in obpi_files.values()],
        "obpi_summary": obpi_summary,
        "verification_steps": [
            {"label": label, "command": command} for label, command in verification_steps
        ],
    }
    init_event = closeout_initiated_event(
        adr_id=adr_id,
        by=get_git_user(),
        mode=lane,
        evidence=evidence,
    )
    ledger.append(init_event)


def _run_closeout_quality_gates(
    *,
    adr_id: str,
    project_root: Path,
    ledger: Ledger,
    verification_steps: list[tuple[str, str]],
    as_json: bool,
) -> list[dict[str, Any]]:
    gate_results: list[dict[str, Any]] = []
    for label, command in verification_steps:
        if not as_json:
            console.print(f"  Running {label}...", end=" ")
        qr = _cli_main().run_command(command, cwd=project_root)
        gate_num = _closeout_gate_number(label)
        gate_status = "pass" if qr.success else "fail"
        gate_results.append(
            {
                "label": label,
                "command": command,
                "returncode": qr.returncode,
                "success": qr.success,
            }
        )
        ledger.append(
            gate_checked_event(
                adr_id,
                gate_num,
                gate_status,
                command,
                qr.returncode,
            )
        )
        if not as_json:
            if qr.success:
                console.print("[green]PASS[/green]")
            else:
                console.print("[red]FAIL[/red]")
                output_snippet = (qr.stderr or qr.stdout).strip()[:200]
                if output_snippet:
                    console.print(f"    {output_snippet}")
        if qr.success:
            continue

        fail_result = {
            "adr": adr_id,
            "pipeline_stage": "gates",
            "gate_results": gate_results,
            "halted": True,
        }
        if as_json:
            print(json.dumps(fail_result, indent=2))  # noqa: T201
        else:
            failed = gate_results[-1]
            console.print(
                f"[red]Closeout halted:[/red] {failed['label']} failed "
                f"(exit {failed['returncode']})"
            )
        raise SystemExit(1)
    return gate_results


def _product_proof_payload(proof_result: ProductProofResult) -> list[dict[str, Any]]:
    """Build JSON-serializable product proof rows."""
    return [
        {
            "obpi_id": p.obpi_id,
            "proof_type": p.proof_type,
            "runbook": p.runbook_found,
            "command_doc": p.command_doc_found,
            "docstring": p.docstring_found,
        }
        for p in proof_result.obpi_proofs
    ]


def _render_product_proof_human(proof_result: ProductProofResult) -> None:
    """Render product proof status table for human output."""
    console.print("\n  [bold]Product Proof Status[/bold]")
    for p in proof_result.obpi_proofs:
        if p.has_proof:
            console.print(f"    {p.obpi_id}: [green]{p.proof_type}[/green]")
        else:
            console.print(f"    {p.obpi_id}: [red]MISSING[/red]")


def _complete_closeout_pipeline(
    *,
    project_root: Path,
    ledger: Ledger,
    adr_id: str,
    adr_file: Path,
    obpi_rows: list[dict[str, Any]],
    verification_steps: list[tuple[str, str]],
    current_ver: str | None,
    adr_ver: str | None,
    needs_bump: bool,
    gate_results: list[dict[str, Any]],
    as_json: bool,
    defense_brief: str | None = None,
) -> None:
    if not as_json:
        console.print("\n  All quality gates passed.")
    attest_status, reason = _prompt_closeout_attestation(quiet=as_json)
    attester = get_git_user()
    ledger.append(attested_event(adr_id, attest_status, attester, reason))

    version_updated: list[str] = []
    if needs_bump and adr_ver is not None:
        version_updated = sync_project_version(project_root, adr_ver)

    to_state = "Dropped" if attest_status == "dropped" else "Completed"
    ledger.append(lifecycle_transition_event(adr_id, "adr", "Proposed", to_state))

    canonical_term = _canonical_attestation_term(attest_status, reason)
    gate_statuses = ledger.get_latest_gate_statuses(adr_id)
    attestation_text = _closeout_form_attestation_text(attest_status, reason)
    timestamp_utc = _closeout_form_timestamp()
    _write_adr_closeout_form(
        project_root,
        adr_id,
        adr_file,
        obpi_rows,
        verification_steps,
        gate_statuses,
        attestation_command=f"uv run gz closeout {adr_id}",
        attestation_text=attestation_text,
        attestation_term=canonical_term,
        attester=attester,
        timestamp_utc=timestamp_utc,
        defense_brief=defense_brief,
    )
    _update_adr_attestation_block(
        adr_file,
        adr_id,
        canonical_term=canonical_term,
        attester=attester,
        attestation_date=date.today().isoformat(),
        attestation_reason=attestation_text,
    )

    # Auto-fix OBPI brief frontmatter to match ledger-derived state (ADR-0.0.9-04)
    from gzkit.commands.closeout_form import auto_fix_obpi_rows

    auto_fix_obpi_rows(project_root, obpi_rows)

    if as_json:
        output = {
            "adr": adr_id,
            "gate_results": gate_results,
            "attestation": {
                "status": attest_status,
                "by": attester,
                "reason": reason,
            },
            "version_sync": {
                "current": current_ver,
                "target": adr_ver,
                "needs_bump": needs_bump,
                "files_updated": version_updated,
            },
            "status_transition": {
                "from": "Proposed",
                "to": to_state,
            },
        }
        print(json.dumps(output, indent=2))  # noqa: T201
        return

    console.print(f"\n[green]Closeout complete:[/green] {adr_id}")
    console.print(f"  Attestation: {canonical_term} (by {attester})")
    if version_updated:
        console.print(f"  Version sync: {current_ver} -> {adr_ver} ({', '.join(version_updated)})")
    console.print(f"  ADR status: {to_state}")


def closeout_cmd(adr: str, as_json: bool, dry_run: bool) -> None:
    """Run the end-to-end closeout pipeline for an ADR.

    Executes quality gates inline, prompts for human attestation, bumps the
    project version, and marks the ADR as Completed -- all within a single
    command invocation.
    """
    config = ensure_initialized()
    project_root = get_project_root()
    manifest = load_manifest(project_root)
    ledger = Ledger(project_root / config.paths.ledger)

    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)
    adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    adr_id = resolve_adr_ledger_id(adr_file, adr_id, ledger)
    _reject_pool_adr_for_lifecycle(adr_id, "closed out")
    graph = ledger.get_artifact_graph()
    adr_info = graph.get(adr_id, {})
    lane = resolve_adr_lane(adr_info, config.mode)

    verification_steps, gate4_na_reason = _closeout_verification_steps(manifest, lane, project_root)
    obpi_files, _expected = _collect_obpi_files_for_adr(project_root, config, ledger, adr_id)
    obpi_rows = _adr_obpi_status_rows(project_root, config, ledger, adr_id)
    obpi_summary = _summarize_obpi_rows(obpi_rows)
    closeout_readiness = _adr_closeout_readiness(obpi_rows)
    blockers = list(closeout_readiness["blockers"])
    next_steps = _closeout_next_steps(
        adr_id, cast(list[str], closeout_readiness.get("blocking_ids", []))
    )

    gate_1_path = str(adr_file.relative_to(project_root))
    attestation_choices = ["Completed", "Completed - Partial: [reason]", "Dropped - [reason]"]

    # --- Blocker check ---
    if blockers:
        _abort_closeout_with_blockers(
            adr_id=adr_id,
            lane=lane,
            dry_run=dry_run,
            blockers=blockers,
            gate_1_path=gate_1_path,
            obpi_summary=obpi_summary,
            obpi_rows=obpi_rows,
            verification_steps=verification_steps,
            gate4_na_reason=gate4_na_reason,
            attestation_choices=attestation_choices,
            next_steps=next_steps,
            as_json=as_json,
        )

    # --- Product proof gate (migrated to FeatureDecisions per OBPI-0.0.8-06) ---
    try:
        decisions = get_decisions()
        enforce_proof = decisions.product_proof_enforced()
    except FlagError:
        enforce_proof = True
    proof_result = check_product_proof(adr_id, obpi_files, project_root)
    if not proof_result.success:
        proof_rows = _product_proof_payload(proof_result)
        missing = [p.obpi_id for p in proof_result.obpi_proofs if not p.has_proof]
        if enforce_proof:
            if as_json:
                print(
                    json.dumps(
                        {"product_proof": proof_rows, "success": False, "blockers": missing},
                        indent=2,
                    )
                )  # noqa: T201
            else:
                _render_product_proof_human(proof_result)
                console.print(
                    f"\n[red]Closeout blocked:[/red] {proof_result.missing_count} "
                    f"OBPI(s) missing product proof"
                )
                for obpi_id in missing:
                    console.print(f"  - {obpi_id}")
            raise SystemExit(1)
        if not as_json:
            console.print(
                f"[yellow]Product proof advisory:[/yellow] {proof_result.missing_count} "
                f"OBPI(s) missing proof (ops.product_proof=false)"
            )

    # --- Defense brief computation ---
    defense_brief = compute_defense_brief(obpi_files, adr_file.parent, proof_result)

    # --- Version sync check (needed for dry-run display and active pipeline) ---
    current_ver, adr_ver, needs_bump = check_version_sync(project_root, adr_id)

    # --- Dry run: show full pipeline plan without executing ---
    if dry_run:
        if not as_json:
            _render_product_proof_human(proof_result)
        _render_closeout_dry_run(
            adr_id=adr_id,
            lane=lane,
            gate_1_path=gate_1_path,
            obpi_summary=obpi_summary,
            obpi_rows=obpi_rows,
            verification_steps=verification_steps,
            gate4_na_reason=gate4_na_reason,
            attestation_choices=attestation_choices,
            current_ver=current_ver,
            adr_ver=adr_ver,
            needs_bump=needs_bump,
            as_json=as_json,
            proof_result=proof_result,
            defense_brief=defense_brief,
        )
        return

    # ===== ACTIVE PIPELINE =====

    # Stage: Record closeout initiation
    _record_closeout_initiation(
        project_root=project_root,
        ledger=ledger,
        adr_id=adr_id,
        lane=lane,
        gate_1_path=gate_1_path,
        obpi_files=obpi_files,
        obpi_summary=obpi_summary,
        verification_steps=verification_steps,
    )

    obpi_total = int(obpi_summary.get("total", 0))
    obpi_completed = int(obpi_summary.get("completed", 0))
    if not as_json:
        console.print(f"[bold]Closeout pipeline: {adr_id}[/bold]")
        console.print(f"  Gate 1 (ADR): {gate_1_path}")
        console.print(f"  OBPI Completion: {obpi_completed}/{obpi_total} complete")
        _render_product_proof_human(proof_result)

    # Stage: Run quality gates inline
    gate_results = _run_closeout_quality_gates(
        adr_id=adr_id,
        project_root=project_root,
        ledger=ledger,
        verification_steps=verification_steps,
        as_json=as_json,
    )
    _complete_closeout_pipeline(
        project_root=project_root,
        ledger=ledger,
        adr_id=adr_id,
        adr_file=adr_file,
        obpi_rows=obpi_rows,
        verification_steps=verification_steps,
        current_ver=current_ver,
        adr_ver=adr_ver,
        needs_bump=needs_bump,
        gate_results=gate_results,
        as_json=as_json,
        defense_brief=defense_brief,
    )
