"""Unit tests for the MX proxy-reality distance detector (OBPI-0.0.74-13).

REQ-0.0.74-13-01 and REQ-0.0.74-13-02 are BEHAVIOR REQs proven by the
``@covers``-decorated methods below.

REQ-0.0.74-13-03 is a [structural-fence] REQ — its proof channel is the live
``@enforces("grader-gaming", ...)`` registration in ``proxy_reality.py`` per
OBPI-0.0.74-18 (structural-fence proof upgrade + ADR-0.0.74 BI#5). A
``@covers`` test is not the proof channel for structural-fence REQs; the
``@enforces`` NC is.
"""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.traceability import covers


def _write_ledger(root: Path, events: list[dict]) -> None:
    gzkit_dir = root / ".gzkit"
    gzkit_dir.mkdir(parents=True, exist_ok=True)
    (gzkit_dir / "ledger.jsonl").write_text(
        "\n".join(json.dumps(e) for e in events) + "\n",
        encoding="utf-8",
    )


class TestScan(unittest.TestCase):
    """REQ-0.0.74-13-01: scan() detects gate-green-but-reality-wrong signals."""

    @covers("REQ-0.0.74-13-01")
    def test_scan_counts_model_induced_fabrication(self) -> None:
        from gzkit.mx import proxy_reality

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(
                root,
                [
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "obpi_completion_repudiated",
                        "id": "OBPI-test-01",
                        "ts": "2026-01-01T00:00:00+00:00",
                        "repudiated_receipt": "receipt-001",
                        "cause": "model-induced-fabrication",
                        "attestor": "g0",
                        "reason": "agent fabricated Gate-5 attestation",
                    }
                ],
            )
            result = proxy_reality.scan(root)

        self.assertEqual(result.count, 1)
        self.assertEqual(len(result.records), 1)
        record = result.records[0]
        self.assertEqual(record.obpi_id, "OBPI-test-01")
        self.assertEqual(record.repudiated_receipt, "receipt-001")
        self.assertEqual(record.clearing_gate, "gate5")
        self.assertEqual(record.cause, "model-induced-fabrication")

    @covers("REQ-0.0.74-13-01")
    def test_scan_ignores_non_fabrication_causes(self) -> None:
        from gzkit.mx import proxy_reality

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(
                root,
                [
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "obpi_completion_repudiated",
                        "id": "OBPI-test-02",
                        "ts": "2026-01-01T00:00:00+00:00",
                        "repudiated_receipt": "receipt-002",
                        "cause": "operator-error",
                        "attestor": "g0",
                        "reason": "wrong OBPI",
                    }
                ],
            )
            result = proxy_reality.scan(root)

        # operator-error is NOT a proxy-reality-distance signal
        self.assertEqual(result.count, 0)

    @covers("REQ-0.0.74-13-01")
    def test_scan_empty_ledger_returns_zero(self) -> None:
        from gzkit.mx import proxy_reality

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gzkit").mkdir(parents=True, exist_ok=True)
            (root / ".gzkit" / "ledger.jsonl").write_text("", encoding="utf-8")
            result = proxy_reality.scan(root)

        self.assertEqual(result.count, 0)
        self.assertEqual(result.records, [])

    @covers("REQ-0.0.74-13-01")
    def test_scan_missing_ledger_returns_zero(self) -> None:
        from gzkit.mx import proxy_reality

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = proxy_reality.scan(root)

        self.assertEqual(result.count, 0)

    @covers("REQ-0.0.74-13-01")
    def test_scan_counts_multiple_fabrication_events(self) -> None:
        from gzkit.mx import proxy_reality

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(
                root,
                [
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "obpi_completion_repudiated",
                        "id": "OBPI-test-03",
                        "ts": "2026-01-02T00:00:00+00:00",
                        "repudiated_receipt": "receipt-003",
                        "cause": "model-induced-fabrication",
                        "attestor": "g0",
                        "reason": "another fabrication",
                    },
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "obpi_completion_repudiated",
                        "id": "OBPI-test-04",
                        "ts": "2026-01-03T00:00:00+00:00",
                        "repudiated_receipt": "receipt-004",
                        "cause": "model-induced-fabrication",
                        "attestor": "g0",
                        "reason": "yet another",
                    },
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "obpi_completion_repudiated",
                        "id": "OBPI-test-05",
                        "ts": "2026-01-04T00:00:00+00:00",
                        "repudiated_receipt": "receipt-005",
                        "cause": "verification-invalid",
                        "attestor": "g0",
                        "reason": "bad evidence",
                    },
                ],
            )
            result = proxy_reality.scan(root)

        self.assertEqual(result.count, 2)  # only the 2 model-induced-fabrication events


