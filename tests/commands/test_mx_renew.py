"""Unit tests for gz mx renew (GHI #1261).

Operator rulings: the close-and-reopen of 2026-10-18 was "a lease renewal inside
one drydock"; 2026-10-20 "yes, we need the concept of a renewal"; and renewal is
lease-only, "as the 10-18 ruling already implies". A renewal refreshes the lease of
the open session and books it; it runs no guard, keeps the marker, and leaves the
advisory debt aging from the contract's first open (GHI #1258).
"""

import json
import os
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from gzkit import lock_manager
from gzkit.commands import mx_cmd
from gzkit.mx import marker
from gzkit.mx.lease import book_lease_expiries
from tests.commands.common import SilencedConsoleTestCase

_LEASE = timedelta(minutes=lock_manager.DEFAULT_LOCK_TTL_MINUTES)


def _open_session(tmp: str) -> Path:
    from gzkit.commands.mx_cmd import mx_enter_cmd

    root = Path(tmp)
    (root / ".gzkit").mkdir(parents=True, exist_ok=True)
    mx_enter_cmd(reason="drydock", attestor="g0", inspection_scope=[], project_root=root)
    return root


def _events(root: Path, event_type: str) -> list[dict]:
    lines = (root / ".gzkit" / "ledger.jsonl").read_text(encoding="utf-8").splitlines()
    rows = [json.loads(line) for line in lines if line.strip()]
    return [row for row in rows if row.get("event") == event_type]


def _age_lock(root: Path, by: timedelta) -> None:
    held = lock_manager.read_lock(root, marker.SESSION_LOCK_KEY)
    assert held is not None
    lock_manager.delete_lock(root, marker.SESSION_LOCK_KEY)
    lock_manager.write_lock(
        root,
        held.model_copy(update={"claimed_at": (datetime.now(UTC) - by).isoformat()}),
    )


class TestRenewRefreshesTheLease(SilencedConsoleTestCase):
    def test_renew_books_the_renewal_and_refreshes_the_lock(self) -> None:
        from gzkit.commands.mx_cmd import mx_renew_cmd

        with TemporaryDirectory() as tmp:
            root = _open_session(tmp)
            _age_lock(root, 2 * _LEASE)
            held = marker.read(root)
            assert held is not None
            session_id = held.session_id

            mx_renew_cmd(attestor="g0", project_root=root)

            lock = lock_manager.read_lock(root, marker.SESSION_LOCK_KEY)
            renewals = _events(root, "mx_session_lease_renewed")
            self.assertIsNotNone(lock)
            assert lock is not None
            self.assertFalse(lock.is_expired)
            self.assertEqual(lock.session_id, session_id)
            self.assertEqual(len(renewals), 1)
            self.assertEqual(renewals[0]["session_id"], session_id)
            self.assertEqual(renewals[0]["attestor"], "g0")

    def test_renew_keeps_the_session_open_and_runs_no_guard(self) -> None:
        from gzkit.commands import mx_cmd

        with TemporaryDirectory() as tmp:
            root = _open_session(tmp)
            before = marker.read(root)
            with patch.object(mx_cmd, "_default_run_guards") as guards:
                mx_cmd.mx_renew_cmd(attestor="g0", project_root=root)

            guards.assert_not_called()
            self.assertEqual(marker.read(root), before)
            self.assertTrue(marker.is_valid(root))
            self.assertEqual(_events(root, "mx_session_closed"), [])

    def test_the_lease_guard_stops_flagging_after_a_renewal(self) -> None:
        from gzkit.commands.mx_cmd import mx_renew_cmd
        from gzkit.mx import hardening

        with TemporaryDirectory() as tmp:
            root = _open_session(tmp)
            later = datetime.now(UTC) + 2 * _LEASE
            self.assertTrue(hardening.ttl_max_open_status(root, now=later).flagged_sessions)

            with patch("gzkit.commands.mx_cmd._now", return_value=later):
                mx_renew_cmd(attestor="g0", project_root=root)

            self.assertEqual(hardening.ttl_max_open_status(root, now=later).flagged_sessions, [])

    def test_a_renewal_does_not_reset_advisory_debt(self) -> None:
        from gzkit.commands.mx_cmd import mx_renew_cmd
        from gzkit.mx import hardening

        with TemporaryDirectory() as tmp:
            root = _open_session(tmp)
            later = datetime.now(UTC) + 2 * _LEASE
            before = hardening.debt_aging_status(root, now=later).age_hours

            with patch("gzkit.commands.mx_cmd._now", return_value=later):
                mx_renew_cmd(attestor="g0", project_root=root)

            after = hardening.debt_aging_status(root, now=later).age_hours
            self.assertAlmostEqual(after, before, places=3)
            self.assertGreater(after, hardening.lease_hours())


