"""``gz wp discrepancy record`` and ``clear``'s wiring: RP-12 O4 task 2, act 2.

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: the coordinator's
unstamped call records a line on its order, and a performer's stamped call records
a find in the work (rulings 9, 172, 178); the coordinator alone clears a line on its
evidence, an issue confirmed through `gh` (rulings 172, 180, 181). Every refusal of
the writers, and the reducer, is proved in `tests/test_discrepancies.py`; these held
tests prove the wiring alone: the stamp, the session and `gh` read at the CLI, the
exit codes and the epilogs (ruling 125).
"""

import json
import os
import shlex
import unittest
from pathlib import Path
from typing import Any, get_args

from gzkit.cli import main
from gzkit.cli.main import _build_parser
from gzkit.dispatch_stamp import STAMP_ID_ENV, STAMP_ROOT_ENV
from gzkit.events import DiscrepancyGrade, DiscrepancySource
from tests.commands.test_wp_entry import _EntryCase
from tests.commands.test_wp_order import _help_parser
from tests.mx.held import open_marker

_LINE = (
    *("--slug", "hook-left-off"),
    *("--grade", "due-by-event", "--due-by", "the restoration"),
    *("--description", "The stamp hook is left off."),
)


def _seat_malformed(event: str, row_id: str) -> None:
    """Append a row of *event* missing its fields, as a broken writer would leave it."""
    row = {"schema": "gzkit.ledger.v1", "event": event, "id": row_id, "ts": "2026-11-20T00:00:00"}
    with (Path(".gzkit") / "ledger.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(row) + "\n")


def _rows(event: str) -> list[dict[str, Any]]:
    text = (Path(".gzkit") / "ledger.jsonl").read_text(encoding="utf-8")
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    return [row for row in rows if row["event"] == event]


class _DiscrepancyCase(_EntryCase):
    """The entry case's commenced order and its Restoration dispatch, an MX session open."""

    def setUp(self) -> None:
        super().setUp()
        open_marker(Path.cwd())

    def run_gz(self, *args: str) -> tuple[int, str]:
        result = self.runner.invoke(main, ["wp", "discrepancy", *args])
        return result.exit_code, " ".join(result.output.split())

    def unstamp(self) -> None:
        for name in (STAMP_ROOT_ENV, STAMP_ID_ENV):
            os.environ.pop(name, None)


class RecordWiringTests(_DiscrepancyCase):
    def test_the_coordinators_call_records_a_line_on_its_order(self) -> None:
        # output-contract: docs/user/manpages/wp-discrepancy-record.md, the line a record prints
        # given an open MX session and the main session's call, carrying no stamp
        # when
        code, output = self.run_gz(
            "record", "--order", "ORD-01-import", "--source", "left-broken", *_LINE
        )
        # then the line is booked on the typed order, with no performer, under the session
        self.assertEqual((code, output), (0, "Recorded DSC-01-hook-left-off on ORD-01-import."))
        self.assertEqual(
            [
                (r["discrepancy_id"], r["order"], r.get("dispatch_id"), r["mx_session_id"])
                for r in _rows("discrepancy_recorded")
            ],
            [("DSC-01-hook-left-off", "ORD-01-import", None, "test-session")],
        )

    def test_json_mode_prints_the_recorded_event(self) -> None:
        # given the coordinator's call
        # when
        code, output = self.run_gz(
            "record", "--order", "ORD-01-import", "--source", "left-broken", *_LINE, "--json"
        )
        # then the event booked, never the human line
        self.assertEqual(code, 0, output)
        printed, (booked,) = json.loads(output), _rows("discrepancy_recorded")
        self.assertEqual(
            {k: v for k, v in printed.items() if k != "ts"},
            {k: v for k, v in booked.items() if k != "ts"},
        )

    def test_a_performers_stamped_call_records_a_find_on_its_own_order(self) -> None:
        # given the call stamped with the Restoration dispatch it names
        self.stamp_as(self.dispatch)
        # when
        code, output = self.run_gz(
            "record", "--dispatch", self.dispatch, "--source", "found-in-work", *_LINE
        )
        # then the order is read from the dispatch, and the performer recorded
        self.assertEqual(code, 0, output)
        ((order, dispatch_id),) = [
            (r["order"], r["dispatch_id"]) for r in _rows("discrepancy_recorded")
        ]
        self.assertEqual((order, dispatch_id), ("ORD-01-import", self.dispatch))

    def test_a_subagents_call_with_no_dispatch_id_is_refused(self) -> None:
        # output-contract: the refusal names its cause (guardrail-feedback-prose)
        # given a subagent's call stamped with a root but no dispatch id
        os.environ[STAMP_ROOT_ENV] = Path.cwd().resolve().as_posix()
        self.addCleanup(os.environ.pop, STAMP_ROOT_ENV, None)
        # when
        code, output = self.run_gz(
            "record", "--order", "ORD-01-import", "--source", "left-broken", *_LINE
        )
        # then neither the coordinator nor a performer made it: exit 3, nothing booked
        self.assertEqual(code, 3, output)
        self.assertIn("stamped with no dispatch id", output)
        self.assertEqual(_rows("discrepancy_recorded"), [])

    def test_the_writers_refusal_exits_3_and_books_nothing(self) -> None:
        # given the coordinator's call naming no order
        # when
        code, output = self.run_gz("record", "--source", "left-broken", *_LINE)
        # then the writer's refusal is the verb's (cli.md § Exit Codes)
        self.assertEqual(code, 3, output)
        self.assertIn("--order is required", output)
        self.assertEqual(_rows("discrepancy_recorded"), [])

    def test_a_malformed_tag_row_refuses_the_record_naming_its_void(self) -> None:
        # given a tag_issued row the tag log cannot read
        _seat_malformed("tag_issued", "TAG-01-size")
        # when the coordinator's line cites a tag, so the record reads the tag log
        code, output = self.run_gz(
            *("record", "--order", "ORD-01-import", "--source", "left-broken", *_LINE),
            *("--tag", "TAG-01-size"),
        )
        # then the reader's refusal is a policy breach naming its recovery, nothing booked
        self.assertEqual(code, 3, output)
        self.assertIn("gz ledger correct", output)
        self.assertEqual(_rows("discrepancy_recorded"), [])


class ClearWiringTests(_DiscrepancyCase):
    def setUp(self) -> None:
        super().setUp()
        self.stamp_as(self.dispatch)
        self.assertEqual(self.book()[0], 0)
        self.unstamp()
        code, output = self.run_gz(
            "record", "--order", "ORD-01-import", "--source", "left-broken", *_LINE
        )
        self.assertEqual(code, 0, output)

    def test_the_coordinator_clears_a_line_on_an_entry(self) -> None:
        # output-contract: docs/user/manpages/wp-discrepancy-clear.md, the line a clear prints
        # given the line and an entry of its package
        # when
        code, output = self.run_gz(
            "clear", "DSC-01-hook-left-off", "--entry", "ENT-01-stamp-import"
        )
        # then the clear is booked, citing the entry
        self.assertEqual((code, output), (0, "Cleared DSC-01-hook-left-off on ORD-01-import."))
        self.assertEqual(
            [(r["discrepancy_id"], r["entry_id"]) for r in _rows("discrepancy_cleared")],
            [("DSC-01-hook-left-off", "ENT-01-stamp-import")],
        )

    def test_json_mode_prints_the_cleared_event_under_its_session(self) -> None:
        # given the line and an entry of its package
        # when the clear asks for JSON
        code, output = self.run_gz(
            "clear", "DSC-01-hook-left-off", "--entry", "ENT-01-stamp-import", "--json"
        )
        # then the event booked, never the human line, under the open MX session (ruling 9)
        self.assertEqual(code, 0, output)
        printed, (booked,) = json.loads(output), _rows("discrepancy_cleared")
        self.assertEqual(
            {k: v for k, v in printed.items() if k != "ts"},
            {k: v for k, v in booked.items() if k != "ts"},
        )
        recorded = _rows("discrepancy_recorded")[0]["mx_session_id"]
        self.assertEqual(booked["mx_session_id"], recorded)

    def test_a_malformed_entry_row_refuses_the_clear_naming_its_void(self) -> None:
        # given an entry_booked row the maintenance record cannot read
        _seat_malformed("entry_booked", "ENT-02-broken")
        # when the clear cites an entry, so it reads the maintenance record
        code, output = self.run_gz(
            "clear", "DSC-01-hook-left-off", "--entry", "ENT-01-stamp-import"
        )
        # then the reader's refusal is a policy breach naming its recovery, nothing booked
        self.assertEqual(code, 3, output)
        self.assertIn("gz ledger correct", output)
        self.assertEqual(_rows("discrepancy_cleared"), [])

    def test_a_subagents_call_is_refused(self) -> None:
        # given the call stamped as the dispatch's subagent
        self.stamp_as(self.dispatch)
        # when
        code, output = self.run_gz(
            "clear", "DSC-01-hook-left-off", "--entry", "ENT-01-stamp-import"
        )
        # then the coordinator alone clears: exit 3, nothing booked
        self.assertEqual(code, 3, output)
        self.assertIn("coordinator's unstamped call alone", output)
        self.assertEqual(_rows("discrepancy_cleared"), [])

    def test_an_issue_gh_cannot_read_exits_2_and_books_nothing(self) -> None:
        # given no gh on the path, so the issue cannot be read
        empty = Path("no-bin")
        empty.mkdir()
        self.addCleanup(os.environ.__setitem__, "PATH", os.environ["PATH"])
        os.environ["PATH"] = empty.resolve().as_posix()
        # when
        code, output = self.run_gz("clear", "DSC-01-hook-left-off", "--ghi", "1412")
        # then a System/IO error, never a policy breach (ruling 180; cli.md § Exit Codes)
        self.assertEqual(code, 2, output)
        self.assertIn("could not be read through `gh`", output)
        self.assertEqual(_rows("discrepancy_cleared"), [])

    def test_each_recurs_citation_reaches_the_writer(self) -> None:
        # given a citation that names nothing, repeated after one that does not either
        # when
        code, output = self.run_gz(
            "clear",
            "DSC-01-hook-left-off",
            "--entry",
            "ENT-01-stamp-import",
            *("--recurs", "2026-01-01T00:00:00+00:00", "--recurs", "#999999999"),
        )
        # then the first citation is read and refused by name, so the flag repeats onto the clear
        self.assertEqual(code, 3, output)
        self.assertIn("--recurs 2026-01-01T00:00:00+00:00 names no", output)

    def test_a_resolved_citation_with_no_threshold_registry_exits_1(self) -> None:
        # given three insight records the citations resolve, and no recurrence registry
        store = Path(".gzkit") / "insights" / "agent-insights.jsonl"
        store.parent.mkdir(parents=True, exist_ok=True)
        cites = [f"2026-0{month}-01T00:00:00+00:00" for month in (1, 2, 3)]
        store.write_text("".join(json.dumps({"ts": c}) + "\n" for c in cites), encoding="utf-8")
        registry = Path("data") / "recurrence_threshold.json"
        registry.unlink(missing_ok=True)
        # when
        code, output = self.run_gz(
            "clear",
            "DSC-01-hook-left-off",
            "--entry",
            "ENT-01-stamp-import",
            *(arg for cite in cites for arg in ("--recurs", cite)),
        )
        # then a config error names the registry, and nothing is booked (cli.md § Exit Codes)
        self.assertEqual(code, 1, output)
        self.assertIn("recurrence_threshold.json", output)
        self.assertEqual(_rows("discrepancy_cleared"), [])

    def install_gh(self, status: str, body: str, rc: int) -> None:
        """Put a stand-in `gh` on the path that answers `gh api --include` for issue 1412.

        Any other call gets no answer, so a clear that asks about the wrong issue, or
        not through the REST endpoint, reads as an outage and fails its test.
        """
        bin_dir = Path("gh-bin")
        bin_dir.mkdir()
        gh = bin_dir / "gh"
        # gh's own line endings (observed 2026-11-20): LF after the status, CRLF headers
        answer = f"HTTP/2.0 {status}\\nContent-Type: application/json\\r\\n\\r\\n{body}\\n"
        gh.write_text(
            "#!/bin/sh\n"
            'if [ "$1 $2 $3" = "api --include repos/{owner}/{repo}/issues/1412" ]; then\n'
            f"  printf '{answer}'\n"
            f"  exit {rc}\n"
            "fi\n"
            "exit 1\n",
            encoding="utf-8",
        )
        gh.chmod(0o755)
        self.addCleanup(os.environ.__setitem__, "PATH", os.environ["PATH"])
        os.environ["PATH"] = bin_dir.resolve().as_posix()

    @unittest.skipIf(os.name == "nt", "the stand-in gh is a POSIX shell script")
    def test_an_issue_gh_reads_open_clears_the_line_citing_it(self) -> None:
        # given a stand-in gh that answers issue 1412 open
        self.install_gh("200 OK", '{"number": 1412, "state": "open"}', 0)
        # when
        code, output = self.run_gz("clear", "DSC-01-hook-left-off", "--ghi", "1412")
        # then the line leaves the list as the open issue it was filed as (ruling 180)
        self.assertEqual(code, 0, output)
        self.assertEqual([r["ghi"] for r in _rows("discrepancy_cleared")], [1412])

    @unittest.skipIf(os.name == "nt", "the stand-in gh is a POSIX shell script")
    def test_a_closed_issue_is_refused_and_books_nothing(self) -> None:
        # given a stand-in gh that answers issue 1412 closed
        self.install_gh("200 OK", '{"number": 1412, "state": "closed"}', 0)
        # when
        code, output = self.run_gz("clear", "DSC-01-hook-left-off", "--ghi", "1412")
        # then a policy breach: a filed line leaves as an open problem report (ruling 180)
        self.assertEqual(code, 3, output)
        self.assertIn("#1412 is closed", output)
        self.assertEqual(_rows("discrepancy_cleared"), [])

    @unittest.skipIf(os.name == "nt", "the stand-in gh is a POSIX shell script")
    def test_an_issue_the_api_says_does_not_exist_is_refused(self) -> None:
        # given a stand-in gh whose API answers issue 1412 404 Not Found
        self.install_gh("404 Not Found", '{"message": "Not Found"}', 1)
        # when
        code, output = self.run_gz("clear", "DSC-01-hook-left-off", "--ghi", "1412")
        # then bad evidence, exit 3, never an outage to retry (ruling 182)
        self.assertEqual(code, 3, output)
        self.assertIn("#1412 does not exist", output)
        self.assertEqual(_rows("discrepancy_cleared"), [])

    def test_a_recurs_ghi_gh_cannot_answer_exits_2_and_books_nothing(self) -> None:
        # given no gh on the path at all
        empty = Path("no-gh")
        empty.mkdir()
        self.addCleanup(os.environ.__setitem__, "PATH", os.environ["PATH"])
        os.environ["PATH"] = empty.resolve().as_posix()
        # when the clear cites a GHI under --recurs
        code, output = self.run_gz(
            *("clear", "DSC-01-hook-left-off", "--entry", "ENT-01-stamp-import"),
            *("--recurs", "#1412"),
        )
        # then an outage, exit 2, never "names nothing" at 3 (ruling 182)
        self.assertEqual(code, 2, output)
        self.assertNotIn("names no", output)
        self.assertEqual(_rows("discrepancy_cleared"), [])


class ShowWiringTests(_DiscrepancyCase):
    def show(self, *args: str) -> tuple[int, str]:
        result = self.runner.invoke(main, ["wp", "discrepancy", "show", *args])
        return result.exit_code, result.output

    def record_and_clear(self) -> None:
        """Record a blocking line, book an entry and clear the line on it."""
        code, output = self.run_gz(
            "record",
            *("--order", "ORD-01-import", "--source", "left-broken", "--slug", "hook-left-off"),
            *("--grade", "blocks-return-to-service", "--description", "The hook is left off."),
        )
        self.assertEqual(code, 0, output)
        self.stamp_as(self.dispatch)
        self.assertEqual(self.book()[0], 0)
        self.unstamp()
        code, output = self.run_gz(
            "clear",
            *("DSC-01-hook-left-off", "--entry", "ENT-01-stamp-import"),
            *("--root-cause", "Disabled for the repair.", "--corrective-action", "Restored."),
        )
        self.assertEqual(code, 0, output)

    def test_with_no_line_it_says_none_is_open_or_recorded(self) -> None:
        # output-contract: docs/user/manpages/wp-discrepancy-show.md, the empty list's lines
        # given no line recorded
        # when
        shown, every = self.show(), self.show("--all")
        # then
        self.assertEqual((shown[0], shown[1].strip()), (0, "No discrepancy is open."))
        self.assertEqual((every[0], every[1].strip()), (0, "No discrepancy has been recorded."))

    def test_show_writes_each_open_line_as_a_block(self) -> None:
        # output-contract: docs/user/manpages/wp-discrepancy-show.md, an open line's block
        # given a due-by line recorded by the coordinator
        code, output = self.run_gz(
            "record", "--order", "ORD-01-import", "--source", "left-broken", *_LINE
        )
        self.assertEqual(code, 0, output)
        # when
        code, output = self.show()
        # then the line, its grade, event and recorder, and no clear
        lines = output.splitlines()
        self.assertEqual(code, 0, output)
        self.assertEqual(lines[0], "DSC-01-hook-left-off on ORD-01-import (WP-01-stamp)")
        self.assertIn("  Grade:       due-by-event", lines)
        self.assertIn("  Due by:      the restoration", lines)
        self.assertIn("  Cleared:     open", lines)
        self.assertTrue(any(line.endswith("by the coordinator") for line in lines), output)

    def test_a_cleared_line_leaves_the_default_view_and_shows_under_all(self) -> None:
        # output-contract: docs/user/manpages/wp-discrepancy-show.md, a cleared line's block
        # given a blocking line cleared on an entry
        self.record_and_clear()
        # when
        default, every = self.show(), self.show("--all")
        # then the open view is empty, and --all marks the line cleared with its evidence
        self.assertEqual(default[1].strip(), "No discrepancy is open.")
        lines = every[1].splitlines()
        self.assertEqual(lines[0], "DSC-01-hook-left-off on ORD-01-import (WP-01-stamp) (cleared)")
        self.assertTrue(any(line.endswith("on ENT-01-stamp-import") for line in lines), every[1])
        self.assertIn("  Root cause:  Disabled for the repair.", lines)
        self.assertIn("  Corrective:  Restored.", lines)

    def test_json_mode_prints_each_line_with_its_clear(self) -> None:
        # given a blocking line cleared on an entry
        self.record_and_clear()
        # when
        code, output = self.show("--all", "--json")
        # then each line is its record's fields with its clear event
        self.assertEqual(code, 0, output)
        (printed,) = json.loads(output)
        (recorded,), (cleared,) = _rows("discrepancy_recorded"), _rows("discrepancy_cleared")
        self.assertEqual({k: v for k, v in printed.items() if k != "clear"}, recorded)
        self.assertEqual(printed["clear"], cleared)


class ShowRefusalWiringTests(_DiscrepancyCase):
    def test_a_malformed_discrepancy_row_exits_3_naming_its_void(self) -> None:
        # given a discrepancy_recorded row the list cannot read
        _seat_malformed("discrepancy_recorded", "DSC-01-broken")
        # when the list is shown
        result = self.runner.invoke(main, ["wp", "discrepancy", "show"])
        # then a policy breach naming the void that recovers the row (ruling 9)
        self.assertEqual(result.exit_code, 3, result.output)
        self.assertIn("gz ledger correct", " ".join(result.output.split()))


class DiscrepancyEpilogTests(unittest.TestCase):
    def test_every_example_parses_as_a_real_invocation(self) -> None:
        # given the help of `gz wp discrepancy` and of each of its leaves
        parser = _build_parser()
        paths = (
            ["wp", "discrepancy"],
            *(["wp", "discrepancy", leaf] for leaf in ("record", "clear", "show")),
        )
        examples = [
            line.strip()
            for path in paths
            for line in (_help_parser(parser, list(path)).epilog or "").splitlines()
            if line.strip().startswith("gz ")
        ]
        group = [
            line.strip()
            for line in (_help_parser(parser, ["wp", "discrepancy"]).epilog or "").splitlines()
            if line.strip().startswith("gz ")
        ]
        # when
        parsed = [parser.parse_args(shlex.split(example)[1:]) for example in examples]
        leaves = {
            parser.parse_args(shlex.split(example)[1:]).discrepancy_command for example in group
        }
        # then each parses, every required flag present, onto a handler
        self.assertGreaterEqual(len(examples), 10)
        self.assertTrue(all(callable(args.func) for args in parsed))
        # and the group's own help shows an example of each of its leaves
        self.assertEqual(leaves, {"record", "clear", "show"})


class DiscrepancyChoicesTests(unittest.TestCase):
    """The parser offers exactly the ledger's closed sets, which it may not import.

    `gzkit.cli` is a driving adapter and imports no module outside its region's row
    (`docs/governance/hexagonal-architecture.md` § The dependency rules), so the parser
    spells the members out; this holds them to `DiscrepancyGrade` and
    `DiscrepancySource`, so a member ruled in or out of either set reaches the CLI.
    """

    def test_record_offers_every_grade_and_source_and_no_other(self) -> None:
        # given the record leaf of `gz wp discrepancy`
        record = _help_parser(_build_parser(), ["wp", "discrepancy", "record"])
        # when its --grade and --source choices are read
        offered = {
            action.dest: set(action.choices or ())
            for action in record._actions
            if action.dest in {"grade", "source"}
        }
        # then they are the ledger's closed sets, member for member
        self.assertEqual(
            offered,
            {"grade": set(get_args(DiscrepancyGrade)), "source": set(get_args(DiscrepancySource))},
        )


if __name__ == "__main__":
    unittest.main()
