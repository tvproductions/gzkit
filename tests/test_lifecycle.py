"""Tests for the content lifecycle state machine."""

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.ledger import Ledger
from gzkit.lifecycle import (
    TRANSITION_TABLES,
    InvalidTransitionError,
    LifecycleStateMachine,
    get_all_states,
    get_allowed_transitions,
    is_valid_transition,
)


class TestTransitionTables(unittest.TestCase):
    """Verify transition table completeness and structure."""

    def test_all_expected_content_types_have_tables(self) -> None:
        expected = {"ADR", "OBPI", "PRD", "Constitution", "Rule", "Skill"}
        self.assertEqual(set(TRANSITION_TABLES.keys()), expected)

    def test_adr_happy_path(self) -> None:
        """Pool → Draft → Proposed → Accepted → Completed → Validated."""
        path = ["Pool", "Draft", "Proposed", "Accepted", "Completed", "Validated"]
        for i in range(len(path) - 1):
            self.assertTrue(
                is_valid_transition("ADR", path[i], path[i + 1]),
                f"ADR: {path[i]} -> {path[i + 1]} should be valid",
            )

    def test_obpi_happy_path(self) -> None:
        """Draft → Active → Completed."""
        self.assertTrue(is_valid_transition("OBPI", "Draft", "Active"))
        self.assertTrue(is_valid_transition("OBPI", "Active", "Completed"))

    def test_skill_happy_path(self) -> None:
        """draft → active → deprecated → retired."""
        path = ["draft", "active", "deprecated", "retired"]
        for i in range(len(path) - 1):
            self.assertTrue(
                is_valid_transition("Skill", path[i], path[i + 1]),
                f"Skill: {path[i]} -> {path[i + 1]} should be valid",
            )

    def test_adr_pool_cannot_skip_to_completed(self) -> None:
        self.assertFalse(is_valid_transition("ADR", "Pool", "Completed"))

    def test_adr_pool_cannot_skip_to_accepted(self) -> None:
        self.assertFalse(is_valid_transition("ADR", "Pool", "Accepted"))

    def test_obpi_draft_cannot_skip_to_completed(self) -> None:
        self.assertFalse(is_valid_transition("OBPI", "Draft", "Completed"))

    def test_adr_proposed_can_go_back_to_draft(self) -> None:
        self.assertTrue(is_valid_transition("ADR", "Proposed", "Draft"))


class TestGetAllowedTransitions(unittest.TestCase):
    """Test the get_allowed_transitions helper."""

    def test_adr_from_draft(self) -> None:
        allowed = get_allowed_transitions("ADR", "Draft")
        self.assertIn("Proposed", allowed)
        self.assertIn("Superseded", allowed)
        self.assertIn("Deprecated", allowed)

    def test_unknown_state_returns_empty(self) -> None:
        self.assertEqual(get_allowed_transitions("ADR", "NonExistent"), [])

    def test_unknown_content_type_returns_empty(self) -> None:
        self.assertEqual(get_allowed_transitions("Unknown", "Draft"), [])


class TestGetAllStates(unittest.TestCase):
    """Test the get_all_states helper."""

    def test_adr_states(self) -> None:
        states = get_all_states("ADR")
        for s in ("Pool", "Draft", "Proposed", "Accepted", "Completed", "Validated"):
            self.assertIn(s, states)

    def test_unknown_content_type(self) -> None:
        self.assertEqual(get_all_states("Unknown"), [])


class TestLifecycleStateMachine(unittest.TestCase):
    """Test the LifecycleStateMachine class."""

    def test_valid_transition_without_ledger(self) -> None:
        sm = LifecycleStateMachine()
        result = sm.transition("ADR-0.16.0", "ADR", "Draft", "Proposed")
        self.assertEqual(result["artifact_id"], "ADR-0.16.0")
        self.assertEqual(result["from_state"], "Draft")
        self.assertEqual(result["to_state"], "Proposed")

    def test_invalid_transition_raises(self) -> None:
        sm = LifecycleStateMachine()
        with self.assertRaises(InvalidTransitionError) as ctx:
            sm.transition("ADR-0.16.0", "ADR", "Pool", "Completed")
        err = ctx.exception
        self.assertEqual(err.content_type, "ADR")
        self.assertEqual(err.from_state, "Pool")
        self.assertEqual(err.to_state, "Completed")
        self.assertIn("Draft", err.allowed)

    def test_unknown_content_type_raises_key_error(self) -> None:
        sm = LifecycleStateMachine()
        with self.assertRaises(KeyError):
            sm.transition("X-1", "Unknown", "A", "B")

    def test_transition_emits_ledger_event(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger_path = Path(tmp) / "ledger.jsonl"
            ledger = Ledger(ledger_path)
            ledger.create()

            sm = LifecycleStateMachine(ledger)
            sm.transition("ADR-0.16.0", "ADR", "Draft", "Proposed")

            lines = ledger_path.read_text().strip().splitlines()
            self.assertEqual(len(lines), 1)

            event = json.loads(lines[0])
            self.assertEqual(event["event"], "lifecycle_transition")
            self.assertEqual(event["id"], "ADR-0.16.0")
            self.assertEqual(event["content_type"], "ADR")
            self.assertEqual(event["from_state"], "Draft")
            self.assertEqual(event["to_state"], "Proposed")

    def test_validate_state_valid(self) -> None:
        sm = LifecycleStateMachine()
        self.assertTrue(sm.validate_state("ADR", "Draft"))
        self.assertTrue(sm.validate_state("Skill", "active"))

    def test_validate_state_invalid(self) -> None:
        sm = LifecycleStateMachine()
        self.assertFalse(sm.validate_state("ADR", "NonExistent"))


class TestInvalidTransitionError(unittest.TestCase):
    """Test error message formatting."""

    def test_message_format(self) -> None:
        err = InvalidTransitionError("ADR", "Pool", "Completed", ["Draft"])
        self.assertIn("ADR", str(err))
        self.assertIn("Pool", str(err))
        self.assertIn("Completed", str(err))
        self.assertIn("Draft", str(err))

    def test_empty_allowed(self) -> None:
        err = InvalidTransitionError("ADR", "Validated", "Pool")
        self.assertIn("none", str(err))


if __name__ == "__main__":
    unittest.main()
