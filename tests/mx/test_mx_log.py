"""Unit tests for the auto-assembled MX log (OBPI-0.0.74-06).

REQ-0.0.74-06-01 / 06-02 / 06-03 are BEHAVIOR REQs proven by the
``@covers``-decorated methods below.
REQ-0.0.74-06-04 is a [support] REQ — the ``mx_session_opened`` /
``mx_session_closed`` typed event classes exist and round-trip through the
discriminated-union parser; proven here AND by ``gz validate --ledger`` exit 0
+ an ``artifact_edited`` ledger event for ``src/gzkit/events.py`` at Stage 3.
"""

import json
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.events import EntryBookedEvent
from gzkit.ledger import Ledger, ledger_row
from gzkit.mx import log, marker
from gzkit.mx.entries import EntryError
from gzkit.traceability import covers
from tests.commands.common import SilencedConsoleTestCase, _isolated_git_env


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


def _session_row(kind: str, ts: str, session_id: str) -> dict:
    """A session's open or close row, as the typed ledger reader admits it."""
    return {
        "schema": "gzkit.ledger.v1",
        "event": kind,
        "id": session_id,
        "ts": ts,
        "session_id": session_id,
    }


def _book_entry(root: Path, entry_id: str, session_id: str) -> None:
    """Seat one maintenance-record entry, as the performer's writer books it (RP-12 ruling 8)."""
    entry = EntryBookedEvent.model_validate(
        {
            "event": "entry_booked",
            "id": entry_id,
            "entry_id": entry_id,
            "order": "ORD-01-import",
            "work_package": "WP-01-stamp",
            "dispatch_id": "D-0000000000000000",
            "description": "The stamp generator imports its template again.",
            "before": "tests.test_stamp fails",
            "after": "tests.test_stamp passes",
            "witness": "uv run -m unittest tests.test_stamp",
            "mx_session_id": session_id,
        }
    )
    Ledger(root / ".gzkit" / "ledger.jsonl").append(ledger_row(entry))


def _init_git_repo(root: Path) -> None:
    """Initialise a real git repo so window assembly can read commits."""
    subprocess.run(["git", "init", "-q"], cwd=root, check=True, env=_isolated_git_env())
    subprocess.run(
        ["git", "config", "user.email", "t@e.st"], cwd=root, check=True, env=_isolated_git_env()
    )
    subprocess.run(
        ["git", "config", "user.name", "tester"], cwd=root, check=True, env=_isolated_git_env()
    )


def _commit(root: Path, filename: str, message: str) -> None:
    (root / filename).write_text("x", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, env=_isolated_git_env())
    subprocess.run(  # noqa: S603 — git argv this test builds
        ["git", "commit", "-q", "-m", message], cwd=root, check=True, env=_isolated_git_env()
    )


# ---------------------------------------------------------------------------
# REQ-06-04 [support]: typed event classes carry the session window.
# ---------------------------------------------------------------------------
class TestMxSessionEventTypes(unittest.TestCase):
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
        assert isinstance(parsed, MxSessionOpenedEvent)
        # The window anchor (ts) and the binding key survive the round-trip.
        self.assertEqual(parsed.session_id, "sid-1")
        self.assertEqual(parsed.inspection_scope, ["ADR-0.0.74"])
        self.assertTrue(parsed.ts)  # enter anchor present

    def test_closed_event_roundtrips_through_typed_parser(self) -> None:
        from gzkit.events import MxSessionClosedEvent, parse_typed_event

        ev = MxSessionClosedEvent(
            event="mx_session_closed", id="sid-1", session_id="sid-1", attestor="g0"
        )
        parsed = parse_typed_event(json.loads(ev.model_dump_json()))
        self.assertIsInstance(parsed, MxSessionClosedEvent)
        assert isinstance(parsed, MxSessionClosedEvent)
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
class TestReopenedSessionWindow(unittest.TestCase):
    """GHI #1273: the harness's session id survives a close, so the log reads the last span."""

    def test_a_reopened_session_is_open_from_its_reopening(self) -> None:
        spans = (
            ("mx_session_opened", "2026-10-01T00:00:00+00:00"),
            ("mx_session_closed", "2026-10-02T00:00:00+00:00"),
            ("mx_session_opened", "2026-10-03T00:00:00+00:00"),
        )
        events = [_session_row(kind, ts, "s") for kind, ts in spans]
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_ledger(root, events)
            window = log.assemble_window(root, "s")
        self.assertEqual(window.opened_at, spans[2][1])
        self.assertIsNone(window.closed_at)

    def test_a_reopened_session_closed_again_reads_its_last_close(self) -> None:
        last = "2026-10-04T00:00:00+00:00"
        spans = (
            ("mx_session_opened", "2026-10-01T00:00:00+00:00"),
            ("mx_session_closed", "2026-10-02T00:00:00+00:00"),
            ("mx_session_opened", "2026-10-03T00:00:00+00:00"),
            ("mx_session_closed", last),
        )
        events = [_session_row(kind, ts, "s") for kind, ts in spans]
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_ledger(root, events)
            window = log.assemble_window(root, "s")
        self.assertEqual((window.opened_at, window.closed_at), (spans[2][1], last))


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


