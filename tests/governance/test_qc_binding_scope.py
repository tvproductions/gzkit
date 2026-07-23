"""Tests for gz validate --qc-binding behavioral audit (OBPI-0.0.73-02).

Validates theater-signature detection, negative-control execution,
exit-code behavior, gz check wiring, and CLI alignment.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from gzkit.enforcement import EnforcementClaimRecord, _run_single_claim
from gzkit.governance.trust_audits.qc_binding import (
    THEATER_SIGNATURES,
    _check_theater_signatures,
    audit_qc_binding,
)
from gzkit.qc_binding import QCStep, build_qc_registry
from gzkit.traceability import covers


def _record(claim_id: str, *, caught: bool) -> EnforcementClaimRecord:
    """A synthetic enforcement-claim record whose entrypoint catches (or not) on demand."""
    return EnforcementClaimRecord(
        claim_id=claim_id,
        fixture=lambda: None,
        entrypoint=lambda _violation: ["found"] if caught else [],
        source_fn="test._record",
    )


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
    """NC-based behavioral detection via the lifted shared engine (REQ-0.0.73-02-01/02/07).

    ADR-0.0.74 (OBPI-0.0.74-16) lifted the run-NC engine into
    ``enforcement._run_single_claim``; the old ``() -> int`` exit signal (0 = hollow)
    is now ``bool(entrypoint(fixture()))`` (falsy = FACADE = hollow).
    """

    @covers("REQ-0.0.73-02-01")
    def test_hollow_claim_flagged_as_facade(self) -> None:
        # Entrypoint returns falsy on its violation fixture → hollow → FACADE.
        result = _run_single_claim(_record("test-step", caught=False))
        self.assertEqual(result.outcome, "FACADE")

    @covers("REQ-0.0.73-02-02")
    def test_genuine_claim_no_false_positive(self) -> None:
        # Entrypoint catches the violation (truthy) → genuinely bound → PASS.
        result = _run_single_claim(_record("test-step", caught=True))
        self.assertEqual(result.outcome, "PASS")

    @covers("REQ-0.0.73-02-02")
    def test_audit_skips_step_without_registered_claim_into_green_by_emptiness(self) -> None:
        # A bound step with no registered claim is flagged green-by-emptiness, never
        # silently passed (the engine has no debt escape).
        errors = audit_qc_binding(Path("."), nc_registry={})
        self.assertTrue(any("green-by-emptiness" in e.message.lower() for e in errors))

    def test_non_bound_step_nc_not_executed(self) -> None:
        # audit_qc_binding gates NC execution on binding == "bound": an advisory step
        # whose claim WOULD be a FACADE is not run, so it produces no finding.
        registry = build_qc_registry()
        advisory = [s for s in registry if s.binding != "bound"]
        if not advisory:
            self.skipTest("No advisory steps in registry")
        # Provide hollow records for advisory ids; audit must not run them.
        reg = {s.id: _record(s.id, caught=False) for s in advisory}
        # Also wire every bound step genuinely so the only candidates are advisory.
        reg.update({s.id: _record(s.id, caught=True) for s in registry if s.binding == "bound"})
        errors = audit_qc_binding(Path("."), nc_registry=reg)
        self.assertEqual(errors, [], [e.message for e in errors])


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
        # A truly clean step set has one genuine (catching) claim per bound step.
        # This synthetic registry proves the pass path without depending on real
        # subprocess NCs.
        genuine = {
            s.id: _record(s.id, caught=True) for s in build_qc_registry() if s.binding == "bound"
        }
        errors = audit_qc_binding(Path("."), nc_registry=genuine)
        self.assertEqual(errors, [], [e.message for e in errors])

    @covers("REQ-0.0.73-02-04")
    def test_audit_qc_binding_flags_green_by_emptiness_on_empty_registry(self) -> None:
        # With no claims registered, every bound step is unwired and must be flagged
        # — the audit no longer passes on zero coverage (no debt escape).
        errors = audit_qc_binding(Path("."), nc_registry={})
        self.assertTrue(
            any("green-by-emptiness" in e.message.lower() for e in errors),
            [e.message for e in errors],
        )

    def test_fail_closed_exit_3_on_theater(self) -> None:
        # Wire every bound step genuinely except one, which is hollow (entrypoint
        # returns falsy → FACADE). The lone finding is the hollow step, not
        # green-by-emptiness noise (ADR-0.0.73, OBPI-06 strengthening).
        registry = build_qc_registry()
        bound_step = next(
            (s for s in registry if s.binding == "bound" and s.id != "qc-binding"), None
        )
        if bound_step is None:
            self.skipTest("No non-owned bound steps in registry")
        reg = {s.id: _record(s.id, caught=True) for s in registry if s.binding == "bound"}
        reg[bound_step.id] = _record(bound_step.id, caught=False)  # hollow
        errors = audit_qc_binding(Path("."), nc_registry=reg)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any("hollow" in e.message.lower() for e in errors))
        self.assertFalse(
            any("green-by-emptiness" in e.message.lower() for e in errors),
            [e.message for e in errors],
        )


class TestGzCheckWiring(unittest.TestCase):
    """QC binding is wired into gz check (REQ-0.0.73-02-05)."""

    def test_qc_binding_step_in_build_check_steps(self) -> None:
        from gzkit.commands.quality import _build_check_steps

        step_names = [name for name, _ in _build_check_steps()]
        self.assertIn("QC binding", step_names)

    def test_qc_binding_in_step_classification(self) -> None:
        from gzkit.qc_binding import _STEP_CLASSIFICATION

        self.assertIn("QC binding", _STEP_CLASSIFICATION)
        kind, subject, binding, locus = _STEP_CLASSIFICATION["QC binding"]
        self.assertEqual(binding, "bound")
        self.assertEqual(locus, "python_function")


class TestStructuralFences(unittest.TestCase):
    """Structural-fence invariants (REQ-0.0.73-02-06 and REQ-0.0.73-02-07)."""

    def test_qc_binding_step_is_bound_not_advisory(self) -> None:
        from gzkit.qc_binding import _STEP_CLASSIFICATION

        _, _, binding, _ = _STEP_CLASSIFICATION["QC binding"]
        self.assertEqual(binding, "bound")

    def test_behavioral_detection_via_nc_not_static_only(self) -> None:
        # A step with no theater_flags is missed by static signature detection, but
        # the behavioral channel (running the claim's NC) catches it: a falsy
        # entrypoint → FACADE.
        step = _make_step(theater_flags=[])  # no static flags
        theater_errors = _check_theater_signatures(step)
        self.assertEqual(len(theater_errors), 0)
        result = _run_single_claim(_record(step.id, caught=False))
        self.assertEqual(result.outcome, "FACADE")


class TestCliAlignment(unittest.TestCase):
    """--qc-binding is documented in the manpage (REQ-0.0.73-02-08)."""

    def test_cli_alignment_exit_0(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "gzkit", "validate", "--cli-alignment"],
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode())


if __name__ == "__main__":
    unittest.main()
