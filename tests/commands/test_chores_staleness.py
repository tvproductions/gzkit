"""Staleness bands for `gz chores status` (GHI #936).

A chore's staleness used to be observable only by running the chore whose
staleness it measures, so an overdue chore announced nothing to anyone. These
tests pin how a declaration plus the chore's run record map to a band. Design
authority: ``docs/governance/chore-class-system.md`` § Staleness (four signals,
graded bands) and § Implementation order step 2 ("Announces; never gates").

Git is injected, never spawned: each case states the surface history it
assumes, so the band follows from the declaration and the record alone.
"""

from __future__ import annotations

import unittest
from datetime import UTC, datetime, timedelta

from gzkit.commands.chores_declaration import ChoreDeclaration
from gzkit.commands.chores_staleness import newest_pass_stamp, read_chore_staleness

_NOW = datetime(2026, 9, 14, 12, 0, tzinfo=UTC)


def _declaration(staleness: dict[str, object]) -> ChoreDeclaration:
    return ChoreDeclaration.model_validate(
        {
            "class": "conformance",
            "rung": "repair",
            "idempotent": True,
            "staleness": staleness,
            "remediation": {"category": "vendor_fix", "details": "Repairs the subject."},
            "nonAuthority": "Never edits canon.",
            "governingRule": "none",
        }
    )


def _log(*blocks: tuple[datetime, str]) -> str:
    return "".join(f"## {when.isoformat()}\n- Status: {status}\n\n" for when, status in blocks)


class _History:
    """Git fake: surface commit dates, and when the declared scan record last changed."""

    def __init__(self, commits: list[datetime], scanned: datetime | None = None) -> None:
        self.commits = sorted(commits)
        self.scanned = scanned

    def artifact_changed(self, _artifacts: tuple[str, ...]) -> datetime | None:
        return self.scanned

    def newest(self, _surfaces: tuple[str, ...]) -> datetime | None:
        return self.commits[-1] if self.commits else None

    def first_after(self, _surfaces: tuple[str, ...], since: datetime) -> datetime | None:
        return next((when for when in self.commits if when > since), None)


def _read(
    declaration: ChoreDeclaration | None,
    log: str | None,
    commits: list[datetime],
    scanned: datetime | None = None,
):
    history = _History(commits, scanned)
    return read_chore_staleness(
        "demo",
        declaration,
        log,
        now=_NOW,
        newest_commit=history.newest,
        first_commit_after=history.first_after,
        artifact_changed=history.artifact_changed,
    )


_ELAPSED = {"signal": "elapsed-time", "periodDays": 30, "graceDays": 7}
_RECORDED = {**_ELAPSED, "artifacts": [".gzkit/chores/demo/proofs/scan-record.md"]}
_DELTA = {"signal": "content-delta", "surfaces": ["src"], "graceDays": 7}


class TestElapsedTimeBands(unittest.TestCase):
    """Period then grace: current, then due (announced), then overdue (loud)."""

    def test_age_against_period_and_grace(self) -> None:
        cases = (
            ("within the period", 10, "current"),
            ("exactly at the period", 30, "current"),
            ("past the period, within grace", 33, "due"),
            ("exactly at period plus grace", 37, "due"),
            ("past period plus grace", 38, "overdue"),
        )
        for label, days_ago, band in cases:
            with self.subTest(label):
                log = _log((_NOW - timedelta(days=days_ago), "PASS"))
                self.assertEqual(_read(_declaration(_ELAPSED), log, []).band, band)

    def test_due_since_is_when_the_period_expired(self) -> None:
        last = _NOW - timedelta(days=33)
        reading = _read(_declaration(_ELAPSED), _log((last, "PASS")), [])
        self.assertEqual(reading.due_since, last + timedelta(days=30))
        self.assertEqual(reading.last_run, last)

    def test_never_run_is_overdue(self) -> None:
        """No record of a run is not evidence of a recent one."""
        for label, log in (("no log", None), ("log without a run", "## 2026-09-01 — notes\n")):
            with self.subTest(label):
                reading = _read(_declaration(_ELAPSED), log, [])
                self.assertEqual(reading.band, "overdue")
                self.assertIsNone(reading.last_run)


