"""Unit tests for runtime invariant monitor (ADR-0.31.0 OBPI-03).

Tests the classifier that validates status transitions against OBPI-01's
CANONICAL_TRANSITIONS.
"""

from unittest import TestCase

from gzkit.core.obpi_state_machine import CANONICAL_TRANSITIONS, OBPIState
from gzkit.governance.obpi_transition_monitor import TransitionMonitor
from gzkit.traceability import covers


class TestTransitionMonitor(TestCase):
    """Verify the transition classifier."""

    def setUp(self) -> None:
        """Initialize the monitor once per test."""
        self.monitor = TransitionMonitor()

    def test_valid_main_sequence_transitions(self) -> None:
        """REQ-0.31.0-03-01: Monitor allows transitions in the canonical sequence."""
        # Drafted → Planned
        self.assertTrue(self.monitor.is_allowed(OBPIState.DRAFTED, OBPIState.PLANNED))
        # Planned → Implementing
        self.assertTrue(self.monitor.is_allowed(OBPIState.PLANNED, OBPIState.IMPLEMENTING))
        # Implementing → Verified
        self.assertTrue(self.monitor.is_allowed(OBPIState.IMPLEMENTING, OBPIState.VERIFIED))
        # Verified → Attested
        self.assertTrue(self.monitor.is_allowed(OBPIState.VERIFIED, OBPIState.ATTESTED))
        # Attested → Synced
        self.assertTrue(self.monitor.is_allowed(OBPIState.ATTESTED, OBPIState.SYNCED))

    def test_withdrawal_from_any_non_terminal_state(self) -> None:
        """Monitor allows withdrawal from any non-terminal state."""
        non_terminal_states = [
            OBPIState.DRAFTED,
            OBPIState.PLANNED,
            OBPIState.IMPLEMENTING,
            OBPIState.VERIFIED,
            OBPIState.ATTESTED,
            OBPIState.SYNCED,
        ]
        for state in non_terminal_states:
            with self.subTest(from_state=state):
                self.assertTrue(
                    self.monitor.is_allowed(state, OBPIState.WITHDRAWN),
                    f"Should allow withdrawal from {state}",
                )

    def test_supersession_from_any_non_terminal_state(self) -> None:
        """Monitor allows supersession from any non-terminal state."""
        non_terminal_states = [
            OBPIState.DRAFTED,
            OBPIState.PLANNED,
            OBPIState.IMPLEMENTING,
            OBPIState.VERIFIED,
            OBPIState.ATTESTED,
            OBPIState.SYNCED,
        ]
        for state in non_terminal_states:
            with self.subTest(from_state=state):
                self.assertTrue(
                    self.monitor.is_allowed(state, OBPIState.SUPERSEDED),
                    f"Should allow supersession from {state}",
                )

    def test_invalid_backward_transition(self) -> None:
        """Monitor refuses backward transitions (e.g., Synced → Attested)."""
        self.assertFalse(self.monitor.is_allowed(OBPIState.SYNCED, OBPIState.ATTESTED))

    def test_invalid_arbitrary_transition(self) -> None:
        """Monitor refuses arbitrary undeclared transitions."""
        self.assertFalse(self.monitor.is_allowed(OBPIState.DRAFTED, OBPIState.IMPLEMENTING))
        self.assertFalse(self.monitor.is_allowed(OBPIState.PLANNED, OBPIState.ATTESTED))
        self.assertFalse(self.monitor.is_allowed(OBPIState.VERIFIED, OBPIState.SYNCED))

    def test_terminal_state_transitions_refused(self) -> None:
        """Monitor refuses any outgoing transition from terminal states."""
        terminal_states = [OBPIState.WITHDRAWN, OBPIState.SUPERSEDED]
        for state in terminal_states:
            for target in OBPIState:
                if target != state:
                    with self.subTest(from_state=state, to_state=target):
                        self.assertFalse(
                            self.monitor.is_allowed(state, target),
                            f"Should refuse transition from terminal state {state} to {target}",
                        )

    def test_self_loop_transitions_refused(self) -> None:
        """Monitor refuses state→state transitions (no self-loops in CANONICAL_TRANSITIONS)."""
        for state in OBPIState:
            with self.subTest(state=state):
                self.assertFalse(
                    self.monitor.is_allowed(state, state),
                    f"Should refuse self-loop transition for {state}",
                )

    @covers("REQ-0.31.0-03-01")
    def test_monitor_uses_canonical_transitions(self) -> None:
        """Allowed iff declared: full-matrix biconditional against CANONICAL_TRANSITIONS.

        REQ-0.31.0-03-01: a (from_state, to_state) pair is classified allowed
        only when it matches a Transition in OBPI-01's CANONICAL_TRANSITIONS;
        every unmatched pair is refused. Asserted over the complete
        OBPIState x OBPIState matrix so neither an over-permissive nor an
        over-restrictive classifier can pass.
        """
        canonical_pairs = {(t.from_state, t.to_state) for t in CANONICAL_TRANSITIONS}
        for from_state in OBPIState:
            for to_state in OBPIState:
                expected = (from_state, to_state) in canonical_pairs
                with self.subTest(from_state=from_state, to_state=to_state):
                    self.assertEqual(
                        self.monitor.is_allowed(from_state, to_state),
                        expected,
                        f"is_allowed({from_state}, {to_state}) must be {expected} "
                        "per CANONICAL_TRANSITIONS membership",
                    )
