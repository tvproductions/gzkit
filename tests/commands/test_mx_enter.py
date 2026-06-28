"""Unit tests for gz mx enter (OBPI-0.0.74-04).

Tests the enter handler directly (not through CLI runner) to keep
fixture setup minimal and assertions tight.

REQ-0.0.74-04-01 through 04-04 are BEHAVIOR REQs proven by the
``@covers``-decorated methods below.
REQ-0.0.74-04-05 is a [support] REQ proven by ``gz validate --cli-alignment``
exit 0 + artifact_edited ledger event — verified at Stage 3, not here.
"""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit import lock_manager
from gzkit.mx import marker
from gzkit.traceability import covers
from tests.commands.common import SilencedConsoleTestCase


def _mk_root(tmp: str) -> Path:
    root = Path(tmp)
    (root / ".gzkit").mkdir(parents=True, exist_ok=True)
    return root


def _read_ledger_events(root: Path, event_type: str) -> list[dict]:
    ledger_path = root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.exists():
        return []
    events = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("event") == event_type:
            events.append(ev)
    return events


class TestMxEnterSetsMarkerAndEvent(SilencedConsoleTestCase):
    """REQ-0.0.74-04-01: enter sets marker, writes mx_session_opened, captures scope."""

    @covers("REQ-0.0.74-04-01")
    def test_enter_sets_marker(self) -> None:
        from gzkit.commands.mx_cmd import mx_enter_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            self.assertFalse(marker.is_active(root))
            mx_enter_cmd(
                reason="test run", attestor="tester", inspection_scope=[], project_root=root
            )
            self.assertTrue(marker.is_active(root))

    @covers("REQ-0.0.74-04-01")
    def test_enter_writes_mx_session_opened_event(self) -> None:
        from gzkit.commands.mx_cmd import mx_enter_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            mx_enter_cmd(
                reason="test run", attestor="tester", inspection_scope=[], project_root=root
            )
            events = _read_ledger_events(root, "mx_session_opened")
            self.assertEqual(len(events), 1)

    @covers("REQ-0.0.74-04-01")
    def test_enter_captures_inspection_scope_in_marker(self) -> None:
        from gzkit.commands.mx_cmd import mx_enter_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            scope = ["ADR-0.0.74", "OBPI-0.0.74-04"]
            mx_enter_cmd(
                reason="test run",
                attestor="tester",
                inspection_scope=scope,
                project_root=root,
            )
            m = marker.read(root)
            self.assertIsNotNone(m)
            assert m is not None
            self.assertEqual(m.inspection_scope, scope)

    @covers("REQ-0.0.74-04-01")
    def test_enter_captures_inspection_scope_in_ledger_event(self) -> None:
        from gzkit.commands.mx_cmd import mx_enter_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            scope = ["ADR-0.0.74"]
            mx_enter_cmd(
                reason="test run",
                attestor="tester",
                inspection_scope=scope,
                project_root=root,
            )
            events = _read_ledger_events(root, "mx_session_opened")
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0].get("inspection_scope"), scope)


class TestMxEnterRequiresAttestor(SilencedConsoleTestCase):
    """REQ-0.0.74-04-02: no agent-autonomous entry; operator-supplied attestor required."""

    @covers("REQ-0.0.74-04-02")
    def test_enter_without_attestor_exits_1(self) -> None:
        from gzkit.commands.mx_cmd import mx_enter_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            with self.assertRaises(SystemExit) as ctx:
                mx_enter_cmd(reason="test run", attestor="", inspection_scope=[], project_root=root)
            self.assertEqual(ctx.exception.code, 1)

    @covers("REQ-0.0.74-04-02")
    def test_no_marker_written_without_attestor(self) -> None:
        from gzkit.commands.mx_cmd import mx_enter_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            with self.assertRaises(SystemExit):
                mx_enter_cmd(reason="test run", attestor="", inspection_scope=[], project_root=root)
            self.assertFalse(marker.is_active(root))


class TestMxEnterFailsClosedOnEmpty(SilencedConsoleTestCase):
    """REQ-0.0.74-04-03: empty reason or attestor → exit 1, no marker, no ledger event."""

    @covers("REQ-0.0.74-04-03")
    def test_empty_reason_exits_1(self) -> None:
        from gzkit.commands.mx_cmd import mx_enter_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            with self.assertRaises(SystemExit) as ctx:
                mx_enter_cmd(reason="", attestor="tester", inspection_scope=[], project_root=root)
            self.assertEqual(ctx.exception.code, 1)

    @covers("REQ-0.0.74-04-03")
    def test_empty_reason_writes_no_marker_or_event(self) -> None:
        from gzkit.commands.mx_cmd import mx_enter_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            with self.assertRaises(SystemExit):
                mx_enter_cmd(reason="", attestor="tester", inspection_scope=[], project_root=root)
            self.assertFalse(marker.is_active(root))
            self.assertEqual(_read_ledger_events(root, "mx_session_opened"), [])

    @covers("REQ-0.0.74-04-03")
    def test_empty_attestor_exits_1(self) -> None:
        from gzkit.commands.mx_cmd import mx_enter_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            with self.assertRaises(SystemExit) as ctx:
                mx_enter_cmd(
                    reason="valid reason", attestor="", inspection_scope=[], project_root=root
                )
            self.assertEqual(ctx.exception.code, 1)

    @covers("REQ-0.0.74-04-03")
    def test_whitespace_only_reason_exits_1(self) -> None:
        from gzkit.commands.mx_cmd import mx_enter_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            with self.assertRaises(SystemExit) as ctx:
                mx_enter_cmd(
                    reason="   ", attestor="tester", inspection_scope=[], project_root=root
                )
            self.assertEqual(ctx.exception.code, 1)

    @covers("REQ-0.0.74-04-03")
    def test_whitespace_only_attestor_exits_1(self) -> None:
        from gzkit.commands.mx_cmd import mx_enter_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            with self.assertRaises(SystemExit) as ctx:
                mx_enter_cmd(
                    reason="valid reason", attestor="   ", inspection_scope=[], project_root=root
                )
            self.assertEqual(ctx.exception.code, 1)


class TestMxEnterUsesLockManagerRail(SilencedConsoleTestCase):
    """REQ-0.0.74-04-04: enter acquires session through lock_manager/token rail."""

    @covers("REQ-0.0.74-04-04")
    def test_enter_acquires_lock_via_lock_manager(self) -> None:
        from gzkit.commands.mx_cmd import mx_enter_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            mx_enter_cmd(
                reason="test run", attestor="tester", inspection_scope=[], project_root=root
            )
            lock = lock_manager.read_lock(root, "mx-session")
            self.assertIsNotNone(lock)

    @covers("REQ-0.0.74-04-04")
    def test_second_enter_while_active_is_rejected(self) -> None:
        from gzkit.commands.mx_cmd import mx_enter_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            mx_enter_cmd(
                reason="first entry", attestor="tester", inspection_scope=[], project_root=root
            )
            with self.assertRaises(SystemExit) as ctx:
                mx_enter_cmd(
                    reason="second entry", attestor="tester", inspection_scope=[], project_root=root
                )
            self.assertEqual(ctx.exception.code, 1)
