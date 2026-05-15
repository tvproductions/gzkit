"""Tests for surface weight validator (OBPI-0.0.33-02).

Covers:
    REQ-0.0.33-02-01 — Corpus at/below floor exits clean (0)
    REQ-0.0.33-02-02 — Yellow band (1801–2200) without waiver exits 3
    REQ-0.0.33-02-03 — Red band (>2200) exits 3 regardless of waiver
    REQ-0.0.33-02-04 — Expired waiver entries are rejected
    REQ-0.0.33-02-05 — Floor drift detected if recalibration event >24h old
    REQ-0.0.33-02-06 — validate_surface_weight resolves from trust_audits re-export

All tests use ``tempfile.TemporaryDirectory`` for sandbox isolation; never
write to the live repo root.
"""

from __future__ import annotations

import inspect
import json
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from gzkit.core.validation_rules import ValidationError
from gzkit.governance import trust_audits as _trust_audits_pkg
from gzkit.governance.trust_audits.surface_weight import validate_surface_weight
from gzkit.traceability import covers


def _make_surface_tree(
    tmp: str,
    line_count: int,
    floor_lines: int,
    waivers: list[dict] | None = None,
    floor_timestamp: str | None = None,
    ledger_events: list[dict] | None = None,
) -> Path:
    """Create temp project root with synthetic surface files and data files.

    Creates:
      AGENTS.md                              ← per-turn surface (line_count lines)
      CLAUDE.md                              ← per-turn surface (empty)
      .claude/rules/test-rule.md             ← per-turn surface (empty)
      data/surface_weight_floor.json         ← floor snapshot
      data/surface_weight_waivers.json       ← waiver entries
      .gzkit/ledger.jsonl                    ← ledger events

    Args:
        tmp: Temporary directory path
        line_count: Number of lines to write to AGENTS.md
        floor_lines: Line count in floor snapshot
        waivers: List of waiver entries (default [])
        floor_timestamp: ISO-8601 timestamp for floor (default now)
        ledger_events: List of ledger event dicts (default [])

    Returns:
        Path to project root
    """
    root = Path(tmp)

    # Create surface files
    agents_path = root / "AGENTS.md"
    agents_content = "\n".join(f"line {i}" for i in range(1, line_count + 1))
    agents_path.write_text(agents_content, encoding="utf-8")

    (root / "CLAUDE.md").write_text("", encoding="utf-8")

    rules_dir = root / ".claude" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    (rules_dir / "test-rule.md").write_text("", encoding="utf-8")

    # Create floor file
    data_dir = root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    if floor_timestamp is None:
        floor_timestamp = datetime.now(tz=UTC).isoformat()

    floor_data = {"lines": floor_lines, "timestamp": floor_timestamp}
    (data_dir / "surface_weight_floor.json").write_text(json.dumps(floor_data), encoding="utf-8")

    # Create waivers file
    if waivers is None:
        waivers = []
    (data_dir / "surface_weight_waivers.json").write_text(json.dumps(waivers), encoding="utf-8")

    # Create ledger file
    ledger_dir = root / ".gzkit"
    ledger_dir.mkdir(parents=True, exist_ok=True)

    if ledger_events is None:
        ledger_events = []

    ledger_path = ledger_dir / "ledger.jsonl"
    with ledger_path.open("w", encoding="utf-8") as f:
        for event in ledger_events:
            f.write(json.dumps(event) + "\n")

    return root


class TestGreenBand(unittest.TestCase):
    """Corpus at or below floor exits clean with no errors."""

    @covers("REQ-0.0.33-02-01")
    def test_corpus_at_floor_exits_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_surface_tree(tmp, line_count=1000, floor_lines=1000)
            errors = validate_surface_weight(root)
            self.assertEqual(
                errors,
                [],
                "Corpus at floor must exit clean (0)",
            )

    @covers("REQ-0.0.33-02-01")
    def test_corpus_below_floor_exits_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_surface_tree(tmp, line_count=800, floor_lines=1000)
            errors = validate_surface_weight(root)
            self.assertEqual(
                errors,
                [],
                "Corpus below floor must exit clean (0)",
            )

    @covers("REQ-0.0.33-02-01")
    def test_corpus_in_green_band_exits_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_surface_tree(tmp, line_count=1500, floor_lines=1000)
            errors = validate_surface_weight(root)
            self.assertEqual(
                errors,
                [],
                "Corpus in green band (≤1800) must exit clean",
            )


