"""Deterministic closeout ceremony with CLI-driven step sequencing.

GHI #59: The agent batched ceremony steps into a single message twice.
This module makes the CLI the step driver — each ``--next`` call returns
exactly one step's content.  The agent cannot skip because it never sees
future steps.

GHI #110: Step-by-step redesign from walkthrough analysis.
"""

from datetime import datetime
from pathlib import Path
from typing import Any

from gzkit.commands.ceremony_data import discover_demo_commands, extract_brief_metadata
from gzkit.commands.ceremony_state import (
    CeremonyState,
    CeremonyStep,
    CeremonyStepRecord,
    _classify_attestation_verdict,
    _cleanup_hook_files,
    _has_more_demos,
    _is_foundation_adr,
    _next_step,
    _now_iso,
    _output,
    _write_turn_lock,
    ceremony_state_path,  # noqa: F401  re-export for closeout.py
    load_ceremony_state,
    save_ceremony_state,
)
from gzkit.commands.ceremony_steps import (
    render_step_1_readiness,
    render_step_2_summary,
    render_step_3_docs_check,
    render_step_4_walkthrough,
    render_step_5_execute,
    render_step_6_attestation,
    render_step_7_closeout,
    render_step_8_issues,
    render_step_9_release_notes,
    render_step_10_release,
    render_step_11_complete,
)
from gzkit.commands.common import (
    GzCliError,
    console,
    ensure_initialized,
    get_project_root,
    load_manifest,
    resolve_adr_file,
    resolve_adr_ledger_id,
)
from gzkit.commands.status import (
    _adr_closeout_readiness,
    _collect_obpi_files_for_adr,
)
from gzkit.ledger import Ledger, resolve_adr_lane

# ---------------------------------------------------------------------------
# Ceremony context (shared across renderers)
# ---------------------------------------------------------------------------


