"""Unit tests for the MX hardening guards (OBPI-0.0.74-14).

The four guards bound the Maintenance Hangar — TTL/max-open, no-normal-release-
while-open, ledger debt-aging, and dangling-state detection — each resolving its
effective severity through the one leveled checkpoint (parent ADR Boundary
Invariant #2).

REQ-0.0.74-14-01..04 are BEHAVIOR REQs proven by the ``@covers``-decorated
methods below. REQ-0.0.74-14-05 is a ``[structural-fence]`` REQ — its proof
channel is parent ADR § Boundary Invariants #2, NOT a ``@covers`` test; the
``TestStructuralFence`` class is a belt-and-suspenders regression guard for the
"no hand-set bool, route through checkpoint" property, not the fence's proof.
"""

import json
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.mx import disposition, levels, marker
from gzkit.mx.marker import Marker
from gzkit.traceability import covers
from tests.commands.common import CliRunner, SilencedConsoleTestCase, _quick_init

_BASE = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _opened(session_id: str, ts: datetime) -> dict:
    return {
        "schema": "gzkit.ledger.v1",
        "event": "mx_session_opened",
        "id": session_id,
        "ts": _iso(ts),
        "session_id": session_id,
        "reason": "test",
        "attestor": "g0",
    }


def _closed(session_id: str, ts: datetime) -> dict:
    return {
        "schema": "gzkit.ledger.v1",
        "event": "mx_session_closed",
        "id": session_id,
        "ts": _iso(ts),
        "session_id": session_id,
        "attestor": "g0",
    }


def _write_ledger(root: Path, events: list[dict]) -> None:
    gzkit_dir = root / ".gzkit"
    gzkit_dir.mkdir(parents=True, exist_ok=True)
    (gzkit_dir / "ledger.jsonl").write_text(
        "\n".join(json.dumps(e) for e in events) + "\n",
        encoding="utf-8",
    )


class TestTtlMaxOpen(unittest.TestCase):
    """REQ-0.0.74-14-01: TTL / max-open guard flags an over-long or over-count hangar."""

    @covers("REQ-0.0.74-14-01")
    def test_session_past_its_lease_is_announced_and_never_grounds(self) -> None:
        """Past its lease a session is flagged and announced; nothing grounds on it.

        Amended at the surface (GHI #1257, operator ruling 2026-10-18: "a hangar
        past its TTL announces but never blocks gz mx exit"; "at worst, we book a
        status at expiry and notify"). The guard once emitted ERROR here, which
        grounds wherever the marker does not demote: outside the hangar and in
        exit's full-strength re-run. The REQ asserts a flag and a GZ_<LEVEL>
        through the checkpoint, and both still hold at WARNING.
        """
        from gzkit.mx import hardening

        states = {
            "no marker": None,
            "hangar open": Marker(session_id="s1"),
            "exit re-run": Marker(session_id="s1", exiting=True),
        }
        for label, held in states.items():
            with self.subTest(state=label), TemporaryDirectory() as tmp:
                root = Path(tmp)
                _write_ledger(root, [_opened("s1", _BASE)])
                if held is not None:
                    marker.write(held, root)
                result = hardening.ttl_max_open_status(root, now=_BASE + timedelta(hours=30))
                self.assertIn("s1", result.flagged_sessions)
                self.assertEqual(result.emitted_level, levels.WARNING)
                self.assertFalse(result.grounds)

    @covers("REQ-0.0.74-14-01")
    def test_the_hangar_lease_is_the_session_lock_ttl(self) -> None:
        """One lease, as in the token block: the hangar reads the lock rail's TTL.

        The TTL is moved under the guard, so a guard that kept its own 24h constant
        would still flag at 30 minutes and fail here.
        """
        from unittest.mock import patch

        from gzkit import lock_manager
        from gzkit.mx import hardening

        with (
            TemporaryDirectory() as tmp,
            patch.object(lock_manager, "DEFAULT_LOCK_TTL_MINUTES", 60),
        ):
            root = Path(tmp)
            _write_ledger(root, [_opened("s1", _BASE)])
            before = hardening.ttl_max_open_status(root, now=_BASE + timedelta(minutes=59))
            after = hardening.ttl_max_open_status(root, now=_BASE + timedelta(minutes=61))
            self.assertEqual(hardening.lease_hours(), 1.0)
        self.assertEqual(before.flagged_sessions, [])
        self.assertEqual(after.flagged_sessions, ["s1"])

    @covers("REQ-0.0.74-14-01")
    def test_session_within_ttl_not_flagged(self) -> None:
        from gzkit.mx import hardening

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(root, [_opened("s1", _BASE)])
            now = _BASE + timedelta(hours=1)  # well within TTL
            result = hardening.ttl_max_open_status(root, now=now)

        self.assertEqual(result.flagged_sessions, [])
        self.assertFalse(result.over_max)
        self.assertEqual(result.emitted_level, levels.INFO)
        self.assertFalse(result.grounds)

    @covers("REQ-0.0.74-14-01")
    def test_over_max_open_grounds_even_under_marker(self) -> None:
        from gzkit.mx import hardening

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(root, [_opened("s1", _BASE), _opened("s2", _BASE)])
            marker.write(Marker(session_id="s1"), root)  # hangar marker active
            now = _BASE + timedelta(hours=1)
            result = hardening.ttl_max_open_status(root, now=now)

        self.assertTrue(result.over_max)
        # max-open is a hard invariant: emits CRITICAL, which the checkpoint pins
        # through the active marker rather than demoting to advisory.
        self.assertEqual(result.emitted_level, levels.CRITICAL)
        self.assertTrue(result.grounds)

    @covers("REQ-0.0.74-14-01")
    def test_session_past_ttl_advisory_under_active_marker(self) -> None:
        from gzkit.mx import hardening

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(root, [_opened("s1", _BASE)])
            marker.write(Marker(session_id="s1"), root)  # hangar open
            now = _BASE + timedelta(hours=30)  # past the 24h TTL
            result = hardening.ttl_max_open_status(root, now=now)

        self.assertIn("s1", result.flagged_sessions)
        self.assertEqual(result.emitted_level, levels.WARNING)
        # Marker active → checkpoint demotes to ADVISORY; it does NOT ground.
        self.assertFalse(result.grounds)


