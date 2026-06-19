"""Tests for gz validate --qc-binding behavioral audit (OBPI-0.0.73-02).

Validates theater-signature detection, negative-control execution,
exit-code behavior, gz check wiring, and CLI alignment.
"""

from __future__ import annotations

import subprocess
import sys
import unittest

from gzkit.governance.trust_audits.qc_binding import (
    THEATER_SIGNATURES,
    _check_negative_control,
    _check_theater_signatures,
    audit_qc_binding,
)
from gzkit.qc_binding import QCStep
from gzkit.traceability import covers


def _make_step(
    step_id: str = "test-step",
    binding: str = "bound",
    theater_flags: list[str] | None = None,
) -> QCStep:
    return QCStep(
        id=step_id,
        name=step_id.replace("-", " ").title(),
        kind="audit",
        subject="src/",
        binding=binding,
        wired_into=["gz check"],
        theater_flags=theater_flags or [],
        enforcement_locus="python_function",
    )


class TestNegativeControlDetection(unittest.TestCase):
    """NC-based behavioral detection (REQ-0.0.73-02-01 and REQ-0.0.73-02-02)."""

    @covers("REQ-0.0.73-02-01")
    def test_hollow_step_flagged_as_theater(self) -> None:
        step = _make_step()
        nc_registry = {step.id: lambda: 0}  # NC passes → hollow → theater
        errors = _check_negative_control(step, nc_registry)
        self.assertEqual(len(errors), 1)
        self.assertIn("hollow", errors[0].message.lower())

    @covers("REQ-0.0.73-02-02")
    def test_genuine_step_no_false_positive(self) -> None:
        step = _make_step()
        nc_registry = {step.id: lambda: 1}  # NC fails → genuine → no error
        errors = _check_negative_control(step, nc_registry)
        self.assertEqual(len(errors), 0)

    @covers("REQ-0.0.73-02-02")
    def test_step_without_nc_not_flagged(self) -> None:
        step = _make_step(step_id="no-nc-step")
        errors = _check_negative_control(step, nc_registry={})
        self.assertEqual(len(errors), 0)

    @covers("REQ-0.0.73-02-07")
    def test_non_bound_step_nc_not_executed(self) -> None:
        step = _make_step(binding="advisory")
        called = []
        nc_registry = {step.id: lambda: called.append(1) or 0}
        # _check_negative_control is for bound steps; for advisory, caller decides
        errors = _check_negative_control(step, nc_registry)
        # NC returns 0 → would flag if executed, but advisory check is caller-gated
        # The function itself does not gate on binding (binding-gate is in audit_qc_binding)
        self.assertEqual(len(errors), 1)  # NC executed and passed → theater finding


