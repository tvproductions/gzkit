"""Unit tests for the MX hangar lease-expiry booking (GHI #1257).

Operator ruling 2026-10-18, verbatim: "what are we going to do? evict? at worst,
we book a status at least expiry and notify." A hangar session past its lease is
booked once as an ``mx_session_lease_expired`` ledger status and left exactly
where it is: the marker and the session lock survive the booking.
"""

import json
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit import lock_manager
from gzkit.events import MxSessionLeaseExpiredEvent, parse_typed_event
from gzkit.lock_manager import LockData
from gzkit.mx import marker
from gzkit.mx.marker import SESSION_LOCK_KEY, Marker
from tests.commands.common import SilencedConsoleTestCase

_BASE = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)
_LEASE = timedelta(minutes=lock_manager.DEFAULT_LOCK_TTL_MINUTES)


def _opened(session_id: str) -> dict:
    return {
        "schema": "gzkit.ledger.v1",
        "event": "mx_session_opened",
        "id": session_id,
        "ts": _BASE.isoformat(),
        "session_id": session_id,
        "reason": "test",
        "attestor": "g0",
    }


def _closed(session_id: str) -> dict:
    return {
        "schema": "gzkit.ledger.v1",
        "event": "mx_session_closed",
        "id": session_id,
        "ts": (_BASE + timedelta(hours=1)).isoformat(),
        "session_id": session_id,
        "attestor": "g0",
    }


def _renewed(session_id: str, at: datetime) -> dict:
    return {
        "schema": "gzkit.ledger.v1",
        "event": "mx_session_lease_renewed",
        "id": session_id,
        "ts": at.isoformat(),
        "session_id": session_id,
        "attestor": "g0",
        "renewed_at": at.isoformat(),
        "lease_minutes": lock_manager.DEFAULT_LOCK_TTL_MINUTES,
    }


def _root_with(tmp: str, events: list[dict]) -> Path:
    root = Path(tmp)
    (root / ".gzkit").mkdir(parents=True, exist_ok=True)
    (root / ".gzkit" / "ledger.jsonl").write_text(
        "".join(json.dumps(e) + "\n" for e in events), encoding="utf-8"
    )
    return root


def _booked(root: Path) -> list[dict]:
    lines = (root / ".gzkit" / "ledger.jsonl").read_text(encoding="utf-8").splitlines()
    rows = [json.loads(line) for line in lines if line.strip()]
    return [row for row in rows if row.get("event") == "mx_session_lease_expired"]


