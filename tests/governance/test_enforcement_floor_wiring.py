"""Tests for OBPI-0.0.74-19: enforcement-floor wiring into gz check and pre-push.

REQ-0.0.74-19-01 [behavior]: run_enforcement_floor_audit registered as gz check step,
    READ-ONLY on clean (root=None passed to run_meta_validator).
REQ-0.0.74-19-02 [behavior]: enforcement floor wired into pre-push guard (guards.main()).
REQ-0.0.74-19-03 [behavior]: new gz check step carries its OWN qc negative control.
REQ-0.0.74-19-04 [structural-fence]: floor lands LAST — only after OBPI-17+18 (parent ADR BI#8).
"""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from gzkit.traceability import covers
from tests.commands.common import SilencedConsoleTestCase


class TestGzCheckStepWiring(unittest.TestCase):
    """REQ-0.0.74-19-01: run_enforcement_floor_audit is a registered gz check step."""

    @covers("REQ-0.0.74-19-01")
    def test_enforcement_floor_step_in_check_steps(self) -> None:
        """'Enforcement floor' step must appear in the gz check step assembly."""
        from gzkit.commands.quality import _build_check_steps

        step_names = [name for name, _ in _build_check_steps()]
        self.assertIn(
            "Enforcement floor",
            step_names,
            "gz check aggregator must include the Enforcement floor step (OBPI-0.0.74-19)",
        )

    @covers("REQ-0.0.74-19-01")
    def test_enforcement_floor_step_returns_quality_result(self) -> None:
        """run_enforcement_floor_audit must return a QualityResult on clean run."""
        from gzkit.quality import QualityResult, run_enforcement_floor_audit

        with patch("gzkit.enforcement.run_meta_validator") as mock_runner:
            mock_result = MagicMock()
            mock_result.facade_count = 0
            mock_result.test_bug_count = 0
            mock_result.verified_count = 5
            mock_result.claim_results = []
            mock_runner.return_value = mock_result

            result = run_enforcement_floor_audit(Path("/tmp/fake-root"))

        self.assertIsInstance(result, QualityResult)
        self.assertTrue(result.success, "clean run must return success=True")
        mock_runner.assert_called_once_with(root=None)

    @covers("REQ-0.0.74-19-01")
    def test_enforcement_floor_step_read_only_on_clean(self) -> None:
        """run_enforcement_floor_audit passes root=None (READ-ONLY) to run_meta_validator."""
        from gzkit.quality import run_enforcement_floor_audit

        calls: list[tuple[object, ...]] = []

        def _capture(**kwargs: object) -> MagicMock:
            calls.append(tuple(kwargs.items()))
            mock_result = MagicMock()
            mock_result.facade_count = 0
            mock_result.test_bug_count = 0
            mock_result.verified_count = 3
            mock_result.claim_results = []
            return mock_result

        with patch("gzkit.enforcement.run_meta_validator", side_effect=_capture):
            run_enforcement_floor_audit(Path("/tmp/fake-root"))

        self.assertEqual(len(calls), 1)
        self.assertIn(("root", None), calls[0], "root=None must be passed (READ-ONLY contract)")

    @covers("REQ-0.0.74-19-01")
    def test_enforcement_floor_step_fails_on_facade(self) -> None:
        """run_enforcement_floor_audit must return success=False when facade_count > 0."""
        from gzkit.quality import run_enforcement_floor_audit

        with patch("gzkit.enforcement.run_meta_validator") as mock_runner:
            mock_claim = MagicMock()
            mock_claim.outcome = "FACADE"
            mock_claim.message = "FACADE: claim 'test' entrypoint did not catch"
            mock_result = MagicMock()
            mock_result.facade_count = 1
            mock_result.test_bug_count = 0
            mock_result.verified_count = 0
            mock_result.claim_results = [mock_claim]
            mock_runner.return_value = mock_result

            result = run_enforcement_floor_audit(Path("/tmp/fake-root"))

        self.assertFalse(result.success, "FACADE outcome must cause success=False")
        self.assertNotEqual(result.returncode, 0, "FACADE outcome must produce non-zero returncode")


