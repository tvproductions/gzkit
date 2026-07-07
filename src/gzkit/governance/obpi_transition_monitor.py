"""Runtime invariant monitor for OBPI state transitions (ADR-0.31.0 OBPI-03).

Pure classifier that validates status transitions against OBPI-01's
CANONICAL_TRANSITIONS. Consumed by the frontmatter reconciler to refuse
silent status drift (GHI #348 class) at the write boundary.

Parent ADR Decision item 4 (verbatim): "A single invariant monitor. Every read
or write to the artifact graph passes through one monitor that asserts: (a) the
operation names a transition declared in (2); (b) preconditions are satisfied;
(c) the witness requirement is met. A frontmatter hand-edit that is not backed
by a declared transition is either rejected (no matching transition allowed) or
auto-emits the transition (so receipts and state never disagree). Today the
reconciler silently picks a winner; the monitor would refuse to let them
disagree in the first place."
"""

from __future__ import annotations

from gzkit.core.obpi_state_machine import CANONICAL_TRANSITIONS, OBPIState


class TransitionMonitor:
    """Classifier for OBPI state transitions against declared canonical transitions."""

    def __init__(self) -> None:
        """Initialize with OBPI-01's CANONICAL_TRANSITIONS."""
        # Build a set of allowed (from_state, to_state) pairs for O(1) lookup.
        self._allowed_transitions: set[tuple[OBPIState, OBPIState]] = {
            (t.from_state, t.to_state) for t in CANONICAL_TRANSITIONS
        }

    def is_allowed(self, from_state: OBPIState, to_state: OBPIState) -> bool:
        """Return True if the transition is declared in CANONICAL_TRANSITIONS.

        Args:
            from_state: The current OBPI state.
            to_state: The requested target state.

        Returns:
            True if the (from_state, to_state) pair matches a declared transition;
            False otherwise.

        """
        return (from_state, to_state) in self._allowed_transitions
