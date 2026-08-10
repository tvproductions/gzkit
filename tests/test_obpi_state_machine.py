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
            transition.to_state = OBPIState.IMPLEMENTING  # ty: ignore[invalid-assignment]


class TestStateModel(unittest.TestCase):
    """REQ-0.31.0-01-03: frozen State model + canonical OBPI_STATES declaration."""

    @covers("REQ-0.31.0-01-03")
    def test_state_declares_terminal_bool(self) -> None:
        state = State(terminal=True)
        self.assertTrue(state.terminal)
        with self.assertRaises(pydantic.ValidationError):
            state.terminal = False  # ty: ignore[invalid-assignment]

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


_FORBIDDEN_MONITOR_COMMAND_MODULES = ("gzkit.governance.invariants", "gzkit.commands")


def _find_forbidden_imports(source: str, forbidden_modules: tuple[str, ...]) -> list[str]:
    """Return every forbidden-module import found in ``source``.

    Checks three shapes: ``import a.b.c``, ``from a.b import c`` (module
    prefix), and ``from a.b import c`` where the *combined* ``module.alias``
    dotted path is what matches (e.g. ``from gzkit.governance import
    invariants`` matching forbidden ``gzkit.governance.invariants``).
    """
    tree = ast.parse(source)
    found: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for forbidden in forbidden_modules:
                    if alias.name == forbidden or alias.name.startswith(forbidden + "."):
                        found.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                combined = f"{module}.{alias.name}" if module else alias.name
                for forbidden in forbidden_modules:
                    if (
                        module == forbidden
                        or module.startswith(forbidden + ".")
                        or combined == forbidden
                        or combined.startswith(forbidden + ".")
                    ):
                        found.append(combined)
    return found


class TestModelMonitorCliSeparationFence(unittest.TestCase):
    """REQ-0.31.0-01-05 [STRUCTURAL-FENCE]: no monitor/command imports."""

    def test_module_imports_no_monitor_or_command_surface(self) -> None:
        # Static-analysis fence (not a doc echo): parse the module source and
        # assert its import graph excludes the monitor/command surfaces. The
        # STRUCTURAL-FENCE REQ's proof channel is the parent-ADR boundary
        # invariant; this is its mechanical guard. The explicit ast.parse marks
        # the source-shape intent so the tautological-test audit's
        # _reads_project_source exemption recognizes it (the import scan itself
        # parses inside _find_forbidden_imports, one frame away).
        source_path = Path(inspect.getfile(obpi_state_machine))
        source = source_path.read_text(encoding="utf-8")
        ast.parse(source)
        found = _find_forbidden_imports(source, _FORBIDDEN_MONITOR_COMMAND_MODULES)
        self.assertEqual(found, [], f"forbidden import(s) found: {found}")

    def test_fence_detects_from_import_of_forbidden_leaf_module(self) -> None:
        # GHI #664 adversarial-review finding: `from gzkit.governance import
        # invariants` names the forbidden module only via the imported
        # alias, not the ImportFrom.module string alone — the fence must
        # combine module + alias to catch this shape.
        found = _find_forbidden_imports(
            "from gzkit.governance import invariants\n",
            _FORBIDDEN_MONITOR_COMMAND_MODULES,
        )
        self.assertEqual(found, ["gzkit.governance.invariants"])


if __name__ == "__main__":
    unittest.main()
