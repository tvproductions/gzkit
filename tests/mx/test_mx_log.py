"""Unit tests for the auto-assembled MX log (OBPI-0.0.74-06).

REQ-0.0.74-06-01 / 06-02 / 06-03 are BEHAVIOR REQs proven by the
``@covers``-decorated methods below.
REQ-0.0.74-06-04 is a [support] REQ — the ``mx_session_opened`` /
``mx_session_closed`` typed event classes exist and round-trip through the
discriminated-union parser; proven here AND by ``gz validate --ledger`` exit 0
+ an ``artifact_edited`` ledger event for ``src/gzkit/events.py`` at Stage 3.
"""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.traceability import covers
from tests.commands.common import SilencedConsoleTestCase


def _mk_root(tmp: str) -> Path:
    root = Path(tmp)
    (root / ".gzkit").mkdir(parents=True, exist_ok=True)
    return root


def _write_ledger(root: Path, events: list[dict]) -> None:
    ledger_path = root / ".gzkit" / "ledger.jsonl"
    with ledger_path.open("w", encoding="utf-8") as fh:
        for ev in events:
            fh.write(json.dumps(ev) + "\n")


def _read_ledger_events(root: Path, event_type: str) -> list[dict]:
    ledger_path = root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.exists():
        return []
    out = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        if ev.get("event") == event_type:
            out.append(ev)
    return out


def _init_git_repo(root: Path) -> None:
    """Initialise a real git repo so window assembly can read commits."""
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@e.st"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "tester"], cwd=root, check=True)


def _commit(root: Path, filename: str, message: str) -> None:
    (root / filename).write_text("x", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", message], cwd=root, check=True)


# ---------------------------------------------------------------------------
# REQ-06-04 [support]: typed event classes carry the session window.
# ---------------------------------------------------------------------------
class TestMxSessionEventTypes(unittest.TestCase):
    @covers("REQ-0.0.74-06-04")
    def test_opened_event_roundtrips_through_typed_parser(self) -> None:
        from gzkit.events import MxSessionOpenedEvent, parse_typed_event

        ev = MxSessionOpenedEvent(
            event="mx_session_opened",
            id="sid-1",
            session_id="sid-1",
            reason="repair",
            attestor="g0",
            inspection_scope=["ADR-0.0.74"],
        )
        parsed = parse_typed_event(json.loads(ev.model_dump_json()))
        self.assertIsInstance(parsed, MxSessionOpenedEvent)
        # The window anchor (ts) and the binding key survive the round-trip.
        self.assertEqual(parsed.session_id, "sid-1")
        self.assertEqual(parsed.inspection_scope, ["ADR-0.0.74"])
        self.assertTrue(parsed.ts)  # enter anchor present

    @covers("REQ-0.0.74-06-04")
    def test_closed_event_roundtrips_through_typed_parser(self) -> None:
        from gzkit.events import MxSessionClosedEvent, parse_typed_event

        ev = MxSessionClosedEvent(
            event="mx_session_closed", id="sid-1", session_id="sid-1", attestor="g0"
        )
        parsed = parse_typed_event(json.loads(ev.model_dump_json()))
        self.assertIsInstance(parsed, MxSessionClosedEvent)
        self.assertEqual(parsed.session_id, "sid-1")
        self.assertTrue(parsed.ts)  # exit anchor present


# ---------------------------------------------------------------------------
# REQ-06-02: parse_artifacts names ADRs/OBPIs/REQs from a commit message.
# ---------------------------------------------------------------------------
class TestParseArtifacts(unittest.TestCase):
    @covers("REQ-0.0.74-06-02")
    def test_parses_adr_obpi_req_from_message(self) -> None:
        from gzkit.mx.log import parse_artifacts

        got = parse_artifacts("fix: repair ADR-0.0.74 — closes REQ-06-01 (OBPI-0.0.74-06)")
        self.assertEqual(got["ADR"], ["ADR-0.0.74"])
        self.assertEqual(got["OBPI"], ["OBPI-0.0.74-06"])
        self.assertEqual(got["REQ"], ["REQ-06-01"])

    @covers("REQ-0.0.74-06-02")
    def test_dedups_and_returns_empty_lists_when_absent(self) -> None:
        from gzkit.mx.log import parse_artifacts

        got = parse_artifacts("chore: tidy whitespace")
        self.assertEqual(got, {"ADR": [], "OBPI": [], "REQ": []})


# ---------------------------------------------------------------------------
# REQ-06-01: window built only from ledger + commits between enter and exit.
# ---------------------------------------------------------------------------
class TestAssembleWindow(unittest.TestCase):
    @covers("REQ-0.0.74-06-01")
    def test_window_bounds_to_opened_event_anchor(self) -> None:
        from gzkit.mx.log import assemble_window

        root = None
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _init_git_repo(root)
            # A commit BEFORE the session opens — must be excluded.
            _commit(root, "before.txt", "pre: ADR-0.0.99 not in window")
            _write_ledger(
                root,
                [
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "mx_session_opened",
                        "id": "sid-1",
                        "ts": "2099-01-01T00:00:00+00:00",
                        "session_id": "sid-1",
                        "reason": "repair",
                        "attestor": "g0",
                        "inspection_scope": ["ADR-0.0.74"],
                    }
                ],
            )
            log = assemble_window(root, "sid-1")
            self.assertEqual(log.session_id, "sid-1")
            self.assertEqual(log.opened_at, "2099-01-01T00:00:00+00:00")
            # No close written yet — the window is still open at assembly time.
            self.assertIsNone(log.closed_at)
            # The pre-session commit's artifact must NOT appear (future anchor).
            self.assertNotIn("ADR-0.0.99", log.artifacts["ADR"])

    @covers("REQ-0.0.74-06-01")
    def test_window_includes_commits_after_open(self) -> None:
        from gzkit.mx.log import assemble_window

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _init_git_repo(root)
            _write_ledger(
                root,
                [
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "mx_session_opened",
                        "id": "sid-2",
                        "ts": "1970-01-01T00:00:00+00:00",
                        "session_id": "sid-2",
                        "reason": "repair",
                        "attestor": "g0",
                        "inspection_scope": [],
                    }
                ],
            )
            # Commit AFTER the (epoch) open anchor — must be in the window.
            _commit(root, "fix.txt", "fix: repair ADR-0.0.74 closes REQ-06-02")
            log = assemble_window(root, "sid-2")
            self.assertEqual(len(log.fixes), 1)
            self.assertIn("ADR-0.0.74", log.artifacts["ADR"])
            self.assertIn("REQ-06-02", log.artifacts["REQ"])