class TestLiveNegativeControl(unittest.TestCase):
    """REQ-0.0.74-13-02: live NC constructs known violation, runs real path, asserts caught."""

    @covers("REQ-0.0.74-13-02")
    def test_live_nc_catches_planted_violation(self) -> None:
        """Passing-on-violation test: the live NC plants a known proxy-reality
        violation and asserts the REAL detection path catches it.

        This is the §5 enforcement-claim live NC for grader-gaming. The NC
        runs through the real ``proxy_reality.scan()`` production path —
        no stub, no mock of the detector itself.
        """
        from gzkit.enforcement import EnforcementClaimRecord, _run_single_claim
        from gzkit.mx.proxy_reality import _build_proxy_reality_violation, _ep_proxy_reality

        signals: list[int] = []

        def capture(root: Path) -> int:
            signal = _ep_proxy_reality(root)
            signals.append(signal)
            return signal

        result = _run_single_claim(
            EnforcementClaimRecord(
                claim_id="proxy-reality-live-nc-test",
                fixture=_build_proxy_reality_violation,
                entrypoint=capture,
                source_fn="test.proxy_reality_live_nc",
            )
        )

        # The violation is caught: count > 0 (truthy)
        self.assertEqual(result.outcome, "PASS", result.message)
        self.assertGreater(signals[0], 0, "live NC must catch the planted violation (count > 0)")

    @covers("REQ-0.0.74-13-02")
    def test_live_nc_fixture_creates_ledger_with_repudiated_event(self) -> None:
        """The fixture builds a valid temp ledger containing a planted repudiation event."""
        from gzkit.enforcement import EnforcementClaimRecord, _run_single_claim
        from gzkit.mx.proxy_reality import _build_proxy_reality_violation, _ep_proxy_reality

        planted_events: list[dict] = []

        def inspect_fixture(root: Path) -> int:
            ledger_path = root / ".gzkit" / "ledger.jsonl"
            lines = [
                json.loads(line)
                for line in ledger_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            planted_events.extend(lines)
            return _ep_proxy_reality(root)

        result = _run_single_claim(
            EnforcementClaimRecord(
                claim_id="proxy-reality-fixture-content-test",
                fixture=_build_proxy_reality_violation,
                entrypoint=inspect_fixture,
                source_fn="test.proxy_reality_fixture_content",
            )
        )

        self.assertEqual(result.outcome, "PASS", result.message)
        self.assertTrue(
            any(
                event.get("event") == "obpi_completion_repudiated"
                and event.get("cause") == "model-induced-fabrication"
                for event in planted_events
            ),
            "fixture must plant a model-induced-fabrication repudiation event",
        )

    @covers("REQ-0.0.74-13-02")
    def test_live_nc_entrypoint_never_stubs_detector(self) -> None:
        """Entrypoint calls the real scan() — not a stub that always returns truthy.

        A scan over an EMPTY ledger must return 0 (falsy). This confirms the
        entrypoint distinguishes 'violation caught' from 'stub always passes'.
        """
        from gzkit.mx.proxy_reality import _ep_proxy_reality

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gzkit").mkdir(parents=True, exist_ok=True)
            (root / ".gzkit" / "ledger.jsonl").write_text("", encoding="utf-8")
            result = _ep_proxy_reality(root)

        self.assertEqual(result, 0, "entrypoint must return 0 (falsy) on an empty ledger")


class TestProductionDiscoveryWiring(unittest.TestCase):
    """Regression guard: the floor members MUST be registered by production discovery.

    This locks the fix for the orphan the adversarial Stage 4b found — the
    ``grader-gaming`` and gate5 ``@enforces`` claims were authored but never
    wired into ``_ensure_production_claims_registered()`` (the single seam
    ``gz check``'s enforcement-floor audit discovers claims through). An orphaned
    claim is a floor facade; these tests fail closed if any floor member silently
    drops out of production discovery again.
    """

    def test_grader_gaming_registered_by_production_discovery(self) -> None:
        """REQ-13-03 binding: grader-gaming is live in the production registry."""
        from gzkit.enforcement import (
            _ensure_production_claims_registered,
            registered_claims,
        )

        _ensure_production_claims_registered()
        self.assertIn(
            "grader-gaming",
            registered_claims(),
            "grader-gaming @enforces claim must be discovered by the production "
            "floor audit — an unwired claim is a floor facade (ADR-0.0.74 BI#5)",
        )

    def test_bound_gate5_floor_members_registered_by_production_discovery(self) -> None:
        """The two BOUND gate5 floor members are live (cures the OBPI-17 orphan)."""
        from gzkit.enforcement import (
            _ensure_production_claims_registered,
            registered_claims,
        )

        _ensure_production_claims_registered()
        claims = registered_claims()
        for member in ("gate5-ledger", "gate5-attestation-absence"):
            with self.subTest(member=member):
                self.assertIn(
                    member,
                    claims,
                    f"bound gate5 floor member '{member}' must be discovered by "
                    "production floor audit (ADR-0.0.74 BI#9)",
                )

    def test_grader_gaming_nc_passes_under_meta_validator(self) -> None:
        """The wired grader-gaming NC passes the real meta-validator (no facade)."""
        from gzkit.enforcement import (
            _ensure_production_claims_registered,
            get_enforcement_registry,
            run_meta_validator,
        )

        _ensure_production_claims_registered()
        registry = get_enforcement_registry()
        result = run_meta_validator(registry=registry, root=None)
        outcomes = {
            cr.claim_id: cr.outcome for cr in result.claim_results if cr.claim_id == "grader-gaming"
        }
        self.assertEqual(
            outcomes.get("grader-gaming"),
            "PASS",
            "grader-gaming NC must PASS the real meta-validator run",
        )


if __name__ == "__main__":
    unittest.main()