class TestLeaseExpiryBooking(unittest.TestCase):
    """An open session past its lease is booked once; nothing else is booked."""

    def test_a_session_past_its_lease_is_booked_once(self) -> None:
        from gzkit.mx import lease

        with TemporaryDirectory() as tmp:
            root = _root_with(tmp, [_opened("s1")])
            now = _BASE + _LEASE + timedelta(hours=2)
            first = lease.book_lease_expiries(root, now=now)
            second = lease.book_lease_expiries(root, now=now + timedelta(hours=5))
            rows = _booked(root)

        self.assertEqual(first, ["s1"])
        self.assertEqual(second, [])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["session_id"], "s1")
        self.assertEqual(rows[0]["lease_minutes"], lock_manager.DEFAULT_LOCK_TTL_MINUTES)
        self.assertEqual(rows[0]["opened_at"], _BASE.isoformat())

    def test_a_renewed_lease_is_booked_again_only_when_it_expires_again(self) -> None:
        """A renewal starts a new lease: expiry is booked once per lease (GHI #1261)."""
        from gzkit.mx import lease

        renewal = _BASE + _LEASE + timedelta(hours=3)
        with TemporaryDirectory() as tmp:
            root = _root_with(tmp, [_opened("s1")])
            first = lease.book_lease_expiries(root, now=_BASE + _LEASE + timedelta(hours=2))
            with (root / ".gzkit" / "ledger.jsonl").open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(_renewed("s1", renewal)) + "\n")
            inside = lease.book_lease_expiries(root, now=renewal + _LEASE - timedelta(minutes=1))
            past = lease.book_lease_expiries(root, now=renewal + _LEASE + timedelta(minutes=1))
            again = lease.book_lease_expiries(root, now=renewal + _LEASE + timedelta(hours=4))

        self.assertEqual((first, inside, past, again), (["s1"], [], ["s1"], []))

    def test_the_booked_status_is_a_typed_ledger_event(self) -> None:
        from gzkit.mx import lease

        with TemporaryDirectory() as tmp:
            root = _root_with(tmp, [_opened("s1")])
            lease.book_lease_expiries(root, now=_BASE + _LEASE + timedelta(minutes=1))
            row = _booked(root)[0]

        self.assertIsInstance(parse_typed_event(row), MxSessionLeaseExpiredEvent)

    def test_the_corpus_projection_accounts_for_the_booked_status(self) -> None:
        """A ledger carrying the status still replays as a complete corpus."""
        from gzkit.ledger import Ledger
        from gzkit.mx import lease
        from gzkit.ontology.corpus import project_corpus

        with TemporaryDirectory() as tmp:
            root = _root_with(tmp, [_opened("s1")])
            lease.book_lease_expiries(root, now=_BASE + _LEASE + timedelta(minutes=1))
            fidelity = project_corpus(Ledger(root / ".gzkit" / "ledger.jsonl")).fidelity

        self.assertTrue(fidelity.complete, fidelity)

    def test_nothing_is_booked_inside_the_lease_or_for_a_closed_session(self) -> None:
        from gzkit.mx import lease

        cases = {
            "inside the lease": ([_opened("s1")], _BASE + _LEASE - timedelta(minutes=1)),
            "closed session": ([_opened("s1"), _closed("s1")], _BASE + 3 * _LEASE),
        }
        for label, (events, now) in cases.items():
            with self.subTest(case=label), TemporaryDirectory() as tmp:
                root = _root_with(tmp, events)
                self.assertEqual(lease.book_lease_expiries(root, now=now), [])
                self.assertEqual(_booked(root), [])

    def test_booking_evicts_nothing(self) -> None:
        """The marker and the session lock are both still there after the booking."""
        from gzkit.mx import lease

        with TemporaryDirectory() as tmp:
            root = _root_with(tmp, [_opened("s1")])
            marker.write(Marker(session_id="s1"), root)
            lock_manager.write_lock(
                root,
                LockData(
                    obpi_id=SESSION_LOCK_KEY,
                    agent="claude-code",
                    pid=1,
                    session_id="s1",
                    claimed_at=_BASE.isoformat(),
                    branch="main",
                    ttl_minutes=lock_manager.DEFAULT_LOCK_TTL_MINUTES,
                ),
            )
            lease.book_lease_expiries(root, now=_BASE + 2 * _LEASE)

            self.assertTrue(marker.is_valid(root))
            self.assertIsNotNone(lock_manager.read_lock(root, SESSION_LOCK_KEY))


