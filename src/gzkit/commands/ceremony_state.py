"""Ceremony state models, persistence, and pure step/verdict helpers.

Extracted from ``closeout_ceremony.py`` to keep both modules under the
600-line budget (`.claude/rules/pythonic.md`; precedent: ``pipeline_markers.py``
and ``ledger_events.py`` carved out of ``pipeline_runtime.py``). The public
API is preserved by re-import in ``closeout_ceremony.py`` — existing
``from gzkit.commands.closeout_ceremony import CeremonyState`` call sites and
``closeout.py``'s ``ceremony_state_path`` import continue to resolve.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from enum import IntEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.commands.common import console

# ---------------------------------------------------------------------------
# Step enum
# ---------------------------------------------------------------------------


class CeremonyStep(IntEnum):
    """Ceremony steps matching the audit-protocol.md ceremony."""

    INITIALIZE = 1
    SUMMARY = 2
    DOCS_CHECK = 3
    WALKTHROUGH = 4
    EXECUTE = 5
    ATTESTATION = 6
    CLOSEOUT = 7
    ISSUES = 8
    RELEASE_NOTES = 9
    RELEASE = 10
    COMPLETE = 11


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
    attempt: int = Field(1, description="R&R attempt number")
    paused_at: str | None = Field(None, description="ISO-8601 when paused for revision")


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


def _cleanup_hook_files(project_root: Path, adr_id: str) -> None:
    """Remove turn-lock and hook-state files after ceremony completes."""
    for path in (_turn_lock_path(project_root, adr_id), _hook_state_path(project_root, adr_id)):
        if path.exists():
            path.unlink()


def _is_foundation_adr(adr_id: str) -> bool:
    return re.match(r"^ADR-0\.0\.\d+(?:[.-].*)?$", adr_id) is not None


# ---------------------------------------------------------------------------
# Step sequencing
# ---------------------------------------------------------------------------


def _next_step(current: int, is_foundation: bool) -> int:
    """Return the next valid step, skipping foundation-excluded steps."""
    candidate = current + 1
    while is_foundation and candidate in FOUNDATION_SKIP_STEPS:
        candidate += 1
    if candidate > CeremonyStep.COMPLETE:
        return -1
    return candidate


def _has_more_demos(state: CeremonyState) -> bool:
    """Return ``True`` when Step 5 has an unpresented demo after ``walkthrough_index``."""
    commands = state.walkthrough_commands
    return bool(commands) and state.walkthrough_index < len(commands) - 1


# ---------------------------------------------------------------------------
# Verdict + output helpers
# ---------------------------------------------------------------------------


def _classify_attestation_verdict(text: str) -> tuple[str, str | None]:
    """Map a ceremony attestation string to ``(status, reason)`` for the ledger.

    Mirrors ``closeout.py``'s canonical ``_parse_ceremony_attestation_text``; kept
    inline because ``closeout.py`` imports from this module (importing back is
    circular) and is outside this OBPI's scope. OBPI-0.0.63-05 (dual-runtime
    collapse) unifies these emission paths under BI-2.
    """
    head = text.strip().lower()[:120]
    if "dropped" in head:
        return "dropped", text.strip()
    if "partial" in head:
        return "partial", text.strip()
    return "completed", None


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
                    "attempt": state.attempt,
                },
                indent=2,
            )
        )
    else:
        console.print(text)
