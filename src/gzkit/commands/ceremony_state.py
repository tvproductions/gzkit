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

from pydantic import BaseModel, ConfigDict, Field, field_validator

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


class WalkthroughDemo(BaseModel):
    """One walkthrough demo: a command plus the exit code that PROVES its claim.

    The expected exit is the whole point (GHI #738). An ADR whose product is a
    refusal, a gate, or a closed door has nothing it can demonstrate while every
    demo must exit 0 — an all-green queue is indistinguishable from the
    enforcement never having been built. ADR-0.34.0's closeout walked 11 commands
    that were all positive assertions while its thesis was that four authoring
    doors now refuse.

    The ``claim`` / ``command`` / ``expected_exit`` shape is taken deliberately
    from ``## Fidelity Assertions`` (``gzkit.fidelity.FidelityAssertion``), which
    could already express a negative while this surface could not. The two now
    share one representation, which was the issue's own diagnosis of the gap.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    command: str = Field(..., description="Command to demonstrate")
    expected_exit: int = Field(0, description="Exit code that proves the claim")
    claim: str | None = Field(None, description="What the demo proves, when a claim is known")


def _coerce_demo(value: object) -> object:
    """Accept a bare command string as a zero-exit demo.

    Ceremony state persists to ``.gzkit/ceremonies/*.json`` and in-flight files
    written before GHI #738 hold ``list[str]``. Coercing on read keeps a paused
    ceremony resumable across the upgrade instead of failing validation on a
    file the operator cannot regenerate without restarting the ceremony.
    """
    return {"command": value} if isinstance(value, str) else value


class CeremonyState(BaseModel):
    """Persistent ceremony state stored in .gzkit/ceremonies/."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    adr_id: str = Field(..., description="Canonical ADR ID")
    current_step: int = Field(..., description="Current step number")
    is_foundation: bool = Field(..., description="0.0.x foundation ADR")
    started_at: str = Field(..., description="ISO-8601 timestamp")
    updated_at: str = Field(..., description="ISO-8601 timestamp")
    step_history: list[CeremonyStepRecord] = Field(default_factory=list, description="Step records")
    walkthrough_commands: list[WalkthroughDemo] = Field(
        default_factory=list, description="Demos for Step 5"
    )
    walkthrough_index: int = Field(0, description="Current command index in Step 5")
    attestation: str | None = Field(None, description="Human attestation text")
    completed_at: str | None = Field(None, description="ISO-8601 when ceremony finished")
    attempt: int = Field(1, description="R&R attempt number")
    paused_at: str | None = Field(None, description="ISO-8601 when paused for revision")

    @field_validator("walkthrough_commands", mode="before")
    @classmethod
    def _accept_legacy_command_strings(cls, value: object) -> object:
        if isinstance(value, list):
            return [_coerce_demo(item) for item in value]
        return value


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

    The single-source verdict classifier for both attestation-emitting paths:
    ``closeout_ceremony`` calls it directly and ``closeout`` imports it through
    the ``closeout_ceremony`` facade (GHI #573 collapsed the former byte-identical
    ``closeout._parse_ceremony_attestation_text`` fork; BI-2, ADR-0.0.63 audit).
    Single-sourcing is the structural guard against the ``attested`` ledger
    event ``status`` silently diverging from the ``lifecycle_transition``
    ``to_state``.

    The ceremony's ``--attest "..."`` argument is freeform but conventionally
    leads with one of the canonical tokens prescribed by Step 6
    (``Completed`` / ``Completed - Partial: <reason>`` / ``Dropped - <reason>``)
    or the AGENTS.md § Attestation pattern (``attest <token> - <enrichment>``).
    The ``partial`` and ``dropped`` keywords are matched case-insensitively in
    the leading 120-char window; the full stripped text is returned as the
    reason for non-completed verdicts so the operator's verbatim attestation
    flows through to the ledger and closeout form unchanged.
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
        console.print(text, markup=False)
