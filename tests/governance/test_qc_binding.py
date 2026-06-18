"""Unit tests for the QCStep model and registry (OBPI-0.0.73-01).

Tests are derived from brief requirements, not from implementation.
"""

from __future__ import annotations

import unittest

from pydantic import ValidationError

from gzkit.traceability import covers


class TestQCStepModelContract(unittest.TestCase):
    """REQ-0.0.73-01-01: QCStep is frozen, extra-forbid, and has all seven fields."""

    def _make_valid_kwargs(self) -> dict:
        return {
            "id": "lint",
            "name": "Lint",
            "kind": "lint",
            "subject": "src/",
            "binding": "bound",
            "wired_into": ["gz check"],
            "theater_flags": [],
            "enforcement_locus": "subprocess",
        }

    @covers("REQ-0.0.73-01-01")
    def test_qcstep_accepts_valid_instance(self) -> None:
        from gzkit.qc_binding import QCStep

        step = QCStep(**self._make_valid_kwargs())
        self.assertEqual(step.id, "lint")

    @covers("REQ-0.0.73-01-01")
    def test_qcstep_is_frozen(self) -> None:
        from pydantic import ValidationError as VE

        from gzkit.qc_binding import QCStep

        step = QCStep(**self._make_valid_kwargs())
        with self.assertRaises((VE, TypeError)):
            step.name = "mutated"  # type: ignore

    @covers("REQ-0.0.73-01-01")
    def test_qcstep_extra_field_forbidden(self) -> None:
        from gzkit.qc_binding import QCStep

        kwargs = self._make_valid_kwargs()
        kwargs["unknown_field"] = "value"
        with self.assertRaises(ValidationError):
            QCStep(**kwargs)

    @covers("REQ-0.0.73-01-01")
    def test_qcstep_has_all_seven_fields(self) -> None:
        from gzkit.qc_binding import QCStep

        expected_fields = {
            "id",
            "name",
            "kind",
            "subject",
            "binding",
            "wired_into",
            "theater_flags",
            "enforcement_locus",
        }
        self.assertEqual(set(QCStep.model_fields), expected_fields)

    @covers("REQ-0.0.73-01-01")
    def test_qcstep_missing_required_field_rejected(self) -> None:
        from gzkit.qc_binding import QCStep

        kwargs = self._make_valid_kwargs()
        del kwargs["id"]
        with self.assertRaises(ValidationError):
            QCStep(**kwargs)


class TestQCRegistryDerivation(unittest.TestCase):
    """REQ-0.0.73-01-02: Registry derives from gz check steps — no extra, no missing."""

    @covers("REQ-0.0.73-01-02")
    def test_registry_matches_gz_check_steps(self) -> None:
        # The BOUND registry is DERIVED from gz check — no extra, no missing. The
        # advisory self-registration channel (ADR-0.0.73, OBPI-07) adds steps
        # wired into other commands (e.g. `gz adr evaluate`); those are not gz
        # check steps and are excluded from this derived-set equality.
        from gzkit.commands.quality import _build_check_steps
        from gzkit.qc_binding import build_qc_registry

        check_step_names = {name for name, _ in _build_check_steps()}
        derived_names = {step.name for step in build_qc_registry() if "gz check" in step.wired_into}
        self.assertEqual(
            derived_names,
            check_step_names,
            "gz-check-derived registry names must match gz check step names exactly "
            "— no extra, no missing",
        )

    @covers("REQ-0.0.73-01-02")
    def test_registry_has_no_duplicates(self) -> None:
        from gzkit.qc_binding import build_qc_registry

        registry = build_qc_registry()
        ids = [step.id for step in registry]
        self.assertEqual(len(ids), len(set(ids)), "Each step ID must be unique in the registry")

    @covers("REQ-0.0.73-01-02")
    def test_registry_step_count_matches_check_steps(self) -> None:
        # Count only the gz-check-derived (bound-channel) steps; advisory
        # self-registered steps (ADR-0.0.73, OBPI-07) are sourced separately.
        from gzkit.commands.quality import _build_check_steps
        from gzkit.qc_binding import build_qc_registry

        derived = [s for s in build_qc_registry() if "gz check" in s.wired_into]
        self.assertEqual(len(derived), len(_build_check_steps()))


class TestQCStepBindingClassification(unittest.TestCase):
    """REQ-0.0.73-01-03: Every step has binding in {bound, advisory, unenforced}."""

    _VALID_BINDINGS = frozenset({"bound", "advisory", "unenforced"})

    @covers("REQ-0.0.73-01-03")
    def test_every_step_has_valid_binding(self) -> None:
        from gzkit.qc_binding import build_qc_registry

        for step in build_qc_registry():
            self.assertIn(
                step.binding,
                self._VALID_BINDINGS,
                f"Step '{step.name}' has invalid binding '{step.binding}'",
            )

    @covers("REQ-0.0.73-01-03")
    def test_every_step_declares_where_it_is_wired(self) -> None:
        # Every step declares a non-empty wired_into. Bound steps are wired into
        # `gz check`; advisory self-registered steps (ADR-0.0.73, OBPI-07) declare
        # the command they run inside (e.g. `gz adr evaluate`). A step that
        # declares no host command is the structural defect this guards against.
        from gzkit.qc_binding import build_qc_registry

        for step in build_qc_registry():
            self.assertTrue(
                step.wired_into,
                f"Step '{step.name}' must declare a non-empty wired_into",
            )
            if step.binding == "bound":
                self.assertIn(
                    "gz check",
                    step.wired_into,
                    f"Bound step '{step.name}' must be wired into gz check",
                )

    @covers("REQ-0.0.73-01-03")
    def test_theater_flags_empty_for_all_steps(self) -> None:
        # OBPI-01 establishes the model; theater_flags are populated by OBPI-02
        # negative-control runs. All flags must be empty at this stage.
        from gzkit.qc_binding import build_qc_registry

        for step in build_qc_registry():
            self.assertEqual(
                step.theater_flags,
                [],
                f"Step '{step.name}' theater_flags must be empty in OBPI-01",
            )


if __name__ == "__main__":
    unittest.main()
