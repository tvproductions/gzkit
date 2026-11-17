"""``gz wp tag issue``'s wiring: RP-12 O3 task 2, act 2.

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: the coordinator issues
a tag with `gz wp tag issue` (rulings 6 and 110), an unstamped call recorded with
the open MX session (ruling 114). Every refusal of the tag-out log is proved in
`tests/test_tag_out.py` against the writer; these held tests prove the wiring
alone, the verb's exit codes, its stamp refusal and its epilog (ruling 125).
"""

import json
import os
import shlex
import unittest
from pathlib import Path
from typing import Any

from gzkit.cli import main
from gzkit.cli.main import _build_parser
from gzkit.dispatch_stamp import STAMP_ID_ENV, STAMP_ROOT_ENV
from tests.commands.common import CliRunner, _quick_init
from tests.commands.test_wp_order import _help_parser, _seed_catalog
from tests.mx.held import open_marker

_ISSUE = (
    "ORD-01-import",
    "--slug",
    "stamp-hook",
    "--class",
    "Danger",
    "--surface",
    "validator:hexagon-tests",
    "--position",
    "off",
    "--hazard",
    "The scope reads a half-built map.",
    "--removal-procedure",
    "Run the scope; it passes.",
    "--source",
    "order-work",
    "--check-level",
    "C",
)


def _tag_rows() -> list[dict[str, Any]]:
    text = (Path(".gzkit") / "ledger.jsonl").read_text(encoding="utf-8")
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    return [row for row in rows if row["event"] == "tag_issued"]


class _TagCase(unittest.TestCase):
    def setUp(self) -> None:
        for name in (STAMP_ROOT_ENV, STAMP_ID_ENV):
            if name in os.environ:
                self.addCleanup(os.environ.__setitem__, name, os.environ.pop(name))
        self.runner = CliRunner()
        self.enterContext(self.runner.isolated_filesystem())
        _quick_init()
        _seed_catalog()
        for args in (
            ["wp", "initiate", "WP-01-stamp", "--operator-text", "open it"],
            [
                *("wp", "order", "new", "WP-01-stamp", "--slug", "import"),
                *("--purpose", "P.", "--operator-text", "open it"),
            ],
        ):
            result = self.runner.invoke(main, args)
            self.assertEqual(result.exit_code, 0, result.output)

    def stamp(self) -> None:
        """Stamp the call as a subagent's, held to this project's root (ruling 38)."""
        os.environ[STAMP_ROOT_ENV] = Path.cwd().resolve().as_posix()
        self.addCleanup(os.environ.pop, STAMP_ROOT_ENV, None)

    def issue(self, *args: str) -> tuple[int, str]:
        result = self.runner.invoke(main, ["wp", "tag", "issue", *args])
        return result.exit_code, " ".join(result.output.split())


class TagIssueWiringTests(_TagCase):
    def test_an_issue_under_an_open_session_books_the_tag_and_prints_its_id(self) -> None:
        # given an open MX session and an opened order of an initiated repair package
        open_marker(Path.cwd())
        # when
        code, output = self.issue(*_ISSUE)
        # then
        self.assertEqual((code, output), (0, "Issued TAG-01-stamp-hook on ORD-01-import."))
        self.assertEqual(
            [(row["tag_id"], row["surface_name"], row["mx_session_id"]) for row in _tag_rows()],
            [("TAG-01-stamp-hook", "hexagon_tests", "test-session")],
        )

    def test_json_mode_prints_the_booked_event(self) -> None:
        # given an open MX session
        open_marker(Path.cwd())
        # when
        code, output = self.issue(*_ISSUE, "--json")
        # then
        self.assertEqual(code, 0, output)
        printed, booked = json.loads(output), _tag_rows()[0]
        # the line item is the booked one; the stamp time is the ledger row's own
        self.assertEqual(
            {k: v for k, v in printed.items() if k != "ts"},
            {k: v for k, v in booked.items() if k != "ts"},
        )

    def test_a_stamped_call_is_refused_and_books_nothing(self) -> None:
        # given an open MX session and a call stamped as a subagent's
        open_marker(Path.cwd())
        self.stamp()
        # when
        code, output = self.issue(*_ISSUE)
        # then
        self.assertEqual(code, 3, output)
        self.assertIn("ruling 114", output)
        self.assertEqual(_tag_rows(), [])

    def test_an_issue_with_no_mx_session_is_refused_and_books_nothing(self) -> None:
        # given no MX session open
        # when
        code, output = self.issue(*_ISSUE)
        # then
        self.assertEqual(code, 3, output)
        self.assertEqual(_tag_rows(), [])

    def test_an_issue_on_an_unknown_order_is_refused_and_books_nothing(self) -> None:
        # given an open MX session and an order the catalog does not hold
        open_marker(Path.cwd())
        # when
        code, output = self.issue("ORD-09-ghost", *_ISSUE[1:])
        # then
        self.assertEqual(code, 3, output)
        self.assertEqual(_tag_rows(), [])


class TagEpilogTests(unittest.TestCase):
    def test_every_example_parses_as_a_real_invocation(self) -> None:
        # given the help of `gz wp tag` and `gz wp tag issue`
        parser = _build_parser()
        examples = [
            line.strip()
            for path in (["wp", "tag"], ["wp", "tag", "issue"])
            for line in (_help_parser(parser, path).epilog or "").splitlines()
            if line.strip().startswith("gz ")
        ]
        # when
        parsed = [parser.parse_args(shlex.split(example)[1:]) for example in examples]
        # then each parses, every required flag present, onto a handler
        self.assertGreaterEqual(len(examples), 3)
        self.assertTrue(all(callable(args.func) for args in parsed))


if __name__ == "__main__":
    unittest.main()