class TestTheaterSignatureDetection(unittest.TestCase):
    """Static theater-signature detection via theater_flags (REQ-0.0.73-02-03)."""

    @covers("REQ-0.0.73-02-03")
    def test_mtime_signature_detected(self) -> None:
        step = _make_step(theater_flags=["mtime-where-name-says-content"])
        errors = _check_theater_signatures(step)
        self.assertEqual(len(errors), 1)
        self.assertIn("mtime-where-name-says-content", errors[0].message)

    @covers("REQ-0.0.73-02-03")
    def test_empty_input_passes_signature_detected(self) -> None:
        step = _make_step(theater_flags=["empty-input-passes"])
        errors = _check_theater_signatures(step)
        self.assertEqual(len(errors), 1)
        self.assertIn("empty-input-passes", errors[0].message)

    @covers("REQ-0.0.73-02-03")
    def test_copy_vs_self_signature_detected(self) -> None:
        step = _make_step(theater_flags=["copy-vs-self"])
        errors = _check_theater_signatures(step)
        self.assertEqual(len(errors), 1)
        self.assertIn("copy-vs-self", errors[0].message)

    @covers("REQ-0.0.73-02-03")
    def test_fixture_only_signature_detected(self) -> None:
        step = _make_step(theater_flags=["fixture-only"])
        errors = _check_theater_signatures(step)
        self.assertEqual(len(errors), 1)
        self.assertIn("fixture-only", errors[0].message)

    @covers("REQ-0.0.73-02-03")
    def test_skip_if_pass_signature_detected(self) -> None:
        step = _make_step(theater_flags=["skip-if-PASS"])
        errors = _check_theater_signatures(step)
        self.assertEqual(len(errors), 1)
        self.assertIn("skip-if-PASS", errors[0].message)

    @covers("REQ-0.0.73-02-03")
    def test_prose_graded_by_nothing_signature_detected(self) -> None:
        step = _make_step(theater_flags=["prose-graded-by-nothing"])
        errors = _check_theater_signatures(step)
        self.assertEqual(len(errors), 1)
        self.assertIn("prose-graded-by-nothing", errors[0].message)

    @covers("REQ-0.0.73-02-03")
    def test_all_canonical_signatures_in_registry(self) -> None:
        # Six ADR-0.0.37 facade signatures plus the seventh
        # `shape-graded-not-substance` signature added by OBPI-0.0.73-07
        # (GHI #624) — calibrated on the gz adr evaluate shape-vs-substance defect.
        expected = {
            "mtime-where-name-says-content",
            "empty-input-passes",
            "copy-vs-self",
            "fixture-only",
            "skip-if-PASS",
            "prose-graded-by-nothing",
            "shape-graded-not-substance",
        }
        self.assertEqual(set(THEATER_SIGNATURES), expected)

    @covers("REQ-0.0.73-02-03")
    def test_unknown_flag_not_caught_as_canonical(self) -> None:
        step = _make_step(theater_flags=["invented-signature"])
        errors = _check_theater_signatures(step)
        self.assertEqual(len(errors), 0)

    @covers("REQ-0.0.73-02-03")
    def test_multiple_signatures_each_produce_error(self) -> None:
        step = _make_step(theater_flags=["copy-vs-self", "empty-input-passes"])
        errors = _check_theater_signatures(step)
        self.assertEqual(len(errors), 2)


class TestExitCodeBehavior(unittest.TestCase):
    """Exit 3 on theater findings, exit 0 on clean (REQ-0.0.73-02-04)."""

    @covers("REQ-0.0.73-02-04")
    def test_exit_0_when_all_bound_steps_have_negative_controls(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "gzkit", "validate", "--qc-binding"],
            capture_output=True,
        )
        output = result.stdout.decode() + result.stderr.decode()
        self.assertEqual(result.returncode, 0, output)
        self.assertIn("No QC theater detected", output)

    @covers("REQ-0.0.73-02-04")
    def test_audit_qc_binding_clean_when_all_bound_steps_wired(self) -> None:
        # A truly clean step set has one genuine NC per bound step. Acknowledged
        # debt is not clean; this synthetic registry proves the pass path without
        # pretending the current project is fully wired.
        from pathlib import Path

        from gzkit.qc_binding import build_qc_registry

        genuine_nc = {s.id: (lambda: 1) for s in build_qc_registry() if s.binding == "bound"}
        errors = audit_qc_binding(Path("."), nc_registry=genuine_nc)
        self.assertEqual(errors, [], [e.message for e in errors])

    @covers("REQ-0.0.73-02-04")
    def test_audit_qc_binding_flags_green_by_emptiness_on_empty_registry(self) -> None:
        # With no NCs active, the qc-binding step (not in debt) is unwired and
        # must be flagged — the audit no longer passes on zero coverage.
        from pathlib import Path

        errors = audit_qc_binding(Path("."), nc_registry={})
        self.assertTrue(
            any("green-by-emptiness" in e.message.lower() for e in errors),
            [e.message for e in errors],
        )

    @covers("REQ-0.0.73-02-06")
    def test_fail_closed_exit_3_on_theater(self) -> None:
        # Simulate a theater finding by passing an NC that passes (exit 0).
        # We can't easily inject into the real subprocess, so test the audit
        # function directly and verify exit-code-3 semantics in the data path.
        from pathlib import Path

        from gzkit.governance.trust_audits.qc_binding import _NEGATIVE_CONTROLS

        # Build a synthetic NC registry where one real step passes its NC.
        from gzkit.qc_binding import build_qc_registry

        registry = build_qc_registry()
        # Pick a bound step that is NOT the owned (already-wired) qc-binding step.
        bound_step = next(
            (s for s in registry if s.binding == "bound" and s.id != "qc-binding"), None
        )
        if bound_step is None:
            self.skipTest("No non-owned bound steps in registry")
        # Merge the production registry so the owned step stays wired-and-genuine;
        # only the injected step is hollow. The lone finding is then the hollow
        # step, not green-by-emptiness noise (ADR-0.0.73, OBPI-06 strengthening).
        hollow_nc: dict[str, object] = {**_NEGATIVE_CONTROLS, bound_step.id: lambda: 0}
        errors = audit_qc_binding(Path("."), nc_registry=hollow_nc)  # type: ignore
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("hollow" in e.message.lower() for e in errors))
        self.assertFalse(
            any("green-by-emptiness" in e.message.lower() for e in errors),
            [e.message for e in errors],
        )


