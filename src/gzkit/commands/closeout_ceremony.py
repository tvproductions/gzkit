"""Deterministic closeout ceremony with CLI-driven step sequencing.

GHI #59: The agent batched ceremony steps into a single message twice.
This module makes the CLI the step driver — each ``--next`` call returns
exactly one step's content.  The agent cannot skip because it never sees
future steps.
"""

import json
import re
from datetime import UTC, datetime
from enum import IntEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from gzkit.commands.ceremony_steps import (
    discover_walkthrough_commands,
    render_step_2_summary,
    render_step_3_walkthrough,
    render_step_4_execute,
    render_step_5_attestation,
    render_step_6_closeout,
    render_step_7_issues,
    render_step_8_release_notes,
    render_step_9_release,
    render_step_10_complete,
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
# Step enum
# ---------------------------------------------------------------------------


class CeremonyStep(IntEnum):
    """Ceremony steps matching the audit-protocol.md ceremony."""

    INITIALIZE = 1
    SUMMARY = 2
    WALKTHROUGH = 3
    EXECUTE = 4
    ATTESTATION = 5
    CLOSEOUT = 6
    ISSUES = 7
    RELEASE_NOTES = 8
    RELEASE = 9
    COMPLETE = 10


FOUNDATION_SKIP_STEPS: frozenset[int] = frozenset(
    {
        CeremonyStep.RELEASE_NOTES,
        CeremonyStep.RELEASE,
    }
)


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class CeremonyStepRecord(BaseModel):
    """One step's presentation/acknowledgment timestamps."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    step: int = Field(..., description="Step number")
    presented_at: str = Field(..., description="ISO-8601 timestamp")
    acknowledged_at: str | None = Field(None, description="ISO-8601 timestamp")


class CeremonyState(BaseModel):
    """Persistent ceremony state stored in .gzkit/ceremonies/."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    adr_id: str = Field(..., description="Canonical ADR ID")
    current_step: int = Field(..., description="Current step number")
    is_foundation: bool = Field(..., description="0.0.x foundation ADR")
    started_at: str = Field(..., description="ISO-8601 timestamp")
    updated_at: str = Field(..., description="ISO-8601 timestamp")
    step_history: list[CeremonyStepRecord] = Field(default_factory=list, description="Step records")
    walkthrough_commands: list[str] = Field(default_factory=list, description="Commands for Step 5")
    walkthrough_index: int = Field(0, description="Current command index in Step 5")
    attestation: str | None = Field(None, description="Human attestation text")
    completed_at: str | None = Field(None, description="ISO-8601 when ceremony finished")


# ---------------------------------------------------------------------------
# State I/O
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ceremony_dir(project_root: Path) -> Path:
    return project_root / ".gzkit" / "ceremonies"


def ceremony_state_path(project_root: Path, adr_id: str) -> Path:
    """Return the ceremony state file path for an ADR."""
    return _ceremony_dir(project_root) / f"{adr_id}.ceremony.json"


def _turn_lock_path(project_root: Path, adr_id: str) -> Path:
    return _ceremony_dir(project_root) / f"{adr_id}.turn-lock"


def _hook_state_path(project_root: Path, adr_id: str) -> Path:
    return _ceremony_dir(project_root) / f"{adr_id}.hook-state.json"


def load_ceremony_state(project_root: Path, adr_id: str) -> CeremonyState | None:
    """Load ceremony state from disk, or None if not started."""
    path = ceremony_state_path(project_root, adr_id)
    if not path.is_file():
        return None
    return CeremonyState.model_validate_json(path.read_text(encoding="utf-8"))


def save_ceremony_state(project_root: Path, state: CeremonyState) -> None:
    """Persist ceremony state atomically."""
    d = _ceremony_dir(project_root)
    d.mkdir(parents=True, exist_ok=True)
    path = ceremony_state_path(project_root, state.adr_id)
    path.write_text(state.model_dump_json(indent=2) + "\n", encoding="utf-8")


def _write_turn_lock(project_root: Path, adr_id: str, step: int) -> None:
    d = _ceremony_dir(project_root)
    d.mkdir(parents=True, exist_ok=True)
    lock = _turn_lock_path(project_root, adr_id)
    lock.write_text(json.dumps({"presented_step": step}) + "\n", encoding="utf-8")


def _is_foundation_adr(adr_id: str) -> bool:
    return re.match(r"^ADR-0\.0\.\d+(?:[.-].*)?$", adr_id) is not None


# ---------------------------------------------------------------------------
# Step transitions
# ---------------------------------------------------------------------------


def _next_step(current: int, is_foundation: bool) -> int:
    """Return the next valid step, skipping foundation-excluded steps."""
    candidate = current + 1
    while is_foundation and candidate in FOUNDATION_SKIP_STEPS:
        candidate += 1
    if candidate > CeremonyStep.COMPLETE:
        return -1
    return candidate


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
) -> str:
    """Route to the renderer for the current step."""
    step = state.current_step
    adr_id = state.adr_id
    if step == CeremonyStep.SUMMARY:
        return render_step_2_summary(adr_id, adr_file, obpi_files, manifest, lane, project_root)
    if step == CeremonyStep.WALKTHROUGH:
        return render_step_3_walkthrough(adr_id, state.walkthrough_commands)
    if step == CeremonyStep.EXECUTE:
        return render_step_4_execute(adr_id, state.walkthrough_commands)
    if step == CeremonyStep.ATTESTATION:
        return render_step_5_attestation(adr_id)
    if step == CeremonyStep.CLOSEOUT:
        return render_step_6_closeout(adr_id)
    if step == CeremonyStep.ISSUES:
        return render_step_7_issues(adr_id)
    if step == CeremonyStep.RELEASE_NOTES:
        return render_step_8_release_notes(adr_id)
    if step == CeremonyStep.RELEASE:
        return render_step_9_release(adr_id)
    if step == CeremonyStep.COMPLETE:
        return render_step_10_complete(state)
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
) -> None:
    """Initialize or resume a ceremony."""
    existing = load_ceremony_state(project_root, adr_id)
    if existing and existing.completed_at:
        raise GzCliError(f"Ceremony for {adr_id} already completed at {existing.completed_at}")
    if existing:
        # Resume from current step
        output = _present_step(existing, project_root, adr_file, lane, manifest, obpi_files)
        _write_turn_lock(project_root, adr_id, existing.current_step)
        _output(as_json, existing, output)
        return

    from gzkit.commands.status import _adr_obpi_status_rows

    config = ensure_initialized()
    ledger = Ledger(get_project_root() / config.paths.ledger)
    obpi_rows = _adr_obpi_status_rows(project_root, config, ledger, adr_id)
    readiness = _adr_closeout_readiness(obpi_rows)
    blockers = readiness.get("blockers", [])
    if blockers:
        raise GzCliError(f"Cannot start ceremony: {'; '.join(blockers)}")

    now = _now_iso()
    commands = discover_walkthrough_commands(project_root, adr_id, obpi_files)
    state = CeremonyState(
        adr_id=adr_id,
        current_step=CeremonyStep.SUMMARY,
        is_foundation=_is_foundation_adr(adr_id),
        started_at=now,
        updated_at=now,
        step_history=[
            CeremonyStepRecord(step=CeremonyStep.INITIALIZE, presented_at=now, acknowledged_at=now),
            CeremonyStepRecord(step=CeremonyStep.SUMMARY, presented_at=now),
        ],
        walkthrough_commands=commands,
    )
    save_ceremony_state(project_root, state)
    output = _present_step(state, project_root, adr_file, lane, manifest, obpi_files)
    _write_turn_lock(project_root, adr_id, CeremonyStep.SUMMARY)
    _output(as_json, state, output)


