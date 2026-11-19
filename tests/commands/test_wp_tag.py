"""``gz wp tag``'s wiring: RP-12 O3 task 2, acts 2 and 3.

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: the coordinator issues
a tag with `gz wp tag issue` (rulings 6 and 110), an unstamped call recorded with
the open MX session (ruling 114), and `gz wp tag show` renders the log, the open
tags by default and every tag on request (rulings 4 and 110). Every refusal of
the tag-out log, and the reducer that reads a tag open or closed, is proved in
`tests/test_tag_out.py`; these held tests prove the wiring alone, the verbs' exit
codes, the stamp refusal and the epilogs (ruling 125). `gz wp tag hang` (O3 task 3,
act 3) is the stamped call of the Repair dispatch it names (ruling 133);
`gz wp tag authorize` (O3 task 4) is the coordinator's unstamped call (ruling 114),
and `gz wp tag clear` the stamped call of the Restoration dispatch it names, an
out-of-position find exiting 3 with the order blocked (rulings 137 to 140).
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
        self.assertTrue(output.startswith("{"), output)  # JSON, never the human line
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

    def test_all_with_no_tag_issued_says_none_has_been_issued(self) -> None:
        # output-contract: docs/user/manpages/wp-tag-show.md names both empty lines
        # given no tag issued
        # when
        code, output = self.show("--all")
        # then
        self.assertEqual((code, output.strip()), (0, "No tag has been issued."))

    def test_json_with_no_tag_open_prints_an_empty_list(self) -> None:
        # given no tag issued
        # when
        code, output = self.show("--json")
        # then the machine form is the list, never the human line
        self.assertEqual((code, output.strip()), (0, "[]"))

    def test_all_marks_each_tag_open_or_closed(self) -> None:
        # output-contract: docs/user/manpages/wp-tag-show.md, the state after the order
        # given a tag issued on an opened order
        open_marker(Path.cwd())
        self.assertEqual(self.issue(*_ISSUE)[0], 0)
        # when read under --all before and after the order closes
        before = self.show("--all")[1].splitlines()[0]
        self.close_order()
        after = self.show("--all")[1].splitlines()[0]
        # then
        self.assertEqual(
            (before, after),
            (
                "TAG-01-stamp-hook on ORD-01-import (open)",
                "TAG-01-stamp-hook on ORD-01-import (closed)",
            ),
        )

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
            [
                "Hung by",
                "Clearance",
                "Cleared by",
                "Class",
                "Surface",
                "Position",
                "Check level",
                "Source",
                "Hazard",
                "Removal",
            ],
        )
        self.assertIn("Hung by:     not hung", lines)
        self.assertIn("Clearance:   not authorized", lines)
        self.assertIn("Cleared by:  not cleared", lines)
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
        listed = json.loads(every_json[1])
        self.assertEqual([type(tag) for tag in listed], [dict])
        self.assertEqual(
            [(tag["tag_id"], tag["is_open"]) for tag in listed],
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
        self.assertEqual([type(tag) for tag in printed], [dict])
        self.assertEqual(
            [
                (
                    tag["tag_id"],
                    tag["order"],
                    tag["is_open"],
                    tag.get("state"),
                    tag.get("hang", "absent"),
                    tag.get("clearance", "absent"),
                    tag.get("clear", "absent"),
                )
                for tag in printed
            ],
            [("TAG-01-stamp-hook", "ORD-01-import", True, "issued", None, None, None)],
        )
        added = {"is_open", "state", "hang", "clearance", "clear"}
        self.assertEqual({k: v for k, v in printed[0].items() if k not in added}, _tag_rows()[0])


class _HungTagCase(_TagCase):
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

    def unstamp(self) -> None:
        """Return to the main session's call, carrying no stamp."""
        for name in (STAMP_ROOT_ENV, STAMP_ID_ENV):
            os.environ.pop(name, None)

    def hang(self, *args: str) -> tuple[int, str]:
        result = self.runner.invoke(main, ["wp", "tag", "hang", *args])
        return result.exit_code, " ".join(result.output.split())