class TestPrePushGuardWiring(SilencedConsoleTestCase):
    """REQ-0.0.74-19-02: enforcement floor wired into the pre-push guard."""

    @covers("REQ-0.0.74-19-02")
    def test_main_calls_enforcement_floor_on_failure(self) -> None:
        """guards.main() must run enforcement floor and return non-zero on failure."""
        from gzkit.hooks import guards
        from gzkit.quality import QualityResult

        failure_result = QualityResult(
            success=False,
            command="enforcement-floor-audit",
            stdout="FACADE: some claim failed",
            stderr="",
            returncode=3,
        )
        success_result = QualityResult(
            success=True,
            command="enforcement-floor-audit",
            stdout="Enforcement floor: 5 claims verified.",
            stderr="",
            returncode=0,
        )

        with (
            patch.object(guards, "forbid_pytest", return_value=0),
            patch.object(guards, "forbid_manual_ledger_edits", return_value=0),
            patch.object(guards, "forbid_skill_sync_drift", return_value=0),
            patch("gzkit.quality.run_enforcement_floor_audit", return_value=failure_result),
        ):
            rc = guards.main()

        self.assertNotEqual(rc, 0, "pre-push must fail when enforcement floor reports FACADE")

        with (
            patch.object(guards, "forbid_pytest", return_value=0),
            patch.object(guards, "forbid_manual_ledger_edits", return_value=0),
            patch.object(guards, "forbid_skill_sync_drift", return_value=0),
            patch("gzkit.quality.run_enforcement_floor_audit", return_value=success_result),
        ):
            rc = guards.main()

        self.assertEqual(rc, 0, "pre-push must succeed when enforcement floor is clean")

    @covers("REQ-0.0.74-19-02")
    def test_enforcement_floor_guard_read_only(self) -> None:
        """The pre-push guard passes root=None via run_enforcement_floor_audit (READ-ONLY)."""
        from gzkit.hooks import guards
        from gzkit.quality import QualityResult

        success_result = QualityResult(
            success=True,
            command="enforcement-floor-audit",
            stdout="Enforcement floor: 5 claims verified.",
            stderr="",
            returncode=0,
        )

        captured_args: list[tuple[object, ...]] = []

        def _capture_call(root: Path) -> QualityResult:
            captured_args.append((root,))
            return success_result

        with (
            patch.object(guards, "forbid_pytest", return_value=0),
            patch.object(guards, "forbid_manual_ledger_edits", return_value=0),
            patch.object(guards, "forbid_skill_sync_drift", return_value=0),
            patch("gzkit.quality.run_enforcement_floor_audit", side_effect=_capture_call),
        ):
            guards.main()

        self.assertEqual(len(captured_args), 1, "enforcement floor must be called exactly once")


class TestEnforcementFloorOwnQcNc(unittest.TestCase):
    """REQ-0.0.74-19-03: the new gz check step carries its own qc negative control."""

    @covers("REQ-0.0.74-19-03")
    def test_enforcement_floor_in_known_claims(self) -> None:
        """'enforcement-floor' must be in _KNOWN_QC_CLAIM_IDS so @enforces accepts it."""
        from gzkit.governance.trust_audits._qc_negative_controls import _KNOWN_QC_CLAIM_IDS

        self.assertIn(
            "enforcement-floor",
            _KNOWN_QC_CLAIM_IDS,
            "'enforcement-floor' must be a known claim id (the floor step is itself NC-covered)",
        )

    @covers("REQ-0.0.74-19-03")
    def test_enforcement_floor_nc_in_table(self) -> None:
        """'enforcement-floor' must appear in _QC_NEGATIVE_CONTROL_TABLE."""
        from gzkit.governance.trust_audits._qc_negative_controls import (
            _QC_NEGATIVE_CONTROL_TABLE,
        )

        # Entries are (claim_id, fixture, entrypoint[, expect]) — the optional 4th
        # element pins the expected finding (GHI #699), so index rather than unpack.
        claim_ids = {entry[0] for entry in _QC_NEGATIVE_CONTROL_TABLE}
        self.assertIn(
            "enforcement-floor",
            claim_ids,
            "'enforcement-floor' must be registered in _QC_NEGATIVE_CONTROL_TABLE",
        )

    @covers("REQ-0.0.74-19-03")
    def test_enforcement_floor_nc_fixture_and_entrypoint_callable(self) -> None:
        """The enforcement-floor NC fixture and entrypoint must be callable."""
        from gzkit.governance.trust_audits._qc_negative_controls import (
            _QC_NEGATIVE_CONTROL_TABLE,
        )

        nc_entry = next(
            (t for t in _QC_NEGATIVE_CONTROL_TABLE if t[0] == "enforcement-floor"), None
        )
        self.assertIsNotNone(nc_entry, "'enforcement-floor' entry not found in NC table")
        assert nc_entry is not None
        _claim_id, fixture, entrypoint = nc_entry
        self.assertTrue(callable(fixture), "fixture must be callable")
        self.assertTrue(callable(entrypoint), "entrypoint must be callable")

    @covers("REQ-0.0.74-19-03")
    def test_enforcement_floor_nc_detects_facade_at_runtime(self) -> None:
        """The NC end-to-end: fixture produces a FACADE record; entrypoint detects it.

        This test exercises the full NC contract without relying on registration alone.
        If _ep_enforcement_floor is gutted to skip FACADE detection, it returns 0 here.
        """
        from gzkit.governance.trust_audits._qc_nc_entrypoints import _ep_enforcement_floor
        from gzkit.governance.trust_audits._qc_negative_controls import (
            _QC_NEGATIVE_CONTROL_TABLE,
        )

        nc_entry = next(
            (t for t in _QC_NEGATIVE_CONTROL_TABLE if t[0] == "enforcement-floor"), None
        )
        self.assertIsNotNone(nc_entry)
        assert nc_entry is not None
        _claim_id, fixture, _ep = nc_entry

        # Run the fixture to get the synthetic FACADE registry.
        records = fixture()

        # Run the entrypoint directly — it must return non-zero (caught the FACADE).
        result = _ep_enforcement_floor(records)
        self.assertGreater(
            result,
            0,
            "_ep_enforcement_floor must return non-zero when given a FACADE record "
            "(facade_count > 0 = meta-validator caught the violation)",
        )


if __name__ == "__main__":
    unittest.main()
