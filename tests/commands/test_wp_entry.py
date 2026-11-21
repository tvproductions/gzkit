"""``gz wp entry book``'s wiring: RP-12 O4 task 1, act 2.

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: the performer books its
own maintenance-record entry (ruling 167), the call stamped with the live
`Implementer`, `SingleDriver` or `Restoration` dispatch it names (ruling 133's form;
ruling 175), its order and package read from the dispatch record (rulings 1 and
130), with the open MX session (ruling 8). Every refusal of the writer, and the
reducer, is proved in `tests/test_entries.py`; these held tests prove the wiring
alone: the stamp and the session read at the CLI, the exit codes and the epilogs
(ruling 125).
"""

import json
import os
import shlex
import subprocess
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from gzkit.cli import main
from gzkit.cli.main import _build_parser
from gzkit.dispatch_stamp import STAMP_ID_ENV, STAMP_ROOT_ENV
from gzkit.mx import marker
from gzkit.mx.marker import Marker
from tests.commands.common import CliRunner, _isolated_git_env, _quick_init
from tests.commands.test_wp_order import _help_parser, _seed_catalog
from tests.mx.held import open_marker

_ENTRY = (
    *("--slug", "stamp-import"),
    *("--description", "The stamp generator imports its template again."),
    *("--before", "tests.test_stamp fails: ImportError on the template"),
    *("--after", "tests.test_stamp passes, 12 tests"),
    *("--witness", "uv run -m unittest tests.test_stamp"),
)


def _land(subject: str) -> str:
    """Commit the working tree with *subject* in a fresh repository, as the coordinator lands work.

    Returns:
        The landing commit's full SHA.

    """
    env = _isolated_git_env()
    for args in (
        ["init", "-q"],
        ["config", "user.email", "t@e.st"],
        ["config", "user.name", "tester"],
        ["add", "-A"],
        ["-c", "commit.gpgsign=false", "commit", "-q", "-m", subject],
    ):
        subprocess.run(["git", *args], check=True, env=env)  # noqa: S603 — git in a temp repo
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], check=True, env=env, capture_output=True, text=True
    )
    return head.stdout.strip()


def _entry_rows() -> list[dict[str, Any]]:
    text = (Path(".gzkit") / "ledger.jsonl").read_text(encoding="utf-8")
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    return [row for row in rows if row["event"] == "entry_booked"]


class _EntryCase(unittest.TestCase):
    """A repair package initiated, its order frozen and commenced, a Restoration booked on it."""

    def setUp(self) -> None:
        for name in (STAMP_ROOT_ENV, STAMP_ID_ENV):
            if name in os.environ:
                self.addCleanup(os.environ.__setitem__, name, os.environ.pop(name))
        self.runner = CliRunner()
        self.enterContext(self.runner.isolated_filesystem())
        _quick_init()
        _seed_catalog()
        store = Path("data") / "catalog" / "work_packages.json"
        held = json.loads(store.read_text(encoding="utf-8"))
        held["work_packages"][0]["modules"] = ["src/stamp.py"]
        store.write_text(json.dumps(held), encoding="utf-8")
        Path("src").mkdir(exist_ok=True)
        Path("src/stamp.py").write_text("STAMP = 1\n", encoding="utf-8")
        root = Path.cwd().resolve().as_posix()
        for args in (
            ["wp", "initiate", "WP-01-stamp", "--operator-text", "open it"],
            [
                *("wp", "order", "new", "WP-01-stamp", "--slug", "import"),
                *("--purpose", "P.", "--operator-text", "open it"),
            ],
            [
                *("wp", "req", "new", "WP-01-stamp", "--statement", "The stamp imports."),
                *("--criterion", "an import|ok|a test", "--kind", "BEHAVIOR"),
                *("--problem-report", "1301"),
            ],
            [
                *("wp", "order", "freeze", "ORD-01-import", "--baseline", "REQ-1@1"),
                *("--risk-note", "Touches the hook.", "--review-receipt", "review-01"),
                *("--evidence", "E"),
            ],
            [
                *("wp", "order", "commence", "ORD-01-import", "--evidence", "E"),
                *("--no-isolation", "The repair touches no guard."),
            ],
        ):
            result = self.runner.invoke(main, args)
            self.assertEqual(result.exit_code, 0, result.output)
        result = self.runner.invoke(
            main,
            [
                *("wp", "dispatch", "WP-01-stamp", "--order", "ORD-01-import"),
                *("--role", "Restoration", "--model", "m", "--root", root, "--json"),
            ],
        )
        self.assertEqual(result.exit_code, 0, result.output)
        self.dispatch = json.loads(result.output)["dispatch_id"]

    def stamp_as(self, dispatch_id: str) -> None:
        """Stamp the call as the named dispatch's subagent, held to this root (ruling 133)."""
        os.environ[STAMP_ROOT_ENV] = Path.cwd().resolve().as_posix()
        os.environ[STAMP_ID_ENV] = dispatch_id
        self.addCleanup(os.environ.pop, STAMP_ROOT_ENV, None)
        self.addCleanup(os.environ.pop, STAMP_ID_ENV, None)

    def book(self, *args: str) -> tuple[int, str]:
        result = self.runner.invoke(
            main, ["wp", "entry", "book", "--dispatch", self.dispatch, *_ENTRY, *args]
        )
        return result.exit_code, " ".join(result.output.split())


