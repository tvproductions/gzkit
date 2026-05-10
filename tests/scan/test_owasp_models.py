"""Schema-invariant tests for OBPI-0.47.0-01 OWASP scan models.

Tests are derived from the brief's REQ-0.47.0-01-NN acceptance criteria,
not from the implementation. Every test is decorated with @covers per
.gzkit/rules/adr-audit.md.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from pydantic import ValidationError

from gzkit.scan.models import OwaspScanReport
from gzkit.traceability import covers

FIXTURES = Path(__file__).parent / "fixtures"


def _load_fixture(name: str) -> dict[str, object]:
    path = FIXTURES / name
    with path.open(encoding="utf-8") as f:
        return json.load(f)


class TestOwaspScanReportInvariants(unittest.TestCase):
    """REQ-derived schema invariant tests."""

    @covers("REQ-0.47.0-01-02")
    def test_a06_must_be_not_mechanical(self) -> None:
        """REQ-02: coverage[A06] != 'not-mechanical' must reject."""
        payload = _load_fixture("invalid_a06_mechanical.json")
        with self.assertRaises(ValidationError) as ctx:
            OwaspScanReport.model_validate(payload)
        self.assertIn("A06", str(ctx.exception))

    @covers("REQ-0.47.0-01-04")
    def test_a07_must_be_not_applicable(self) -> None:
        """REQ-04: coverage[A07] != 'not-applicable' must reject."""
        payload = _load_fixture("invalid_a07_other.json")
        with self.assertRaises(ValidationError) as ctx:
            OwaspScanReport.model_validate(payload)
        self.assertIn("A07", str(ctx.exception))

    @covers("REQ-0.47.0-01-03")
    def test_mechanical_floor_invariant(self) -> None:
        """REQ-03: coverage=mechanical without finding/attestation must reject."""
        payload = _load_fixture("invalid_mechanical_floor.json")
        with self.assertRaises(ValidationError):
            OwaspScanReport.model_validate(payload)
        # Paired GREEN-side: same payload with coverage_attestations[A04]=True must accept.
        payload["coverage_attestations"] = {"A04": True}
        accepted = OwaspScanReport.model_validate(payload)
        self.assertEqual(accepted.coverage["A04"], "mechanical")

    @covers("REQ-0.47.0-01-05")
    def test_round_trip_equality(self) -> None:
        """REQ-05: model_dump_json -> model_validate_json round-trip is equal."""
        payload = _load_fixture("valid_minimal_report.json")
        original = OwaspScanReport.model_validate(payload)
        rehydrated = OwaspScanReport.model_validate_json(original.model_dump_json())
        self.assertEqual(original, rehydrated)

    @covers("REQ-0.47.0-01-06")
    def test_path_serialization_posix(self) -> None:
        """REQ-06: backslash in OwaspFinding.path must reject (Windows regression)."""
        from gzkit.scan.models import OwaspFinding

        with self.assertRaises(ValidationError) as ctx:
            OwaspFinding(
                category="A04",
                source="ruff-S",
                severity="medium",
                path="src\\foo.py",
                line=1,
                rule_id="S324",
                summary="x",
                evidence="y",
            )
        self.assertIn("posix", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