class TestRenewKeepsTheMxSessionAsHolder(SilencedConsoleTestCase):
    """RP-12 rulings 3 and 149: a renewal from any harness session is held by the MX session."""

    def test_the_renewed_lease_is_held_by_the_mx_session(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _open_session(tmp)
            harness = {"CLAUDECODE": "1", "CLAUDE_CODE_SESSION_ID": "after-a-clear"}
            with patch.dict(os.environ, harness):
                mx_cmd.mx_renew_cmd(attestor="g0", project_root=root)
            held = marker.read(root)
            lock = lock_manager.read_lock(root, marker.SESSION_LOCK_KEY)
        assert held is not None
        assert lock is not None
        self.assertEqual((lock.agent, lock.session_id), (held.session_id, held.session_id))


class TestRenewBooksALapsedLeasesExpiry(SilencedConsoleTestCase):
    """GHI #1257 and #1261: a lease that ran out mid-session is booked expired at its renewal."""

    def renew_at(self, root: Path, when: datetime) -> str:
        """Renew at ``when`` and return what the verb printed."""
        with (
            patch("gzkit.commands.mx_cmd._now", return_value=when),
            patch.object(mx_cmd.console, "print") as printed,
        ):
            mx_cmd.mx_renew_cmd(attestor="g0", project_root=root)
        return "\n".join(str(call.args[0]) for call in printed.call_args_list)

    def test_a_lapsed_lease_is_booked_expired_before_the_renewal(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _open_session(tmp)
            printed = self.renew_at(root, datetime.now(UTC) + 2 * _LEASE)
            rows = [
                row["event"]
                for row in _events(root, "mx_session_lease_expired")
                + _events(root, "mx_session_lease_renewed")
            ]
            self.assertEqual(rows, ["mx_session_lease_expired", "mx_session_lease_renewed"])
            (opened,) = _events(root, "mx_session_opened")
            (expired,) = _events(root, "mx_session_lease_expired")
            lines = (root / ".gzkit" / "ledger.jsonl").read_text(encoding="utf-8")
        self.assertEqual(expired["lease_started_at"], opened["ts"])
        self.assertLess(
            lines.index('"mx_session_lease_expired"'), lines.index('"mx_session_lease_renewed"')
        )
        # output-contract: the expiry is booked and announced, never silent (ruling 2026-10-18)
        self.assertIn("Lease expiry booked", printed)

    def test_a_live_lease_books_no_expiry(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _open_session(tmp)
            printed = self.renew_at(root, datetime.now(UTC))
            self.assertEqual(_events(root, "mx_session_lease_expired"), [])
        self.assertNotIn("Lease expiry booked", printed)

    def test_a_renewed_lease_that_lapses_is_booked_against_its_own_start(self) -> None:
        """GHI #1261: expiry is once per lease, so a renewed lease's runs from its renewal."""
        with TemporaryDirectory() as tmp:
            root = _open_session(tmp)
            first = datetime.now(UTC) + timedelta(hours=1)
            self.renew_at(root, first)
            self.renew_at(root, first + 2 * _LEASE)
            expired = _events(root, "mx_session_lease_expired")
        self.assertEqual([row["lease_started_at"] for row in expired], [first.isoformat()])

    def test_an_expiry_the_orientation_booked_is_not_booked_again(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _open_session(tmp)
            later = datetime.now(UTC) + 2 * _LEASE
            book_lease_expiries(root, now=later)
            self.renew_at(root, later)
            self.assertEqual(len(_events(root, "mx_session_lease_expired")), 1)


class TestRenewIsReachableFromTheCli(SilencedConsoleTestCase):
    def test_gz_mx_renew_routes_to_the_handler_with_the_attestor(self) -> None:
        from gzkit.cli.main import main

        with patch("gzkit.commands.mx_cmd.mx_renew_cmd") as handler:
            main(["mx", "renew", "--attestor", "g0"])
        handler.assert_called_once_with(attestor="g0")


class TestRenewRefusals(SilencedConsoleTestCase):
    def test_renew_refuses_without_an_open_session(self) -> None:
        from gzkit.commands.mx_cmd import mx_renew_cmd

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gzkit").mkdir()
            with self.assertRaises(SystemExit) as ctx:
                mx_renew_cmd(attestor="g0", project_root=root)
            self.assertEqual(ctx.exception.code, 1)

    def test_renew_refuses_a_marker_with_no_open_ledger_session(self) -> None:
        from gzkit.commands.mx_cmd import mx_renew_cmd
        from gzkit.mx.marker import Marker

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gzkit").mkdir()
            marker.write(Marker(session_id="hand-made"), root)
            with self.assertRaises(SystemExit) as ctx:
                mx_renew_cmd(attestor="g0", project_root=root)
            self.assertEqual(ctx.exception.code, 1)

    def test_renew_refuses_an_empty_attestor(self) -> None:
        from gzkit.commands.mx_cmd import mx_renew_cmd

        with TemporaryDirectory() as tmp:
            root = _open_session(tmp)
            with self.assertRaises(SystemExit) as ctx:
                mx_renew_cmd(attestor="  ", project_root=root)
            self.assertEqual(ctx.exception.code, 1)
            self.assertEqual(_events(root, "mx_session_lease_renewed"), [])


if __name__ == "__main__":
    unittest.main()
