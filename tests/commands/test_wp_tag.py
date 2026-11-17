"""``gz wp tag``'s wiring: RP-12 O3 task 2, acts 2 and 3.

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: the coordinator issues
a tag with `gz wp tag issue` (rulings 6 and 110), an unstamped call recorded with
the open MX session (ruling 114), and `gz wp tag show` renders the log, the open
tags by default and every tag on request (rulings 4 and 110). Every refusal of
the tag-out log, and the reducer that reads a tag open or closed, is proved in
`tests/test_tag_out.py`; these held tests prove the wiring alone, the verbs' exit
codes, the stamp refusal and the epilogs (ruling 125). `gz wp tag hang` (O3 task 3,
act 3) is the stamped call of the Repair dispatch it names (ruling 133).
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
from gzkit.mx import marker
from gzkit.mx.marker import Marker
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


def _tag_rows(event: str = "tag_issued") -> list[dict[str, Any]]:
    text = (Path(".gzkit") / "ledger.jsonl").read_text(encoding="utf-8")
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    return [row for row in rows if row["event"] == event]


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

    def show(self, *args: str) -> tuple[int, str]:
        result = self.runner.invoke(main, ["wp", "tag", "show", *args])
        return result.exit_code, result.output


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
        self.assertEqual(_tag_rows(), [])

    def test_an_issue_with_no_mx_session_is_refused_and_books_nothing(self) -> None:
        # given no MX session open
        # when
        code, output = self.issue(*_ISSUE)
        # then
        self.assertEqual(code, 3, output)
        self.assertEqual(_tag_rows(), [])

    def test_a_marker_present_but_unbound_names_its_repair_not_entry(self) -> None:
        # output-contract: the refusal's next step is its contract (guardrail-feedback-prose)
        # given a marker no open session binds, which `gz mx enter` would refuse to replace
        marker.write(Marker(session_id="ghost-session"), Path.cwd())
        # when
        code, output = self.issue(*_ISSUE)
        # then the refusal names the repair its cause needs, and nothing is booked
        self.assertEqual(code, 3, output)
        self.assertIn("present but unbound", output)
        self.assertIn("gz mx repair", output)
        self.assertEqual(_tag_rows(), [])

    def test_an_issue_on_an_unknown_order_is_refused_and_books_nothing(self) -> None:
        # given an open MX session and an order the catalog does not hold
        open_marker(Path.cwd())
        # when
        code, output = self.issue("ORD-09-ghost", *_ISSUE[1:])
        # then
        self.assertEqual(code, 3, output)
        self.assertEqual(_tag_rows(), [])


class TagShowWiringTests(_TagCase):
    def close_order(self) -> None:
        """Terminate ORD-01-import from opened, so its tag reads closed (ruling 122)."""
        result = self.runner.invoke(
            main,
            [
                *("wp", "order", "close", "ORD-01-import", "--decision", "terminate"),
                *("--attestor", "g0", "--attestation-text", "stop it", "--evidence", "e"),
            ],
        )
        self.assertEqual(result.exit_code, 0, result.output)

    def test_show_with_no_tag_issued_says_none_is_open(self) -> None:
        # given no tag issued
        # when
        code, output = self.show()
        # then
        self.assertEqual((code, output.strip()), (0, "No tag is open."))

    def test_show_after_an_issue_lists_the_open_tag(self) -> None:
        # given a tag issued on ORD-01-import under an open MX session
        open_marker(Path.cwd())
        self.assertEqual(self.issue(*_ISSUE)[0], 0)
        # when
        code, output = self.show()
        # then
        self.assertEqual(code, 0, output)
        self.assertIn("TAG-01-stamp-hook", output)
        self.assertIn("ORD-01-import", output)

    def test_show_writes_each_tag_as_its_whole_line_item(self) -> None:
        # output-contract: ruling 126 names the labelled-block rendering the view's form
        # given a tag issued on ORD-01-import under an open MX session
        open_marker(Path.cwd())
        self.assertEqual(self.issue(*_ISSUE)[0], 0)
        # when
        code, output = self.show()
        # then each field of the line item is on its own labelled line
        lines = [line.strip() for line in output.splitlines()]
        self.assertEqual(code, 0, output)
        self.assertEqual(lines[0], "TAG-01-stamp-hook on ORD-01-import")
        self.assertEqual(
            [line.split(":", 1)[0] for line in lines[1:]],
            ["Class", "Surface", "Position", "Check level", "Source", "Hazard", "Removal"],
        )
        self.assertIn("Hazard:      The scope reads a half-built map.", lines)
        self.assertIn("Removal:     Run the scope; it passes.", lines)

    def test_show_over_a_row_it_cannot_read_exits_3(self) -> None:
        # given a tag_issued row on the ledger that the event's shape does not admit
        row = {"schema": "gzkit.ledger.v1", "event": "tag_issued", "id": "TAG-7-bad"}
        with (Path(".gzkit") / "ledger.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({**row, "ts": "2026-11-17T00:00:00+00:00"}) + "\n")
        # when
        code, output = self.show()
        # then the view refuses, a policy breach, rather than crash
        self.assertEqual(code, 3, output)

    def test_all_lists_a_closed_orders_tag_the_default_omits(self) -> None:
        # given a tag issued on ORD-01-import, then the order terminated
        open_marker(Path.cwd())
        self.assertEqual(self.issue(*_ISSUE)[0], 0)
        self.close_order()
        # when
        default, every, every_json = self.show(), self.show("--all"), self.show("--all", "--json")
        # then the default omits it, and --all lists it, read closed
        self.assertEqual(default, (0, "No tag is open.\n"))
        self.assertEqual((every[0], every_json[0]), (0, 0), every[1] + every_json[1])
        self.assertIn("TAG-01-stamp-hook", every[1])
        self.assertEqual(
            [(tag["tag_id"], tag["is_open"]) for tag in json.loads(every_json[1])],
            [("TAG-01-stamp-hook", False)],
        )

    def test_json_mode_prints_each_tag_with_whether_it_is_open(self) -> None:
        # given one tag issued and still open
        open_marker(Path.cwd())
        self.assertEqual(self.issue(*_ISSUE)[0], 0)
        # when
        code, output = self.show("--json")
        # then
        self.assertEqual(code, 0, output)
        printed = json.loads(output)
        self.assertEqual(
            [(tag["tag_id"], tag["order"], tag["is_open"]) for tag in printed],
            [("TAG-01-stamp-hook", "ORD-01-import", True)],
        )
        self.assertEqual({k: v for k, v in printed[0].items() if k != "is_open"}, _tag_rows()[0])


class TagHangWiringTests(_TagCase):
    """A tag issued on ORD-01-import, the order frozen, a Repair dispatch booked on it."""

    def setUp(self) -> None:
        super().setUp()
        open_marker(Path.cwd())
        self.assertEqual(self.issue(*_ISSUE)[0], 0)
        store = Path("data") / "catalog" / "work_packages.json"
        held = json.loads(store.read_text(encoding="utf-8"))
        held["work_packages"][0]["modules"] = ["src/stamp.py"]
        store.write_text(json.dumps(held), encoding="utf-8")
        Path("src").mkdir(exist_ok=True)
        Path("src/stamp.py").write_text("STAMP = 1\n", encoding="utf-8")
        root = Path.cwd().resolve().as_posix()
        for args in (
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
        ):
            result = self.runner.invoke(main, args)
            self.assertEqual(result.exit_code, 0, result.output)
        result = self.runner.invoke(
            main,
            [
                *("wp", "dispatch", "WP-01-stamp", "--order", "ORD-01-import"),
                *("--role", "Repair", "--model", "m", "--root", root, "--json"),
            ],
        )
        self.assertEqual(result.exit_code, 0, result.output)
        self.dispatch = json.loads(result.output)["dispatch_id"]

    def stamp_as(self, dispatch_id: str) -> None:
        """Stamp the call as the named dispatch's subagent, held to this root (ruling 133)."""
        self.stamp()
        os.environ[STAMP_ID_ENV] = dispatch_id
        self.addCleanup(os.environ.pop, STAMP_ID_ENV, None)

    def hang(self, *args: str) -> tuple[int, str]:
        result = self.runner.invoke(main, ["wp", "tag", "hang", *args])
        return result.exit_code, " ".join(result.output.split())

    def test_the_named_repair_dispatchs_stamped_call_hangs_the_tag(self) -> None:
        # given the call stamped with the Repair dispatch it names
        self.stamp_as(self.dispatch)
        # when
        code, output = self.hang("TAG-01-stamp-hook", "--dispatch", self.dispatch)
        # then
        self.assertEqual((code, output), (0, f"Hung TAG-01-stamp-hook by {self.dispatch}."))
        self.assertEqual(
            [(r["tag_id"], r["dispatch_id"], r["mx_session_id"]) for r in _tag_rows("tag_hung")],
            [("TAG-01-stamp-hook", self.dispatch, "test-session")],
        )

    def test_an_unstamped_hang_is_refused_and_books_nothing(self) -> None:
        # given the main session's call, carrying no stamp
        # when
        code, output = self.hang("TAG-01-stamp-hook", "--dispatch", self.dispatch)
        # then
        self.assertEqual(code, 3, output)
        self.assertEqual(_tag_rows("tag_hung"), [])


class TagEpilogTests(unittest.TestCase):
    def test_every_example_parses_as_a_real_invocation(self) -> None:
        # given the help of `gz wp tag` and of each of its leaves
        parser = _build_parser()
        leaves = (["wp", "tag", leaf] for leaf in ("issue", "show", "hang"))
        examples = [
            line.strip()
            for path in (["wp", "tag"], *leaves)
            for line in (_help_parser(parser, path).epilog or "").splitlines()
            if line.strip().startswith("gz ")
        ]
        # when
        parsed = [parser.parse_args(shlex.split(example)[1:]) for example in examples]
        # then each parses, every required flag present, onto a handler
        self.assertGreaterEqual(len(examples), 7)
        self.assertTrue(all(callable(args.func) for args in parsed))


if __name__ == "__main__":
    unittest.main()
