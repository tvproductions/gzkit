"""Facade regression corpus — one fixture per theater signature (OBPI-0.0.73-06).

Each test loads a fixture from tests/governance/fixtures/facade_corpus/, creates
a QCStep with the corresponding theater flag, and asserts that
_check_theater_signatures detects it. This corpus ensures the six ADR-0.0.37
facade signatures stay caught — none can silently pass a future refactor.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.qc_binding import (
    _check_negative_control,
    _check_theater_signatures,
)
from gzkit.qc_binding import QCStep
from gzkit.traceability import covers

_CORPUS_DIR = Path(__file__).parent / "fixtures" / "facade_corpus"


def _load_fixture(filename: str) -> QCStep:
    data = json.loads((_CORPUS_DIR / filename).read_text(encoding="utf-8"))
    return QCStep(**data)


class TestFacadeRegressionCorpus(unittest.TestCase):
    """REQ-0.0.73-06-02: Each theater signature is detected; none silently passes."""

    @covers("REQ-0.0.73-06-02")
    def test_mtime_where_name_says_content_detected(self) -> None:
        step = _load_fixture("mtime_where_name_says_content.json")
        errors = _check_theater_signatures(step)
        self.assertGreaterEqual(len(errors), 1)
        self.assertTrue(
            any("mtime-where-name-says-content" in e.message for e in errors),
            f"Expected mtime-where-name-says-content in errors, got: {[e.message for e in errors]}",
        )

    @covers("REQ-0.0.73-06-02")
    def test_empty_input_passes_detected(self) -> None:
        step = _load_fixture("empty_input_passes.json")
        errors = _check_theater_signatures(step)
        self.assertGreaterEqual(len(errors), 1)
        self.assertTrue(
            any("empty-input-passes" in e.message for e in errors),
            f"Expected empty-input-passes in errors, got: {[e.message for e in errors]}",
        )

    @covers("REQ-0.0.73-06-02")
    def test_copy_vs_self_detected(self) -> None:
        step = _load_fixture("copy_vs_self.json")
        errors = _check_theater_signatures(step)
        self.assertGreaterEqual(len(errors), 1)
        self.assertTrue(
            any("copy-vs-self" in e.message for e in errors),
            f"Expected copy-vs-self in errors, got: {[e.message for e in errors]}",
        )

    @covers("REQ-0.0.73-06-02")
    def test_fixture_only_detected(self) -> None:
        step = _load_fixture("fixture_only.json")
        errors = _check_theater_signatures(step)
        self.assertGreaterEqual(len(errors), 1)
        self.assertTrue(
            any("fixture-only" in e.message for e in errors),
            f"Expected fixture-only in errors, got: {[e.message for e in errors]}",
        )

    @covers("REQ-0.0.73-06-02")
    def test_skip_if_pass_detected(self) -> None:
        step = _load_fixture("skip_if_pass.json")
        errors = _check_theater_signatures(step)
        self.assertGreaterEqual(len(errors), 1)
        self.assertTrue(
            any("skip-if-PASS" in e.message for e in errors),
            f"Expected skip-if-PASS in errors, got: {[e.message for e in errors]}",
        )

    @covers("REQ-0.0.73-06-02")
    def test_prose_graded_by_nothing_detected(self) -> None:
        step = _load_fixture("prose_graded_by_nothing.json")
        errors = _check_theater_signatures(step)
        self.assertGreaterEqual(len(errors), 1)
        self.assertTrue(
            any("prose-graded-by-nothing" in e.message for e in errors),
            f"Expected prose-graded-by-nothing in errors, got: {[e.message for e in errors]}",
        )

    @covers("REQ-0.0.73-07-04")
    def test_shape_graded_not_substance_detected(self) -> None:
        # Seventh signature (OBPI-0.0.73-07, GHI #624): calibrated on the
        # gz adr evaluate shape-vs-substance defect, distinct from the six
        # ADR-0.0.37 signatures.
        step = _load_fixture("shape_graded_not_substance.json")
        errors = _check_theater_signatures(step)
        self.assertGreaterEqual(len(errors), 1)
        self.assertTrue(
            any("shape-graded-not-substance" in e.message for e in errors),
            f"Expected shape-graded-not-substance in errors, got: {[e.message for e in errors]}",
        )

    @covers("REQ-0.0.73-06-02")
    def test_every_signature_has_a_fixture(self) -> None:
        from gzkit.governance.trust_audits.qc_binding import THEATER_SIGNATURES

        fixture_files = list(_CORPUS_DIR.glob("*.json"))
        self.assertEqual(
            len(fixture_files),
            len(THEATER_SIGNATURES),
            f"Expected one fixture per signature ({len(THEATER_SIGNATURES)}), "
            f"found {len(fixture_files)} fixture files.",
        )


class TestBehavioralCatch(unittest.TestCase):
    """REQ-0.0.73-06-02: the corpus exercises catch via the negative-control path,
    not just static flag-echo. A genuinely hollow bound step (one that PASSES its
    own negative control) is caught; a genuinely bound one is not.
    """

    def _bare_step(self) -> QCStep:
        return QCStep(
            id="behavioral-x",
            name="Behavioral X",
            kind="audit",
            subject="src/",
            binding="bound",
            wired_into=["gz check"],
            theater_flags=[],
            enforcement_locus="python_function",
        )

    @covers("REQ-0.0.73-06-02")
    def test_hollow_step_caught_by_negative_control(self) -> None:
        # NC returns 0 (the step passed its own negative control) → hollow → caught.
        # This is behavioral detection: the step carries NO theater flag, so
        # flag-echo would miss it. Only running the NC reveals the theater.
        step = self._bare_step()
        errors = _check_negative_control(step, {"behavioral-x": lambda: 0})
        self.assertEqual(len(errors), 1)
        self.assertIn("hollow", errors[0].message.lower())

    @covers("REQ-0.0.73-06-02")
    def test_genuine_step_passes_negative_control(self) -> None:
        # NC returns non-zero (the step FAILED its negative control, the right
        # reason) → genuinely bound → no finding. Proves the corpus can pass for
        # the right reason, not only fail.
        step = self._bare_step()
        errors = _check_negative_control(step, {"behavioral-x": lambda: 1})
        self.assertEqual(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
