"""Persona-dispatch channel for `gz adr evaluate` (GHI #770).

`gz-adr-evaluate` SKILL.md § Persona Dispatch mandates three personas —
`spec-reviewer`, `quality-reviewer`, `narrator` — because "a single driver
scoring its own scoring is the precise optimistic-bias defect `spec-reviewer`'s
anti-traits name". That mandate was T1 doctrine with no T2 evidence: a
single-driver evaluation and a properly dispatched one were **byte-identical in
every artifact the system produces**, so the mandate could be skipped silently
and was (ADR-0.35.0, 2026-08-07).

This module is the honest dispatch channel, and it is deliberately the same
shape as `adr_eval_substance.py` (GHI #624): a dispatch is credited ONLY from a
recorded receipt and is reported **NOT DISPATCHED** absent one. It is never
inferred from the presence of scores — the same reason substance is never
inferred from shape. The scorecard renderer emits this channel unconditionally,
so "the dispatch did not run" is stated rather than merely not-claimed.

**Scope boundary, named rather than assumed.** The full attestation machinery
that would *cause* a dispatch to be recorded — `persona_adopted` /
`pipeline_dispatched` events carrying persona file SHA and session anchor, plus
their validator scope — is `ADR-pool.obpi-pipeline-dispatch-attestation`
Target Scopes #5/#6, still unpromoted. Nothing emits `persona_dispatched`
today, so this channel truthfully reports SINGLE-DRIVER on every scorecard.
That is the disclosure GHI #770 asks for, not a placeholder: the substance
channel ships on exactly these terms (zero `adr_substance_verdict` events on
disk, UNGRADED on every scorecard) and populates without a renderer change once
its producer exists. This one does too.
"""

from __future__ import annotations

import json
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

# The personas `gz-adr-evaluate` SKILL.md § Persona Dispatch mandates. Kept in
# declaration order so the rendered channel reads in the order the ceremony
# names them. `implementer` is deliberately absent — the skill excludes it
# ("evaluation is pre-implementation review — no code exists to write").
MANDATED_EVALUATION_PERSONAS: tuple[str, ...] = (
    "spec-reviewer",
    "quality-reviewer",
    "narrator",
)

# Ledger event that would record a persona dispatch. Unbuilt upstream — see the
# module docstring's scope boundary.
_DISPATCH_EVENT = "persona_dispatched"


class DispatchState(StrEnum):
    """Whether a mandated persona produced independent input.

    NOT_DISPATCHED is the honest default: it means no dispatch receipt has been
    recorded. It is NEVER produced by observing that scores exist — the whole
    point is that output cannot evidence its own independence.
    """

    DISPATCHED = "DISPATCHED"
    NOT_DISPATCHED = "NOT DISPATCHED"


class PersonaDispatchRecord(BaseModel):
    """Dispatch state for one mandated persona in one ceremony run.

    A DISPATCHED record MUST carry a receipt id — an event asserting a dispatch
    with nothing citable behind it is the "agent narrative recall instead of
    receipts" failure the pool ADR names. A NOT_DISPATCHED record carries none
    and asserts only the absence of evidence.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    persona_id: str = Field(..., description="Mandated persona stem")
    state: DispatchState = Field(..., description="Dispatch state for this persona")
    receipt_id: str = Field("", description="Dispatch receipt id (DISPATCHED only)")

    @property
    def is_dispatched(self) -> bool:
        """Return True when a receipted dispatch is recorded."""
        return self.state is DispatchState.DISPATCHED


def not_dispatched(persona_id: str) -> PersonaDispatchRecord:
    """Return the honest default: no dispatch receipt for this persona."""
    return PersonaDispatchRecord(persona_id=persona_id, state=DispatchState.NOT_DISPATCHED)


def get_dispatch_record_for_adr(
    project_root: Path,
    adr_id: str,
    persona_id: str,
) -> PersonaDispatchRecord:
    """Read the latest recorded dispatch receipt for one ADR/persona pair.

    Returns a DISPATCHED record only when a receipted event cites BOTH this ADR
    and this persona; otherwise NOT_DISPATCHED. Requiring the event to cite its
    subject is the GHI #647 lesson: an event of the right type that names a
    different subject proves nothing about this one.
    """
    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.exists():
        return not_dispatched(persona_id)

    latest: PersonaDispatchRecord | None = None
    for raw in ledger_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or _DISPATCH_EVENT not in line:
            continue
        record = _parse_dispatch_event(line, adr_id, persona_id)
        if record is not None:
            latest = record  # later lines win; ledger is append-only chronological
    return latest if latest is not None else not_dispatched(persona_id)


def _parse_dispatch_event(line: str, adr_id: str, persona_id: str) -> PersonaDispatchRecord | None:
    """Parse one ledger line into a receipted PersonaDispatchRecord, or None."""
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        return None
    if event.get("event") != _DISPATCH_EVENT:
        return None
    if event.get("adr_id") != adr_id or event.get("persona_id") != persona_id:
        return None
    receipt_id = str(event.get("receipt_id", ""))
    # Discipline gate: an undisciplined record does NOT silently credit a dispatch.
    if not receipt_id:
        return None
    return PersonaDispatchRecord(
        persona_id=persona_id,
        state=DispatchState.DISPATCHED,
        receipt_id=receipt_id,
    )


def dispatch_channel_for_adr(project_root: Path, adr_id: str) -> list[PersonaDispatchRecord]:
    """Return the full dispatch channel: one record per mandated persona."""
    return [
        get_dispatch_record_for_adr(project_root, adr_id, persona)
        for persona in MANDATED_EVALUATION_PERSONAS
    ]


def is_single_driver(channel: list[PersonaDispatchRecord]) -> bool:
    """Return True unless EVERY mandated persona produced receipted input.

    Partial dispatch is still single-driver. The three personas score different
    dimension families, so crediting a partial run as independent would let one
    cheap dispatch launder the two that never happened.
    """
    return not all(record.is_dispatched for record in channel)
