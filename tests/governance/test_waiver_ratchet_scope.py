"""Waiver-ratchet honesty contract (OBPI-0.0.73-09, ADR-0.0.73 BI #8).

Every gate-bearing waiver/grandfather/baseline surface must declare exactly one
honesty mechanism (closed-set-lock | dated-cutover | shrink-ratchet); an
unratcheted or unregistered surface fails closed. These tests pin each mechanism,
the growth-fails-closed property, and the green-by-emptiness / silent-bypass guard.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from gzkit.governance.trust_audits.waiver_ratchet import audit_waiver_ratchet
from gzkit.traceability import covers


def _project(registry: dict, data_files: dict[str, object]) -> tempfile.TemporaryDirectory:
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    (root / "data").mkdir(parents=True, exist_ok=True)
    (root / "data" / "waiver_ratchet_registry.json").write_text(
        json.dumps(registry), encoding="utf-8"
    )
    for name, payload in data_files.items():
        (root / "data" / name).write_text(json.dumps(payload), encoding="utf-8")
    return tmp


class TestUnratchetedFailsClosed(unittest.TestCase):
    """REQ-0.0.73-09-01: a surface with no/invalid mechanism is flagged (exit 3)."""

    @covers("REQ-0.0.73-09-01")
    def test_invalid_mechanism_flagged(self) -> None:
        reg = {"surfaces": [{"data_file": "data/x_waivers.json", "mechanism": "none"}]}
        with _project(reg, {"x_waivers.json": {"waivers": []}}) as d:
            errs = audit_waiver_ratchet(Path(d))
        self.assertTrue(errs)
        self.assertIn("mechanism", errs[0].message.lower())

    @covers("REQ-0.0.73-09-01")
    def test_missing_registry_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "data").mkdir()
            errs = audit_waiver_ratchet(Path(d))
        self.assertTrue(errs)
        self.assertIn("registry", errs[0].artifact)


class TestMechanismsPass(unittest.TestCase):
    """REQ-0.0.73-09-02: a surface satisfying its mechanism passes (no false positive)."""

    @covers("REQ-0.0.73-09-02")
    def test_closed_set_lock_all_locked_passes(self) -> None:
        reg = {
            "surfaces": [
                {
                    "data_file": "data/h_waivers.json",
                    "mechanism": "closed-set-lock",
                    "entries_path": "waivers",
                    "lock_field": "added_under",
                }
            ]
        }
        data = {
            "h_waivers.json": {"waivers": [{"added_under": "OBPI-1"}, {"added_under": "OBPI-2"}]}
        }
        with _project(reg, data) as d:
            self.assertEqual(audit_waiver_ratchet(Path(d)), [])

    @covers("REQ-0.0.73-09-02")
    def test_dated_cutover_past_passes(self) -> None:
        reg = {
            "surfaces": [
                {
                    "data_file": "data/c_waivers.json",
                    "mechanism": "dated-cutover",
                    "cutover_date": "2026-01-01",
                }
            ]
        }
        with _project(reg, {"c_waivers.json": {"waivers": []}}) as d:
            self.assertEqual(audit_waiver_ratchet(Path(d), today=date(2026, 6, 19)), [])

    @covers("REQ-0.0.73-09-02")
    def test_shrink_ratchet_at_baseline_passes(self) -> None:
        reg = {
            "surfaces": [
                {
                    "data_file": "data/s_waivers.json",
                    "mechanism": "shrink-ratchet",
                    "entries_path": "waivers",
                    "baseline_count": 2,
                }
            ]
        }
        with _project(reg, {"s_waivers.json": {"waivers": ["a", "b"]}}) as d:
            self.assertEqual(audit_waiver_ratchet(Path(d)), [])


class TestMechanismViolationsFailClosed(unittest.TestCase):
    """REQ-0.0.73-09-01/03: each mechanism's violation fails closed."""

    @covers("REQ-0.0.73-09-01")
    def test_closed_set_lock_unlocked_entry_flagged(self) -> None:
        reg = {
            "surfaces": [
                {
                    "data_file": "data/h_waivers.json",
                    "mechanism": "closed-set-lock",
                    "entries_path": "waivers",
                    "lock_field": "added_under",
                }
            ]
        }
        data = {"h_waivers.json": {"waivers": [{"added_under": "OBPI-1"}, {"note": "no lock"}]}}
        with _project(reg, data) as d:
            errs = audit_waiver_ratchet(Path(d))
        self.assertTrue(errs)
        self.assertIn("added_under", errs[0].message)

    @covers("REQ-0.0.73-09-01")
    def test_future_cutover_flagged(self) -> None:
        reg = {
            "surfaces": [
                {
                    "data_file": "data/c_waivers.json",
                    "mechanism": "dated-cutover",
                    "cutover_date": "2099-01-01",
                }
            ]
        }
        with _project(reg, {"c_waivers.json": {"waivers": []}}) as d:
            errs = audit_waiver_ratchet(Path(d), today=date(2026, 6, 19))
        self.assertTrue(errs)
        self.assertIn("future", errs[0].message.lower())

    @covers("REQ-0.0.73-09-03")
    def test_shrink_ratchet_growth_fails_closed(self) -> None:
        # The behave_coverage_waivers hole: a waiver appended beyond baseline.
        reg = {
            "surfaces": [
                {
                    "data_file": "data/behave_coverage_waivers.json",
                    "mechanism": "shrink-ratchet",
                    "entries_path": "waivers",
                    "baseline_count": 2,
                }
            ]
        }
        grown = {"behave_coverage_waivers.json": {"waivers": ["a", "b", "c"]}}
        with _project(reg, grown) as d:
            errs = audit_waiver_ratchet(Path(d))
        self.assertTrue(errs)
        self.assertIn("baseline", errs[0].message.lower())

    @covers("REQ-0.0.73-09-03")
    def test_shrink_ratchet_below_baseline_passes(self) -> None:
        reg = {
            "surfaces": [
                {
                    "data_file": "data/s_waivers.json",
                    "mechanism": "shrink-ratchet",
                    "entries_path": "waivers",
                    "baseline_count": 5,
                }
            ]
        }
        with _project(reg, {"s_waivers.json": {"waivers": ["a"]}}) as d:
            self.assertEqual(audit_waiver_ratchet(Path(d)), [])


class TestSilentBypassGuard(unittest.TestCase):
    """REQ-0.0.73-09-06: an unregistered waiver data file fails closed (green-by-emptiness)."""

    def test_unregistered_waiver_file_flagged(self) -> None:
        reg = {"surfaces": []}
        with _project(reg, {"sneaky_waivers.json": {"waivers": ["a"]}}) as d:
            errs = audit_waiver_ratchet(Path(d))
        self.assertTrue(errs)
        self.assertIn("sneaky_waivers.json", errs[0].artifact)

    def test_excluded_waiver_file_not_flagged(self) -> None:
        reg = {"surfaces": [], "excluded": ["data/sneaky_waivers.json"]}
        with _project(reg, {"sneaky_waivers.json": {"waivers": ["a"]}}) as d:
            self.assertEqual(audit_waiver_ratchet(Path(d)), [])


class TestRealRegistryIsGreen(unittest.TestCase):
    """REQ-0.0.73-09-02: the committed registry passes over the real data/ tree."""

    @covers("REQ-0.0.73-09-02")
    def test_committed_registry_green(self) -> None:
        errs = audit_waiver_ratchet(Path.cwd())
        self.assertEqual(errs, [], f"committed registry not green: {[e.artifact for e in errs]}")


if __name__ == "__main__":
    unittest.main()
