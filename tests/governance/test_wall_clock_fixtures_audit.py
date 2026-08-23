"""Detector for wall-clock-sensitive test fixtures (GHI #865, arm 1).

Arm 2 gave `LockData` an injectable clock, which removes the hazard for anyone
who uses it. Nothing makes them. This audit is the net: it flags a test fixture
that pins an absolute timestamp into a field feeding a wall-clock predicate,
because that fixture's verdict changes with the calendar rather than with the
behavior under test.

The instance it exists to prevent detonated at 2026-08-23T01:00Z — a fixture
pinned `2026-08-22T01:00:00+00:00` against a 1440-minute TTL, passed for a day,
then failed forever in a change that touched zero Python.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.wall_clock_fixtures import (
    FINDING_PREFIX,
    audit_wall_clock_fixtures,
)


class TestWallClockFixtureAudit(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "tests").mkdir()
        self.addCleanup(self._tmp.cleanup)

    def _write(self, body: str, name: str = "test_thing.py") -> None:
        (self.root / "tests" / name).write_text(body, encoding="utf-8")

    BOMB = (
        'lock = LockData(claimed_at="2026-08-22T01:00:00+00:00", ttl_minutes=1440)\n'
        "self.assertFalse(lock.is_expired)\n"
    )

    def test_flags_an_absolute_claimed_at(self):
        """The exact shape that detonated: fixed date AND a wall-clock verdict."""
        self._write(self.BOMB)
        errors = audit_wall_clock_fixtures(self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn("tests/test_thing.py:1", errors[0].artifact)

    def test_clean_when_the_timestamp_is_computed(self):
        """A fixture derived from `now` cannot decay, so it must not be flagged."""
        self._write(
            "lock = LockData(claimed_at=(datetime.now(UTC) - timedelta(minutes=1)).isoformat())\n"
            "self.assertFalse(lock.is_expired)\n"
        )
        self.assertEqual(audit_wall_clock_fixtures(self.root), [])

    def test_clean_when_the_seam_supplies_the_clock(self):
        """Arm 2's seam is the sanctioned way to be deterministic.

        `is_expired_at(now)` answers the question without consulting the wall
        clock at all, so an absolute timestamp beside it is inert — flagging it
        would push authors away from the fix.
        """
        self._write(
            'CLAIMED = "2026-08-22T01:00:00+00:00"\n'
            "self.assertTrue(lock.is_expired_at(base + timedelta(minutes=120)))\n"
        )
        self.assertEqual(audit_wall_clock_fixtures(self.root), [])

    def test_far_past_expiry_fixture_is_not_flagged(self):
        """A date no TTL can make live asserts EXPIRY, which never decays.

        `_ANCIENT_CLAIM = "2020-01-01…"` is the correct hardcoded shape and the
        opposite of the bomb. An audit that flagged it would be telling authors
        to break a fixture that cannot rot.
        """
        self._write('_ANCIENT_CLAIM = "2020-01-01T00:00:00+00:00"\n')
        self.assertEqual(audit_wall_clock_fixtures(self.root), [])

    def test_only_scans_the_tests_tree(self):
        """Production code legitimately carries absolute timestamps."""
        (self.root / "src").mkdir()
        (self.root / "src" / "mod.py").write_text(
            'DEFAULT = "2026-08-22T01:00:00+00:00"\n', encoding="utf-8"
        )
        self.assertEqual(audit_wall_clock_fixtures(self.root), [])

    def test_message_names_the_seam_not_just_the_problem(self):
        """A detector that only reports leaves the author guessing.

        Arm 2 exists; the finding should route to it.
        """
        self._write(self.BOMB)
        message = audit_wall_clock_fixtures(self.root)[0].message
        self.assertIn("is_expired_at", message)

    def test_clean_tree_returns_no_errors(self):
        self._write("x = 1\n")
        self.assertEqual(audit_wall_clock_fixtures(self.root), [])


class TestPredicateRequiresBothHalves(unittest.TestCase):
    """Either half alone is inert; only the pair is a bomb (GHI #865).

    Measured 2026-08-23: two files in this repo carry an absolute `claimed_at`
    and take ZERO liveness verdicts. Their timestamps are coherent fixture
    dates — `claimed_at` at 09:00 paired with `last_lock_event_timestamp` at
    10:00 — that never reach a wall-clock predicate. Flagging them would demand
    a change breaking that coupling for no safety gain, which is what makes a
    one-half predicate a proxy rather than a detector.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / "tests").mkdir()
        self.addCleanup(self._tmp.cleanup)

    def _write(self, body: str) -> None:
        (self.root / "tests" / "test_thing.py").write_text(body, encoding="utf-8")

    def test_absolute_timestamp_without_a_verdict_is_inert(self):
        """No wall-clock verdict in the file means nothing can decay."""
        self._write('lock = LockData(claimed_at="2026-08-22T01:00:00+00:00", ttl_minutes=1440)\n')
        self.assertEqual(audit_wall_clock_fixtures(self.root), [])

    def test_verdict_without_an_absolute_timestamp_is_inert(self):
        """A computed timestamp cannot decay however it is judged."""
        self._write(
            "lock = LockData(claimed_at=_live_claim())\nself.assertFalse(lock.is_expired)\n"
        )
        self.assertEqual(audit_wall_clock_fixtures(self.root), [])

    def test_both_halves_together_are_flagged(self):
        self._write(
            'lock = LockData(claimed_at="2026-08-22T01:00:00+00:00", ttl_minutes=1440)\n'
            "self.assertFalse(lock.is_expired)\n"
        )
        self.assertEqual(len(audit_wall_clock_fixtures(self.root)), 1)

    def test_the_repo_is_clean_under_this_predicate(self):
        """Regression fence: the tree is clean today and must stay clean.

        Without this, the audit could be wired in, pass vacuously, and nobody
        would notice it had stopped matching anything.
        """
        repo = Path(__file__).resolve().parents[2]
        self.assertEqual(audit_wall_clock_fixtures(repo), [])


class TestFoldedIntoTheTestQualityScope(unittest.TestCase):
    """The detector must be REACHABLE, not merely defined (GHI #865).

    An audit no scope calls protects nothing — the reachability chore says it
    outright: *"a validator reachable from nothing protects nothing; it reads as
    coverage while running on no commit path."* This detector has no flag of its
    own by design (`cli/parser_maintenance.py` and `commands/validate_cmd.py`
    are both AT their shrink-only ceilings), so its whole reachability comes
    from being folded into `audit_test_quality`. If that fold is ever undone,
    the detector goes silent and every gate stays green.
    """

    def test_test_quality_scope_includes_the_wall_clock_detector(self):
        from gzkit.tautological_tests import audit_test_quality

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "tests").mkdir()
            (root / "tests" / "test_bomb.py").write_text(
                'lock = LockData(claimed_at="2026-08-22T01:00:00+00:00", ttl_minutes=1440)\n'
                "self.assertFalse(lock.is_expired)\n",
                encoding="utf-8",
            )
            findings = audit_test_quality(root)

        self.assertTrue(
            any(f.message.startswith(FINDING_PREFIX) for f in findings),
            "the wall-clock detector is not reachable from the test-quality scope",
        )


if __name__ == "__main__":
    unittest.main()