class TestNormalReleaseBlocked(SilencedConsoleTestCase):
    """REQ-0.0.74-14-02: no normal release while the hangar is open."""

    @covers("REQ-0.0.74-14-02")
    def test_blocked_under_active_marker(self) -> None:
        from gzkit.mx import hardening

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gzkit").mkdir(parents=True, exist_ok=True)
            marker.write(Marker(session_id="s1"), root)
            result = hardening.normal_release_blocked(root)

        self.assertTrue(result.blocked)
        self.assertTrue(disposition.grounds(result.route))

    @covers("REQ-0.0.74-14-02")
    def test_not_blocked_without_marker(self) -> None:
        from gzkit.mx import hardening

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gzkit").mkdir(parents=True, exist_ok=True)
            result = hardening.normal_release_blocked(root)

        self.assertFalse(result.blocked)

    @covers("REQ-0.0.74-14-02")
    def test_patch_release_refused_at_real_site_under_marker(self) -> None:
        """The block is exercised at the real release site, not just the predicate."""
        from gzkit.commands.patch_release import patch_release_cmd

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            marker.write(Marker(session_id="s1"), root)
            with self.assertRaises(SystemExit) as cm:
                patch_release_cmd(dry_run=False, as_json=False, full=False)

        self.assertEqual(cm.exception.code, 3)

    @covers("REQ-0.0.74-14-02")
    def test_closeout_refused_at_real_site_under_marker(self) -> None:
        from gzkit.commands.closeout import closeout_cmd

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            marker.write(Marker(session_id="s1"), root)
            with self.assertRaises(SystemExit) as cm:
                closeout_cmd("ADR-0.0.74", as_json=False, dry_run=False)

        self.assertEqual(cm.exception.code, 3)