# ---------------------------------------------------------------------------
# RP-12 O4 task 4: the MX log is the maintenance record's view at exit
# (docs/governance/harbor-ro12-contractor-kit.md rulings 166, 170, 189 to 191).
# ---------------------------------------------------------------------------
def _record_window(tmp: str, subjects: list[str]) -> Path:
    """Open session ``s``, book one entry under it and one under another, land *subjects*."""
    root = _mk_root(tmp)
    _init_git_repo(root)
    _write_ledger(root, [_session_row("mx_session_opened", "1970-01-01T00:00:00+00:00", "s")])
    _book_entry(root, "ENT-01-stamp-import", "s")
    _book_entry(root, "ENT-02-other-session", "elsewhere")
    for n, subject in enumerate(subjects):
        _commit(root, f"f{n}.txt", subject)
    return root


def _seat_unreadable_entry(root: Path) -> None:
    """Seat an `entry_booked` row its event's shape does not admit (ruling 190)."""
    row = _session_row("entry_booked", "2026-11-21T00:00:00+00:00", "ENT-03-x")
    with (root / ".gzkit" / "ledger.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


class TestTheLogIsTheRecordsView(unittest.TestCase):
    @covers("REQ-0.0.74-06-02")
    def test_each_session_entry_is_joined_to_its_commits_and_the_rest_named_unrecorded(
        self,
    ) -> None:
        landing, sync = "fix(stamp): imports again (ENT-01-stamp-import)", "chore: sync"
        with TemporaryDirectory() as tmp:
            window = log.assemble_window(_record_window(tmp, [landing, sync]), "s")
        self.assertEqual([view.entry.entry_id for view in window.entries], ["ENT-01-stamp-import"])
        self.assertEqual(
            {k: [c.subject for c in v] for k, v in window.landed.items()},
            {"ENT-01-stamp-import": [landing]},
        )
        self.assertEqual([(u.commit.subject, u.unheld) for u in window.unrecorded], [(sync, [])])
        self.assertEqual(len(window.fixes), 2)

    @covers("REQ-0.0.74-06-02")
    def test_a_commit_naming_an_entry_the_record_does_not_hold_is_unrecorded_named(
        self,
    ) -> None:
        stray = "fix(x): a mistyped id (ENT-07-ghost)"
        other = "fix(x): another session's entry (ENT-02-other-session)"
        with TemporaryDirectory() as tmp:
            window = log.assemble_window(_record_window(tmp, [stray, other]), "s")
        self.assertCountEqual(
            [(u.commit.subject, u.unheld) for u in window.unrecorded],
            [(stray, ["ENT-07-ghost"]), (other, ["ENT-02-other-session"])],
        )
        self.assertEqual(window.landed, {"ENT-01-stamp-import": []})

    def test_an_unreadable_record_is_refused_with_its_void(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _record_window(tmp, [])
            _seat_unreadable_entry(root)
            with self.assertRaises(EntryError) as raised:
                log.assemble_window(root, "s")
        self.assertIn("gz ledger correct", str(raised.exception))


class TestRecordViewRendering(unittest.TestCase):
    """The record's view at exit (rulings 166, 189 and 191)."""

    def test_entries_render_by_order_and_unrecorded_work_names_what_it_cites(self) -> None:
        # output-contract: docs/user/manpages/mx-exit.md, the record's view before the signature
        landing, stray = "fix(stamp): imports again (ENT-01-stamp-import)", "fix(x): (ENT-07-ghost)"
        with TemporaryDirectory() as tmp:
            out = log.render(log.assemble_window(_record_window(tmp, [landing, stray]), "s"))
        after = out.split("Maintenance record (1 entry):", 1)[1]
        record, unrecorded = after.split("Unrecorded work", 1)
        self.assertIn("  ORD-01-import (WP-01-stamp):", record.splitlines())
        self.assertIn("    ENT-01-stamp-import on ORD-01-import (WP-01-stamp)", record.splitlines())
        self.assertIn(landing, record)
        self.assertIn("names ENT-07-ghost, which the record does not hold", unrecorded)
        self.assertIn("Fixes (2):", unrecorded)


class TestEmptyRecordRendering(unittest.TestCase):
    """A session with no entry and no unrecorded commit says so in each section (ruling 166)."""

    def test_an_empty_record_and_no_unrecorded_work_each_read_as_none(self) -> None:
        # output-contract: docs/user/manpages/mx-exit.md, the record's view with nothing in it
        window = log.MxLog(session_id="s", opened_at="1970-01-01T00:00:00+00:00")
        lines = log.render(window).splitlines()
        record = lines.index("Maintenance record (0 entries):")
        unrecorded = lines.index("Unrecorded work (0):")
        self.assertEqual(lines[record + 1], "  (no entry booked in this session)")
        self.assertEqual(lines[unrecorded + 1], "  (none)")


class TestExitRefusesAnUnreadableRecord(SilencedConsoleTestCase):
    """Ruling 190: the operator never signs over a record that could not be read."""

    def test_exit_refuses_at_3_writes_no_close_and_releases_the_hold(self) -> None:
        from gzkit.commands.mx_cmd import mx_enter_cmd, mx_exit_cmd  # noqa: PLC0415

        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            mx_enter_cmd(
                reason="repair", attestor="g0", inspection_scope=["ADR-0.0.74"], project_root=root
            )
            _seat_unreadable_entry(root)
            with self.assertRaises(SystemExit) as exited:
                mx_exit_cmd(attestor="g0", project_root=root, _run_guards=lambda r: 0)
            held = marker.read(root)
            closes = _read_ledger_events(root, "mx_session_closed")
        self.assertEqual(exited.exception.code, 3)
        self.assertEqual(closes, [])
        assert held is not None
        self.assertFalse(held.exiting)


if __name__ == "__main__":
    unittest.main()


class TestParseArtifactsRefusesWildcards(unittest.TestCase):
    """``parse_artifacts`` names artifacts, so a wildcard must name none.

    The docstring's contract is that nothing in the window can be "forgotten
    or narrated away". Emitting a truncation of an author's wildcard is the
    inverse failure: it narrates IN an artifact the ledger never recorded,
    and a truncation is indistinguishable downstream from a real citation.
    """

    def test_a_wildcard_suffix_names_no_obpi(self) -> None:
        from gzkit.mx.log import parse_artifacts  # noqa: PLC0415

        for wildcard in ("OBPI-0.51.0-0x", "OBPI-0.0.74-1[5-9]", "OBPI-0.52.0-0{1,2,3}"):
            with self.subTest(wildcard=wildcard):
                got = parse_artifacts(f"fix(x): touches {wildcard} today")
                self.assertEqual(got["OBPI"], [], f"{wildcard} produced {got['OBPI']}")

    def test_a_real_two_digit_obpi_is_still_named(self) -> None:
        from gzkit.mx.log import parse_artifacts  # noqa: PLC0415

        got = parse_artifacts("fix(x): OBPI-0.35.0-08 and OBPI-0.1.0-10-templates")
        self.assertIn("OBPI-0.35.0-08", got["OBPI"])
        self.assertIn("OBPI-0.1.0-10", got["OBPI"])
