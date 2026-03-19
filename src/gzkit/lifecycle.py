"""Content lifecycle state machine.

Enforces valid state transitions per content type. Each content type has
defined states and allowed transitions. Invalid transitions raise
``InvalidTransitionError``. Successful transitions emit a ledger event.

The state machine is the Django parallel to model save() — you cannot
persist invalid state.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class InvalidTransitionError(Exception):
    """Raised when an invalid lifecycle state transition is attempted."""

    def __init__(
        self,
        content_type: str,
        from_state: str,
        to_state: str,
        allowed: list[str] | None = None,
    ) -> None:
        self.content_type = content_type
        self.from_state = from_state
        self.to_state = to_state
        self.allowed = allowed or []
        allowed_str = ", ".join(self.allowed) if self.allowed else "none"
        super().__init__(
            f"Invalid transition for {content_type}: "
            f"{from_state!r} -> {to_state!r} "
            f"(allowed from {from_state!r}: {allowed_str})"
        )


class TransitionRule(BaseModel):
    """A single allowed state transition."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    from_state: str = Field(..., description="Source state")
    to_state: str = Field(..., description="Target state")


# ---------------------------------------------------------------------------
# Per-content-type transition tables
# ---------------------------------------------------------------------------

ADR_TRANSITIONS: list[TransitionRule] = [
    TransitionRule(from_state="Pool", to_state="Draft"),
    TransitionRule(from_state="Draft", to_state="Proposed"),
    TransitionRule(from_state="Proposed", to_state="Accepted"),
    TransitionRule(from_state="Accepted", to_state="Completed"),
    TransitionRule(from_state="Completed", to_state="Validated"),
    # Backward transitions for rejection/rework
    TransitionRule(from_state="Proposed", to_state="Draft"),
    # Deprecation/supersession from any active state
    TransitionRule(from_state="Draft", to_state="Superseded"),
    TransitionRule(from_state="Proposed", to_state="Superseded"),
    TransitionRule(from_state="Accepted", to_state="Superseded"),
    TransitionRule(from_state="Draft", to_state="Deprecated"),
    TransitionRule(from_state="Proposed", to_state="Deprecated"),
    TransitionRule(from_state="Accepted", to_state="Deprecated"),
]

OBPI_TRANSITIONS: list[TransitionRule] = [
    TransitionRule(from_state="Draft", to_state="Active"),
    TransitionRule(from_state="Active", to_state="Completed"),
    TransitionRule(from_state="Draft", to_state="Abandoned"),
    TransitionRule(from_state="Active", to_state="Abandoned"),
]

PRD_TRANSITIONS: list[TransitionRule] = [
    TransitionRule(from_state="Draft", to_state="Review"),
    TransitionRule(from_state="Review", to_state="Approved"),
    TransitionRule(from_state="Review", to_state="Draft"),
    TransitionRule(from_state="Approved", to_state="Superseded"),
]

CONSTITUTION_TRANSITIONS: list[TransitionRule] = [
    TransitionRule(from_state="Draft", to_state="Ratified"),
    TransitionRule(from_state="Ratified", to_state="Amended"),
    TransitionRule(from_state="Amended", to_state="Superseded"),
    TransitionRule(from_state="Ratified", to_state="Superseded"),
]

RULE_TRANSITIONS: list[TransitionRule] = [
    TransitionRule(from_state="Active", to_state="Deprecated"),
]

SKILL_TRANSITIONS: list[TransitionRule] = [
    TransitionRule(from_state="draft", to_state="active"),
    TransitionRule(from_state="active", to_state="deprecated"),
    TransitionRule(from_state="deprecated", to_state="retired"),
]

# Master mapping of content type name → transition rules
TRANSITION_TABLES: dict[str, list[TransitionRule]] = {
    "ADR": ADR_TRANSITIONS,
    "OBPI": OBPI_TRANSITIONS,
    "PRD": PRD_TRANSITIONS,
    "Constitution": CONSTITUTION_TRANSITIONS,
    "Rule": RULE_TRANSITIONS,
    "Skill": SKILL_TRANSITIONS,
}


def get_allowed_transitions(content_type: str, from_state: str) -> list[str]:
    """Return the list of states reachable from ``from_state`` for the given content type."""
    rules = TRANSITION_TABLES.get(content_type, [])
    return [r.to_state for r in rules if r.from_state == from_state]


def is_valid_transition(content_type: str, from_state: str, to_state: str) -> bool:
    """Check whether a transition is allowed without raising."""
    return to_state in get_allowed_transitions(content_type, from_state)


def get_all_states(content_type: str) -> list[str]:
    """Return all unique states defined for a content type's transition table."""
    rules = TRANSITION_TABLES.get(content_type, [])
    seen: set[str] = set()
    ordered: list[str] = []
    for rule in rules:
        for state in (rule.from_state, rule.to_state):
            if state not in seen:
                seen.add(state)
                ordered.append(state)
    return ordered


class LifecycleStateMachine:
    """Validates and records lifecycle transitions for governance artifacts.

    Usage::

        from gzkit.lifecycle import LifecycleStateMachine
        from gzkit.ledger import Ledger

        ledger = Ledger(Path(".gzkit/ledger.jsonl"))
        sm = LifecycleStateMachine(ledger)
        sm.transition("ADR-0.16.0", "ADR", "Draft", "Proposed")
    """

    def __init__(self, ledger: Any | None = None) -> None:
        """Initialize with an optional ledger for event recording.

        Args:
            ledger: A ``Ledger`` instance. If None, transitions are validated
                    but no events are emitted.
        """
        self._ledger = ledger

    def transition(
        self,
        artifact_id: str,
        content_type: str,
        from_state: str,
        to_state: str,
    ) -> dict[str, str]:
        """Validate and execute a lifecycle transition.

        Args:
            artifact_id: Identifier of the artifact (e.g., "ADR-0.16.0").
            content_type: Registry content type name (e.g., "ADR").
            from_state: Current state of the artifact.
            to_state: Desired target state.

        Returns:
            Dict with transition details (artifact_id, content_type, from_state, to_state).

        Raises:
            InvalidTransitionError: If the transition is not allowed.
            KeyError: If the content type has no transition table.
        """
        if content_type not in TRANSITION_TABLES:
            raise KeyError(f"No transition table for content type: {content_type}")

        allowed = get_allowed_transitions(content_type, from_state)
        if to_state not in allowed:
            raise InvalidTransitionError(content_type, from_state, to_state, allowed)

        if self._ledger is not None:
            from gzkit.ledger import lifecycle_transition_event

            event = lifecycle_transition_event(
                artifact_id=artifact_id,
                content_type=content_type,
                from_state=from_state,
                to_state=to_state,
            )
            self._ledger.append(event)

        return {
            "artifact_id": artifact_id,
            "content_type": content_type,
            "from_state": from_state,
            "to_state": to_state,
        }

    def validate_state(self, content_type: str, state: str) -> bool:
        """Check whether a state is valid for a content type.

        Returns True if the state appears in the transition table.
        """
        return state in get_all_states(content_type)
