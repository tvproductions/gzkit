"""Tests for the MX session-lock lifecycle (GHI #848).

The marker has a symmetric pair — written on enter, unlinked on exit. The lock
had only the acquire half, so a cleanly-closed hangar left a lock that
`write_lock` (exclusive-creation, TTL-blind) refused forever. The defect is
invisible on the happy path: the FIRST enter/exit cycle in any repository
succeeds completely, and only the SECOND enter fails.
"""

from __future__ import annotations

import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from gzkit import lock_manager
from gzkit.commands import mx_cmd
from gzkit.lock_manager import LockData

MX_KEY = "mx-session"


def _root() -> Path:
    root = Path(tempfile.mkdtemp(prefix="gzkit-mxlock-"))
    (root / ".gzkit" / "locks" / "obpi").mkdir(parents=True)
    return root


def _live_claim(*, minutes_ago: int = 1) -> str:
    """A claim timestamp that is ALWAYS inside the default TTL.

    Never hardcode an absolute timestamp for a lock a test needs to be live.
    A fixed date plus a finite TTL is a time bomb: it passes until the wall
    clock crosses `claimed_at + ttl`, then fails forever, and it fails in a
    run that changed nothing. Observed 2026-08-23T01:14Z — two tests here
    pinned `2026-08-22T01:00:00+00:00` against `ttl_minutes=1440` and went red
    fourteen minutes after that lock's expiry, during an unrelated change.

    Liveness is the property under test, so compute it from `now` and let the
    name say so.
    """
    return (datetime.now(UTC) - timedelta(minutes=minutes_ago)).isoformat()


# Far enough in the past that no TTL can make it live again. Safe to hardcode
# for the same reason `_live_claim` must not be: the assertion is expiry.
_ANCIENT_CLAIM = "2020-01-01T00:00:00+00:00"


def _lock(claimed_at: str, *, agent: str = "a", ttl: int = 1440) -> LockData:
    return LockData(
        obpi_id=MX_KEY,
        agent=agent,
        pid=1,
        session_id="s",
        claimed_at=claimed_at,
        branch="main",
        ttl_minutes=ttl,
    )


class TestExitReleasesItsLock(unittest.TestCase):
    """Arm 1 — a resource acquired on one edge must be released on the other."""

    def test_release_removes_the_session_lock(self) -> None:
        root = _root()
        lock_manager.write_lock(root, _lock(_live_claim()))
        self.assertTrue(mx_cmd._release_session_lock(root))
        self.assertIsNone(lock_manager.read_lock(root, MX_KEY))

    def test_release_is_idempotent_when_no_lock_is_present(self) -> None:
        """Exit must not fail because the lock was already gone."""
        self.assertFalse(mx_cmd._release_session_lock(_root()))

    def test_enter_after_release_succeeds(self) -> None:
        """The cycle this defect broke: enter, exit, enter again.

        The first cycle always worked, which is why nothing caught it.
        """
        root = _root()
        lock_manager.write_lock(root, _lock(_live_claim()))
        mx_cmd._release_session_lock(root)
        lock_manager.write_lock(root, _lock(_live_claim(), agent="b"))
        self.assertIsNotNone(lock_manager.read_lock(root, MX_KEY))


class TestEnterReapsAnExpiredOrphan(unittest.TestCase):
    """Arm 2 — the crash path, which releasing on exit cannot reach.

    If the process dies between enter and exit, no exit ever runs, so arm 1
    never fires. `write_lock` is exclusive-creation and TTL-blind, so the
    orphan blocks every future entry regardless of age.
    """

    def test_expired_orphan_is_cleared_before_claiming(self) -> None:
        root = _root()
        lock_manager.write_lock(root, _lock(_ANCIENT_CLAIM))
        self.assertTrue(lock_manager.read_lock(root, MX_KEY).is_expired)
        self.assertTrue(mx_cmd._clear_expired_session_lock(root))
        self.assertIsNone(lock_manager.read_lock(root, MX_KEY))

    def test_live_lock_is_never_cleared(self) -> None:
        """A genuine concurrent claim must still win — this is the whole point.

        An always-clear implementation would delete the exclusion property the
        lock exists to provide, which is worse than the orphan it fixes.
        """
        root = _root()
        lock_manager.write_lock(root, _lock(_live_claim(), ttl=1440))
        self.assertFalse(lock_manager.read_lock(root, MX_KEY).is_expired)
        self.assertFalse(mx_cmd._clear_expired_session_lock(root))
        self.assertIsNotNone(lock_manager.read_lock(root, MX_KEY))

    def test_absent_lock_is_a_no_op(self) -> None:
        self.assertFalse(mx_cmd._clear_expired_session_lock(_root()))


