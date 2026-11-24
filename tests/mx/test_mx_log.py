"""Unit tests for the auto-assembled MX log (OBPI-0.0.74-06).

REQ-0.0.74-06-01 / 06-02 / 06-03 are BEHAVIOR REQs proven by the
``@covers``-decorated methods below.
REQ-0.0.74-06-04 is a [support] REQ — the ``mx_session_opened`` /
``mx_session_closed`` typed event classes exist and round-trip through the
discriminated-union parser; proven here AND by ``gz validate --ledger`` exit 0
+ an ``artifact_edited`` ledger event for ``src/gzkit/events.py`` at Stage 3.
"""

import json
import os
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any
from unittest.mock import patch

from gzkit.commands.common import console
from gzkit.commands.mx_cmd import mx_enter_cmd, mx_exit_cmd
from gzkit.events import EntryBookedEvent
from gzkit.ledger import Ledger, ledger_row
from gzkit.mx import log, marker
from gzkit.mx.entries import EntryError
from gzkit.mx.git_commits import CommitsUnreadableError, git_log
from gzkit.traceability import covers
from tests.commands.common import SilencedConsoleTestCase, _isolated_git_env
from tests.commands.test_mx_exit import _answer

if TYPE_CHECKING:
    from collections.abc import Callable
    from contextlib import AbstractContextManager


def _mk_root(tmp: str) -> Path:
    root = Path(tmp)
    (root / ".gzkit").mkdir(parents=True, exist_ok=True)
    return root


def _write_ledger(root: Path, events: list[dict[str, Any]]) -> None:
    ledger_path = root / ".gzkit" / "ledger.jsonl"
    with ledger_path.open("w", encoding="utf-8") as fh:
        for ev in events:
            fh.write(json.dumps(ev) + "\n")


def _read_ledger_events(root: Path, event_type: str) -> list[dict[str, Any]]:
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
        if isinstance(ev, dict) and ev.get("event") == event_type:
            out.append(ev)
    return out


def _session_row(kind: str, ts: str, session_id: str) -> dict[str, Any]:
    """A session's open or close row, as the typed ledger reader admits it."""
    return {
        "schema": "gzkit.ledger.v1",
        "event": kind,
        "id": session_id,
        "ts": ts,
        "session_id": session_id,
    }