class TagHangWiringTests(_HungTagCase):
    def test_show_names_a_hung_tags_dispatch_in_its_block_and_json(self) -> None:
        # output-contract: ruling 129 names the hang's dispatch in the view's block and JSON
        # given the tag hung by the Repair dispatch's stamped call
        self.stamp_as(self.dispatch)
        self.assertEqual(self.hang("TAG-01-stamp-hook", "--dispatch", self.dispatch)[0], 0)
        for name in (STAMP_ROOT_ENV, STAMP_ID_ENV):
            os.environ.pop(name, None)
        # when
        block = self.runner.invoke(main, ["wp", "tag", "show"])
        printed = self.runner.invoke(main, ["wp", "tag", "show", "--json"])
        # then
        self.assertIn(f"Hung by:     {self.dispatch}", block.output)
        record = json.loads(printed.output)[0]
        self.assertIsInstance(record, dict)
        hang = record.get("hang") or {}
        self.assertEqual((record.get("state"), hang.get("dispatch_id")), ("hung", self.dispatch))

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

    def test_json_mode_prints_the_booked_hang(self) -> None:
        # given the Repair dispatch's stamped call
        self.stamp_as(self.dispatch)
        # when
        result = self.runner.invoke(
            main, ["wp", "tag", "hang", "TAG-01-stamp-hook", "--dispatch", self.dispatch, "--json"]
        )
        # then the event booked, never the human line
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertTrue(result.output.startswith("{"), result.output)
        printed = json.loads(result.output)
        self.assertEqual((printed["event"], printed["dispatch_id"]), ("tag_hung", self.dispatch))

    def test_an_unstamped_hang_is_refused_and_books_nothing(self) -> None:
        # given the main session's call, carrying no stamp
        # when
        code, output = self.hang("TAG-01-stamp-hook", "--dispatch", self.dispatch)
        # then refused for its own reason, not an earlier check's
        self.assertEqual(code, 3, output)
        self.assertIn("This call is not stamped", output)
        self.assertEqual(_tag_rows("tag_hung"), [])

    def test_an_id_with_no_stamped_root_is_no_stamp(self) -> None:
        # given the dispatch's id in the environment and no stamped root (ruling 133)
        os.environ[STAMP_ID_ENV] = self.dispatch
        self.addCleanup(os.environ.pop, STAMP_ID_ENV, None)
        # when
        code, output = self.hang("TAG-01-stamp-hook", "--dispatch", self.dispatch)
        # then gz's entry keeps no id, so the call reads unstamped
        self.assertEqual(code, 3, output)
        self.assertIn("This call is not stamped", output)
        self.assertEqual(_tag_rows("tag_hung"), [])

    def test_a_stamped_root_with_a_blank_id_keeps_no_id(self) -> None:
        # given a stamped root and a dispatch id of whitespace alone
        self.stamp_as("  ")
        # when
        code, output = self.hang("TAG-01-stamp-hook", "--dispatch", self.dispatch)
        # then the blank id is no id, never a stamp of blanks
        self.assertEqual(code, 3, output)
        self.assertIn("This call is not stamped", output)
        self.assertEqual(_tag_rows("tag_hung"), [])


class TagAuthorizeWiringTests(_HungTagCase):
    """The tag hung, the order commenced, the hanging dispatch voided after a kill."""

    def setUp(self) -> None:
        super().setUp()
        self.stamp_as(self.dispatch)
        self.assertEqual(self.hang("TAG-01-stamp-hook", "--dispatch", self.dispatch)[0], 0)
        self.unstamp()
        for args in (
            ["wp", "order", "commence", "ORD-01-import", "--evidence", "E"],
            [*("wp", "dispatch", "WP-01-stamp", "--void", self.dispatch), "--reason", "killed"],
        ):
            result = self.runner.invoke(main, args)
            self.assertEqual(result.exit_code, 0, result.output)

    def authorize(self, *args: str) -> tuple[int, str]:
        result = self.runner.invoke(main, ["wp", "tag", "authorize", *args])
        return result.exit_code, " ".join(result.output.split())

    def test_the_coordinators_call_authorizes_the_clearance_and_show_reads_it(self) -> None:
        # given the main session's call and the hanging dispatch voided
        # when
        code, output = self.authorize("TAG-01-stamp-hook")
        printed = self.runner.invoke(main, ["wp", "tag", "show", "--json"])
        # then the clearance is booked not available, read over by the void
        expected = (
            f"Clearance of TAG-01-stamp-hook authorized; {self.dispatch} voided, "
            "repair activity not available."
        )
        self.assertEqual((code, output), (0, expected))
        (row,) = _tag_rows("tag_clearance_authorized")
        self.assertEqual(
            (row["hanging_dispatch_id"], row["repair_activity"], row["mx_session_id"]),
            (self.dispatch, "not-available", "test-session"),
        )
        record = json.loads(printed.output)[0]
        self.assertEqual(record.get("state"), "authorized")

    def test_json_mode_prints_the_booked_clearance(self) -> None:
        # given the main session's call
        # when
        result = self.runner.invoke(main, ["wp", "tag", "authorize", "TAG-01-stamp-hook", "--json"])
        # then the event booked, never the human line
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertTrue(result.output.startswith("{"), result.output)
        printed = json.loads(result.output)
        self.assertEqual(printed["event"], "tag_clearance_authorized")

    def test_show_reads_the_clearance_in_its_block_and_json(self) -> None:
        # output-contract: docs/user/manpages/wp-tag-show.md, the Clearance line
        # given the clearance authorized
        self.assertEqual(self.authorize("TAG-01-stamp-hook")[0], 0)
        # when
        block = self.runner.invoke(main, ["wp", "tag", "show"]).output
        record = json.loads(self.runner.invoke(main, ["wp", "tag", "show", "--json"]).output)[0]
        # then
        self.assertIn("Clearance:   authorized", block)
        self.assertEqual((record.get("clearance") or {}).get("tag_id"), "TAG-01-stamp-hook")

    def test_a_writer_refusal_exits_3_with_its_prose_and_books_nothing(self) -> None:
        # given a tag the ledger does not hold
        # when
        code, output = self.authorize("TAG-99-none")
        # then the writer's refusal is the verb's, exit 3 (cli.md § Exit Codes)
        self.assertEqual(code, 3, output)
        self.assertIn("Tag 'TAG-99-none' is not issued in the ledger", output)
        self.assertEqual(_tag_rows("tag_clearance_authorized"), [])

    def test_a_stamped_authorize_is_refused_and_books_nothing(self) -> None:
        # given a call stamped as a subagent's (ruling 114)
        self.stamp_as(self.dispatch)
        # when
        code, output = self.authorize("TAG-01-stamp-hook")
        # then refused for its own reason, not the writer's
        self.assertEqual(code, 3, output)
        self.assertIn("A clearance is refused from a subagent's call", output)
        self.assertEqual(_tag_rows("tag_clearance_authorized"), [])