class TestDeclaredScanRecordDatesAnElapsedTimeChore(unittest.TestCase):
    """A chore declaring a scan record is read as its gate reads it (GHI #935, reopened).

    ``scripts/check_proof_freshness.py`` dates such a chore by the record's last
    change and never by a run block, because the gated run writes those blocks. The
    board must agree, or it reports current a chore whose next run the gate refuses.
    """

    def test_the_record_decides_the_band_whatever_the_run_blocks_say(self) -> None:
        cases = (
            ("scan done, last PASS long overdue", 10, 60, "current"),
            ("bare run today, scan past period and grace", 40, 0, "overdue"),
            ("bare run today, scan within grace", 33, 0, "due"),
        )
        for label, scanned_days, pass_days, band in cases:
            with self.subTest(label):
                scanned = _NOW - timedelta(days=scanned_days)
                log = _log((_NOW - timedelta(days=pass_days), "PASS"))
                reading = _read(_declaration(_RECORDED), log, [], scanned)
                self.assertEqual(reading.band, band)
                self.assertEqual(reading.last_run, scanned)

    def test_a_record_that_never_changed_is_overdue_despite_a_passing_run(self) -> None:
        log = _log((_NOW - timedelta(days=1), "PASS"))
        reading = _read(_declaration(_RECORDED), log, [], None)
        self.assertEqual(reading.band, "overdue")
        self.assertIsNone(reading.last_run)

    def test_a_chore_declaring_no_record_keeps_reading_its_passing_runs(self) -> None:
        """Ungated elapsed-time chores keep the run block; only the record is new."""
        last = _NOW - timedelta(days=10)
        reading = _read(_declaration(_ELAPSED), _log((last, "PASS")), [], _NOW)
        self.assertEqual(reading.band, "current")
        self.assertEqual(reading.last_run, last)


class TestContentDeltaBands(unittest.TestCase):
    """Due from the first surface commit after the last passing run."""

    def test_surface_movement_against_the_last_run(self) -> None:
        last = _NOW - timedelta(days=40)
        cases = (
            ("no surface commit since the run", [last - timedelta(days=5)], "current"),
            (
                "surface moved within grace",
                [last - timedelta(days=5), _NOW - timedelta(days=3)],
                "due",
            ),
            (
                "surface moved beyond grace",
                [_NOW - timedelta(days=20), _NOW - timedelta(days=1)],
                "overdue",
            ),
        )
        for label, commits, band in cases:
            with self.subTest(label):
                reading = _read(_declaration(_DELTA), _log((last, "PASS")), commits)
                self.assertEqual(reading.band, band)

    def test_due_since_is_the_oldest_commit_after_the_run(self) -> None:
        """Later commits must not reset the clock, or a busy surface never goes overdue."""
        last = _NOW - timedelta(days=40)
        first = _NOW - timedelta(days=20)
        reading = _read(
            _declaration(_DELTA), _log((last, "PASS")), [first, _NOW - timedelta(days=1)]
        )
        self.assertEqual(reading.due_since, first)
        self.assertEqual(reading.band, "overdue")

    def test_never_run_is_overdue_when_the_surface_has_history(self) -> None:
        reading = _read(_declaration(_DELTA), None, [_NOW - timedelta(days=100)])
        self.assertEqual(reading.band, "overdue")

    def test_surfaces_without_history_are_unmeasured_never_current(self) -> None:
        """An absent surface (an adopter lacking the path) proves nothing either way."""
        for label, log in (
            ("ran once", _log((_NOW - timedelta(days=1), "PASS"))),
            ("never ran", None),
        ):
            with self.subTest(label):
                reading = _read(_declaration(_DELTA), log, [])
                self.assertEqual(reading.band, "unmeasured")
                self.assertTrue(reading.reason)


class TestUnmeasuredAndPaused(unittest.TestCase):
    """Declared values, never absences: nothing is silently rendered current."""

    def test_accumulated_work_is_unmeasured_with_a_reason(self) -> None:
        declaration = _declaration({"signal": "accumulated-work", "graceDays": 7})
        reading = _read(declaration, None, [])
        self.assertEqual(reading.band, "unmeasured")
        self.assertIn("counter", reading.reason)

    def test_undeclared_chore_is_unmeasured(self) -> None:
        reading = _read(None, None, [])
        self.assertEqual(reading.band, "unmeasured")
        self.assertIsNone(reading.signal)

    def test_paused_wins_over_every_signal(self) -> None:
        """Intentional dormancy is silent and not a failure, however old the run."""
        for staleness in (_ELAPSED, _DELTA):
            with self.subTest(staleness["signal"]):
                declaration = _declaration({**staleness, "paused": True})
                self.assertEqual(_read(declaration, None, [_NOW]).band, "paused")


class TestOnlyAPassingRunResetsTheClock(unittest.TestCase):
    """The witness is a governed run, never an artifact someone wrote (GHI #935)."""

    def test_failed_run_and_narrative_heading_are_not_runs(self) -> None:
        old_pass = _NOW - timedelta(days=40)
        log = (
            _log((old_pass, "PASS"), (_NOW - timedelta(days=1), "FAIL"))
            + f"## {_NOW.date().isoformat()} — findings written by hand\n"
        )
        self.assertEqual(newest_pass_stamp(log), old_pass)
        self.assertEqual(_read(_declaration(_ELAPSED), log, []).band, "overdue")

    def test_newest_stamp_wins_regardless_of_file_order(self) -> None:
        newer = _NOW - timedelta(days=2)
        log = _log((newer, "PASS"), (_NOW - timedelta(days=90), "PASS"))
        self.assertEqual(newest_pass_stamp(log), newer)

    def test_offsetless_stamp_is_read_as_utc(self) -> None:
        self.assertEqual(
            newest_pass_stamp("## 2026-09-01T00:00:00\n- Status: PASS\n"),
            datetime(2026, 9, 1, tzinfo=UTC),
        )


if __name__ == "__main__":
    unittest.main()
