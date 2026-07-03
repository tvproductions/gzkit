"""Tests for the canonical OBPI state machine model layer (ADR-0.31.0 / OBPI-0.31.0-01)."""

import ast
import inspect
import unittest
from pathlib import Path

import pydantic

from gzkit.core import obpi_state_machine
from gzkit.core.obpi_state_machine import (
    CANONICAL_TRANSITIONS,
    OBPI_STATES,
    OBPIState,
    State,
    Transition,
    WitnessRequirement,
    obpi_state_machine_json_schema,
)
from gzkit.schemas import load_schema
from gzkit.traceability import covers


class TestOBPIStateEnum(unittest.TestCase):
    """REQ-0.31.0-01-01: closed OBPIState StrEnum."""

    @covers("REQ-0.31.0-01-01")
    def test_obpi_state_members_are_exactly_the_eight_canonical_states(self) -> None:
        expected = [
            "drafted",
            "planned",
            "implementing",
            "verified",
            "attested",
            "synced",
            "withdrawn",
            "superseded",
        ]
        self.assertEqual([member.value for member in OBPIState], expected)
        self.assertEqual([member.name.lower() for member in OBPIState], expected)


class TestTransitionModel(unittest.TestCase):
    """REQ-0.31.0-01-02: frozen, extra-forbid Transition model typed to OBPIState."""

    @covers("REQ-0.31.0-01-02")
    def test_transition_accepts_valid_member_states_and_witness(self) -> None:
        transition = Transition(
            from_state=OBPIState.DRAFTED,
            to_state=OBPIState.PLANNED,
            required_evidence=["plan_receipt"],
            witness=WitnessRequirement.SELF_CLOSE,
        )
        self.assertEqual(transition.from_state, OBPIState.DRAFTED)
        self.assertEqual(transition.to_state, OBPIState.PLANNED)
        self.assertEqual(transition.required_evidence, ["plan_receipt"])
        self.assertEqual(transition.witness, WitnessRequirement.SELF_CLOSE)

    @covers("REQ-0.31.0-01-02")
    def test_transition_rejects_non_member_state(self) -> None:
        with self.assertRaises(pydantic.ValidationError):
            Transition(
                from_state="bogus",
                to_state=OBPIState.PLANNED,
                required_evidence=[],
                witness=WitnessRequirement.SELF_CLOSE,
            )

    @covers("REQ-0.31.0-01-02")
    def test_transition_rejects_unknown_field(self) -> None:
        with self.assertRaises(pydantic.ValidationError):
            Transition(
                from_state=OBPIState.DRAFTED,
                to_state=OBPIState.PLANNED,
                required_evidence=[],
                witness=WitnessRequirement.SELF_CLOSE,
                bogus_field="nope",
            )

    @covers("REQ-0.31.0-01-02")
    def test_transition_is_frozen(self) -> None:
        transition = Transition(
            from_state=OBPIState.DRAFTED,
            to_state=OBPIState.PLANNED,
            required_evidence=[],
            witness=WitnessRequirement.SELF_CLOSE,
        )
        with self.assertRaises(pydantic.ValidationError):
            transition.to_state = OBPIState.IMPLEMENTING  # type: ignore[misc]


class TestStateModel(unittest.TestCase):
    """REQ-0.31.0-01-03: frozen State model + canonical OBPI_STATES declaration."""

    @covers("REQ-0.31.0-01-03")
    def test_state_declares_terminal_bool(self) -> None:
        state = State(terminal=True)
        self.assertTrue(state.terminal)
        with self.assertRaises(pydantic.ValidationError):
            state.terminal = False  # type: ignore[misc]

    @covers("REQ-0.31.0-01-03")
    def test_obpi_states_has_exactly_one_entry_per_member(self) -> None:
        self.assertEqual(set(OBPI_STATES.keys()), set(OBPIState))
        for state in OBPIState:
            self.assertIsInstance(OBPI_STATES[state], State)

    @covers("REQ-0.31.0-01-03")
    def test_terminal_states_are_withdrawn_and_superseded_only(self) -> None:
        terminal_states = {state for state, model in OBPI_STATES.items() if model.terminal}
        self.assertEqual(terminal_states, {OBPIState.WITHDRAWN, OBPIState.SUPERSEDED})
        non_terminal_states = {state for state, model in OBPI_STATES.items() if not model.terminal}
        self.assertEqual(
            non_terminal_states,
            {
                OBPIState.DRAFTED,
                OBPIState.PLANNED,
                OBPIState.IMPLEMENTING,
                OBPIState.VERIFIED,
                OBPIState.ATTESTED,
                OBPIState.SYNCED,
            },
        )


class TestCanonicalTransitions(unittest.TestCase):
    """CANONICAL_TRANSITIONS: forward lifecycle + withdraw/supersede edges."""

    def test_canonical_transitions_is_nonempty_tuple_of_transitions(self) -> None:
        self.assertIsInstance(CANONICAL_TRANSITIONS, tuple)
        self.assertGreater(len(CANONICAL_TRANSITIONS), 0)
        for transition in CANONICAL_TRANSITIONS:
            self.assertIsInstance(transition, Transition)

    def test_verified_to_attested_requires_human_attested(self) -> None:
        matches = [
            t
            for t in CANONICAL_TRANSITIONS
            if t.from_state == OBPIState.VERIFIED and t.to_state == OBPIState.ATTESTED
        ]
        self.assertTrue(matches)
        for transition in matches:
            self.assertEqual(transition.witness, WitnessRequirement.HUMAN_ATTESTED)

    def test_withdraw_and_supersede_transitions_require_human_attested(self) -> None:
        matches = [
            t
            for t in CANONICAL_TRANSITIONS
            if t.to_state in (OBPIState.WITHDRAWN, OBPIState.SUPERSEDED)
        ]
        self.assertTrue(matches)
        for transition in matches:
            self.assertEqual(transition.witness, WitnessRequirement.HUMAN_ATTESTED)


class TestSchemaCoherence(unittest.TestCase):
    """REQ-0.31.0-01-04: committed schema equals the model projection."""

    @covers("REQ-0.31.0-01-04")
    def test_committed_schema_equals_model_projection(self) -> None:
        self.assertEqual(load_schema("obpi_state_machine"), obpi_state_machine_json_schema())

    @covers("REQ-0.31.0-01-04")
    def test_schema_projection_is_nontrivial(self) -> None:
        schema = obpi_state_machine_json_schema()
        self.assertNotEqual(schema, {})


class TestModelMonitorCliSeparationFence(unittest.TestCase):
    """REQ-0.31.0-01-05 [STRUCTURAL-FENCE]: no monitor/command imports."""

    @covers("REQ-0.31.0-01-05")
    def test_module_imports_no_monitor_or_command_surface(self) -> None:
        source_path = Path(inspect.getfile(obpi_state_machine))
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        forbidden_modules = ("gzkit.governance.invariants", "gzkit.commands")

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    for forbidden in forbidden_modules:
                        self.assertFalse(
                            alias.name == forbidden or alias.name.startswith(forbidden + "."),
                            f"forbidden import found: {alias.name}",
                        )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for forbidden in forbidden_modules:
                    self.assertFalse(
                        module == forbidden or module.startswith(forbidden + "."),
                        f"forbidden import-from found: {module}",
                    )


if __name__ == "__main__":
    unittest.main()
