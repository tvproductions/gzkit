"""Chore check levels and date intervals (R&D run repair-work-organization, row 3).

The operator admitted the row-3 advice on 2026-11-03, verbatim: *"A, admit as
advised, marked provisional"*. Each chore carries an FAA-style check level, A to
D, marked provisional until the classification program reclassifies it; each
check includes the levels below it; and every chore is due by date, so a period
declared beside a content-delta or accumulated-work signal makes the chore due
at whichever comes first. Advice: ``docs/rnd/repair-work-organization/row3-chore-levels.md``.
"""

import json
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from pydantic import ValidationError

from gzkit.cli import main
from gzkit.commands.chores_declaration import ChoreDeclaration
from gzkit.commands.chores_staleness import (
    ChoreStalenessReading,
    in_check_package,
    read_chore_staleness,
)
from tests.commands.common import CliRunner

_NOW = datetime(2026, 11, 3, 12, 0, tzinfo=UTC)
_REGISTRY = Path(__file__).resolve().parents[2] / ".gzkit" / "chores" / "registry.json"


def _declaration(staleness: dict[str, object], check: object = None) -> ChoreDeclaration:
    raw: dict[str, object] = {
        "class": "conformance",
        "rung": "repair",
        "idempotent": True,
        "staleness": staleness,
        "remediation": {"category": "vendor_fix", "details": "Repairs the subject."},
        "nonAuthority": "Never edits canon.",
        "governingRule": "none",
    }
    if check is not None:
        raw["check"] = check
    return ChoreDeclaration.model_validate(raw)


def _log(when: datetime) -> str:
    return f"## {when.isoformat()}\n- Status: PASS\n\n"


def _read(declaration: ChoreDeclaration, last_run: datetime, commits: list[datetime]):
    ordered = sorted(commits)
    return read_chore_staleness(
        "demo",
        declaration,
        _log(last_run),
        now=_NOW,
        newest_commit=lambda _s: ordered[-1] if ordered else None,
        first_commit_after=lambda _s, since: next((c for c in ordered if c > since), None),
        artifact_changed=lambda _a: None,
    )


_SURFACES: dict[str, object] = {"signal": "content-delta", "surfaces": ["src"], "graceDays": 7}


class TestCheckLevelDeclaration(unittest.TestCase):
    def test_a_declared_level_reaches_the_reading(self) -> None:
        declaration = _declaration(_SURFACES, {"level": "C", "provisional": True})
        reading = _read(declaration, _NOW - timedelta(days=1), [_NOW - timedelta(days=5)])
        self.assertEqual(reading.check_level, "C")
        self.assertTrue(reading.check_provisional)

    def test_a_level_outside_a_to_d_is_refused(self) -> None:
        with self.assertRaises(ValidationError):
            _declaration(_SURFACES, {"level": "E", "provisional": True})

    def test_provisional_must_be_stated(self) -> None:
        with self.assertRaises(ValidationError):
            _declaration(_SURFACES, {"level": "A"})


class TestDueByDateWhicheverFirst(unittest.TestCase):
    def test_unmoved_surfaces_still_come_due_when_the_period_elapses(self) -> None:
        declaration = _declaration({**_SURFACES, "periodDays": 14})
        reading = _read(declaration, _NOW - timedelta(days=30), [_NOW - timedelta(days=40)])
        self.assertEqual(reading.band, "overdue")
        self.assertEqual(reading.due_since, _NOW - timedelta(days=16))

    def test_a_surface_move_before_the_date_makes_it_due_first(self) -> None:
        declaration = _declaration({**_SURFACES, "periodDays": 90})
        moved = _NOW - timedelta(days=3)
        reading = _read(declaration, _NOW - timedelta(days=10), [moved])
        self.assertEqual(reading.band, "due")
        self.assertEqual(reading.due_since, moved)

    def test_within_the_period_and_unmoved_reads_current(self) -> None:
        declaration = _declaration({**_SURFACES, "periodDays": 90})
        reading = _read(declaration, _NOW - timedelta(days=10), [_NOW - timedelta(days=40)])
        self.assertEqual(reading.band, "current")

    def test_accumulated_work_with_a_period_is_measured_by_date(self) -> None:
        declaration = _declaration({"signal": "accumulated-work", "periodDays": 30, "graceDays": 7})
        reading = _read(declaration, _NOW - timedelta(days=60), [])
        self.assertEqual(reading.band, "overdue")

    def test_accumulated_work_without_a_period_stays_unmeasured(self) -> None:
        declaration = _declaration({"signal": "accumulated-work", "graceDays": 7})
        reading = _read(declaration, _NOW - timedelta(days=60), [])
        self.assertEqual(reading.band, "unmeasured")


class TestCheckPackages(unittest.TestCase):
    def test_each_check_includes_the_levels_below_it(self) -> None:
        self.assertTrue(in_check_package("A", "B"))
        self.assertTrue(in_check_package("B", "B"))
        self.assertFalse(in_check_package("C", "B"))
        self.assertTrue(all(in_check_package(level, "D") for level in "ABCD"))

    def test_a_chore_with_no_level_is_in_no_package(self) -> None:
        self.assertFalse(in_check_package(None, "D"))


class TestStatusReadsOneCheckPackage(unittest.TestCase):
    def test_check_b_reports_only_the_a_and_b_chores(self) -> None:
        readings = [
            ChoreStalenessReading(
                slug=f"chore-{level}", band="overdue", reason="x", check_level=level
            )
            for level in ("A", "B", "C", "D")
        ]
        with patch(
            "gzkit.commands.chores_status_cmd.collect_chore_staleness", return_value=readings
        ):
            result = CliRunner().invoke(main, ["chores", "status", "--check", "B", "--json"])
        self.assertEqual(result.exit_code, 0, result.output)
        payload = json.loads(result.output[result.output.index("{") :])
        self.assertEqual([c["slug"] for c in payload["chores"]], ["chore-A", "chore-B"])
        self.assertEqual(payload["counts"]["overdue"], 2)


class TestRegistryAdmitsTheAdvice(unittest.TestCase):
    """Every registered chore carries a provisional level and a date interval."""

    def setUp(self) -> None:
        self.chores = json.loads(_REGISTRY.read_text(encoding="utf-8"))["chores"]

    def test_every_chore_declares_a_provisional_check_level(self) -> None:
        for chore in self.chores:
            with self.subTest(chore=chore["slug"]):
                self.assertIn(chore["check"]["level"], {"A", "B", "C", "D"})
                self.assertTrue(chore["check"]["provisional"])

    def test_every_chore_is_due_by_date(self) -> None:
        for chore in self.chores:
            with self.subTest(chore=chore["slug"]):
                self.assertGreater(chore["staleness"].get("periodDays", 0), 0)


if __name__ == "__main__":
    unittest.main()