class EntryBookWiringTests(_EntryCase):
    def test_the_named_dispatchs_stamped_call_books_the_entry(self) -> None:
        # output-contract: docs/user/manpages/wp-entry-book.md, the line a booking prints
        # given an open MX session and the call stamped with the Restoration it names
        open_marker(Path.cwd())
        self.stamp_as(self.dispatch)
        # when
        code, output = self.book()
        # then the entry is booked on the dispatch's own order, under the open session
        self.assertEqual(
            (code, output), (0, f"Booked ENT-01-stamp-import on ORD-01-import by {self.dispatch}.")
        )
        self.assertEqual(
            [
                (r["entry_id"], r["order"], r["work_package"], r["dispatch_id"], r["mx_session_id"])
                for r in _entry_rows()
            ],
            [
                (
                    "ENT-01-stamp-import",
                    "ORD-01-import",
                    "WP-01-stamp",
                    self.dispatch,
                    "test-session",
                )
            ],
        )

    def test_json_mode_prints_the_booked_event(self) -> None:
        # given an open MX session and the dispatch's stamped call
        open_marker(Path.cwd())
        self.stamp_as(self.dispatch)
        # when
        code, output = self.book("--json")
        # then the event booked, never the human line
        self.assertEqual(code, 0, output)
        self.assertTrue(output.startswith("{"), output)
        printed, (booked,) = json.loads(output), _entry_rows()
        self.assertEqual(
            {k: v for k, v in printed.items() if k != "ts"},
            {k: v for k, v in booked.items() if k != "ts"},
        )

    def test_an_unstamped_call_is_refused_and_books_nothing(self) -> None:
        # output-contract: the refusal names its cause (guardrail-feedback-prose)
        # given an open MX session and the main session's call, carrying no stamp
        open_marker(Path.cwd())
        # when
        code, output = self.book()
        # then the writer's refusal is the verb's, exit 3 (cli.md § Exit Codes)
        self.assertEqual(code, 3, output)
        self.assertIn("not stamped", output)
        self.assertEqual(_entry_rows(), [])

    def test_with_no_mx_session_the_entry_is_refused_and_books_nothing(self) -> None:
        # output-contract: the refusal names its cause (guardrail-feedback-prose)
        # given the dispatch's stamped call and no MX session open
        self.stamp_as(self.dispatch)
        # when
        code, output = self.book()
        # then
        self.assertEqual(code, 3, output)
        self.assertIn("No MX session is open", output)
        self.assertEqual(_entry_rows(), [])

    def test_a_marker_present_but_unbound_names_its_repair_not_entry(self) -> None:
        # output-contract: the refusal's next step is its contract (guardrail-feedback-prose)
        # given a marker no open session binds, which `gz mx enter` would refuse to replace
        marker.write(Marker(session_id="ghost-session"), Path.cwd())
        self.stamp_as(self.dispatch)
        # when
        code, output = self.book()
        # then the refusal names the repair its cause needs, and nothing is booked
        self.assertEqual(code, 3, output)
        self.assertIn("present but unbound", output)
        self.assertIn("gz mx repair", output)
        self.assertEqual(_entry_rows(), [])


