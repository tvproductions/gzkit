"""Tests for core lifecycle domain logic (extracted from lifecycle.py)."""

import unittest

from pydantic import ValidationError

from gzkit.core.lifecycle import (
    TRANSITION_TABLES,
    InvalidTransitionError,
    TransitionRule,
    get_all_states,
    get_allowed_transitions,
    is_valid_transition,
)


class TestCoreTransitionRule(unittest.TestCase):
    """Verify TransitionRule model is importable from core."""

    def test_transition_rule_frozen(self) -> None:
        rule = TransitionRule(from_state="Draft", to_state="Proposed")
        self.assertEqual(rule.from_state, "Draft")
        self.assertEqual(rule.to_state, "Proposed")

    def test_transition_rule_immutable(self) -> None:
        rule = TransitionRule(from_state="Draft", to_state="Proposed")
        with self.assertRaises(ValidationError):
            rule.from_state = "Active"


class TestCoreTransitionTables(unittest.TestCase):
    """Verify transition tables are accessible from core."""

    def test_adr_transitions_exist(self) -> None:
        self.assertIn("ADR", TRANSITION_TABLES)
        self.assertGreater(len(TRANSITION_TABLES["ADR"]), 0)

    def test_obpi_transitions_exist(self) -> None:
        self.assertIn("OBPI", TRANSITION_TABLES)

    def test_all_content_types_present(self) -> None:
        expected = {"ADR", "OBPI", "PRD", "Constitution", "Rule", "Skill"}
        self.assertEqual(set(TRANSITION_TABLES.keys()), expected)


class TestCorePureFunctions(unittest.TestCase):
    """Verify pure validation functions work from core."""

    def test_get_allowed_transitions(self) -> None:
        allowed = get_allowed_transitions("ADR", "Draft")
        self.assertIn("Proposed", allowed)

    def test_is_valid_transition(self) -> None:
        self.assertTrue(is_valid_transition("ADR", "Draft", "Proposed"))
        self.assertFalse(is_valid_transition("ADR", "Draft", "Completed"))

    def test_get_all_states(self) -> None:
        states = get_all_states("ADR")
        self.assertIn("Draft", states)
        self.assertIn("Proposed", states)

    def test_invalid_transition_error(self) -> None:
        with self.assertRaises(InvalidTransitionError):
            raise InvalidTransitionError("ADR", "Draft", "Completed", ["Proposed"])


class TestCoreReExports(unittest.TestCase):
    """Verify original module re-exports work (backward compat)."""

    def test_lifecycle_reexports_transition_tables(self) -> None:
        from gzkit.lifecycle import TRANSITION_TABLES as orig

        self.assertIs(orig, TRANSITION_TABLES)

    def test_lifecycle_reexports_functions(self) -> None:
        from gzkit.lifecycle import get_allowed_transitions as orig

        self.assertIs(orig, get_allowed_transitions)


if __name__ == "__main__":
    unittest.main()