class TestOneLeaseKey(SilencedConsoleTestCase):
    """`gz mx enter`, `gz mx exit` and the reaper name the lease by one key (GHI #1257)."""

    def test_enter_and_exit_claim_and_release_the_lease_under_the_marker_key(self) -> None:
        from unittest.mock import patch

        from gzkit.commands.mx_cmd import mx_enter_cmd, mx_exit_cmd

        with (
            TemporaryDirectory() as tmp,
            patch.object(marker, "SESSION_LOCK_KEY", "lease-under-test"),
        ):
            root = Path(tmp)
            (root / ".gzkit").mkdir()
            mx_enter_cmd(reason="r", attestor="g0", inspection_scope=[], project_root=root)
            claimed = lock_manager.read_lock(root, "lease-under-test")
            mx_exit_cmd(attestor="g0", project_root=root, _run_guards=lambda _r: 0)
            released = lock_manager.read_lock(root, "lease-under-test")
        self.assertIsNotNone(claimed)
        self.assertIsNone(released)

    def _lease_lock(self, root: Path, claimed: datetime, agent: str = "other-agent") -> None:
        lock_manager.write_lock(
            root,
            LockData(
                obpi_id="lease-under-test",
                agent=agent,
                pid=1,
                session_id="earlier",
                claimed_at=claimed.isoformat(),
                branch="main",
                ttl_minutes=lock_manager.DEFAULT_LOCK_TTL_MINUTES,
            ),
        )

    def test_enter_clears_an_expired_orphan_under_the_marker_key(self) -> None:
        from unittest.mock import patch

        from gzkit.commands.mx_cmd import mx_enter_cmd

        with (
            TemporaryDirectory() as tmp,
            patch.object(marker, "SESSION_LOCK_KEY", "lease-under-test"),
        ):
            root = Path(tmp)
            (root / ".gzkit").mkdir()
            self._lease_lock(root, datetime.now(UTC) - 2 * _LEASE)
            mx_enter_cmd(reason="r", attestor="g0", inspection_scope=[], project_root=root)
            fresh = lock_manager.read_lock(root, "lease-under-test")
        self.assertIsNotNone(fresh)
        assert fresh is not None
        self.assertFalse(fresh.is_expired)

    def test_a_live_lease_refuses_entry_and_names_its_key(self) -> None:
        from unittest.mock import patch

        from gzkit.commands.mx_cmd import _entry_refusal_message, mx_enter_cmd

        with (
            TemporaryDirectory() as tmp,
            patch.object(marker, "SESSION_LOCK_KEY", "lease-under-test"),
        ):
            root = Path(tmp)
            (root / ".gzkit").mkdir()
            self._lease_lock(root, datetime.now(UTC))
            with self.assertRaises(SystemExit) as refused:
                mx_enter_cmd(reason="r", attestor="g0", inspection_scope=[], project_root=root)
            orphan = lock_manager.read_lock(root, "lease-under-test")
            assert orphan is not None
            expired = orphan.model_copy(
                update={"claimed_at": (datetime.now(UTC) - 2 * _LEASE).isoformat()}
            )
            message = _entry_refusal_message(expired)
        self.assertEqual(refused.exception.code, 1)
        self.assertIn("gz obpi lock release lease-under-test", message)


class TestReaperLeavesAnOpenHangarsLock(unittest.TestCase):
    """The lock reaper does not evict the session lock of a hangar that is open."""

    def _write_expired_session_lock(self, root: Path) -> None:
        lock_manager.write_lock(
            root,
            LockData(
                obpi_id=SESSION_LOCK_KEY,
                agent="claude-code",
                pid=1,
                session_id="s1",
                claimed_at=(datetime.now(UTC) - 2 * _LEASE).isoformat(),
                branch="main",
                ttl_minutes=lock_manager.DEFAULT_LOCK_TTL_MINUTES,
            ),
        )

    def test_an_open_hangars_expired_lock_survives_the_reaper(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _root_with(tmp, [_opened("s1")])
            marker.write(Marker(session_id="s1"), root)
            self._write_expired_session_lock(root)
            reaped = lock_manager.reap_expired_locks(root, reaper_agent="claude-code")
            self.assertEqual(reaped, [])
            self.assertIsNotNone(lock_manager.read_lock(root, SESSION_LOCK_KEY))

    def test_an_orphaned_session_lock_is_still_reaped(self) -> None:
        """No open hangar backs the lock, so it is the crash orphan GHI #848 clears."""
        with TemporaryDirectory() as tmp:
            root = _root_with(tmp, [_opened("s1"), _closed("s1")])
            self._write_expired_session_lock(root)
            reaped = lock_manager.reap_expired_locks(root, reaper_agent="claude-code")
            self.assertEqual([lock.obpi_id for lock in reaped], [SESSION_LOCK_KEY])
            self.assertIsNone(lock_manager.read_lock(root, SESSION_LOCK_KEY))


if __name__ == "__main__":
    unittest.main()