def _build_obpi_context(
    project_root: Path,
    config: Any,
    ledger: Ledger,
    adr_id: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build OBPI rows and readiness for Step 1."""
    from gzkit.commands.status import _adr_obpi_status_rows

    obpi_rows = _adr_obpi_status_rows(project_root, config, ledger, adr_id)
    readiness = _adr_closeout_readiness(obpi_rows)
    return obpi_rows, readiness


# ---------------------------------------------------------------------------
# Ceremony orchestration
# ---------------------------------------------------------------------------


def _resolve_adr_context(
    adr: str,
) -> tuple[Path, str, Path, str, dict[str, Any], list[Path]]:
    """Resolve ADR file, ID, lane, manifest, and OBPI files as a list."""
    config = ensure_initialized()
    project_root = get_project_root()
    manifest = load_manifest(project_root)
    ledger = Ledger(project_root / config.paths.ledger)
    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)
    adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    adr_id = resolve_adr_ledger_id(adr_file, adr_id, ledger)
    graph = ledger.get_artifact_graph()
    adr_info = graph.get(adr_id, {})
    lane = resolve_adr_lane(adr_info, config.mode)
    obpi_map, _ = _collect_obpi_files_for_adr(project_root, config, ledger, adr_id)
    return project_root, adr_id, adr_file, lane, manifest, list(obpi_map.values())


def _present_step(
    state: CeremonyState,
    project_root: Path,
    adr_file: Path,
    lane: str,
    manifest: dict[str, Any],
    obpi_files: list[Path],
    obpi_rows: list[dict[str, Any]] | None = None,
    readiness: dict[str, Any] | None = None,
) -> str:
    """Route to the renderer for the current step."""
    step = state.current_step
    adr_id = state.adr_id
    if step == CeremonyStep.INITIALIZE:
        return render_step_1_readiness(
            adr_id,
            obpi_rows or [],
            readiness or {"ready": True, "blockers": []},
        )
    if step == CeremonyStep.SUMMARY:
        return render_step_2_summary(adr_id, adr_file, obpi_files, lane, project_root)
    if step == CeremonyStep.DOCS_CHECK:
        return render_step_3_docs_check(adr_id, project_root, obpi_files)
    if step == CeremonyStep.WALKTHROUGH:
        return render_step_4_walkthrough(adr_id, state.walkthrough_commands, obpi_files)
    if step == CeremonyStep.EXECUTE:
        return render_step_5_execute(
            adr_id,
            state.walkthrough_commands,
            state.walkthrough_index,
        )
    if step == CeremonyStep.ATTESTATION:
        ln_entries: list[dict[str, Any]] = []
        for f in obpi_files:
            ln_entries.extend(extract_brief_metadata(f).get("ln_entries", []))
        return render_step_6_attestation(adr_id, ln_entries=ln_entries)
    if step == CeremonyStep.CLOSEOUT:
        return render_step_7_closeout(adr_id)
    if step == CeremonyStep.ISSUES:
        return render_step_8_issues(adr_id)
    if step == CeremonyStep.RELEASE_NOTES:
        return render_step_9_release_notes(adr_id, state.is_foundation)
    if step == CeremonyStep.RELEASE:
        return render_step_10_release(adr_id, state.is_foundation)
    if step == CeremonyStep.COMPLETE:
        return render_step_11_complete(state)
    msg = f"Unknown ceremony step: {step}"
    raise GzCliError(msg)


def _initialize_ceremony(
    project_root: Path,
    adr_id: str,
    adr_file: Path,
    lane: str,
    manifest: dict[str, Any],
    obpi_files: list[Path],
    as_json: bool,
    restart: bool,
) -> None:
    """Initialize or resume a ceremony."""
    existing = load_ceremony_state(project_root, adr_id)

    if existing and existing.completed_at and not restart:
        # Offer restart vs resume
        console.print(
            f"Ceremony for {adr_id} completed at {existing.completed_at} "
            f"(attempt {existing.attempt}).\n"
            f"To restart: gz closeout {adr_id} --ceremony --restart\n"
            f"To view:    gz closeout {adr_id} --ceremony --ceremony-status"
        )
        return

    if existing and not existing.completed_at and not restart:
        # Resume from current step
        output = _present_step(existing, project_root, adr_file, lane, manifest, obpi_files)
        _write_turn_lock(project_root, adr_id, existing.current_step)
        _output(as_json, existing, output)
        return

    # Compute attempt number
    attempt = (existing.attempt + 1) if existing else 1

    # Build readiness data for Step 1
    config = ensure_initialized()
    ledger = Ledger(get_project_root() / config.paths.ledger)
    obpi_rows, readiness = _build_obpi_context(project_root, config, ledger, adr_id)
    blockers = readiness.get("blockers", [])
    if blockers:
        raise GzCliError(f"Cannot start ceremony: {'; '.join(blockers)}")

    now = _now_iso()
    commands = discover_demo_commands(project_root, adr_id, obpi_files)
    state = CeremonyState(
        adr_id=adr_id,
        current_step=CeremonyStep.INITIALIZE,
        is_foundation=_is_foundation_adr(adr_id),
        started_at=now,
        updated_at=now,
        step_history=[
            CeremonyStepRecord(step=CeremonyStep.INITIALIZE, presented_at=now),
        ],
        walkthrough_commands=commands,
        attempt=attempt,
    )
    save_ceremony_state(project_root, state)
    output = _present_step(
        state,
        project_root,
        adr_file,
        lane,
        manifest,
        obpi_files,
        obpi_rows=obpi_rows,
        readiness=readiness,
    )
    _write_turn_lock(project_root, adr_id, CeremonyStep.INITIALIZE)
    _output(as_json, state, output)


def _advance_demo_index(
    project_root: Path,
    state: CeremonyState,
    adr_file: Path,
    lane: str,
    manifest: dict[str, Any],
    obpi_files: list[Path],
    as_json: bool,
    now: str,
) -> None:
    """Advance the walkthrough_index within Step 5 without changing step."""
    new_state = state.model_copy(
        update={
            "walkthrough_index": state.walkthrough_index + 1,
            "updated_at": now,
        }
    )
    save_ceremony_state(project_root, new_state)
    output = _present_step(new_state, project_root, adr_file, lane, manifest, obpi_files)
    _write_turn_lock(project_root, state.adr_id, CeremonyStep.EXECUTE)
    _output(as_json, new_state, output)


def _has_fresh_attestation_receipt(project_root: Path, state: CeremonyState) -> bool:
    """Return ``True`` iff an ``attested`` ledger event for this ADR was emitted
    during the current ceremony run (event ``ts`` >= the run's ``started_at``).

    An event emitted during this run necessarily postdates the run's start, so a
    prior closeout's or a prior ``--restart`` attempt's attestation is correctly
    ignored. Timestamps are parsed and compared as ``datetime`` objects — string
    comparison is wrong because ``started_at`` is second-resolution Zulu
    (``...SSZ``) while event ``ts`` carries fractional seconds and a ``+00:00``
    offset (``.`` sorts before ``Z`` in ASCII).
    """
    config = ensure_initialized()
    ledger = Ledger(project_root / config.paths.ledger)
    run_start = datetime.fromisoformat(state.started_at)
    events = ledger.query(event_type="attested", artifact_id=state.adr_id)
    return any(datetime.fromisoformat(event.ts) >= run_start for event in events)


def _gate_proof_binding(project_root: Path, state: CeremonyState) -> None:
    """Fail-close EXECUTE -> ATTESTATION when proof binding is incomplete (OBPI-0.0.63-06).

    Only fires at the EXECUTE -> ATTESTATION transition edge: an in-progress
    closeout whose Acceptance-Criteria REQs have no ledger-present receipt
    bindings must not advance to the attestation step. No-op for every other
    step. Mirrors the scope discipline of ``_gate_attestation_boundary``.
    """
    if state.current_step != CeremonyStep.EXECUTE:
        return
    from gzkit.governance.trust_audits.closeout_proof_binding import (
        validate_closeout_proof_binding,
    )

    errors = validate_closeout_proof_binding(project_root, adr_id=state.adr_id)
    if not errors:
        return
    from gzkit.core.exceptions import PolicyBreachError

    unbound = [e.message for e in errors[:5]]
    raise PolicyBreachError(
        "EXECUTE -> ATTESTATION transition blocked: proof binding incomplete.\n"
        + "\n".join(f"  {m}" for m in unbound)
        + (f"\n  ... and {len(errors) - 5} more" if len(errors) > 5 else "")
        + "\nFix the brief's `ln:` field to bind each REQ to a ledger-present "
        "receipt-ID, then retry."
    )


def _gate_attestation_boundary(project_root: Path, state: CeremonyState) -> None:
    """Fail-close the Step 6 -> Step 7 edge without a fresh ledger receipt (BI-3).

    The ATTESTATION -> CLOSEOUT transition is the human-attestation boundary — the
    one edge the agent must not self-advance with ``--next``. Every other
    transition is a no-op here.
    """
    if state.current_step != CeremonyStep.ATTESTATION:
        return
    if _has_fresh_attestation_receipt(project_root, state):
        return
    from gzkit.core.exceptions import PolicyBreachError

    raise PolicyBreachError(
        f"Step {int(CeremonyStep.ATTESTATION)} (ATTESTATION) -> "
        f"{int(CeremonyStep.CLOSEOUT)} (CLOSEOUT) is the human-attestation "
        "boundary and cannot be self-advanced with --next: no `attested` ledger "
        "receipt was recorded for this ceremony run. Record the operator's "
        f'verdict first:\n  gz closeout {state.adr_id} --ceremony --attest "<verdict>"'
    )


def _commit_advance(
    project_root: Path,
    state: CeremonyState,
    adr_file: Path,
    lane: str,
    manifest: dict[str, Any],
    obpi_files: list[Path],
    as_json: bool,
    now: str,
    *,
    extra_update: dict[str, Any] | None = None,
) -> None:
    """Acknowledge the current step and advance to the next valid step.

    The single shared advance path for both ``--next`` and ``--attest`` (BI-3):
    the Step 6 -> 7 edge is ledger-gated here, so neither path can walk past the
    human-attestation boundary without a fresh ``attested`` receipt.

    The EXECUTE -> ATTESTATION edge is additionally proof-binding-gated
    (OBPI-0.0.63-06): an unbound closeout cannot advance to attestation.
    """
    _gate_proof_binding(project_root, state)
    _gate_attestation_boundary(project_root, state)

    history = list(state.step_history)
    if history and history[-1].acknowledged_at is None:
        history[-1] = history[-1].model_copy(update={"acknowledged_at": now})

    next_s = _next_step(state.current_step, state.is_foundation)
    if next_s == -1:
        new_state = state.model_copy(
            update={"step_history": history, "completed_at": now, "updated_at": now}
        )
        save_ceremony_state(project_root, new_state)
        _cleanup_hook_files(project_root, state.adr_id)
        _output(as_json, new_state, "Ceremony already at final step.")
        return

    history.append(CeremonyStepRecord(step=next_s, presented_at=now))
    completed_at = now if next_s == CeremonyStep.COMPLETE else None
    update: dict[str, Any] = {
        "current_step": next_s,
        "step_history": history,
        "updated_at": now,
        "completed_at": completed_at,
    }
    if extra_update:
        update.update(extra_update)
    new_state = state.model_copy(update=update)
    save_ceremony_state(project_root, new_state)
    output = _present_step(new_state, project_root, adr_file, lane, manifest, obpi_files)
    if completed_at:
        _cleanup_hook_files(project_root, state.adr_id)
    else:
        _write_turn_lock(project_root, state.adr_id, next_s)
    _output(as_json, new_state, output)


def _advance_ceremony(
    project_root: Path,
    adr_id: str,
    adr_file: Path,
    lane: str,
    manifest: dict[str, Any],
    obpi_files: list[Path],
    as_json: bool,
) -> None:
    """Acknowledge current step and advance to the next.

    At Step 5 EXECUTE (GHI #260), ``--next`` advances one demo command at a
    time via ``walkthrough_index``; the ceremony only moves to Step 6
    ATTESTATION after every command has been presented. The Step 6 -> 7
    transition is ledger-gated by ``_commit_advance`` (BI-3): ``--next`` cannot
    self-advance past the human-attestation boundary.
    """
    state = load_ceremony_state(project_root, adr_id)
    if state is None:
        raise GzCliError(f"No ceremony in progress for {adr_id}. Run --ceremony first.")
    if state.completed_at:
        raise GzCliError(f"Ceremony for {adr_id} already completed.")

    now = _now_iso()

    if state.current_step == CeremonyStep.EXECUTE and _has_more_demos(state):
        _advance_demo_index(project_root, state, adr_file, lane, manifest, obpi_files, as_json, now)
        return

    _commit_advance(project_root, state, adr_file, lane, manifest, obpi_files, as_json, now)


def _record_attestation(
    project_root: Path,
    adr_id: str,
    adr_file: Path,
    lane: str,
    manifest: dict[str, Any],
    obpi_files: list[Path],
    attestation: str,
    as_json: bool,
) -> None:
    """Record attestation at step 6 and advance to step 7.

    Emits the ``attested`` ledger receipt that is the BI-3 expected receipt for
    the attestation step, then advances through the shared ledger-gated
    ``_commit_advance`` — so ``--attest`` exercises the gate's fresh-receipt
    pass-path while bare ``--next`` (no receipt) fail-closes. Reuses the existing
    ``attested`` surface (BI-2: ``--attest`` is not a parallel emitter); the
    transitional double-emit with the Step-7 closeout (``closeout.py``) is
    collapsed by OBPI-0.0.63-05.
    """
    from gzkit.commands.common import get_git_user
    from gzkit.ledger import attested_event

    state = load_ceremony_state(project_root, adr_id)
    if state is None:
        raise GzCliError(f"No ceremony in progress for {adr_id}.")
    if state.current_step != CeremonyStep.ATTESTATION:
        from gzkit.core.exceptions import PolicyBreachError

        raise PolicyBreachError(
            f"Attestation only valid at step {CeremonyStep.ATTESTATION} "
            f"(current: {state.current_step}). "
            "Cannot attest outside the attestation step."
        )

    config = ensure_initialized()
    ledger = Ledger(project_root / config.paths.ledger)
    status, reason = _classify_attestation_verdict(attestation)
    ledger.append(attested_event(adr_id, status, get_git_user(), reason))

    _commit_advance(
        project_root,
        state,
        adr_file,
        lane,
        manifest,
        obpi_files,
        as_json,
        _now_iso(),
        extra_update={"attestation": attestation},
    )


def _pause_ceremony(
    project_root: Path,
    adr_id: str,
    as_json: bool,
) -> None:
    """Pause ceremony for revise-and-resubmit."""
    state = load_ceremony_state(project_root, adr_id)
    if state is None:
        raise GzCliError(f"No ceremony in progress for {adr_id}.")
    if state.completed_at:
        raise GzCliError(f"Ceremony for {adr_id} already completed.")

    now = _now_iso()
    new_state = state.model_copy(update={"paused_at": now, "updated_at": now})
    save_ceremony_state(project_root, new_state)
    _cleanup_hook_files(project_root, adr_id)

    output = "\n".join(
        [
            f"Ceremony for {adr_id} paused at Step {state.current_step} (attempt {state.attempt}).",
            "",
            "Fix the identified issues, then restart:",
            f"  gz closeout {adr_id} --ceremony --restart",
            "",
            "Or resume from current step:",
            f"  gz closeout {adr_id} --ceremony",
        ]
    )
    _output(as_json, new_state, output)


def _show_status(project_root: Path, adr_id: str, as_json: bool) -> None:
    """Show current ceremony step."""
    state = load_ceremony_state(project_root, adr_id)
    if state is None:
        console.print(f"No ceremony in progress for {adr_id}.")
        return
    if as_json:
        print(state.model_dump_json(indent=2))
    else:
        step_name = CeremonyStep(state.current_step).name
        status = "COMPLETED" if state.completed_at else "IN PROGRESS"
        if state.paused_at:
            status = "PAUSED"
        console.print(
            f"Ceremony {adr_id}: Step {state.current_step} ({step_name}) "
            f"- {status} (attempt {state.attempt})"
        )
        if state.attestation:
            console.print(f"  Attestation: {state.attestation}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def ceremony_cmd(
    adr: str,
    as_json: bool,
    ceremony_next: bool,
    ceremony_status: bool,
    ceremony_attest: str | None,
    ceremony_pause: bool = False,
    ceremony_restart: bool = False,
) -> None:
    """Dispatch ceremony sub-commands."""
    # Validate flag combinations
    flags = [ceremony_next, bool(ceremony_attest), ceremony_pause]
    if sum(flags) > 1:
        raise GzCliError("Cannot combine --next, --attest, and --pause.")

    project_root, adr_id, adr_file, lane, manifest, obpi_files = _resolve_adr_context(adr)

    if ceremony_status:
        _show_status(project_root, adr_id, as_json)
        return

    if ceremony_pause:
        _pause_ceremony(project_root, adr_id, as_json)
        return

    if ceremony_attest:
        _record_attestation(
            project_root,
            adr_id,
            adr_file,
            lane,
            manifest,
            obpi_files,
            ceremony_attest,
            as_json,
        )
        return

    if ceremony_next:
        _advance_ceremony(
            project_root,
            adr_id,
            adr_file,
            lane,
            manifest,
            obpi_files,
            as_json,
        )
        return

    # Bare --ceremony: initialize or resume
    _initialize_ceremony(
        project_root,
        adr_id,
        adr_file,
        lane,
        manifest,
        obpi_files,
        as_json,
        restart=ceremony_restart,
    )