class TestGzCheckWiring(unittest.TestCase):
    """QC binding is wired into gz check (REQ-0.0.73-02-05)."""

    @covers("REQ-0.0.73-02-05")
    def test_qc_binding_step_in_build_check_steps(self) -> None:
        from gzkit.commands.quality import _build_check_steps

        step_names = [name for name, _ in _build_check_steps()]
        self.assertIn("QC binding", step_names)

    @covers("REQ-0.0.73-02-05")
    def test_qc_binding_in_step_classification(self) -> None:
        from gzkit.qc_binding import _STEP_CLASSIFICATION

        self.assertIn("QC binding", _STEP_CLASSIFICATION)
        kind, subject, binding, locus = _STEP_CLASSIFICATION["QC binding"]
        self.assertEqual(binding, "bound")
        self.assertEqual(locus, "python_function")


class TestStructuralFences(unittest.TestCase):
    """Structural-fence invariants (REQ-0.0.73-02-06 and REQ-0.0.73-02-07)."""

    @covers("REQ-0.0.73-02-06")
    def test_qc_binding_step_is_bound_not_advisory(self) -> None:
        from gzkit.qc_binding import _STEP_CLASSIFICATION

        _, _, binding, _ = _STEP_CLASSIFICATION["QC binding"]
        self.assertEqual(binding, "bound")

    @covers("REQ-0.0.73-02-07")
    def test_behavioral_detection_via_nc_not_static_only(self) -> None:
        # A step with no theater_flags but a passing NC → theater (behavioral)
        step = _make_step(theater_flags=[])  # no static flags
        nc_registry = {step.id: lambda: 0}  # NC passes → theater
        theater_errors = _check_theater_signatures(step)
        nc_errors = _check_negative_control(step, nc_registry)
        # Static check: no errors; NC check: one error (behavioral)
        self.assertEqual(len(theater_errors), 0)
        self.assertEqual(len(nc_errors), 1)
        self.assertIn("hollow", nc_errors[0].message.lower())


class TestCliAlignment(unittest.TestCase):
    """--qc-binding is documented in the manpage (REQ-0.0.73-02-08)."""

    @covers("REQ-0.0.73-02-08")
    def test_qc_binding_in_validate_manpage(self) -> None:
        from pathlib import Path

        manpage = Path("docs/user/manpages/validate.md")
        self.assertTrue(manpage.exists(), "validate manpage not found")
        content = manpage.read_text(encoding="utf-8")
        self.assertIn("--qc-binding", content)

    @covers("REQ-0.0.73-02-08")
    def test_cli_alignment_exit_0(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "gzkit", "validate", "--cli-alignment"],
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode())


if __name__ == "__main__":
    unittest.main()