class TestYellowBand(unittest.TestCase):
    """Yellow band (1801–2200) without waiver exits 3 with ValidationError."""

    @covers("REQ-0.0.33-02-02")
    def test_yellow_band_no_waiver_exits_3(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_surface_tree(tmp, line_count=1900, floor_lines=1000)
            errors = validate_surface_weight(root)
            self.assertEqual(
                len(errors),
                1,
                "Yellow band without waiver must emit exactly one error",
            )

    @covers("REQ-0.0.33-02-02")
    def test_yellow_band_error_type_is_surface_weight(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_surface_tree(tmp, line_count=1900, floor_lines=1000)
            errors = validate_surface_weight(root)
            self.assertEqual(errors[0].type, "surface_weight")

    @covers("REQ-0.0.33-02-02")
    def test_yellow_band_error_names_delta(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_surface_tree(tmp, line_count=1900, floor_lines=1000)
            errors = validate_surface_weight(root)
            delta = 1900 - 1000  # 900
            self.assertIn(
                str(delta),
                errors[0].message,
                "Error message must name the delta (900)",
            )

    @covers("REQ-0.0.33-02-02")
    def test_yellow_band_upper_boundary_2200(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_surface_tree(tmp, line_count=2200, floor_lines=1000)
            errors = validate_surface_weight(root)
            self.assertEqual(
                len(errors),
                1,
                "Exactly 2200 (yellow ceiling) must emit error",
            )

    @covers("REQ-0.0.33-02-02")
    def test_yellow_band_lower_boundary_1801(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_surface_tree(tmp, line_count=1801, floor_lines=1000)
            errors = validate_surface_weight(root)
            self.assertEqual(
                len(errors),
                1,
                "1801 (just into yellow) must emit error without waiver",
            )


class TestYellowBandWithWaiver(unittest.TestCase):
    """Yellow band with active waiver covering delta exits clean."""

    @covers("REQ-0.0.33-02-02")
    def test_yellow_band_with_active_waiver_exits_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            today = datetime.now(tz=UTC).date()
            tomorrow = today + timedelta(days=1)
            waivers = [
                {
                    "waiver_id": "W001",
                    "expires": tomorrow.isoformat(),
                    "delta_lines": 1000,
                    "attestor": "Test User",
                    "reason": "Test waiver",
                }
            ]
            root = _make_surface_tree(tmp, line_count=1900, floor_lines=1000, waivers=waivers)
            errors = validate_surface_weight(root)
            self.assertEqual(
                errors,
                [],
                "Yellow band with active waiver covering delta must exit clean",
            )

    @covers("REQ-0.0.33-02-02")
    def test_yellow_band_waiver_insufficient_delta_dispensation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            today = datetime.now(tz=UTC).date()
            tomorrow = today + timedelta(days=1)
            waivers = [
                {
                    "waiver_id": "W001",
                    "expires": tomorrow.isoformat(),
                    "delta_lines": 500,  # Only covers 500 lines
                    "attestor": "Test User",
                    "reason": "Test waiver",
                }
            ]
            root = _make_surface_tree(tmp, line_count=1900, floor_lines=1000, waivers=waivers)
            errors = validate_surface_weight(root)
            self.assertEqual(
                len(errors),
                1,
                "Waiver with insufficient delta_lines must not prevent error",
            )


class TestRedBand(unittest.TestCase):
    """Red band (>2200) exits 3 regardless of waiver."""

    @covers("REQ-0.0.33-02-03")
    def test_red_band_exits_3_even_with_active_waiver(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            today = datetime.now(tz=UTC).date()
            tomorrow = today + timedelta(days=1)
            waivers = [
                {
                    "waiver_id": "W001",
                    "expires": tomorrow.isoformat(),
                    "delta_lines": 5000,  # Very large, but doesn't matter
                    "attestor": "Test User",
                    "reason": "Test waiver",
                }
            ]
            root = _make_surface_tree(tmp, line_count=2500, floor_lines=1000, waivers=waivers)
            errors = validate_surface_weight(root)
            self.assertEqual(
                len(errors),
                1,
                "Red band must exit 3 even with active waiver",
            )

    @covers("REQ-0.0.33-02-03")
    def test_red_band_no_dispensation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_surface_tree(tmp, line_count=2300, floor_lines=1000)
            errors = validate_surface_weight(root)
            self.assertEqual(
                len(errors),
                1,
                "Red band (>2200) must emit error with no dispensation",
            )

    @covers("REQ-0.0.33-02-03")
    def test_red_band_exactly_2201(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_surface_tree(tmp, line_count=2201, floor_lines=1000)
            errors = validate_surface_weight(root)
            self.assertEqual(
                len(errors),
                1,
                "2201 (just into red) must emit error",
            )


class TestExpiredWaiver(unittest.TestCase):
    """Expired waiver entries are rejected."""

    @covers("REQ-0.0.33-02-04")
    def test_expired_waiver_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            today = datetime.now(tz=UTC).date()
            yesterday = today - timedelta(days=1)
            waivers = [
                {
                    "waiver_id": "W001",
                    "expires": yesterday.isoformat(),
                    "delta_lines": 1000,
                    "attestor": "Test User",
                    "reason": "Test waiver",
                }
            ]
            root = _make_surface_tree(tmp, line_count=1900, floor_lines=1000, waivers=waivers)
            errors = validate_surface_weight(root)
            self.assertEqual(
                len(errors),
                1,
                "Expired waiver must be rejected, delta treated as un-waived",
            )

    @covers("REQ-0.0.33-02-04")
    def test_waiver_expires_today_is_active(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            today = datetime.now(tz=UTC).date()
            waivers = [
                {
                    "waiver_id": "W001",
                    "expires": today.isoformat(),
                    "delta_lines": 1000,
                    "attestor": "Test User",
                    "reason": "Test waiver",
                }
            ]
            root = _make_surface_tree(tmp, line_count=1900, floor_lines=1000, waivers=waivers)
            errors = validate_surface_weight(root)
            self.assertEqual(
                errors,
                [],
                "Waiver expiring today must still be active",
            )


class TestFloorDrift(unittest.TestCase):
    """Floor drift detected when recalibration event >24h old."""

    @covers("REQ-0.0.33-02-05")
    def test_floor_drift_detected_exits_3(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            now = datetime.now(tz=UTC)
            floor_ts = (now - timedelta(hours=48)).isoformat()  # 48h old

            ledger_events = [
                {
                    "event": "surface_weight_recalibrated",
                    "ts": now.isoformat(),
                }
            ]

            root = _make_surface_tree(
                tmp,
                line_count=1000,
                floor_lines=1000,
                floor_timestamp=floor_ts,
                ledger_events=ledger_events,
            )
            errors = validate_surface_weight(root)
            self.assertEqual(
                len(errors),
                1,
                "Floor >24h old with recent recalibration event must emit drift error",
            )

    @covers("REQ-0.0.33-02-05")
    def test_floor_drift_error_type_is_surface_weight(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            now = datetime.now(tz=UTC)
            floor_ts = (now - timedelta(hours=48)).isoformat()

            ledger_events = [
                {
                    "event": "surface_weight_recalibrated",
                    "ts": now.isoformat(),
                }
            ]

            root = _make_surface_tree(
                tmp,
                line_count=1000,
                floor_lines=1000,
                floor_timestamp=floor_ts,
                ledger_events=ledger_events,
            )
            errors = validate_surface_weight(root)
            self.assertEqual(errors[0].type, "surface_weight")

    @covers("REQ-0.0.33-02-05")
    def test_floor_drift_error_cites_floor_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            now = datetime.now(tz=UTC)
            floor_ts = (now - timedelta(hours=48)).isoformat()

            ledger_events = [
                {
                    "event": "surface_weight_recalibrated",
                    "ts": now.isoformat(),
                }
            ]

            root = _make_surface_tree(
                tmp,
                line_count=1000,
                floor_lines=1000,
                floor_timestamp=floor_ts,
                ledger_events=ledger_events,
            )
            errors = validate_surface_weight(root)
            self.assertIn(
                "floor drift",
                errors[0].message.lower(),
                "Drift error message must cite floor drift",
            )

    @covers("REQ-0.0.33-02-05")
    def test_no_drift_when_floor_recent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            now = datetime.now(tz=UTC)
            floor_ts = (now - timedelta(hours=12)).isoformat()  # 12h old

            ledger_events = [
                {
                    "event": "surface_weight_recalibrated",
                    "ts": now.isoformat(),
                }
            ]

            root = _make_surface_tree(
                tmp,
                line_count=1000,
                floor_lines=1000,
                floor_timestamp=floor_ts,
                ledger_events=ledger_events,
            )
            errors = validate_surface_weight(root)
            self.assertEqual(
                errors,
                [],
                "Floor <24h old must not trigger drift error",
            )

    @covers("REQ-0.0.33-02-05")
    def test_no_drift_detection_on_bootstrap_no_recalibration_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            now = datetime.now(tz=UTC)
            floor_ts = (now - timedelta(hours=48)).isoformat()  # 48h old

            # No recalibration events — bootstrap state
            ledger_events = []

            root = _make_surface_tree(
                tmp,
                line_count=1000,
                floor_lines=1000,
                floor_timestamp=floor_ts,
                ledger_events=ledger_events,
            )
            errors = validate_surface_weight(root)
            self.assertEqual(
                errors,
                [],
                "Bootstrap (no recalibration events) must skip drift detection",
            )


class TestPackageReExport(unittest.TestCase):
    """validate_surface_weight resolves from the trust_audits package re-export."""

    @covers("REQ-0.0.33-02-06")
    def test_validate_surface_weight_importable(self) -> None:
        fn = getattr(_trust_audits_pkg, "validate_surface_weight", None)
        self.assertTrue(callable(fn))

    @covers("REQ-0.0.33-02-06")
    def test_function_signature_accepts_path(self) -> None:
        sig = inspect.signature(validate_surface_weight)
        params = list(sig.parameters)
        self.assertEqual(
            params,
            ["project_root"],
            "Function must accept exactly project_root: Path",
        )

    @covers("REQ-0.0.33-02-06")
    def test_function_returns_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_surface_tree(tmp, line_count=1000, floor_lines=1000)
            result = validate_surface_weight(root)
            self.assertIsInstance(result, list)

    @covers("REQ-0.0.33-02-06")
    def test_function_returns_list_of_validation_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_surface_tree(tmp, line_count=2300, floor_lines=1000)
            result = validate_surface_weight(root)
            self.assertGreater(len(result), 0)
            self.assertIsInstance(result[0], ValidationError)


if __name__ == "__main__":
    unittest.main()
