"""Unit tests for dispatch-attestation pool ADR absorption (OBPI-0.0.73-05).

Tests are derived from brief requirements, not from implementation.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.traceability import covers


class TestDispatchAttestationInRegistry(unittest.TestCase):
    """REQ-0.0.73-05-01: dispatch-attestation step appears as bound in the QC registry."""

    @covers("REQ-0.0.73-05-01")
    def test_dispatch_attestation_bound_in_registry(self) -> None:
        """Given build_qc_registry(), the dispatch-attestation step must appear as bound.

        The registry is derived from _build_check_steps() — if 'Dispatch attestation'
        is in the step list with a 'bound' classification, the concern is no longer
        a free-floating unpromoted pool item but a registered enforcement step.
        """
        from gzkit.qc_binding import build_qc_registry

        registry = build_qc_registry()
        dispatch_steps = [s for s in registry if "dispatch" in s.id]
        self.assertTrue(
            dispatch_steps,
            "No step with 'dispatch' in its id found in the QC registry. "
            "Expected 'dispatch-attestation' to be registered (OBPI-0.0.73-05).",
        )
        for step in dispatch_steps:
            self.assertEqual(
                step.binding,
                "bound",
                f"Step {step.id!r} has binding={step.binding!r}; expected 'bound'.",
            )

    @covers("REQ-0.0.73-05-01")
    def test_dispatch_attestation_step_id_and_kind(self) -> None:
        """The dispatch-attestation step has the correct id, kind, and enforcement_locus."""
        from gzkit.qc_binding import build_qc_registry

        registry = build_qc_registry()
        ids = {s.id: s for s in registry}
        self.assertIn(
            "dispatch-attestation",
            ids,
            "Step id 'dispatch-attestation' not found in registry.",
        )
        step = ids["dispatch-attestation"]
        self.assertEqual(step.kind, "audit")
        self.assertEqual(step.enforcement_locus, "python_function")
        self.assertEqual(step.binding, "bound")


class TestPoolAdrAnnotation(unittest.TestCase):
    """REQ-0.0.73-05-02 + REQ-0.0.73-05-03: pool ADR is annotated and no longer floating."""

    def test_dispatch_attestation_audit_passes_on_project(self) -> None:
        """run_dispatch_attestation_audit passes over the actual project root.

        This test is the live proof that the annotation is in place and the
        audit step returns success — satisfying the REQ-0.0.73-05-02 'bound'
        enforcement requirement.
        """
        from gzkit.quality import run_dispatch_attestation_audit

        project_root = Path(__file__).parent.parent.parent
        result = run_dispatch_attestation_audit(project_root)
        self.assertTrue(
            result.success,
            f"run_dispatch_attestation_audit failed over project root: {result.stderr}",
        )
        self.assertEqual(result.returncode, 0)


class TestDispatchAttestationAuditNegativeControl(unittest.TestCase):
    """Negative control: audit fails when the absorption marker is missing."""

    @covers("REQ-0.0.73-05-01")
    def test_audit_fails_when_marker_missing(self) -> None:
        """run_dispatch_attestation_audit returns exit 3 when the pool ADR lacks the marker.

        This is the negative control that proves the step is 'bound' — it
        fails on the correct condition, not just when the file is absent.
        """
        from gzkit.quality import run_dispatch_attestation_audit

        pool_adr_content = """\
---
id: ADR-pool.obpi-pipeline-dispatch-attestation
status: Pool
parent: PRD-GZKIT-1.0.0
---

# ADR-pool: OBPI Pipeline Subagent Dispatch Attestation

## Intent

Close the OBPI pipeline's subagent-dispatch attestation gap.
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_root = Path(tmpdir)
            pool_dir = tmp_root / "docs" / "design" / "adr" / "pool"
            pool_dir.mkdir(parents=True)
            (pool_dir / "ADR-pool.obpi-pipeline-dispatch-attestation.md").write_text(
                pool_adr_content, encoding="utf-8"
            )
            result = run_dispatch_attestation_audit(tmp_root)

        self.assertFalse(result.success, "Audit should fail when absorption marker is absent.")
        self.assertEqual(result.returncode, 3)
        self.assertIn("absorbed_into", result.stderr)

    @covers("REQ-0.0.73-05-01")
    def test_audit_fails_when_pool_adr_missing(self) -> None:
        """run_dispatch_attestation_audit returns exit 3 when the pool ADR file is missing."""
        from gzkit.quality import run_dispatch_attestation_audit

        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_dispatch_attestation_audit(Path(tmpdir))

        self.assertFalse(result.success)
        self.assertEqual(result.returncode, 3)


if __name__ == "__main__":
    unittest.main()
