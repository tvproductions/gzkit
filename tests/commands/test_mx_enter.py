"""Unit tests for gz mx enter (OBPI-0.0.74-04).

Tests the enter handler directly (not through CLI runner) to keep
fixture setup minimal and assertions tight.

REQ-0.0.74-04-01 through 04-04 are BEHAVIOR REQs proven by the
``@covers``-decorated methods below.
REQ-0.0.74-04-05 is a [support] REQ proven by ``gz validate --cli-alignment``
exit 0 + artifact_edited ledger event — verified at Stage 3, not here.
"""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit import lock_manager
from gzkit.cli import main
from gzkit.mx import marker
from gzkit.traceability import covers
from tests.commands.common import CliRunner, SilencedConsoleTestCase


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


class TestMxEnterSafeMode(SilencedConsoleTestCase):
    """GHI #1244: ``--mode safe --contract <path>`` opens safe mode."""

    def _contract(self, root: Path) -> str:
        path = root / "docs" / "governance" / "pilotage.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# contract\n", encoding="utf-8")
        return "docs/governance/pilotage.md"

    def test_safe_mode_writes_mode_and_contract_to_marker_and_event(self) -> None:
        from gzkit.commands.mx_cmd import mx_enter_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            contract = self._contract(root)
            mx_enter_cmd(
                reason="harbor pilotage",
                attestor="g0",
                inspection_scope=[],
                project_root=root,
                mode="safe",
                contract=contract,
            )
            m = marker.read(root)
            self.assertIsNotNone(m)
            assert m is not None
            self.assertEqual((m.level, m.contract), ("drydock", contract))
            events = _read_ledger_events(root, "mx_session_opened")
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0].get("mode"), "safe")
            self.assertEqual(events[0].get("contract"), contract)

    def test_the_default_mode_is_the_hangar(self) -> None:
        from gzkit.commands.mx_cmd import mx_enter_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            mx_enter_cmd(reason="repair", attestor="g0", inspection_scope=[], project_root=root)
            m = marker.read(root)
            assert m is not None
            self.assertEqual((m.level, m.contract), ("hangar", ""))
            self.assertEqual(_read_ledger_events(root, "mx_session_opened")[0].get("mode"), "mx")

    def test_safe_mode_without_a_contract_is_refused(self) -> None:
        import io
        from unittest.mock import patch

        from rich.console import Console

        from gzkit.commands.mx_cmd import mx_enter_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            buffer = io.StringIO()
            console = Console(file=buffer, width=200, color_system=None)
            with (
                patch("gzkit.commands.mx_cmd.console", console),
                self.assertRaises(SystemExit) as ctx,
            ):
                mx_enter_cmd(
                    reason="harbor pilotage",
                    attestor="g0",
                    inspection_scope=[],
                    project_root=root,
                    mode="safe",
                )
            self.assertEqual(ctx.exception.code, 1)
            # The refusal names the missing contract, not a file that could not be read.
            self.assertIn("requires --contract", buffer.getvalue())
            self.assertNotIn("not a readable file", buffer.getvalue())
            self.assertFalse(marker.is_active(root))
            self.assertEqual(_read_ledger_events(root, "mx_session_opened"), [])

    def test_safe_mode_with_a_missing_contract_file_is_refused(self) -> None:
        from gzkit.commands.mx_cmd import mx_enter_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            with self.assertRaises(SystemExit) as ctx:
                mx_enter_cmd(
                    reason="harbor pilotage",
                    attestor="g0",
                    inspection_scope=[],
                    project_root=root,
                    mode="safe",
                    contract="docs/governance/absent.md",
                )
            self.assertEqual(ctx.exception.code, 1)
            self.assertFalse(marker.is_active(root))

    def test_a_contract_under_the_hangar_mode_is_refused(self) -> None:
        from gzkit.commands.mx_cmd import mx_enter_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            contract = self._contract(root)
            with self.assertRaises(SystemExit) as ctx:
                mx_enter_cmd(
                    reason="repair",
                    attestor="g0",
                    inspection_scope=[],
                    project_root=root,
                    contract=contract,
                )
            self.assertEqual(ctx.exception.code, 1)
            self.assertFalse(marker.is_active(root))

    def test_an_unknown_mode_is_refused(self) -> None:
        from gzkit.commands.mx_cmd import mx_enter_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            # A valid contract rides along, so the refusal can only come from the mode guard.
            contract = self._contract(root)
            with self.assertRaises(SystemExit) as ctx:
                mx_enter_cmd(
                    reason="x",
                    attestor="g0",
                    inspection_scope=[],
                    project_root=root,
                    mode="lenient",
                    contract=contract,
                )
            self.assertEqual(ctx.exception.code, 1)
            self.assertFalse(marker.is_active(root))

    def test_a_contract_outside_the_project_is_refused(self) -> None:
        from gzkit.commands.mx_cmd import mx_enter_cmd

        with TemporaryDirectory() as tmp, TemporaryDirectory() as elsewhere:
            root = _mk_root(tmp)
            outside = Path(elsewhere) / "contract.md"
            outside.write_text("# elsewhere\n", encoding="utf-8")
            with self.assertRaises(SystemExit) as ctx:
                mx_enter_cmd(
                    reason="x",
                    attestor="g0",
                    inspection_scope=[],
                    project_root=root,
                    mode="safe",
                    contract=str(outside),
                )
            self.assertEqual(ctx.exception.code, 1)
            self.assertFalse(marker.is_active(root))


