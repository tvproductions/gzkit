"""Canonical OBPI state machine model layer (ADR-0.31.0 / OBPI-0.31.0-01).

Lays the canonical OBPI-state-machine **model layer** as pure, additive
domain code: a closed :class:`OBPIState` StrEnum naming the eight canonical
states, plus frozen Pydantic :class:`State` and :class:`Transition` models
declaring each transition's predecessor state, required adjacent evidence,
and witness requirement, projected to a committed JSON schema
(``gzkit.schemas.load_schema("obpi_state_machine")``).

This module is the state anchor the runtime invariant monitor (OBPI-03) and
the withdraw/supersede CLI verbs (OBPI-02) consume. Per parent ADR
Boundary Invariant #1 (model / monitor / CLI separation), this module is
pure, additive domain code that imports NO runtime-monitor and NO command
surface -- it never depends on its consumers.

Parent ADR Decision item 1 (verbatim): "Named states (closed enum,
schema-bound). Every OBPI is in exactly one of: ``drafted``, ``planned``,
``implementing``, ``verified``, ``attested``, ``synced``, ``withdrawn``,
``superseded``. The current ``STATUS_VOCAB_MAPPING`` becomes a
*legacy-import* table only -- new briefs author against the closed enum
directly, and the vocab table shrinks rather than grows."

Parent ADR Decision item 2 (verbatim): "Named transitions (closed enum,
schema-bound). Every state change is an event with a name (e.g.
``obpi.transitioned.attested``), declared preconditions (predecessor state,
required adjacent evidence), declared postconditions (successor state,
emitted ancillary events), and a declared witness requirement:
``human_attested`` (a human attests -- transport-agnostic, relayed verbatim
via ``--attestor-present`` / ``--attestation-text``) or ``self_close`` per
Exception-mode rules. Human attestation is sacrosanct and transport-agnostic;
no TTY/PTY/interactive-terminal mechanism gates the witness -- the mechanism
serves the attestation, never gates it (canon-owner directive). The witness
requirement is a property of the transition, not of one CLI command."
"""

from __future__ import annotations

import enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class OBPIState(enum.StrEnum):
    """Closed set of canonical OBPI lifecycle states (Decision item 1)."""

    DRAFTED = "drafted"
    PLANNED = "planned"
    IMPLEMENTING = "implementing"
    VERIFIED = "verified"
    ATTESTED = "attested"
    SYNCED = "synced"
    WITHDRAWN = "withdrawn"
    SUPERSEDED = "superseded"


class WitnessRequirement(enum.StrEnum):
    """Transport-agnostic witness requirement for a transition (Boundary Invariant #2).

    No TTY/PTY/interactive-terminal value exists here by design.
    """

    HUMAN_ATTESTED = "human_attested"
    SELF_CLOSE = "self_close"


class State(BaseModel):
    """A single canonical OBPI lifecycle state (Decision item 1)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    terminal: bool = Field(
        ..., description="True when this state has no outgoing canonical transitions."
    )


class Transition(BaseModel):
    """A single named, schema-bound state change (Decision item 2)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    from_state: OBPIState = Field(..., description="Predecessor state.")
    to_state: OBPIState = Field(..., description="Successor state.")
    required_evidence: list[str] = Field(
        ..., description="Adjacent evidence required as a precondition for this transition."
    )
    witness: WitnessRequirement = Field(
        ..., description="Witness requirement: human_attested or self_close."
    )


OBPI_STATES: dict[OBPIState, State] = {
    OBPIState.DRAFTED: State(terminal=False),
    OBPIState.PLANNED: State(terminal=False),
    OBPIState.IMPLEMENTING: State(terminal=False),
    OBPIState.VERIFIED: State(terminal=False),
    OBPIState.ATTESTED: State(terminal=False),
    OBPIState.SYNCED: State(terminal=False),
    OBPIState.WITHDRAWN: State(terminal=True),
    OBPIState.SUPERSEDED: State(terminal=True),
}

CANONICAL_TRANSITIONS: tuple[Transition, ...] = (
    (
        Transition(
            from_state=OBPIState.DRAFTED,
            to_state=OBPIState.PLANNED,
            required_evidence=["plan_receipt"],
            witness=WitnessRequirement.SELF_CLOSE,
        ),
        Transition(
            from_state=OBPIState.PLANNED,
            to_state=OBPIState.IMPLEMENTING,
            required_evidence=["task_start_receipt"],
            witness=WitnessRequirement.SELF_CLOSE,
        ),
        Transition(
            from_state=OBPIState.IMPLEMENTING,
            to_state=OBPIState.VERIFIED,
            required_evidence=["test_results"],
            witness=WitnessRequirement.SELF_CLOSE,
        ),
        Transition(
            from_state=OBPIState.VERIFIED,
            to_state=OBPIState.ATTESTED,
            required_evidence=["attestation_text"],
            witness=WitnessRequirement.HUMAN_ATTESTED,
        ),
        Transition(
            from_state=OBPIState.ATTESTED,
            to_state=OBPIState.SYNCED,
            required_evidence=["git_sync_receipt"],
            witness=WitnessRequirement.SELF_CLOSE,
        ),
    )
    + tuple(
        Transition(
            from_state=state,
            to_state=OBPIState.WITHDRAWN,
            required_evidence=["attestation_text"],
            witness=WitnessRequirement.HUMAN_ATTESTED,
        )
        for state in OBPIState
        if not OBPI_STATES[state].terminal
    )
    + tuple(
        Transition(
            from_state=state,
            to_state=OBPIState.SUPERSEDED,
            required_evidence=["attestation_text"],
            witness=WitnessRequirement.HUMAN_ATTESTED,
        )
        for state in OBPIState
        if not OBPI_STATES[state].terminal
    )
)


def obpi_state_machine_json_schema() -> dict[str, Any]:
    """Project the canonical state machine to a JSON schema.

    Composes the ``State``/``Transition`` model schemas with the enumerated
    ``OBPIState`` members and their per-state terminal flags, plus the
    canonical transition set -- a single deterministic dict, coherence-checked
    against the committed ``schemas/obpi_state_machine.json`` file.
    """
    return {
        "state_schema": State.model_json_schema(),
        "transition_schema": Transition.model_json_schema(),
        "states": {state.value: OBPI_STATES[state].model_dump() for state in OBPIState},
        "transitions": [t.model_dump() for t in CANONICAL_TRANSITIONS],
    }