# ---------------------------------------------------------------------------
# REQ-06-02 (roll-up) + render.
# ---------------------------------------------------------------------------
class TestRender(unittest.TestCase):
    @covers("REQ-0.0.74-06-02")
    def test_render_names_window_and_artifacts(self) -> None:
        from gzkit.mx.log import assemble_window, render

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _init_git_repo(root)
            _write_ledger(
                root,
                [
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "mx_session_opened",
                        "id": "sid-3",
                        "ts": "1970-01-01T00:00:00+00:00",
                        "session_id": "sid-3",
                        "reason": "repair",
                        "attestor": "g0",
                        "inspection_scope": [],
                    }
                ],
            )
            _commit(root, "fix.txt", "fix: repair ADR-0.0.74 (OBPI-0.0.74-06)")
            out = render(assemble_window(root, "sid-3"))
            self.assertIn("Window:", out)
            self.assertIn("sid-3", out)
            # Assert the artifact names appear in the rolled-up "Artifacts touched:"
            # section — which is built from parse_artifacts, NOT the verbatim commit
            # subject line. Asserting against the whole output would pass even if
            # extraction were broken (the subject echoes "ADR-0.0.74"); scoping to
            # the roll-up makes the assertion bite the extraction logic.
            self.assertIn("Artifacts touched:", out)
            roll_up = out.split("Artifacts touched:", 1)[1]
            self.assertIn("ADR-0.0.74", roll_up)
            self.assertIn("OBPI-0.0.74-06", roll_up)


# ---------------------------------------------------------------------------
# REQ-06-03: at exit, the log is rendered for review BEFORE the close signature.
# ---------------------------------------------------------------------------
class TestExitRendersLogBeforeSigning(SilencedConsoleTestCase):
    @covers("REQ-0.0.74-06-03")
    def test_log_rendered_before_mx_session_closed_written(self) -> None:
        from unittest.mock import patch

        from gzkit.commands.mx_cmd import mx_enter_cmd, mx_exit_cmd

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            mx_enter_cmd(
                reason="repair", attestor="g0", inspection_scope=["ADR-0.0.74"], project_root=root
            )

            closed_count_at_render: list[int] = []

            def spy(r: Path, sid: str) -> str:
                # At render time, NO mx_session_closed event may exist yet — the
                # log is reviewed BEFORE the signature is taken (REQ-06-03).
                closed_count_at_render.append(len(_read_ledger_events(r, "mx_session_closed")))
                return "<<assembled MX log>>"

            # Patch the assembler the exit handler calls (mx_cmd holds a reference
            # to the same gzkit.mx.log module object).
            with patch("gzkit.mx.log.assemble_and_render", spy):
                mx_exit_cmd(attestor="g0", project_root=root, _run_guards=lambda r: 0)

            # Render ran exactly once, and the close event did not exist at that moment.
            self.assertEqual(closed_count_at_render, [0])
            # The close event exists AFTER exit completes (signature taken after review).
            self.assertEqual(len(_read_ledger_events(root, "mx_session_closed")), 1)


if __name__ == "__main__":
    unittest.main()