class TagClearWiringTests(_HungTagCase):
    """The tag hung, the order commenced, the clearance authorized, a Restoration booked."""

    def setUp(self) -> None:
        super().setUp()
        self.stamp_as(self.dispatch)
        self.assertEqual(self.hang("TAG-01-stamp-hook", "--dispatch", self.dispatch)[0], 0)
        self.unstamp()
        root = Path.cwd().resolve().as_posix()
        for args in (
            ["wp", "order", "commence", "ORD-01-import", "--evidence", "E"],
            [*("wp", "dispatch", "WP-01-stamp", "--void", self.dispatch), "--reason", "killed"],
            ["wp", "tag", "authorize", "TAG-01-stamp-hook"],
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
        self.restorer = json.loads(result.output)["dispatch_id"]
        self.stamp_as(self.restorer)

    def clear(self, found: str) -> tuple[int, str]:
        args = ["TAG-01-stamp-hook", "--dispatch", self.restorer, "--position-found", found]
        result = self.runner.invoke(main, ["wp", "tag", "clear", *args])
        return result.exit_code, " ".join(result.output.split())

    def test_the_restorations_stamped_call_clears_the_tag_and_show_reads_it_closed(self) -> None:
        # given the call stamped as the Restoration dispatch, the surface found as hung
        # when
        code, output = self.clear("off")
        self.unstamp()
        printed = self.runner.invoke(main, ["wp", "tag", "show", "--all", "--json"])
        # then the clear is booked and the tag reads closed (ruling 129)
        expected = f"Cleared TAG-01-stamp-hook by {self.restorer}, found off."
        self.assertEqual((code, output), (0, expected))
        (row,) = _tag_rows("tag_cleared")
        self.assertEqual(
            (row["dispatch_id"], row["hanging_dispatch_id"], row["position_found"]),
            (self.restorer, self.dispatch, "off"),
        )
        record = json.loads(printed.output)[0]
        self.assertEqual((record.get("state"), record.get("is_open")), ("cleared", False))

    def test_json_mode_prints_the_booked_clear(self) -> None:
        # given the Restoration dispatch's stamped call, the surface found as hung
        # when
        result = self.runner.invoke(
            main,
            [
                *("wp", "tag", "clear", "TAG-01-stamp-hook", "--dispatch", self.restorer),
                *("--position-found", "off", "--json"),
            ],
        )
        # then the event booked, never the human line
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertTrue(result.output.startswith("{"), result.output)
        self.assertEqual(json.loads(result.output)["event"], "tag_cleared")

    def test_show_reads_the_clear_in_its_block_and_json(self) -> None:
        # output-contract: docs/user/manpages/wp-tag-show.md, the Cleared by line
        # given the tag cleared
        self.assertEqual(self.clear("off")[0], 0)
        self.unstamp()
        # when
        block = self.runner.invoke(main, ["wp", "tag", "show", "--all"]).output
        record = json.loads(
            self.runner.invoke(main, ["wp", "tag", "show", "--all", "--json"]).output
        )[0]
        # then
        self.assertIn(f"Cleared by:  {self.restorer}, found off", block)
        self.assertEqual((record.get("clear") or {}).get("dispatch_id"), self.restorer)

    def test_a_writer_refusal_exits_3_with_its_prose_and_books_nothing(self) -> None:
        # given a tag the ledger does not hold
        # when
        args = ["TAG-99-none", "--dispatch", self.restorer, "--position-found", "off"]
        result = self.runner.invoke(main, ["wp", "tag", "clear", *args])
        # then the writer's refusal is the verb's, exit 3 (cli.md § Exit Codes)
        self.assertEqual(result.exit_code, 3, result.output)
        self.assertIn("TAG-99-none", result.output)
        self.assertEqual(_tag_rows("tag_cleared"), [])

    def test_an_out_of_position_block_prints_its_order_and_reads_its_counts(self) -> None:
        # output-contract: the verb's docstring, the block printed then exit 3
        # given the surface found back on
        # when
        code, output = self.clear("on")
        # then the human line names the order, and the counts were read (ruling 8)
        self.assertEqual(code, 3, output)
        self.assertIn("Blocked order ORD-01-import on the operator:", output)
        (block,) = _tag_rows("work_package_blocked")
        self.assertNotIn("acceptance history unreadable", block["reason"])

    def test_json_mode_prints_the_out_of_position_block_booked(self) -> None:
        # given the surface found back on
        # when
        result = self.runner.invoke(
            main,
            [
                *("wp", "tag", "clear", "TAG-01-stamp-hook", "--dispatch", self.restorer),
                *("--position-found", "on", "--json"),
            ],
        )
        # then the block event first, never the human line, then exit 3
        self.assertEqual(result.exit_code, 3, result.output)
        self.assertTrue(result.output.startswith("{"), result.output)
        printed, _ = json.JSONDecoder().raw_decode(result.output)
        self.assertEqual(
            (printed["event"], printed["order"]), ("work_package_blocked", "ORD-01-import")
        )

    def test_an_unreadable_acceptance_history_is_named_in_the_block(self) -> None:
        # given an acceptance record on the order the replay cannot read
        row = {
            "schema": "gzkit.ledger.v1",
            "event": "acceptance_recorded",
            "id": "ORD-01-import",
            "ts": "2026-11-19T00:00:00+00:00",
            "record_type": "not-a-record-type",
            "payload": {},
        }
        with Path(".gzkit/ledger.jsonl").open("a", encoding="utf-8") as ledger:
            ledger.write(json.dumps(row) + "\n")
        # when
        code, output = self.clear("on")
        # then the block is still booked, its reason saying what it could not count
        self.assertEqual(code, 3, output)
        (block,) = _tag_rows("work_package_blocked")
        self.assertIn("(acceptance history unreadable, refutations not counted)", block["reason"])

    def test_an_out_of_position_clear_exits_3_with_the_order_blocked(self) -> None:
        # given the surface found back on, not off as it was hung (rulings 137, 140)
        # when
        code, output = self.clear("on")
        # then the order's block is booked, no clear, and the tag stays hung
        self.assertEqual(code, 3, output)
        self.assertEqual(_tag_rows("tag_cleared"), [])
        (block,) = _tag_rows("work_package_blocked")
        self.assertEqual(block["order"], "ORD-01-import")
        self.unstamp()
        printed = self.runner.invoke(main, ["wp", "tag", "show", "--json"])
        record = json.loads(printed.output)[0]
        self.assertEqual((record.get("state"), record.get("is_open")), ("authorized", True))


class TagEpilogTests(unittest.TestCase):
    def test_every_example_parses_as_a_real_invocation(self) -> None:
        # given the help of `gz wp tag` and of each of its leaves
        parser = _build_parser()
        leaves = (["wp", "tag", leaf] for leaf in ("issue", "show", "hang", "authorize", "clear"))
        examples = [
            line.strip()
            for path in (["wp", "tag"], *leaves)
            for line in (_help_parser(parser, path).epilog or "").splitlines()
            if line.strip().startswith("gz ")
        ]
        # when
        parsed = [parser.parse_args(shlex.split(example)[1:]) for example in examples]
        # then each parses, every required flag present, onto a handler
        self.assertGreaterEqual(len(examples), 11)
        self.assertTrue(all(callable(args.func) for args in parsed))


if __name__ == "__main__":
    unittest.main()
