"""Tests for intrinsic-complexity-attestation ledger event shape (OBPI-0.0.29-07).

Coverage:
    REQ-0.0.29-07-06 — validate_intrinsic_attestation returns no errors for
        well-formed events and ValidationErrors for malformed events.
        All tests use tempfile-backed ledger; never touch live ledger.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.intrinsic_attestation import validate_intrinsic_attestation
from gzkit.traceability import covers


def _write_ledger(project_root: Path, events: list[dict]) -> None:
    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")


def _well_formed_event(
    *,
    file_path: str = "/tmp/foo.py",
    qualname: str = "Foo.bar",
    reason: str = "irreducible state machine",
    attestor: str = "Jeffry",
    attestation_date: str = "2026-05-07",
    metric: str = "radon_cc",
    crossing_band: str = "block",
    crossing_value: float = 14.0,
) -> dict:
    return {
        "schema": "gzkit.ledger.v1",
        "event": "intrinsic-complexity-attestation",
        "id": f"{file_path}::{qualname}",
        "ts": "2026-05-07T00:00:00+00:00",
        "file_path": file_path,
        "qualname": qualname,
        "reason": reason,
        "attestor": attestor,
        "attestation_date": attestation_date,
        "metric": metric,
        "crossing_band": crossing_band,
        "crossing_value": crossing_value,
    }


class TestIntrinsicAttestationEventShape(unittest.TestCase):
    """REQ-0.0.29-07-06: validate event shapes, tempfile-backed ledger."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.project_root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @covers("REQ-0.0.29-07-06")
    def test_well_formed_event_returns_no_errors(self) -> None:
        """A complete, well-formed event passes validation with no errors."""
        _write_ledger(self.project_root, [_well_formed_event()])
        errors = validate_intrinsic_attestation(self.project_root)
        self.assertEqual(errors, [])

    @covers("REQ-0.0.29-07-06")
    def test_missing_required_field_returns_error(self) -> None:
        """An event missing a required string field returns a ValidationError."""
        ev = _well_formed_event()
        del ev["reason"]
        _write_ledger(self.project_root, [ev])
        errors = validate_intrinsic_attestation(self.project_root)
        self.assertEqual(len(errors), 1)
        self.assertIn("reason", errors[0].message)

    @covers("REQ-0.0.29-07-06")
    def test_empty_required_field_returns_error(self) -> None:
        """An event with an empty required string field returns a ValidationError."""
        ev = _well_formed_event(attestor="")
        _write_ledger(self.project_root, [ev])
        errors = validate_intrinsic_attestation(self.project_root)
        self.assertEqual(len(errors), 1)
        self.assertIn("attestor", errors[0].message)

    @covers("REQ-0.0.29-07-06")
    def test_invalid_crossing_band_returns_error(self) -> None:
        """An event with an invalid crossing_band returns a ValidationError."""
        ev = _well_formed_event(crossing_band="critical")
        _write_ledger(self.project_root, [ev])
        errors = validate_intrinsic_attestation(self.project_root)
        self.assertTrue(any("crossing_band" in e.message for e in errors))

    @covers("REQ-0.0.29-07-06")
    def test_non_numeric_crossing_value_returns_error(self) -> None:
        """An event with a string crossing_value returns a ValidationError."""
        ev = _well_formed_event()
        ev["crossing_value"] = "fourteen"
        _write_ledger(self.project_root, [ev])
        errors = validate_intrinsic_attestation(self.project_root)
        self.assertTrue(any("crossing_value" in e.message for e in errors))

    @covers("REQ-0.0.29-07-06")
    def test_no_ledger_returns_empty(self) -> None:
        """Missing ledger file returns an empty list (no errors)."""
        errors = validate_intrinsic_attestation(self.project_root)
        self.assertEqual(errors, [])

    @covers("REQ-0.0.29-07-06")
    def test_non_matching_events_are_skipped(self) -> None:
        """Events of other types are silently skipped."""
        other_event = {
            "schema": "gzkit.ledger.v1",
            "event": "adr_created",
            "id": "ADR-0.0.1",
            "ts": "2026-01-01T00:00:00+00:00",
            "parent": "PRD-1",
            "lane": "foundation",
        }
        _write_ledger(self.project_root, [other_event])
        errors = validate_intrinsic_attestation(self.project_root)
        self.assertEqual(errors, [])

    @covers("REQ-0.0.29-07-06")
    def test_multiple_events_all_validated(self) -> None:
        """Multiple events are all validated; each malformed event contributes errors."""
        good = _well_formed_event(qualname="Foo.good")
        bad = _well_formed_event(qualname="Foo.bad", reason="")
        _write_ledger(self.project_root, [good, bad])
        errors = validate_intrinsic_attestation(self.project_root)
        self.assertEqual(len(errors), 1)
        self.assertIn("Foo.bad", errors[0].artifact)


if __name__ == "__main__":
    unittest.main()