class TestRefusalProseNamesTheRealCause(unittest.TestCase):
    """The third defect in the same path: the message misattributed the cause.

    'Concurrent MX entry detected — another session is opening' is wrong when
    the prior session closed cleanly and left an orphan, and it sends the
    reader looking for a concurrency problem that does not exist.
    """

    def test_message_distinguishes_a_live_claim_from_a_stale_orphan(self) -> None:
        live = mx_cmd._entry_refusal_message(_lock(_live_claim()))
        stale = mx_cmd._entry_refusal_message(_lock(_ANCIENT_CLAIM))
        self.assertNotEqual(live, stale)
        self.assertIn("another session", live.lower())
        self.assertIn("expired", stale.lower())

    def test_stale_message_names_the_recovery_THAT_ACTUALLY_WORKS(self) -> None:
        """The bare release verb is refused twice over, so naming it is useless.

        Observed 2026-08-22: `gz obpi lock release mx-session` fails ownership
        validation (the holder is a different agent id) and `--force` alone then
        fail-closes on token-block discipline, which requires an exchange
        record. Only the both-flags form releases an orphan.
        """
        stale = mx_cmd._entry_refusal_message(_lock(_ANCIENT_CLAIM))
        self.assertIn("gz obpi lock release", stale)
        self.assertIn("--force", stale)
        self.assertIn("--abandon reaping:", stale)

    def test_message_survives_an_unreadable_lock(self) -> None:
        """An unreadable lock must still produce prose, not a crash."""
        self.assertIn("mx-session", mx_cmd._entry_refusal_message(None))


class TestRegisterEntryScope(unittest.TestCase):
    """A non-OBPI lock's register entry is out of the token-block contract's scope.

    `HandoffFrontmatter` requires a well-formed OBPI id and parent ADR. The
    `mx-session` mutex has neither, so scanning its release record asserts a
    contract it can never satisfy — and the ledger event referencing that record
    is append-only, so the record cannot be deleted either. The tree traps.
    """

    def test_non_obpi_entry_is_out_of_scope(self) -> None:
        from gzkit.quality import _is_non_obpi_register_entry

        self.assertTrue(_is_non_obpi_register_entry("---\nobpi_id: mx-session\n---\n"))

    def test_real_obpi_entry_stays_in_scope(self) -> None:
        """The exemption must not swallow genuine OBPI register entries."""
        from gzkit.quality import _is_non_obpi_register_entry

        self.assertFalse(_is_non_obpi_register_entry("---\nobpi_id: OBPI-0.35.0-09-codex\n---\n"))


class TestLiveClaimHelperCannotTimeBomb(unittest.TestCase):
    """Pin the helper's contract so the bomb cannot be reintroduced.

    Without this, `_live_claim` is a convention: the next author adds a case
    with a hardcoded date, it passes for weeks, and it goes red in someone
    else's unrelated change. This asserts the property the name promises.
    """

    def test_live_claim_is_not_expired_under_the_default_ttl(self) -> None:
        self.assertFalse(_lock(_live_claim()).is_expired)

    def test_live_claim_is_still_live_at_the_ttl_boundary(self) -> None:
        """A whole TTL minus a minute is the widest a caller can reasonably ask."""
        self.assertFalse(_lock(_live_claim(minutes_ago=1439)).is_expired)

    def test_ancient_claim_is_expired(self) -> None:
        """The other half: the expiry fixtures must never drift into liveness."""
        self.assertTrue(_lock(_ANCIENT_CLAIM).is_expired)


if __name__ == "__main__":
    unittest.main()