class TestDebtAging(unittest.TestCase):
    """REQ-0.0.74-14-03: accrued advisory debt grows louder the longer it sits."""

    @covers("REQ-0.0.74-14-03")
    def test_emitted_level_rises_with_age(self) -> None:
        from gzkit.mx import hardening

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(root, [_opened("s1", _BASE)])
            levels_seen = [
                hardening.debt_aging_status(root, now=_BASE + timedelta(hours=h)).emitted_level
                for h in (1, 8, 13, 25)
            ]

        # The top rung is WARNING, never a grounding level: debt past the lease
        # announces at full volume but blocks nothing (GHI #1257, operator ruling
        # 2026-10-18). Amended at the surface; the REQ asserts a rising level.
        self.assertEqual(levels_seen, [levels.INFO, levels.NOTICE, levels.WARNING, levels.WARNING])
        # Monotonic non-decreasing: debt never gets quieter as it ages.
        self.assertEqual(levels_seen, sorted(levels_seen))

    @covers("REQ-0.0.74-14-03")
    def test_the_debt_rungs_are_fractions_of_the_lease(self) -> None:
        """A quarter of the lease is NOTICE and a half warns, whatever the lease is."""
        from unittest.mock import patch

        from gzkit import lock_manager
        from gzkit.mx import hardening

        with (
            TemporaryDirectory() as tmp,
            patch.object(lock_manager, "DEFAULT_LOCK_TTL_MINUTES", 60),
        ):
            root = Path(tmp)
            _write_ledger(root, [_opened("s1", _BASE)])
            seen = [
                hardening.debt_aging_status(root, now=_BASE + timedelta(minutes=m)).emitted_level
                for m in (10, 16, 31)
            ]
        self.assertEqual(seen, [levels.INFO, levels.NOTICE, levels.WARNING])

    @covers("REQ-0.0.74-14-03")
    def test_no_open_session_is_silent(self) -> None:
        from gzkit.mx import hardening

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(root, [_opened("s1", _BASE), _closed("s1", _BASE)])
            result = hardening.debt_aging_status(root, now=_BASE + timedelta(hours=48))

        self.assertFalse(result.flagged)
        self.assertEqual(result.emitted_level, levels.INFO)

    @covers("REQ-0.0.74-14-03")
    def test_debt_aging_advisory_under_active_marker(self) -> None:
        from gzkit.mx import hardening

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(root, [_opened("s1", _BASE)])
            marker.write(Marker(session_id="s1"), root)  # hangar open
            now = _BASE + timedelta(hours=30)  # past the lease
            result = hardening.debt_aging_status(root, now=now)

        self.assertTrue(result.flagged)
        self.assertEqual(result.emitted_level, levels.WARNING)
        # Debt grows louder but does not ground, in the hangar or out of it.
        self.assertFalse(result.grounds)

    @covers("REQ-0.0.74-14-03")
    def test_aged_debt_never_grounds_exit(self) -> None:
        """Exit's full-strength re-run sees aged debt and is not blocked by it."""
        from gzkit.mx import hardening

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(root, [_opened("s1", _BASE)])
            marker.write(Marker(session_id="s1", exiting=True), root)
            result = hardening.debt_aging_status(root, now=_BASE + timedelta(hours=72))

        self.assertTrue(result.flagged)
        self.assertFalse(result.grounds)


def _opened_under(session_id: str, ts: datetime, contract: str) -> dict:
    return {**_opened(session_id, ts), "mode": "safe", "contract": contract}


class TestDebtAgesPerContract(unittest.TestCase):
    """GHI #1258: debt ages from the first safe-mode open under the same contract.

    Operator ruling 2026-10-18, 'Per contract (Rec.)': a session cycle renews the
    lease but does not reset the drydock's debt.
    """

    _CONTRACT = "docs/governance/harbor.md"

    def _after_cycle(self, second_contract: str | None) -> tuple[float, int]:
        from gzkit.mx import hardening

        cycle = _BASE + timedelta(hours=20)
        second = (
            _opened_under("s2", cycle, second_contract) if second_contract else _opened("s2", cycle)
        )
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(
                root,
                [_opened_under("s1", _BASE, self._CONTRACT), _closed("s1", cycle), second],
            )
            result = hardening.debt_aging_status(root, now=cycle + timedelta(hours=1))
        return result.age_hours, result.emitted_level

    @covers("REQ-0.0.74-14-03")
    def test_a_cycle_under_the_same_contract_keeps_the_debt(self) -> None:
        # 21 h is past half the 24 h lease; the second session alone is 1 h old.
        self.assertEqual(self._after_cycle(self._CONTRACT), (21.0, levels.WARNING))

    @covers("REQ-0.0.74-14-03")
    def test_a_new_contract_starts_its_own_debt(self) -> None:
        self.assertEqual(self._after_cycle("docs/governance/other.md"), (1.0, levels.INFO))

    @covers("REQ-0.0.74-14-03")
    def test_a_session_without_a_contract_ages_alone(self) -> None:
        self.assertEqual(self._after_cycle(None), (1.0, levels.INFO))

    @covers("REQ-0.0.74-14-03")
    def test_cycled_hangar_sessions_share_no_debt(self) -> None:
        """Two contract-less sessions are never one period, however close."""
        from gzkit.mx import hardening

        cycle = _BASE + timedelta(hours=20)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(root, [_opened("s1", _BASE), _closed("s1", cycle), _opened("s2", cycle)])
            result = hardening.debt_aging_status(root, now=cycle + timedelta(hours=1))
        self.assertEqual((result.age_hours, result.emitted_level), (1.0, levels.INFO))


