"""Unit tests for gz mx exit (OBPI-0.0.74-05).

Tests the exit handler directly (not through CLI runner) to keep
fixture setup minimal and assertions tight.

REQ-0.0.74-05-01, 05-02, 05-03, 05-06 are BEHAVIOR REQs proven by the
``@covers``-decorated methods below.
REQ-0.0.74-05-04 is a [support] REQ proven by ``gz validate --cli-alignment``
exit 0 + artifact_edited ledger event — verified at Stage 3, not here.
REQ-0.0.74-05-05 is a [structural-fence] REQ; proof channel is parent ADR
Boundary Invariant #4 — no @covers test required.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.mx import marker
from gzkit.traceability import covers


def _mk_root(tmp: str) -> Path:
    root = Path(tmp)
    (root / ".gzkit").mkdir(parents=True, exist_ok=True)
    return root


def _mk_root_with_session(tmp: str) -> Path:
    """Create a temp root with an active MX session (marker + ledger event)."""
    from gzkit.commands.mx_cmd import mx_enter_cmd

    root = _mk_root(tmp)
    mx_enter_cmd(
        reason="test session",
        attestor="tester",
        inspection_scope=["ADR-0.0.74"],
        project_root=root,
    )
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


def _green_guard(root: Path) -> int:  # noqa: ARG001
    return 0


def _red_guard(root: Path) -> int:  # noqa: ARG001
    return 1


class TestMxExitFullStrengthRerun(unittest.TestCase):
    """REQ-0.0.74-05-01: guards re-run at full strength (marker absent during run)."""

    @covers("REQ-0.0.74-05-01")
    def test_exit_removes_marker_during_rerun(self) -> None:
        from gzkit.commands.mx_cmd import mx_exit_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root_with_session(tmp)
            self.assertTrue(marker.is_active(root))

            marker_state_during_run: list[bool] = []

            def capturing_guard(r: Path) -> int:
                marker_state_during_run.append(marker.is_active(r))
                return 0

            mx_exit_cmd(attestor="tester", project_root=root, _run_guards=capturing_guard)

            self.assertEqual(len(marker_state_during_run), 1)
            # Marker MUST be absent during the guard run (full-strength — no advisory demotion).
            self.assertFalse(marker_state_during_run[0])

    @covers("REQ-0.0.74-05-01")
    def test_exit_passes_project_root_to_guards(self) -> None:
        from gzkit.commands.mx_cmd import mx_exit_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root_with_session(tmp)

            received: list[Path] = []

            def capturing_guard(r: Path) -> int:
                received.append(r)
                return 0

            mx_exit_cmd(attestor="tester", project_root=root, _run_guards=capturing_guard)

            self.assertEqual(len(received), 1)
            self.assertEqual(received[0], root)


class TestMxExitHardRefuseOnRed(unittest.TestCase):
    """REQ-0.0.74-05-02: any guard red → exit 3, marker stays, no mx_session_closed."""

    @covers("REQ-0.0.74-05-02")
    def test_exit_red_raises_exit3(self) -> None:
        from gzkit.commands.mx_cmd import mx_exit_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root_with_session(tmp)
            with self.assertRaises(SystemExit) as ctx:
                mx_exit_cmd(attestor="tester", project_root=root, _run_guards=_red_guard)
            self.assertEqual(ctx.exception.code, 3)

    @covers("REQ-0.0.74-05-02")
    def test_exit_red_leaves_marker_in_place(self) -> None:
        from gzkit.commands.mx_cmd import mx_exit_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root_with_session(tmp)
            with self.assertRaises(SystemExit):
                mx_exit_cmd(attestor="tester", project_root=root, _run_guards=_red_guard)
            # Marker MUST remain after a red refuse.
            self.assertTrue(marker.is_active(root))

    @covers("REQ-0.0.74-05-02")
    def test_exit_red_writes_no_closed_event(self) -> None:
        from gzkit.commands.mx_cmd import mx_exit_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root_with_session(tmp)
            with self.assertRaises(SystemExit):
                mx_exit_cmd(attestor="tester", project_root=root, _run_guards=_red_guard)
            # No mx_session_closed event may be written when guards are red.
            events = _read_ledger_events(root, "mx_session_closed")
            self.assertEqual(events, [])


class TestMxExitGreenPath(unittest.TestCase):
    """REQ-0.0.74-05-03: all-green + attestor → write mx_session_closed, remove marker."""

    @covers("REQ-0.0.74-05-03")
    def test_exit_green_writes_mx_session_closed_event(self) -> None:
        from gzkit.commands.mx_cmd import mx_exit_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root_with_session(tmp)
            mx_exit_cmd(attestor="g0", project_root=root, _run_guards=_green_guard)
            events = _read_ledger_events(root, "mx_session_closed")
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0].get("attestor"), "g0")

    @covers("REQ-0.0.74-05-03")
    def test_exit_green_removes_marker(self) -> None:
        from gzkit.commands.mx_cmd import mx_exit_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root_with_session(tmp)
            mx_exit_cmd(attestor="g0", project_root=root, _run_guards=_green_guard)
            # Marker MUST be gone after a green close.
            self.assertFalse(marker.is_active(root))

    @covers("REQ-0.0.74-05-03")
    def test_exit_empty_attestor_exits1(self) -> None:
        from gzkit.commands.mx_cmd import mx_exit_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root_with_session(tmp)
            with self.assertRaises(SystemExit) as ctx:
                mx_exit_cmd(attestor="", project_root=root, _run_guards=_green_guard)
            self.assertEqual(ctx.exception.code, 1)
            # Marker MUST still be active after an empty-attestor refuse.
            self.assertTrue(marker.is_active(root))

    @covers("REQ-0.0.74-05-03")
    def test_exit_whitespace_attestor_exits1(self) -> None:
        from gzkit.commands.mx_cmd import mx_exit_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root_with_session(tmp)
            with self.assertRaises(SystemExit) as ctx:
                mx_exit_cmd(attestor="   ", project_root=root, _run_guards=_green_guard)
            self.assertEqual(ctx.exception.code, 1)


class TestMxExitLiveNegativeControl(unittest.TestCase):
    """REQ-0.0.74-05-06: known violation at exit time IS still caught (not a stub)."""

    @covers("REQ-0.0.74-05-06")
    def test_live_exit_nc_catches_known_violation(self) -> None:
        """A known violation injected as a red guard MUST be caught — exit hard-refuses.

        This is the live exit negative-control: the guard (a real enforcement
        mechanism) sees a violation and returns non-zero; exit MUST refuse with
        exit 3 and leave the marker in place.  A stub that auto-greens would
        pass here instead of refusing.
        """
        from gzkit.commands.mx_cmd import mx_exit_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root_with_session(tmp)

            # The "known violation": a guard that represents a failing check.
            violation_caught: list[bool] = []

            def violation_guard(r: Path) -> int:  # noqa: ARG001
                violation_caught.append(True)
                return 1  # violation: non-zero = red

            with self.assertRaises(SystemExit) as ctx:
                mx_exit_cmd(attestor="tester", project_root=root, _run_guards=violation_guard)

            # Guard MUST have been invoked (re-run happened, not skipped).
            self.assertTrue(violation_caught)
            # Exit MUST be 3 (hard refuse, not 0/1/2).
            self.assertEqual(ctx.exception.code, 3)
            # Marker MUST remain — no clearing on a red violation.
            self.assertTrue(marker.is_active(root))


if __name__ == "__main__":
    unittest.main()
