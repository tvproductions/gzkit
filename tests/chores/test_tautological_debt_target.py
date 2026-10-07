"""Declining-target tests for the tautological-test debt gate (GHI #808).

`decommission-tautological-tests` gated only on the drift ratchet, which is
green at 274 outstanding ops and at 0 alike, so four PASS receipts were logged
across a seven-week stall. The operator ruled a declining target (2026-09-28):
the ceiling falls on a fixed schedule and the chore fails whenever outstanding
debt sits above it, so a stall turns red on its own.

These tests drive the pure functions with synthetic data and an injected date;
the committed target and the live scan are enforced by the chore criterion
itself, not re-measured here.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import unittest
from datetime import UTC, date, datetime, timedelta, timezone
from pathlib import Path
from types import ModuleType
from unittest import mock

from gzkit.commands.common import get_project_root

# The canonical authored copy; `gz agent sync control-surfaces` mirrors it to
# `src/gzkit/chores/` and `gz validate --distribution` fails closed on drift.
_SCRIPT = (
    get_project_root()
    / ".gzkit"
    / "chores"
    / "decommission-tautological-tests"
    / "check_debt_target.py"
)

# The generated copy is the one an adopter's gate resolves, having no overlay.
_SHIPPED = (
    get_project_root()
    / "src"
    / "gzkit"
    / "chores"
    / "decommission-tautological-tests"
    / "check_debt_target.py"
)


def _load_gate(script: Path = _SCRIPT) -> ModuleType:
    """Import the chore script by path; its directory name is not an identifier."""
    spec = importlib.util.spec_from_file_location("_tautological_debt_gate", script)
    if spec is None or spec.loader is None:
        raise unittest.SkipTest(f"cannot load {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _target(start_count: int = 240, rate: int = 20) -> dict:
    return {"start_date": "2026-01-01", "start_count": start_count, "decline_per_month": rate}


class TestCeiling(unittest.TestCase):
    """The ceiling declines with elapsed time, never below zero."""

    def setUp(self) -> None:
        self.gate = _load_gate()

    def test_ceiling_equals_start_count_on_start_date(self) -> None:
        self.assertEqual(self.gate.ceiling_on(_target(), date(2026, 1, 1)), 240)

    def test_ceiling_does_not_rise_before_start_date(self) -> None:
        self.assertEqual(self.gate.ceiling_on(_target(), date(2025, 6, 1)), 240)

    def test_ceiling_falls_by_the_rate_over_one_year(self) -> None:
        # 12 months at 20/month is 240 ops: the schedule reaches zero once a
        # year of mean-length months (365.25 days) has elapsed, and not before.
        self.assertGreater(self.gate.ceiling_on(_target(), date(2026, 12, 31)), 0)
        self.assertEqual(self.gate.ceiling_on(_target(), date(2027, 1, 2)), 0)

    def test_ceiling_falls_roughly_one_rate_per_month(self) -> None:
        ceiling = self.gate.ceiling_on(_target(), date(2026, 2, 1))
        self.assertLess(ceiling, 240)
        self.assertGreaterEqual(ceiling, 219)

    def test_ceiling_is_floored_at_zero(self) -> None:
        self.assertEqual(self.gate.ceiling_on(_target(), date(2030, 1, 1)), 0)


class TestOutstandingDebt(unittest.TestCase):
    """Debt is live ops not dispositioned by a file waiver."""

    def setUp(self) -> None:
        self.gate = _load_gate()

    def test_waiver_slots_discharge_ops_in_their_own_file_only(self) -> None:
        live = ["a.py", "a.py", "b.py"]
        waivers = {"a.py": ["k1"], "c.py": ["k2", "k3"]}
        self.assertEqual(self.gate.outstanding_debt(live, waivers), 2)

    def test_waiver_slots_beyond_live_ops_do_not_go_negative(self) -> None:
        self.assertEqual(self.gate.outstanding_debt(["a.py"], {"a.py": ["k1", "k2"]}), 0)


class TestVerdict(unittest.TestCase):
    """A stall turns red: debt above the ceiling is a breach."""

    def setUp(self) -> None:
        self.gate = _load_gate()

    def test_stalled_debt_breaches_once_the_ceiling_passes_it(self) -> None:
        # Nothing processed in three months: 240 outstanding against ~180.
        self.assertTrue(self.gate.is_breach(240, _target(), date(2026, 4, 1)))

    def test_debt_at_or_below_the_ceiling_passes(self) -> None:
        self.assertFalse(self.gate.is_breach(240, _target(), date(2026, 1, 1)))
        self.assertFalse(self.gate.is_breach(150, _target(), date(2026, 4, 1)))

    def test_a_target_missing_a_field_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            self.gate.validate_target({"start_date": "2026-01-01", "start_count": 10})

    def test_a_negative_rate_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            self.gate.validate_target(_target(rate=-5))


class TestScheduleDate(unittest.TestCase):
    """One instant yields one schedule date on every machine (GHI #1177)."""

    script = _SCRIPT

    def setUp(self) -> None:
        self.gate = _load_gate(self.script)
        # 2026-10-06T00:03Z: the UTC date has turned and a caller at UTC-5 still
        # reads 2026-10-05 on its wall clock.
        self.instant = datetime(2026, 10, 6, 0, 3, tzinfo=UTC)

    def test_callers_east_and_west_of_utc_compute_the_same_ceiling(self) -> None:
        target = {"start_date": "2026-09-28", "start_count": 232, "decline_per_month": 20}
        west = self.instant.astimezone(timezone(timedelta(hours=-5)))
        east = self.instant.astimezone(timezone(timedelta(hours=9)))
        self.assertNotEqual(west.date(), east.date())
        dates = {self.gate.schedule_date(now) for now in (west, east)}
        self.assertEqual(dates, {date(2026, 10, 6)})
        self.assertEqual({self.gate.ceiling_on(target, day) for day in dates}, {227})

    def test_the_schedule_date_is_the_utc_date_of_the_instant(self) -> None:
        west = self.instant.astimezone(timezone(timedelta(hours=-5)))
        self.assertEqual(self.gate.schedule_date(west), date(2026, 10, 6))

    def test_the_verdict_is_computed_on_the_schedule_date(self) -> None:
        out, err = io.StringIO(), io.StringIO()
        with (
            mock.patch.object(self.gate, "schedule_date", return_value=date(2100, 1, 1)),
            contextlib.redirect_stdout(out),
            contextlib.redirect_stderr(err),
        ):
            code = self.gate.main([])
        self.assertEqual(code, 3)
        self.assertIn("ceiling 0 on 2100-01-01 UTC", out.getvalue())


class TestScheduleDateShippedCopy(TestScheduleDate):
    """The same contract holds for the copy an adopter's gate runs."""

    script = _SHIPPED


if __name__ == "__main__":
    unittest.main()