class TestDanglingState(unittest.TestCase):
    """REQ-0.0.74-14-04: ledger says open but the marker is missing on disk."""

    @covers("REQ-0.0.74-14-04")
    def test_ledger_open_marker_missing_is_dangling(self) -> None:
        from gzkit.mx import hardening

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(root, [_opened("s1", _BASE)])  # no marker file written
            result = hardening.dangling_state_status(root)

        self.assertTrue(result.dangling)
        self.assertIn("s1", result.dangling_sessions)
        # Marker absent → ERROR is not demoted → grounds.
        self.assertTrue(result.grounds)

    @covers("REQ-0.0.74-14-04")
    def test_ledger_open_marker_present_not_dangling(self) -> None:
        from gzkit.mx import hardening

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(root, [_opened("s1", _BASE)])
            marker.write(Marker(session_id="s1"), root)
            result = hardening.dangling_state_status(root)

        self.assertFalse(result.dangling)

    @covers("REQ-0.0.74-14-04")
    def test_ledger_closed_marker_missing_not_dangling(self) -> None:
        from gzkit.mx import hardening

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_ledger(root, [_opened("s1", _BASE), _closed("s1", _BASE)])
            result = hardening.dangling_state_status(root)

        self.assertFalse(result.dangling)


class TestStructuralFence(unittest.TestCase):
    """Regression guard for REQ-0.0.74-14-05's property (proof channel is BI#2, not this).

    The fence is "each guard resolves severity through the leveled checkpoint —
    none hand-sets its own severity with a module-level bool." These assertions
    lock that property mechanically; the audited proof is the parent-ADR anchor.
    """

    def test_no_module_level_fail_closed_bool(self) -> None:
        from gzkit.mx import hardening

        offenders = [name for name in vars(hardening) if name.endswith("_FAIL_CLOSED")]
        self.assertEqual(
            offenders, [], "no hand-set _*_FAIL_CLOSED staging flag may exist (REQ-14-05)"
        )

    def test_each_guard_route_derives_from_checkpoint(self) -> None:
        """Each guard's route is the checkpoint's verdict for an INDEPENDENTLY-known
        emitted level — not a hand-set route, and not the guard's own stored level
        fed back in.

        The expected level for each guard is a literal derived from the REQ
        semantics for this fixture (one session aged past every threshold, no
        marker on disk), NOT ``result.emitted_level``. This breaks the circularity
        of feeding the guard's own output back into the oracle: a guard that
        computes the WRONG level now fails the level assertion, and a guard that
        hand-sets a route inconsistent with the checkpoint fails the route
        assertion. (REQ-14-05 property; proof channel is parent-ADR BI#2.)
        """
        from gzkit.mx import checkpoint, hardening

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            # One open session aged 30h, no marker file on disk. From this fixture
            # the REQ semantics fix each guard's emitted level without consulting
            # the guard: TTL past the lease → WARNING; debt aged past the lease →
            # WARNING; ledger-open + marker-missing → ERROR; no marker → release
            # guard emits INFO.
            _write_ledger(root, [_opened("s1", _BASE)])
            now = _BASE + timedelta(hours=30)
            cases = (
                (hardening.ttl_max_open_status(root, now=now), "mx-ttl-max-open", levels.WARNING),
                (hardening.debt_aging_status(root, now=now), "mx-debt-aging", levels.WARNING),
                (hardening.dangling_state_status(root), "mx-dangling-state", levels.ERROR),
                (hardening.normal_release_blocked(root), "mx-normal-release", levels.INFO),
            )
            for result, name, expected_level in cases:
                with self.subTest(guard=name):
                    # Guard computed the level the REQ semantics require for this
                    # fixture — asserted against a literal, independent of result.
                    self.assertEqual(result.emitted_level, expected_level)
                    # ...and the route is the checkpoint's verdict for THAT
                    # independently-known level, not for result.emitted_level.
                    self.assertEqual(
                        result.route,
                        checkpoint.resolve(name, expected_level, root),
                    )


if __name__ == "__main__":
    unittest.main()