def _book_entry(
    root: Path,
    entry_id: str,
    session_id: str,
    *,
    order: str = "ORD-01-import",
    ts: str | None = None,
) -> None:
    """Seat one maintenance-record entry, as the performer's writer books it (RP-12 ruling 8)."""
    entry = EntryBookedEvent.model_validate(
        {
            "event": "entry_booked",
            "id": entry_id,
            **({"ts": ts} if ts not in {None, ""} else {}),
            "entry_id": entry_id,
            "order": order,
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
        [
            "git",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-q",
            "--allow-empty-message",
            "-m",
            message,
        ],
        cwd=root,
        check=True,
        env=_isolated_git_env(),
    )


def _raised(act: Callable[[], object]) -> Exception | None:
    """Run *act* and return what it raised, so a crash fails an assertion (RP-12 ruling 156)."""
    try:
        act()
    except Exception as exc:  # a crash in place of the behaviour must fail, not error
        return exc
    return None


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

    def test_a_commit_naming_a_held_and_an_unheld_entry_shows_in_both_places(self) -> None:
        mixed = "fix(stamp): two acts (ENT-01-stamp-import, ENT-09-typo)"
        with TemporaryDirectory() as tmp:
            window = log.assemble_window(_record_window(tmp, [mixed]), "s")
        self.assertEqual([c.subject for c in window.landed["ENT-01-stamp-import"]], [mixed])
        self.assertEqual(
            [(u.commit.subject, u.unheld) for u in window.unrecorded], [(mixed, ["ENT-09-typo"])]
        )

    def test_an_unreadable_record_is_refused_with_its_void(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _record_window(tmp, [])
            _seat_unreadable_entry(root)
            with self.assertRaises(EntryError) as raised:
                log.assemble_window(root, "s")
        self.assertIn("gz ledger correct", str(raised.exception))
        self.assertIn("ENT-03-x", str(raised.exception))
        self.assertIn("2026-11-21T00:00:00+00:00", str(raised.exception))

    @covers("REQ-0.0.74-06-01")
    def test_an_entry_from_an_earlier_span_of_a_reopened_id_is_outside_the_window(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_ledger(
                root,
                [
                    _session_row("mx_session_opened", "2026-10-01T00:00:00+00:00", "s"),
                    _session_row("mx_session_closed", "2026-10-02T00:00:00+00:00", "s"),
                    _session_row("mx_session_opened", "2026-10-03T00:00:00+00:00", "s"),
                ],
            )
            _book_entry(root, "ENT-01-earlier", "s", ts="2026-10-01T12:00:00+00:00")
            _book_entry(root, "ENT-02-current", "s", ts="2026-10-03T12:00:00+00:00")
            window = log.assemble_window(root, "s")
        self.assertEqual([view.entry.entry_id for view in window.entries], ["ENT-02-current"])

    def test_a_wrapped_subject_names_its_entry_as_git_reads_the_subject(self) -> None:
        wrapped = (
            "fix(stamp): the template generator imports its template\nagain (ENT-01-stamp-import)"
        )
        with TemporaryDirectory() as tmp:
            window = log.assemble_window(_record_window(tmp, [wrapped]), "s")
        self.assertEqual(
            [c.subject for c in window.landed["ENT-01-stamp-import"]],
            ["fix(stamp): the template generator imports its template again (ENT-01-stamp-import)"],
        )
        self.assertEqual(window.unrecorded, [])

    def test_an_entry_named_in_the_body_alone_is_not_landed(self) -> None:
        in_body = "fix(stamp): imports again\n\nLands ENT-01-stamp-import."
        with TemporaryDirectory() as tmp:
            window = log.assemble_window(_record_window(tmp, [in_body]), "s")
        self.assertEqual(window.landed, {"ENT-01-stamp-import": []})
        self.assertEqual(
            [u.commit.subject for u in window.unrecorded], ["fix(stamp): imports again"]
        )


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
        self.assertIn("names ENT-07-ghost, which this session's record does not hold", unrecorded)
        self.assertIn("Fixes (2):", unrecorded)

    def test_entries_of_two_orders_render_under_each_order_once(self) -> None:
        # output-contract: docs/user/manpages/mx-exit.md, the record by order (ruling 191)
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_ledger(
                root, [_session_row("mx_session_opened", "1970-01-01T00:00:00+00:00", "s")]
            )
            _book_entry(root, "ENT-01-first", "s")
            _book_entry(root, "ENT-02-second", "s", order="ORD-02-other")
            _book_entry(root, "ENT-03-third", "s")
            lines = log.render(log.assemble_window(root, "s")).splitlines()
        headers = [line for line in lines if line.startswith("  ORD-")]
        ids = [line.split()[0] for line in lines if line.startswith("    ENT-")]
        self.assertEqual(
            headers, ["  ORD-01-import (WP-01-stamp):", "  ORD-02-other (WP-01-stamp):"]
        )
        self.assertEqual(ids, ["ENT-01-first", "ENT-03-third", "ENT-02-second"])


class TestUnreadableGit(unittest.TestCase):
    """Ruling 193: a git that cannot be read is named, never read as no commit."""

    def test_the_log_names_why_the_commits_could_not_be_read(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_ledger(
                root, [_session_row("mx_session_opened", "1970-01-01T00:00:00+00:00", "s")]
            )
            _book_entry(root, "ENT-01-stamp-import", "s")
            with _no_repository_above(tmp):
                window = log.assemble_window(root, "s")
                with self.assertRaises(CommitsUnreadableError) as raised:
                    log.assemble_and_render(root, "s")
        assert window.commits_unread is not None
        self.assertIn("`git log` exited", window.commits_unread)
        self.assertEqual(str(raised.exception), window.commits_unread)
        self.assertEqual((window.fixes, window.unrecorded), ([], []))


def _no_repository_above(tmp: str) -> AbstractContextManager[object]:
    """Hold git's search for a repository to *tmp*, so one above the temp dir is never read."""
    return patch.dict(os.environ, {"GIT_CEILING_DIRECTORIES": str(Path(tmp).resolve().parent)})


class TestGitReader(unittest.TestCase):
    """The one git reader both views call (rulings 192 and 193)."""

    def test_a_commit_with_an_empty_message_reads_as_an_empty_subject(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _init_git_repo(root)
            _commit(root, "f.txt", "")
            records = git_log(root, [], ("%s", "%B"))
        self.assertEqual([fields[1:] for fields in records], [["", ""]])

    def test_a_message_carrying_a_separator_is_refused_never_misread(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _init_git_repo(root)
            _commit(root, "f.txt", "fix: a subject\n\na body with a \x1e record separator")
            with self.assertRaises(CommitsUnreadableError) as raised:
                git_log(root, [], ("%s", "%B"))
        self.assertIn("did not parse", str(raised.exception))

    def test_a_repository_with_no_commit_yet_cannot_be_read(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _init_git_repo(root)
            with self.assertRaises(CommitsUnreadableError) as raised:
                git_log(root, [], ("%s",))
        self.assertIn("`git log` exited", str(raised.exception))

    @covers("REQ-0.0.74-06-01")
    def test_a_session_never_opened_reads_no_commit(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _init_git_repo(root)
            _commit(root, "f.txt", "fix: a commit outside any window")
            _write_ledger(root, [])
            _book_entry(root, "ENT-01-stamp-import", "never-opened")
            window = log.assemble_window(root, "never-opened")
        self.assertEqual((window.fixes, window.commits_unread, window.entries), ([], None, []))


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


class TestParseArtifactsRefusesWildcards(unittest.TestCase):
    """``parse_artifacts`` names artifacts, so a wildcard must name none.

    The docstring's contract is that nothing in the window can be "forgotten
    or narrated away". Emitting a truncation of an author's wildcard is the
    inverse failure: it narrates IN an artifact the ledger never recorded,
    and a truncation is indistinguishable downstream from a real citation.
    """

    def test_a_wildcard_suffix_names_no_obpi(self) -> None:
        for wildcard in ("OBPI-0.51.0-0x", "OBPI-0.0.74-1[5-9]", "OBPI-0.52.0-0{1,2,3}"):
            with self.subTest(wildcard=wildcard):
                got = log.parse_artifacts(f"fix(x): touches {wildcard} today")
                self.assertEqual(got["OBPI"], [], f"{wildcard} produced {got['OBPI']}")

    def test_a_real_two_digit_obpi_is_still_named(self) -> None:
        got = log.parse_artifacts("fix(x): OBPI-0.35.0-08 and OBPI-0.1.0-10-templates")
        self.assertIn("OBPI-0.35.0-08", got["OBPI"])
        self.assertIn("OBPI-0.1.0-10", got["OBPI"])


class TestExitRefusesWhatItCannotRead(unittest.TestCase):
    """Rulings 190 and 193: the operator never signs over a record or commits it could not read."""

    def _exit(self, root: Path) -> tuple[int | str | None, str]:
        # Ruling 156: the refusal's code is read; an error escaping in its place fails by
        # assertion, never as a test error.
        with console.capture() as captured:
            code = _answer(
                self, lambda: mx_exit_cmd(attestor="g0", project_root=root, _run_guards=lambda r: 0)
            )
        return code, " ".join(captured.get().split())

    def _assert_held_open(self, root: Path) -> None:
        held = marker.read(root)
        assert held is not None
        self.assertFalse(held.exiting)
        self.assertEqual(_read_ledger_events(root, "mx_session_closed"), [])

    def test_an_unreadable_record_refuses_at_3_naming_its_row_and_void(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _init_git_repo(root)
            _commit(root, "seed.txt", "chore: seed")
            mx_enter_cmd(
                reason="repair", attestor="g0", inspection_scope=["ADR-0.0.74"], project_root=root
            )
            _seat_unreadable_entry(root)
            code, printed = self._exit(root)
            self._assert_held_open(root)
        self.assertEqual(code, 3)
        self.assertIn("ENT-03-x", printed)
        self.assertIn("gz ledger correct", printed)
        self.assertIn("2026-11-21T00:00:00+00:00", printed)
        # output-contract: docs/user/manpages/mx-exit.md, the refusal names its cause, the
        # maintenance record (ruling 190), never the window's commits (ruling 193; ruling
        # 97). The EntryError text names the record too, so the verb's own line is pinned.
        self.assertIn("The maintenance record cannot be read. MX session remains open.", printed)
        self.assertNotIn("window's commits", printed)

    def test_the_log_prints_brackets_as_written_never_as_markup(self) -> None:
        # output-contract: docs/user/manpages/mx-exit.md, the log printed as plain text
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _init_git_repo(root)
            _commit(root, "seed.txt", "chore: seed")
            mx_enter_cmd(
                reason="repair", attestor="g0", inspection_scope=["ADR-0.0.74"], project_root=root
            )
            subject = "fix(ci): keep the [skip ci] tag, the [/tmp] path and :fire: as written " + (
                "and a subject long enough that no console would leave it on one line " * 3
            )
            _commit(root, "fix.txt", subject.strip())
            with console.capture() as captured:
                code = _answer(
                    self,
                    lambda: mx_exit_cmd(attestor="g0", project_root=root, _run_guards=lambda r: 0),
                )
        self.assertEqual(code, 0)
        self.assertIn(subject.strip(), captured.get())

    def test_a_git_it_cannot_read_refuses_at_3_naming_the_cause(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            mx_enter_cmd(
                reason="repair", attestor="g0", inspection_scope=["ADR-0.0.74"], project_root=root
            )
            with _no_repository_above(tmp):
                code, printed = self._exit(root)
            self._assert_held_open(root)
        self.assertEqual(code, 3)
        self.assertIn("`git log` exited", printed)
        self.assertIn("window's commits cannot be read", printed)

    def test_a_ledger_it_cannot_read_refuses_at_3_and_signs_nothing(self) -> None:
        # Ruling 204: the ledger is the exit's evidence; an unread one is never an empty window.
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _init_git_repo(root)
            _commit(root, "seed.txt", "chore: seed")
            mx_enter_cmd(
                reason="repair", attestor="g0", inspection_scope=["ADR-0.0.74"], project_root=root
            )
            ledger_path = root / ".gzkit" / "ledger.jsonl"
            ledger_path.unlink()
            code, printed = self._exit(root)
            held = marker.read(root)
            ledger_written = ledger_path.exists()
        self.assertEqual(code, 3)
        assert held is not None
        self.assertFalse(held.exiting)
        self.assertFalse(ledger_written, "the refusal booked a close over an unread ledger")
        self.assertIn(".gzkit/ledger.jsonl", printed)
        self.assertIn("ledger cannot be read", printed)

    def test_a_ledger_row_that_does_not_parse_refuses_at_3_and_signs_nothing(self) -> None:
        # Ruling 204: a row the ledger's reader cannot decode is a ledger the exit cannot
        # read, refused as rulings 190 and 193 refuse, never a crash past green guards.
        for row in ("not json at all", "[1, 2]", '{"schema": "gzkit.ledger.v1"}'):
            with self.subTest(row=row), TemporaryDirectory() as tmp:
                root = _mk_root(tmp)
                _init_git_repo(root)
                _commit(root, "seed.txt", "chore: seed")
                mx_enter_cmd(
                    reason="repair",
                    attestor="g0",
                    inspection_scope=["ADR-0.0.74"],
                    project_root=root,
                )
                with (root / ".gzkit" / "ledger.jsonl").open("a", encoding="utf-8") as fh:
                    fh.write(row + "\n")
                code, printed = self._exit(root)
                self._assert_held_open(root)
                self.assertEqual(code, 3, printed)
                self.assertIn("ledger cannot be read", printed)


# ---------------------------------------------------------------------------
# RP-12 O4's dock trial (ruling 27): the triage's test gaps and crash rows.
# ---------------------------------------------------------------------------
def _row(kind: str, ts: str, session_id: str = "s", **fields: str) -> dict[str, Any]:
    """A session-scoped ledger row, as the session's verbs book it."""
    return {**_session_row(kind, ts, session_id), **fields}


class TestParseArtifactsNamesEachIdOnce(unittest.TestCase):
    @covers("REQ-0.0.74-06-02")
    def test_an_id_named_twice_is_named_once(self) -> None:
        # REQ-0.0.74-06-02 and parse_artifacts' contract: "the unique ids of that kind found".
        got = log.parse_artifacts(
            "fix: ADR-0.0.74 again ADR-0.0.74 (OBPI-0.0.74-06, OBPI-0.0.74-06) REQ-06-01 REQ-06-01"
        )
        self.assertEqual(
            got, {"ADR": ["ADR-0.0.74"], "OBPI": ["OBPI-0.0.74-06"], "REQ": ["REQ-06-01"]}
        )


class TestTheWindowIsTheSessionsOwn(unittest.TestCase):
    """REQ-0.0.74-06-01: the window is bounded by this session's open and matching close."""

    @covers("REQ-0.0.74-06-01")
    def test_a_commit_after_the_close_is_outside_the_window(self) -> None:
        # REQ-0.0.74-06-01: the matching mx_session_closed bounds the window when present.
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _init_git_repo(root)
            _write_ledger(
                root,
                [
                    _row("mx_session_opened", "1970-01-01T00:00:00+00:00"),
                    _row("mx_session_closed", "2000-01-01T00:00:00+00:00"),
                ],
            )
            _commit(root, "f.txt", "fix: landed after the close ADR-0.0.99")
            window = log.assemble_window(root, "s")
        self.assertEqual(window.fixes, [])

    @covers("REQ-0.0.74-06-01")
    def test_another_sessions_open_and_close_do_not_bound_this_window(self) -> None:
        # REQ-0.0.74-06-01: the window is this session's open and "the matching" close.
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_ledger(
                root,
                [
                    _row("mx_session_opened", "2026-10-01T00:00:00+00:00", reason="mine"),
                    _row("mx_session_opened", "2026-10-02T00:00:00+00:00", "t", reason="theirs"),
                    _row("mx_session_closed", "2026-10-03T00:00:00+00:00", "t"),
                ],
            )
            window = log.assemble_window(root, "s")
        self.assertEqual(
            (window.opened_at, window.closed_at, window.reason),
            ("2026-10-01T00:00:00+00:00", None, "mine"),
        )

    @covers("REQ-0.0.74-06-01")
    def test_a_lease_renewal_leaves_the_window_open(self) -> None:
        # REQ-0.0.74-06-01 and ruling 166: only the matching close ends the window; a renewal
        # carries the session's id (mx-mode rule § The lease) and closes nothing.
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_ledger(
                root,
                [
                    _row("mx_session_opened", "2026-10-01T00:00:00+00:00"),
                    _row("mx_session_lease_renewed", "2026-10-02T00:00:00+00:00"),
                ],
            )
            window = log.assemble_window(root, "s")
        self.assertIsNone(window.closed_at)

    @covers("REQ-0.0.74-06-01")
    def test_the_ledger_events_counted_are_those_inside_the_window(self) -> None:
        # docs/user/manpages/mx-exit.md § Fixes: "the count of ledger events in the window".
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_ledger(
                root,
                [
                    _row("mx_session_lease_expired", "2026-09-01T00:00:00+00:00", "x"),
                    _row("mx_session_opened", "2026-10-01T00:00:00+00:00"),
                    _row("mx_session_lease_renewed", "2026-10-02T00:00:00+00:00"),
                    _row("mx_session_closed", "2026-10-03T00:00:00+00:00"),
                    _row("mx_session_lease_expired", "2026-10-04T00:00:00+00:00", "y"),
                ],
            )
            window = log.assemble_window(root, "s")
        self.assertEqual(
            window.ledger_event_types,
            ["mx_session_opened", "mx_session_lease_renewed", "mx_session_closed"],
        )


class TestTheAssemblyAnswers(unittest.TestCase):
    """Ruling 156's form: a call that should answer is run through `_raised`."""

    @covers("REQ-0.0.74-06-01")
    def test_an_open_window_over_a_readable_git_answers_with_its_commits(self) -> None:
        # REQ-0.0.74-06-01: an open window reads every commit since its open.
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _init_git_repo(root)
            _write_ledger(root, [_row("mx_session_opened", "1970-01-01T00:00:00+00:00")])
            _commit(root, "f.txt", "fix: one")
            held: list[log.MxLog] = []
            raised = _raised(lambda: held.append(log.assemble_window(root, "s")))
        self.assertIsNone(raised)
        self.assertEqual([fix.subject for fix in held[0].fixes], ["fix: one"])

    def test_a_git_it_cannot_read_answers_with_the_cause(self) -> None:
        # Ruling 193 and assemble_window's contract: a git that cannot be read names its cause
        # in `commits_unread`, leaving no commit.
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _write_ledger(root, [_row("mx_session_opened", "1970-01-01T00:00:00+00:00")])
            held: list[log.MxLog] = []
            with _no_repository_above(tmp):
                raised = _raised(lambda: held.append(log.assemble_window(root, "s")))
        self.assertIsNone(raised)
        self.assertIn("`git log` exited", held[0].commits_unread or "")
        self.assertEqual(held[0].fixes, [])

    @covers("REQ-0.0.74-06-03")
    def test_the_entry_point_renders_a_readable_window(self) -> None:
        # REQ-0.0.74-06-03 and assemble_and_render's contract: it returns the rendered log
        # for review, refusing only a git it could not read (ruling 193).
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _init_git_repo(root)
            _write_ledger(root, [_row("mx_session_opened", "1970-01-01T00:00:00+00:00")])
            _commit(root, "f.txt", "fix: one")
            held: list[str] = []
            raised = _raised(lambda: held.append(log.assemble_and_render(root, "s")))
        self.assertIsNone(raised)
        self.assertIn("fix: one", held[0])


class TestRecordViewLinesRendering(unittest.TestCase):
    """docs/user/manpages/mx-exit.md, the record's view: each section's lines (ruling 166)."""

    def test_a_record_with_an_entry_and_one_unrecorded_commit_reads_each_line(self) -> None:
        # output-contract: docs/user/manpages/mx-exit.md, Maintenance record, Unrecorded work
        # and Fixes; "names <id>, ..." only for an unheld id (ruling 189).
        landing, sync = "fix(stamp): imports again (ENT-01-stamp-import)", "chore: sync"
        with TemporaryDirectory() as tmp:
            window = log.assemble_window(_record_window(tmp, [landing, sync]), "s")
        lines = log.render(window).splitlines()
        sha = {fix.subject: fix.commit_sha[:12] for fix in window.fixes}
        self.assertNotIn("  (no entry booked in this session)", lines)
        self.assertIn("Unrecorded work (1):", lines)
        unrecorded = lines.index("Unrecorded work (1):")
        self.assertEqual(lines[unrecorded + 1 : unrecorded + 3], [f"  - {sha[sync]} {sync}", ""])
        self.assertIn("Fixes (2):", lines)
        fixes = lines.index("Fixes (2):")
        self.assertCountEqual(
            lines[fixes + 1 : fixes + 3],
            [
                f"  - {sha[landing]} {landing} [(no artifacts named)]",
                f"  - {sha[sync]} {sync} [(no artifacts named)]",
            ],
        )

    def test_a_window_with_no_commit_says_so_under_fixes(self) -> None:
        # output-contract: docs/user/manpages/mx-exit.md, Fixes over a window with no commit
        lines = log.render(log.MxLog(session_id="s", opened_at="1970-01-01T00:00:00+00:00"))
        lines = lines.splitlines()
        self.assertIn("Fixes (0):", lines)
        self.assertEqual(lines[lines.index("Fixes (0):") + 1], "  (no commits in window)")

    def test_the_record_header_counts_its_entries(self) -> None:
        # output-contract: docs/user/manpages/mx-exit.md, "Maintenance record (1 entry):"
        empty = log.render(log.MxLog(session_id="s", opened_at="1970-01-01T00:00:00+00:00"))
        with TemporaryDirectory() as tmp:
            one = log.render(log.assemble_window(_record_window(tmp, []), "s"))
        self.assertIn("Maintenance record (0 entries):", empty.splitlines())
        self.assertIn("Maintenance record (1 entry):", one.splitlines())


class TestGitReaderNamesItsCause(unittest.TestCase):
    """Ruling 193 and mx-exit.md: the reader names git's cause, never a crash of its own."""

    def test_a_git_that_cannot_run_raises_the_readers_refusal(self) -> None:
        # Ruling 193: `git could not run (<error>)`, a CommitsUnreadableError both views catch.
        with TemporaryDirectory() as tmp:
            missing = Path(tmp) / "no-such-project"
            with _no_repository_above(tmp):
                raised = _raised(lambda: git_log(missing, [], ("%s",)))
        self.assertIsInstance(raised, CommitsUnreadableError)
        self.assertIn("git could not run", str(raised))

    def test_the_cause_is_gits_own_first_line(self) -> None:
        # output-contract: docs/user/manpages/mx-exit.md, `git log` exited <code>: <git's message>
        with TemporaryDirectory() as tmp:
            root = _mk_root(tmp)
            _init_git_repo(root)
            said = subprocess.run(
                ["git", "log"],
                cwd=root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
                env=_isolated_git_env(),
            )
            raised = _raised(lambda: git_log(root, [], ("%s",)))
        self.assertIsInstance(raised, CommitsUnreadableError)
        first = said.stderr.strip().splitlines()[0]
        self.assertEqual(str(raised), f"`git log` exited {said.returncode}: {first}")

    def test_a_git_that_exits_without_a_word_is_named_with_no_message(self) -> None:
        # output-contract: docs/user/manpages/mx-exit.md, `git log` exited <code>: <message>,
        # a git killed by a signal writing no stderr still refused, never a crash.
        silent = subprocess.CompletedProcess(["git"], -9, stdout="", stderr="")
        with patch("gzkit.mx.git_commits.subprocess.run", return_value=silent):
            raised = _raised(lambda: git_log(Path(), [], ("%s",)))
        self.assertIsInstance(raised, CommitsUnreadableError)
        self.assertEqual(str(raised), "`git log` exited -9: no message")


if __name__ == "__main__":
    unittest.main()