def _advance_ceremony(
    project_root: Path,
    adr_id: str,
    adr_file: Path,
    lane: str,
    manifest: dict[str, Any],
    obpi_files: list[Path],
    as_json: bool,
) -> None:
    """Acknowledge current step and advance to the next."""
    state = load_ceremony_state(project_root, adr_id)
    if state is None:
        raise GzCliError(f"No ceremony in progress for {adr_id}. Run --ceremony first.")
    if state.completed_at:
        raise GzCliError(f"Ceremony for {adr_id} already completed.")

    now = _now_iso()
    # Acknowledge current step
    history = list(state.step_history)
    if history and history[-1].acknowledged_at is None:
        history[-1] = history[-1].model_copy(update={"acknowledged_at": now})

    next_s = _next_step(state.current_step, state.is_foundation)
    if next_s == -1:
        new_state = state.model_copy(
            update={
                "step_history": history,
                "completed_at": now,
                "updated_at": now,
            }
        )
        save_ceremony_state(project_root, new_state)
        _cleanup_hook_files(project_root, adr_id)
        output = "Ceremony already at final step."
        _output(as_json, new_state, output)
        return

    history.append(CeremonyStepRecord(step=next_s, presented_at=now))
    completed_at = now if next_s == CeremonyStep.COMPLETE else None
    new_state = state.model_copy(
        update={
            "current_step": next_s,
            "step_history": history,
            "updated_at": now,
            "completed_at": completed_at,
        }
    )
    save_ceremony_state(project_root, new_state)
    output = _present_step(new_state, project_root, adr_file, lane, manifest, obpi_files)
    if completed_at:
        _cleanup_hook_files(project_root, adr_id)
    else:
        _write_turn_lock(project_root, adr_id, next_s)
    _output(as_json, new_state, output)


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
    """Record attestation at step 5 and advance to step 6."""
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

    now = _now_iso()
    history = list(state.step_history)
    if history and history[-1].acknowledged_at is None:
        history[-1] = history[-1].model_copy(update={"acknowledged_at": now})

    next_s = _next_step(state.current_step, state.is_foundation)
    history.append(CeremonyStepRecord(step=next_s, presented_at=now))
    new_state = state.model_copy(
        update={
            "current_step": next_s,
            "attestation": attestation,
            "step_history": history,
            "updated_at": now,
        }
    )
    save_ceremony_state(project_root, new_state)
    output = _present_step(new_state, project_root, adr_file, lane, manifest, obpi_files)
    _write_turn_lock(project_root, adr_id, next_s)
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
        console.print(f"Ceremony {adr_id}: Step {state.current_step} ({step_name}) — {status}")
        if state.attestation:
            console.print(f"  Attestation: {state.attestation}")


def _cleanup_hook_files(project_root: Path, adr_id: str) -> None:
    """Remove turn-lock and hook-state files after ceremony completes."""
    for path in (_turn_lock_path(project_root, adr_id), _hook_state_path(project_root, adr_id)):
        if path.exists():
            path.unlink()


def _output(as_json: bool, state: CeremonyState, text: str) -> None:
    """Print output in the requested format."""
    if as_json:
        print(
            json.dumps(
                {
                    "adr_id": state.adr_id,
                    "step": state.current_step,
                    "content": text,
                    "completed": state.completed_at is not None,
                },
                indent=2,
            )
        )
    else:
        console.print(text)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def ceremony_cmd(
    adr: str,
    as_json: bool,
    ceremony_next: bool,
    ceremony_status: bool,
    ceremony_attest: str | None,
) -> None:
    """Dispatch ceremony sub-commands."""
    # Validate flag combinations
    if ceremony_next and ceremony_attest:
        raise GzCliError("Cannot use --next and --attest together.")

    project_root, adr_id, adr_file, lane, manifest, obpi_files = _resolve_adr_context(adr)

    if ceremony_status:
        _show_status(project_root, adr_id, as_json)
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
    )