class EntryShowWiringTests(_EntryCase):
    def show(self, *args: str) -> tuple[int, str]:
        result = self.runner.invoke(main, ["wp", "entry", "show", *args])
        return result.exit_code, result.output

    def booked(self) -> None:
        open_marker(Path.cwd())
        self.stamp_as(self.dispatch)
        self.assertEqual(self.book()[0], 0)
        for name in (STAMP_ROOT_ENV, STAMP_ID_ENV):
            os.environ.pop(name, None)

    def test_with_no_entry_booked_it_says_none_has_been(self) -> None:
        # output-contract: docs/user/manpages/wp-entry-show.md, the empty record's line
        # given no entry booked
        # when
        code, output = self.show()
        # then
        self.assertEqual((code, output.strip()), (0, "No entry has been booked."))

    def test_show_writes_each_entry_as_a_block_with_its_gate_5(self) -> None:
        # output-contract: docs/user/manpages/wp-entry-show.md, one labelled line per element
        # given an entry booked on a commenced order, not yet closed at Gate 5, and no
        # commit naming it
        self.booked()
        _land("chore: an unrelated commit")
        # when
        code, output = self.show()
        # then the whole entry reads, its signature not yet given (ruling 8)
        self.assertEqual(code, 0, output)
        lines = [line.strip() for line in output.splitlines()]
        self.assertEqual(lines[0], "ENT-01-stamp-import on ORD-01-import (WP-01-stamp)")
        self.assertIn(f"Performer:   {self.dispatch}", lines)
        self.assertIn("Before:      tests.test_stamp fails: ImportError on the template", lines)
        self.assertIn("Witness:     uv run -m unittest tests.test_stamp", lines)
        self.assertIn("MX session:  test-session", lines)
        self.assertIn("Landed:      not landed", lines)
        self.assertIn("Gate 5:      not signed", lines)

    def test_an_entry_a_commit_subject_names_reads_landed_by_it(self) -> None:
        # output-contract: docs/user/manpages/wp-entry-show.md, the Landed line (ruling 192)
        # given an entry booked, then the coordinator's commit naming it in its subject
        self.booked()
        subject = "fix(stamp): the template imports again (ENT-01-stamp-import)"
        sha = _land(subject)
        # when
        code, output = self.show()
        # then the view joins the commit to the entry it names
        self.assertEqual(code, 0, output)
        self.assertIn(f"Landed: {sha[:12]} {subject} Gate 5:", " ".join(output.split()))

    def test_json_mode_prints_each_entry_with_its_gate_5(self) -> None:
        # given an entry booked on an order not closed, and no commit naming it
        self.booked()
        _land("chore: an unrelated commit")
        # when
        code, output = self.show("--json")
        # then each entry is its booked event with its order's Gate 5, here none
        self.assertEqual(code, 0, output)
        (printed,) = json.loads(output)
        (booked,) = _entry_rows()
        self.assertEqual({k: v for k, v in printed.items() if k not in {"gate5", "landed"}}, booked)
        self.assertIsNone(printed["gate5"])
        self.assertEqual(printed["landed"], [])

    def test_an_entry_named_in_a_commit_body_alone_reads_not_landed(self) -> None:
        # output-contract: docs/user/manpages/wp-entry-show.md, the subject alone (ruling 170)
        # given an entry booked and a commit naming it in its body, not its subject
        self.booked()
        _land("fix(stamp): the template imports again\n\nLands ENT-01-stamp-import.")
        # when
        code, output = self.show()
        # then the view reads it not landed
        self.assertEqual(code, 0, output)
        self.assertIn("Landed: not landed", " ".join(output.split()))

    def test_outside_a_git_repository_each_landed_line_names_why(self) -> None:
        # output-contract: docs/user/manpages/wp-entry-show.md, git not read (ruling 193)
        # given an entry booked in a project that is no git repository, git's search
        # for one held to the project so a repository above the temp dir is not read
        self.booked()
        ceiling = {"GIT_CEILING_DIRECTORIES": str(Path.cwd().resolve().parent)}
        # when
        with patch.dict(os.environ, ceiling):
            code, output = self.show()
            json_code, json_output = self.show("--json")
        # then the Landed line names the cause, and JSON reads landed as unknown
        flat = " ".join(output.split())
        self.assertEqual((code, json_code), (0, 0), output)
        self.assertIn("Landed: commits could not be read: `git log` exited", flat)
        self.assertNotIn("not landed", flat)
        self.assertIsNone(json.loads(json_output)[0]["landed"])

    def test_json_mode_lists_each_landing_commit(self) -> None:
        # given an entry booked and a commit naming it
        self.booked()
        subject = "fix(stamp): the template imports again (ENT-01-stamp-import)"
        sha = _land(subject)
        # when
        code, output = self.show("--json")
        # then the entry carries its landing commit, as the human form reads it (ruling 192)
        self.assertEqual(code, 0, output)
        (printed,) = json.loads(output)
        self.assertEqual(printed["landed"], [{"commit_sha": sha, "subject": subject}])


class EntryEpilogTests(unittest.TestCase):
    def test_every_example_parses_as_a_real_invocation(self) -> None:
        # given the help of `gz wp entry` and of each of its leaves
        parser = _build_parser()
        examples = [
            line.strip()
            for path in (["wp", "entry"], ["wp", "entry", "book"], ["wp", "entry", "show"])
            for line in (_help_parser(parser, path).epilog or "").splitlines()
            if line.strip().startswith("gz ")
        ]
        group = [
            line.strip()
            for line in (_help_parser(parser, ["wp", "entry"]).epilog or "").splitlines()
            if line.strip().startswith("gz ")
        ]
        # when
        parsed = [parser.parse_args(shlex.split(example)[1:]) for example in examples]
        leaves = {parser.parse_args(shlex.split(example)[1:]).entry_command for example in group}
        # then each parses, every required flag present, onto a handler
        self.assertGreaterEqual(len(examples), 5)
        self.assertTrue(all(callable(args.func) for args in parsed))
        # and the group's own help shows an example of each of its leaves
        self.assertEqual(leaves, {"book", "show"})


if __name__ == "__main__":
    unittest.main()
