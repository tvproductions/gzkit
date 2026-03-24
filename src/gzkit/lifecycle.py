"""Content lifecycle state machine.

Enforces valid state transitions per content type. Each content type has
defined states and allowed transitions. Invalid transitions raise
``InvalidTransitionError``. Successful transitions emit a ledger event.

The state machine is the Django parallel to model save() — you cannot
persist invalid state.

Pure domain logic (rules, models, validation) lives in ``gzkit.core.lifecycle``.
This module re-exports those and adds the I/O-coupled LifecycleStateMachine.
"""

from __future__ import annotations

from typing import Any

from gzkit.core.lifecycle import (
    ADR_TRANSITIONS,
    CONSTITUTION_TRANSITIONS,
    OBPI_TRANSITIONS,
    PRD_TRANSITIONS,
    RULE_TRANSITIONS,
    SKILL_TRANSITIONS,
    TRANSITION_TABLES,
    InvalidTransitionError,
    TransitionRule,
    get_all_states,
    get_allowed_transitions,
    is_valid_transition,
)

__all__ = [
    "ADR_TRANSITIONS",
    "CONSTITUTION_TRANSITIONS",
    "InvalidTransitionError",
    "LifecycleStateMachine",
    "OBPI_TRANSITIONS",
    "PRD_TRANSITIONS",
    "RULE_TRANSITIONS",
    "SKILL_TRANSITIONS",
    "TRANSITION_TABLES",
    "TransitionRule",
    "get_all_states",
    "get_allowed_transitions",
    "is_valid_transition",
]


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
            from gzkit.ledger import lifecycle_transition_event  # noqa: PLC0415

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
