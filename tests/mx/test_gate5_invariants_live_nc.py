"""Live un-forced negative controls for the gate5_invariants floor (OBPI-0.0.74-17).

Each of the four GATE5_INVARIANTS members lacking an @enforces entry is migrated
onto the enforcement-claim surface here:

* ``ledger`` and ``gate5-attestation`` are BOUND to a genuine gate5 production path
  and carry a live un-forced negative control that runs that real path against a
  synthetic violation and asserts it is caught.
* ``secrets`` and ``operator-pii`` are the HONEST NEGATIVE (ADR-0.0.74
  §Consequences/Negative #7): no unified gate5 production entrypoint exists today
  (``validate_no_secrets`` is handoff-scoped; ``_EMAIL_RE`` is insights-scoped), so
  they are surfaced as named-not-enforced — NEVER bound to a narrower proxy.

Genuineness is structural (parent ADR § Boundary Invariants #7): the fixture builds
the violation and NEVER calls the validator; only the production entrypoint decides
catch/no-catch. The NCs are UN-FORCED — no entrypoint pre-binds a forcing kwarg.

REQ-0.0.74-17-01 [behavior]: secrets surfaced named-not-enforced, no proxy bound.
REQ-0.0.74-17-02 [behavior]: operator-pii surfaced named-not-enforced, no proxy bound.
REQ-0.0.74-17-03 [behavior]: ledger @enforces NC catches a corrupted ledger.
REQ-0.0.74-17-04 [behavior]: gate5-attestation @enforces NC catches the ABSENCE case.
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.enforcement import (
    EnforcementClaimRecord,
    _run_single_claim,
    get_enforcement_registry,
    registered_claims,
    reset_enforcement_registry,
)
from gzkit.mx.invariants import (
    _GATE5_NAMED_NOT_ENFORCED,
    _build_gate5_attestation_absence,
    _build_gate5_ledger_violation,
    _ensure_gate5_claims_registered,
    _ep_gate5_attestation_absence,
    _ep_gate5_ledger,
)
from gzkit.traceability import covers


class TestGate5NamedNotEnforced(unittest.TestCase):
    """REQ-17-01 / REQ-17-02: secrets and operator-pii are honest named-not-enforced.

    No gate5 production entrypoint exists for either, so neither carries an
    @enforces entry and NEITHER may be bound to a narrower proxy. The members are
    surfaced through the _GATE5_NAMED_NOT_ENFORCED constant instead.
    """

    def setUp(self) -> None:
        reset_enforcement_registry()
        _ensure_gate5_claims_registered()

    def tearDown(self) -> None:
        reset_enforcement_registry()

    @covers("REQ-0.0.74-17-01")
    def test_secrets_is_named_not_enforced(self) -> None:
        self.assertIn(
            "secrets",
            _GATE5_NAMED_NOT_ENFORCED,
            "secrets must be surfaced as named-not-enforced (no gate5 production gate today)",
        )

    @covers("REQ-0.0.74-17-01")
    def test_no_secrets_proxy_claim_bound(self) -> None:
        # The honest-negative forbids binding a narrower proxy entrypoint to fake
        # coverage. No registered enforcement claim may name a gate5 secrets binding.
        claims = set(registered_claims())
        for forbidden in ("gate5-secrets", "secrets"):
            self.assertNotIn(
                forbidden,
                claims,
                f"'{forbidden}' must NOT be a registered @enforces claim — "
                "binding a narrower proxy for secrets is forbidden (ADR-0.0.74 Neg #7)",
            )

    @covers("REQ-0.0.74-17-02")
    def test_operator_pii_is_named_not_enforced(self) -> None:
        self.assertIn(
            "operator-pii",
            _GATE5_NAMED_NOT_ENFORCED,
            "operator-pii must be surfaced as named-not-enforced (no gate5 production gate today)",
        )

    @covers("REQ-0.0.74-17-02")
    def test_no_operator_pii_proxy_claim_bound(self) -> None:
        claims = set(registered_claims())
        for forbidden in ("gate5-operator-pii", "operator-pii"):
            self.assertNotIn(
                forbidden,
                claims,
                f"'{forbidden}' must NOT be a registered @enforces claim — "
                "binding a narrower proxy for operator-pii is forbidden (ADR-0.0.74 Neg #7)",
            )


class TestGate5LedgerLiveNC(unittest.TestCase):
    """REQ-17-03: the ledger floor member carries a live un-forced NC that catches.

    The gzkit ledger is append-only JSONL with no cryptographic hash chain; its
    integrity path is ``validate_ledger`` (schema/shape conformance). The synthetic
    violation is a corrupted ledger (invalid JSON + a line missing required fields)
    run through that genuine path.
    """

    def setUp(self) -> None:
        reset_enforcement_registry()
        _ensure_gate5_claims_registered()

    def tearDown(self) -> None:
        reset_enforcement_registry()

    @covers("REQ-0.0.74-17-03")
    def test_ledger_claim_registered(self) -> None:
        self.assertIn(
            "gate5-ledger",
            registered_claims(),
            "gate5-ledger must carry an @enforces entry after registration",
        )

    @covers("REQ-0.0.74-17-03")
    def test_ledger_nc_catches_corrupted_ledger(self) -> None:
        # Run the real validate_ledger path against the synthetic violation: it must
        # return a non-empty error list (truthy = caught). The fixture never calls
        # the validator — only the entrypoint does.
        caught_errors: list[object] = []

        def capture(root: Path) -> list[object]:
            errors = _ep_gate5_ledger(root)
            caught_errors.extend(errors)
            return errors

        result = _run_single_claim(
            EnforcementClaimRecord(
                claim_id="gate5-ledger-live-nc-test",
                fixture=_build_gate5_ledger_violation,
                entrypoint=capture,
                source_fn="test.gate5_ledger_live_nc",
            )
        )

        self.assertEqual(result.outcome, "PASS", result.message)
        self.assertTrue(
            caught_errors,
            "validate_ledger must flag the corrupted ledger — a falsy result is a FACADE",
        )

    @covers("REQ-0.0.74-17-03")
    def test_ledger_nc_does_not_flag_valid_ledger(self) -> None:
        # Genuineness guard: the same entrypoint must return falsy on a VALID ledger.
        # If it flagged anything, the NC would be forced (always-catches theatre).
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gzkit").mkdir(parents=True, exist_ok=True)
            (root / ".gzkit" / "ledger.jsonl").write_text(
                '{"schema": "gzkit.ledger.v1", "event": "prd_created", '
                '"id": "PRD-gate5-nc", "ts": "2026-01-01T00:00:00+00:00"}\n',
                encoding="utf-8",
            )
            errors = _ep_gate5_ledger(root)
            self.assertFalse(
                errors,
                f"validate_ledger must accept a well-formed ledger; got: {errors}",
            )


class TestGate5AttestationAbsenceLiveNC(unittest.TestCase):
    """REQ-17-04: the gate5-attestation floor member catches the ABSENCE case.

    A missing attestation on a heavy/foundation completion is rejected through the
    real ``_requires_human_obpi_attestation`` gate. Forgery-detection is OUT — canon
    holds the operator's verbatim relayed attestation IS Gate 5, so only the absence
    case is NC-able.
    """

    def setUp(self) -> None:
        reset_enforcement_registry()
        _ensure_gate5_claims_registered()

    def tearDown(self) -> None:
        reset_enforcement_registry()

    @covers("REQ-0.0.74-17-04")
    def test_attestation_absence_claim_registered(self) -> None:
        self.assertIn(
            "gate5-attestation-absence",
            registered_claims(),
            "gate5-attestation-absence must carry an @enforces entry after registration",
        )

    @covers("REQ-0.0.74-17-04")
    def test_attestation_absence_nc_catches_missing_attestation(self) -> None:
        # Run the real gate against the absence scenario: a heavy completion with an
        # empty attestation must be caught (truthy).
        scenario = _build_gate5_attestation_absence()
        self.assertTrue(
            _ep_gate5_attestation_absence(scenario),
            "a missing attestation on a heavy completion must be rejected — falsy is a FACADE",
        )

    @covers("REQ-0.0.74-17-04")
    def test_attestation_absence_nc_does_not_flag_present_attestation(self) -> None:
        # Genuineness guard: a PRESENT, otherwise-valid attestation payload must NOT
        # be flagged by the real field validator. If it were, the NC would be forced
        # (always-rejects theatre) and forgery-detection — explicitly OUT — would be
        # smuggled in.
        scenario = {
            "attestor": "Test Attestor",
            "evidence": {
                "human_attestation": True,
                "attestation_text": "attest completed — verified",
                "attestation_date": "2026-01-01",
            },
        }
        self.assertFalse(
            _ep_gate5_attestation_absence(scenario),
            "a present attestation must NOT be flagged (only the absence case is NC-able)",
        )


class TestGate5EnrollmentIsIdempotent(unittest.TestCase):
    """Registration is reset-safe and idempotent (no duplicate registry entries)."""

    def setUp(self) -> None:
        reset_enforcement_registry()

    def tearDown(self) -> None:
        reset_enforcement_registry()

    @covers("REQ-0.0.74-17-03")
    def test_double_registration_does_not_duplicate(self) -> None:
        _ensure_gate5_claims_registered()
        _ensure_gate5_claims_registered()
        claim_ids = [r.claim_id for r in get_enforcement_registry()]
        for gate5_id in ("gate5-ledger", "gate5-attestation-absence"):
            with self.subTest(claim=gate5_id):
                self.assertEqual(
                    claim_ids.count(gate5_id),
                    1,
                    f"{gate5_id} registered {claim_ids.count(gate5_id)} times — must be idempotent",
                )

    @covers("REQ-0.0.74-17-04")
    def test_module_exposes_named_not_enforced_set(self) -> None:
        self.assertEqual(
            _GATE5_NAMED_NOT_ENFORCED,
            frozenset({"secrets", "operator-pii"}),
            "the named-not-enforced set must be exactly secrets and operator-pii",
        )


if __name__ == "__main__":
    unittest.main()