class TestMxEnterCliOutputForm(unittest.TestCase):
    """The parser carries ``--mode`` and ``--contract``, and the verb says which mode opened."""

    # output-contract: the opened-mode line and the help example are the operator-facing rendering.

    def test_the_verb_opens_safe_mode_through_its_flags(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            root = Path.cwd()
            (root / ".gzkit").mkdir()
            contract = root / "docs" / "governance" / "pilotage.md"
            contract.parent.mkdir(parents=True)
            contract.write_text("# contract\n", encoding="utf-8")
            for flags in (["--level", "drydock"], ["--mode", "safe"]):
                with self.subTest(flags=flags):
                    result = runner.invoke(
                        main,
                        [
                            "mx",
                            "enter",
                            *flags,
                            "--contract",
                            "docs/governance/pilotage.md",
                            "--reason",
                            "harbor pilotage",
                            "--attestor",
                            "g0",
                        ],
                    )
                    self.assertEqual(result.exit_code, 0, result.output)
                    opened = marker.read(root)
                    self.assertIsNotNone(opened)
                    assert opened is not None
                    self.assertEqual(
                        (opened.level, opened.contract),
                        ("drydock", "docs/governance/pilotage.md"),
                    )
                    self.assertIn("Safe mode opened", result.output)
                    self.assertIn("contract=docs/governance/pilotage.md", result.output)
                    marker.marker_path(root).unlink()
                    lock_manager.delete_lock(root, marker.SESSION_LOCK_KEY)

    def test_the_help_shows_the_safe_mode_example(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["mx", "enter", "--help"])
            self.assertIn("--level drydock --contract", " ".join(result.output.split()))
            # Safe mode is the sole term (operator ruling 2026-10-16).
            self.assertNotIn("martial", result.output.lower())

    def test_safe_mode_is_the_sole_term_on_the_mode_fields(self) -> None:
        """Operator ruling 2026-10-16, verbatim "safe mode is the sole term, update the
        canon": the marker's ``level`` and the event's ``mode`` descriptions name safe mode
        and no other regime."""
        from gzkit.events import MxSessionOpenedEvent

        for model, field in ((marker.Marker, "level"), (MxSessionOpenedEvent, "mode")):
            with self.subTest(model=model.__name__):
                description = (model.model_fields[field].description or "").lower()
                self.assertIn("safe mode", description)
                self.assertNotIn("martial", description)
