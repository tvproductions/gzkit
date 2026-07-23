"""Tests for the enforcement meta-validator runner (OBPI-0.0.74-16).

Tests derive from acceptance criteria in the OBPI brief:
  REQ-0.0.74-16-01  runner discovers, runs entrypoint(fixture()), asserts failure, strict
  REQ-0.0.74-16-02  emits enforcement_claim_verified receipt per claim; READ-ONLY on clean
  REQ-0.0.74-16-03  per-claim FACADE vs TEST-BUG guardrail-feedback + repro command
  REQ-0.0.74-16-04  engine lifted; un-forced NCs pass; qc_binding behavior preserved
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from gzkit.enforcement import (
    ClaimRunResult,
    EnforcementClaimRecord,
    RunnerResult,
    _run_single_claim,
    reset_enforcement_registry,
    run_meta_validator,
    set_known_claims,
)
from gzkit.traceability import covers

_TEST_CLAIMS = frozenset({"lint", "format", "typecheck"})


def _fixture_catches() -> Path:
    """Returns a violation path where the entrypoint WILL flag an error."""
    root = Path(tempfile.mkdtemp(prefix="gzkit-test-"))
    (root / "violation.txt").write_text("violation", encoding="utf-8")
    return root


def _entrypoint_catches(root: Path) -> list[str]:
    """Entrypoint that detects the violation (truthy → PASS)."""
    f = root / "violation.txt"
    return ["found"] if f.exists() else []


def _fixture_passes() -> Path:
    """Returns a 'violation' path that is actually clean — FACADE."""
    root = Path(tempfile.mkdtemp(prefix="gzkit-test-"))
    return root


def _entrypoint_passes(root: Path) -> list[str]:
    """Entrypoint that never detects anything (falsy → FACADE)."""
    return []


def _fixture_int_catches() -> Path:
    """Fixture for an int-signal entrypoint (non-zero = caught)."""
    root = Path(tempfile.mkdtemp(prefix="gzkit-test-"))
    (root / "bad.py").write_text("x = 1\n", encoding="utf-8")
    return root


def _entrypoint_int_catches(root: Path) -> int:
    """Returns non-zero (caught) if bad.py exists."""
    return 1 if (root / "bad.py").exists() else 0


def _fixture_raises() -> Path:
    """Fixture that raises (simulates TEST_BUG on fixture side)."""
    raise RuntimeError("fixture build failed")


def _entrypoint_ok(root: Path) -> list[str]:
    return []


def _fixture_ok() -> Path:
    return Path(tempfile.mkdtemp(prefix="gzkit-test-"))


def _entrypoint_raises(root: Path) -> list[str]:
    """Entrypoint that raises (simulates TEST_BUG on entrypoint side)."""
    raise RuntimeError("entrypoint failed")


class TestRunSingleClaim(unittest.TestCase):
    """_run_single_claim(record) returns ClaimRunResult with correct outcome (REQ-16-01)."""

    def setUp(self) -> None:
        reset_enforcement_registry()
        set_known_claims(_TEST_CLAIMS)

    def tearDown(self) -> None:
        reset_enforcement_registry()

    @covers("REQ-0.0.74-16-01")
    def test_pass_when_entrypoint_returns_truthy_list(self) -> None:
        record = EnforcementClaimRecord(
            claim_id="lint",
            fixture=_fixture_catches,
            entrypoint=_entrypoint_catches,
            source_fn="tests._fixture_catches",
        )
        result = _run_single_claim(record)
        self.assertIsInstance(result, ClaimRunResult)
        self.assertEqual(result.outcome, "PASS")
        self.assertEqual(result.claim_id, "lint")

    @covers("REQ-0.0.74-16-01")
    def test_pass_when_entrypoint_returns_nonzero_int(self) -> None:
        """Runner invokes entrypoint(fixture()) — fixture and entrypoint are structurally separate.

        The NC (fixture builder) does not call the validator; only the runner does, via
        entrypoint(). This structural separation makes forcing impossible by construction (BI#7).
        """
        record = EnforcementClaimRecord(
            claim_id="lint",
            fixture=_fixture_int_catches,
            entrypoint=_entrypoint_int_catches,
            source_fn="tests._fixture_int_catches",
        )
        result = _run_single_claim(record)
        self.assertEqual(result.outcome, "PASS")

    @covers("REQ-0.0.74-16-01")
    def test_facade_when_entrypoint_returns_falsy(self) -> None:
        record = EnforcementClaimRecord(
            claim_id="lint",
            fixture=_fixture_passes,
            entrypoint=_entrypoint_passes,
            source_fn="tests._fixture_passes",
        )
        result = _run_single_claim(record)
        self.assertEqual(result.outcome, "FACADE")

    @covers("REQ-0.0.74-16-01")
    def test_test_bug_when_fixture_raises(self) -> None:
        record = EnforcementClaimRecord(
            claim_id="lint",
            fixture=_fixture_raises,
            entrypoint=_entrypoint_ok,
            source_fn="tests._fixture_raises",
        )
        result = _run_single_claim(record)
        self.assertEqual(result.outcome, "TEST_BUG")
        self.assertIn("fixture", result.message.lower())

    @covers("REQ-0.0.74-16-01")
    def test_test_bug_when_entrypoint_raises(self) -> None:
        record = EnforcementClaimRecord(
            claim_id="lint",
            fixture=_fixture_ok,
            entrypoint=_entrypoint_raises,
            source_fn="tests._fixture_ok",
        )
        result = _run_single_claim(record)
        self.assertEqual(result.outcome, "TEST_BUG")
        self.assertIn("entrypoint", result.message.lower())

    @covers("REQ-0.0.74-16-01")
    def test_cleanup_is_called_after_pass(self) -> None:
        """Runner cleans up the fixture path after the entrypoint runs."""
        created: list[Path] = []

        def _fixture_tracking() -> Path:
            root = Path(tempfile.mkdtemp(prefix="gzkit-test-"))
            created.append(root)
            (root / "violation.txt").write_text("v", encoding="utf-8")
            return root

        record = EnforcementClaimRecord(
            claim_id="lint",
            fixture=_fixture_tracking,
            entrypoint=_entrypoint_catches,
            source_fn="test._fixture_tracking",
        )
        _run_single_claim(record)
        self.assertEqual(len(created), 1)
        self.assertFalse(created[0].exists(), "fixture path should be cleaned up")


class TestRunMetaValidator(unittest.TestCase):
    """run_meta_validator() collects results and returns RunnerResult (REQ-16-01, -02, -03)."""

    def setUp(self) -> None:
        reset_enforcement_registry()
        set_known_claims(_TEST_CLAIMS)

    def tearDown(self) -> None:
        reset_enforcement_registry()

    @covers("REQ-0.0.74-16-01")
    def test_all_pass_returns_runner_result_verified_count(self) -> None:
        records = [
            EnforcementClaimRecord(
                claim_id="lint",
                fixture=_fixture_catches,
                entrypoint=_entrypoint_catches,
                source_fn="tests._fixture_catches",
            ),
            EnforcementClaimRecord(
                claim_id="format",
                fixture=_fixture_catches,
                entrypoint=_entrypoint_catches,
                source_fn="tests._fixture_catches",
            ),
        ]
        result = run_meta_validator(registry=records)
        self.assertIsInstance(result, RunnerResult)
        self.assertEqual(result.verified_count, 2)
        self.assertEqual(result.facade_count, 0)
        self.assertEqual(result.test_bug_count, 0)

    @covers("REQ-0.0.74-16-01")
    def test_facade_claim_increments_facade_count(self) -> None:
        records = [
            EnforcementClaimRecord(
                claim_id="lint",
                fixture=_fixture_passes,
                entrypoint=_entrypoint_passes,
                source_fn="tests._fixture_passes",
            ),
        ]
        result = run_meta_validator(registry=records)
        self.assertEqual(result.verified_count, 0)
        self.assertEqual(result.facade_count, 1)

    @covers("REQ-0.0.74-16-01")
    def test_empty_registry_returns_zero_counts(self) -> None:
        result = run_meta_validator(registry=[])
        self.assertEqual(result.verified_count, 0)
        self.assertEqual(result.facade_count, 0)
        self.assertEqual(result.test_bug_count, 0)

    @covers("REQ-0.0.74-16-02")
    def test_receipts_emitted_count_matches_verified_claims(self) -> None:
        """On all-pass, one receipt per verified claim (read-only contract, tested via mock)."""
        emitted: list[Any] = []

        def _mock_emit(results: list[ClaimRunResult], root: Path) -> None:
            emitted.extend(r for r in results if r.outcome == "PASS")

        records = [
            EnforcementClaimRecord(
                claim_id="lint",
                fixture=_fixture_catches,
                entrypoint=_entrypoint_catches,
                source_fn="tests._fixture_catches",
            ),
            EnforcementClaimRecord(
                claim_id="format",
                fixture=_fixture_catches,
                entrypoint=_entrypoint_catches,
                source_fn="tests._fixture_catches",
            ),
        ]
        with patch("gzkit.enforcement._emit_verified_receipts", _mock_emit):
            run_meta_validator(registry=records, root=None)

        self.assertEqual(len(emitted), 2)

    @covers("REQ-0.0.74-16-03")
    def test_facade_failure_message_names_facade(self) -> None:
        records = [
            EnforcementClaimRecord(
                claim_id="lint",
                fixture=_fixture_passes,
                entrypoint=_entrypoint_passes,
                source_fn="tests._fixture_passes",
            ),
        ]
        result = run_meta_validator(registry=records)
        facade_results = [r for r in result.claim_results if r.outcome == "FACADE"]
        self.assertEqual(len(facade_results), 1)
        self.assertIn("FACADE", facade_results[0].message)

    @covers("REQ-0.0.74-16-03")
    def test_facade_message_contains_repro_command(self) -> None:
        """Failure message names a single-NC repro command, not a bare count."""
        records = [
            EnforcementClaimRecord(
                claim_id="lint",
                fixture=_fixture_passes,
                entrypoint=_entrypoint_passes,
                source_fn="tests._fixture_passes",
            ),
        ]
        result = run_meta_validator(registry=records)
        facade = next(r for r in result.claim_results if r.outcome == "FACADE")
        # Message must contain a repro command that is not just a count
        self.assertNotRegex(facade.message, r"^\d+ failed$")
        # Must name the claim and repro path
        self.assertIn("lint", facade.message)

    @covers("REQ-0.0.74-16-03")
    def test_test_bug_failure_message_names_test_bug(self) -> None:
        records = [
            EnforcementClaimRecord(
                claim_id="lint",
                fixture=_fixture_raises,
                entrypoint=_entrypoint_ok,
                source_fn="tests._fixture_raises",
            ),
        ]
        result = run_meta_validator(registry=records)
        test_bug_results = [r for r in result.claim_results if r.outcome == "TEST_BUG"]
        self.assertEqual(len(test_bug_results), 1)
        self.assertIn("TEST_BUG", test_bug_results[0].message)


class TestRunnerResultFields(unittest.TestCase):
    """RunnerResult carries all claim results for introspection (REQ-16-01)."""

    def setUp(self) -> None:
        reset_enforcement_registry()
        set_known_claims(_TEST_CLAIMS)

    def tearDown(self) -> None:
        reset_enforcement_registry()

    @covers("REQ-0.0.74-16-01")
    def test_runner_result_has_claim_results_list(self) -> None:
        records = [
            EnforcementClaimRecord(
                claim_id="lint",
                fixture=_fixture_catches,
                entrypoint=_entrypoint_catches,
                source_fn="tests._fixture_catches",
            ),
        ]
        result = run_meta_validator(registry=records)
        self.assertTrue(hasattr(result, "claim_results"))
        self.assertEqual(len(result.claim_results), 1)
        self.assertEqual(result.claim_results[0].claim_id, "lint")

    @covers("REQ-0.0.74-16-01")
    def test_claim_run_result_has_required_fields(self) -> None:
        record = EnforcementClaimRecord(
            claim_id="lint",
            fixture=_fixture_catches,
            entrypoint=_entrypoint_catches,
            source_fn="tests._fixture_catches",
        )
        result = _run_single_claim(record)
        self.assertTrue(hasattr(result, "claim_id"))
        self.assertTrue(hasattr(result, "outcome"))
        self.assertTrue(hasattr(result, "message"))


class TestEnforcementClaimVerifiedEvent(unittest.TestCase):
    """enforcement_claim_verified event class exists and is valid (REQ-16-02)."""

    @covers("REQ-0.0.74-16-02")
    def test_event_class_importable(self) -> None:
        from gzkit.events import EnforcementClaimVerifiedEvent

        self.assertTrue(hasattr(EnforcementClaimVerifiedEvent, "model_fields"))

    @covers("REQ-0.0.74-16-02")
    def test_event_class_in_typed_ledger_union(self) -> None:
        """EnforcementClaimVerifiedEvent is in the TypedLedgerEvent discriminated union."""
        from gzkit.events import parse_typed_event

        # Build a minimal valid event dict and parse it
        data = {
            "schema": "gz/ledger/v1",
            "event": "enforcement_claim_verified",
            "id": "test-id-001",
            "ts": "2026-06-24T00:00:00+00:00",
            "claim_id": "lint",
            "outcome": "PASS",
            "source_fn": "gzkit.enforcement.run_meta_validator",
        }
        parsed = parse_typed_event(data)
        from gzkit.events import EnforcementClaimVerifiedEvent

        self.assertIsInstance(parsed, EnforcementClaimVerifiedEvent)
        self.assertEqual(parsed.claim_id, "lint")
        self.assertEqual(parsed.outcome, "PASS")


class TestUnforcedNegativeControls(unittest.TestCase):
    """The 2 formerly-forced NCs now run un-forced through the lifted engine (REQ-16-04).

    Genuineness is absolute (D1): the production entrypoints pass no ``fail_closed=True``,
    and running each claim against its violation fixture still PASSes (catches genuinely).
    """

    @staticmethod
    def _production_record(claim_id: str) -> EnforcementClaimRecord:
        from gzkit.enforcement import _ensure_production_claims_registered, get_enforcement_registry

        _ensure_production_claims_registered()
        records = {r.claim_id: r for r in get_enforcement_registry()}
        return records[claim_id]

    @covers("REQ-0.0.74-16-04")
    def test_rendition_freshness_entrypoint_not_forced(self) -> None:
        import inspect

        from gzkit.governance.trust_audits import _qc_nc_entrypoints

        src = inspect.getsource(_qc_nc_entrypoints._ep_rendition_freshness)
        self.assertNotIn("fail_closed=True", src)

    @covers("REQ-0.0.74-16-04")
    def test_rendition_floor_coherence_entrypoint_not_forced(self) -> None:
        import inspect

        from gzkit.governance.trust_audits import _qc_nc_entrypoints

        src = inspect.getsource(_qc_nc_entrypoints._ep_rendition_floor_coherence)
        self.assertNotIn("fail_closed=True", src)

    @covers("REQ-0.0.74-16-04")
    def test_rendition_freshness_claim_still_catches_unforced(self) -> None:
        result = _run_single_claim(self._production_record("rendition-freshness"))
        self.assertEqual(result.outcome, "PASS", result.message)

    @covers("REQ-0.0.74-16-04")
    def test_rendition_floor_coherence_claim_still_catches_unforced(self) -> None:
        result = _run_single_claim(self._production_record("rendition-floor-coherence"))
        self.assertEqual(result.outcome, "PASS", result.message)


class TestQcBindingBehaviorPreserved(unittest.TestCase):
    """After engine lift, audit_qc_binding's gz-check behavior is preserved (REQ-16-04)."""

    @covers("REQ-0.0.74-16-04")
    def test_audit_qc_binding_still_accepts_nc_registry_param(self) -> None:
        """audit_qc_binding still accepts an optional nc_registry for test isolation."""
        import inspect

        from gzkit.governance.trust_audits.qc_binding import audit_qc_binding

        sig = inspect.signature(audit_qc_binding)
        self.assertIn("nc_registry", sig.parameters)

    @covers("REQ-0.0.74-16-04")
    def test_audit_qc_binding_returns_validation_errors(self) -> None:
        """audit_qc_binding(root) returns a list (may be empty on a clean project)."""
        from pathlib import Path

        from gzkit.governance.trust_audits.qc_binding import audit_qc_binding

        with tempfile.TemporaryDirectory() as tmp:
            # Empty project — may have no errors (steps not found), but must not crash
            errors = audit_qc_binding(Path(tmp))
            self.assertIsInstance(errors, list)


class TestNoNegativeControlDebt(unittest.TestCase):
    """No _NEGATIVE_CONTROL_DEBT-style escape exists in enforcement (REQ-16-06)."""

    def test_enforcement_module_has_no_debt_escape(self) -> None:
        import gzkit.enforcement as enforcement_mod

        self.assertFalse(
            hasattr(enforcement_mod, "_NEGATIVE_CONTROL_DEBT"),
            "_NEGATIVE_CONTROL_DEBT must not exist in enforcement.py (strict no-debt BI#8)",
        )

    def test_run_meta_validator_fails_on_facade(self) -> None:
        """A FACADE claim in the registry causes runner to report failure — no debt escape."""
        reset_enforcement_registry()
        set_known_claims(_TEST_CLAIMS)
        try:
            records = [
                EnforcementClaimRecord(
                    claim_id="lint",
                    fixture=_fixture_passes,
                    entrypoint=_entrypoint_passes,
                    source_fn="tests._fixture_passes",
                ),
            ]
            result = run_meta_validator(registry=records)
            # A FACADE means the runner reports a failure — not silently green
            self.assertGreater(result.facade_count, 0)
            self.assertEqual(result.verified_count, 0)
        finally:
            reset_enforcement_registry()


class TestProductionRegistryDiscovery(unittest.TestCase):
    """REQ-16-01: the NO-ARGUMENT production-discovery branch genuinely works.

    Closes the test-gap the Stage-4 adversary (Codex, GHI #643) found: every other
    test injects ``registry=...``, so a regression of the default production-discovery
    branch (e.g. the engine un-lifting → 0 claims discovered) would NOT fail the scoped
    unittest suite — only the Stage-4 demo caught it. This test calls ``run_meta_validator()``
    with no registry, exercising ``_ensure_production_claims_registered`` + the real
    enforcement registry, and asserts the production invariant.
    """

    def setUp(self) -> None:
        # Reset so the no-arg run re-derives the production registry from scratch
        # (and is not contaminated by another test's injected known-claims set).
        reset_enforcement_registry()

    def tearDown(self) -> None:
        reset_enforcement_registry()

    @covers("REQ-0.0.74-16-01")
    def test_no_arg_run_discovers_and_verifies_production_claims(self) -> None:
        result = run_meta_validator()  # no registry → production discovery
        self.assertGreaterEqual(
            result.verified_count,
            38,
            f"production discovery verified only {result.verified_count} claims "
            "(expected >= 38) — the engine lift / @enforces registration regressed",
        )
        self.assertEqual(result.facade_count, 0, "a production claim is a FACADE")
        self.assertEqual(result.test_bug_count, 0, "a production claim's fixture did not build")

    @covers("REQ-0.0.74-16-04")
    def test_production_discovery_includes_qc_binding_and_lifted_ncs(self) -> None:
        # The lifted shared engine: the qc-binding self-NC and the lifted qc NCs are all
        # discovered as enforcement claims by the no-arg runner (one engine, BI#6).
        result = run_meta_validator()
        claim_ids = {r.claim_id for r in result.claim_results}
        for expected in ("qc-binding", "rendition-freshness", "rendition-floor-coherence", "lint"):
            self.assertIn(expected, claim_ids, f"production claim {expected!r} not discovered")


if __name__ == "__main__":
    unittest.main()
