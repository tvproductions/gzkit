"""The airlock on the work package (RO-14 act 6, GHI #1185).

A work package enters through the airlock at commencement and leaves it at
acceptance, and the exit names every file the package changed outside its declared
footprint. Operator rulings 2026-11-01, by selection: "Repair declares
(Recommended)", "Task trailer (Recommended)" and "Refuse at accept (Recommended)".

The package's commits are real commits in a real repository, because attribution
is what these tests are for: a hand-built list of changed files would hide a
trailer the exit does not read.
"""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import TYPE_CHECKING, Any
from unittest import mock

from gzkit.cli import main
from gzkit.ledger import Ledger
from gzkit.models.catalog import load_catalog
from gzkit.work_package_transit import package_changes, package_slice
from tests.commands.common import CliRunner, _isolated_git_env, _quick_init
from tests.commands.test_wp_acceptance import _record as _delivery_record
from tests.commands.test_wp_acceptance import _req, _seed

if TYPE_CHECKING:
    from gzkit.airlock.model import TransitObservation

_PACKAGE = "WP-01-loop"
_TRAILER = "TASK-wp-01-loop-#1185"
_MODULE = "src/gzkit/inside/"
_INSIDE = "src/gzkit/inside/fix.py"
_OUTSIDE = "src/gzkit/outside.py"
_EVIDENCE = ("--evidence", "e")
_CHANGE_ORDER = (
    "wp",
    "change",
    _PACKAGE,
    "--rung",
    "change_order",
    "--approver",
    "operator",
    "--change",
    "c",
    "--superseded",
    "s",
    "--work-stopped",
)


def _record(modules: list[str], kind: str = "repair") -> dict[str, object]:
    repair = kind == "repair"
    return {
        "id": _PACKAGE,
        "kind": kind,
        "outcome": None if repair else "H1",
        "issues": [1185] if repair else [],
        "lane": "lite" if repair else None,
        "aliases": [],
        "modules": modules,
        "initial_conditions": "NA",
        "procedure": "NA",
        "test_and_inspection": "NA",
        "system_restoration": "NA",
        "oqe": [],
        "alterations": [],
        "departures": [],
    }


def _seed_store(package: dict[str, object]) -> None:
    catalog = Path("data") / "catalog"
    catalog.mkdir(parents=True, exist_ok=True)
    for kind, entries in (
        ("families", []),
        ("outcomes", []),
        ("reqs", []),
        ("externals", []),
        ("work_packages", [package]),
    ):
        text = json.dumps({"_doc": "Fixture catalog.", kind: entries})
        (catalog / f"{kind}.json").write_text(text, encoding="utf-8")


def _git(*args: str) -> None:
    subprocess.run(  # noqa: S603
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
        check=True,
        capture_output=True,
        env=_isolated_git_env(),
    )


def _commit(path: str, trailer: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("x = 1\n", encoding="utf-8")
    _git("add", path)
    _git("commit", "--no-verify", "-m", f"work on {path}\n\nTask: {trailer}\n")


def _changes() -> TransitObservation:
    changes = package_changes(Path.cwd(), _PACKAGE)
    if changes is None:
        msg = "git should show this repository's changes"
        raise AssertionError(msg)
    return changes


class _AirlockCase(unittest.TestCase):
    modules: tuple[str, ...] = (_MODULE,)

    def setUp(self) -> None:
        # Acceptance is not this suite's subject: tests/commands/test_wp_acceptance.py is.
        gate = mock.patch("gzkit.commands.wp.acceptance_blockers", return_value=[])
        gate.start()
        self.addCleanup(gate.stop)
        self.runner = CliRunner()
        self.enterContext(self.runner.isolated_filesystem())
        _quick_init()
        Path(_MODULE).mkdir(parents=True)
        _seed_store(_record(list(self.modules)))
        _git("init", "--quiet")
        _git("add", "-A")
        _git("commit", "--no-verify", "--quiet", "-m", "baseline")

    def _wp(self, *args: str) -> str:
        result = self.runner.invoke(main, ["wp", *args])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        return result.output

    def _commence(self) -> None:
        self._wp("initiate", _PACKAGE, "--operator-text", "go")
        self._wp("freeze", _PACKAGE, "--risk-note", "r", "--review-receipt", "v", "--evidence", "e")
        self._wp("commence", _PACKAGE, "--evidence", "e")

    def _rows(self, event: str) -> list[dict[str, Any]]:
        ledger = Ledger(Path(".gzkit") / "ledger.jsonl")
        return [
            {"id": row.id, **row.extra}
            for row in ledger.query(event_type=event)
            if row.id == _PACKAGE
        ]


class TestEntry(_AirlockCase):
    def test_commencing_books_one_airlock_in_for_the_package(self) -> None:
        self._commence()
        rows = self._rows("airlock_in")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["decision"], "proceed")

    def test_gz_airlock_in_takes_a_work_package_and_reads_its_footprint(self) -> None:
        result = self.runner.invoke(
            main, ["airlock", "in", "--target", _PACKAGE, "--dry-run", "--json"]
        )
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertEqual(json.loads(result.output)["seam_map"]["bodies"], 1)
        self.assertEqual(self._rows("airlock_in"), [])


class TestAttribution(_AirlockCase):
    def test_a_commit_is_the_packages_when_its_task_trailer_names_the_package(self) -> None:
        _commit(_INSIDE, _TRAILER)
        changes = _changes()
        self.assertEqual(changes.commits, 1)
        self.assertIn(_INSIDE, changes.files)

    def test_a_defect_fix_under_its_own_trailer_is_not_attributed(self) -> None:
        _commit(_OUTSIDE, "TASK-defect-fix-#9")
        changes = _changes()
        self.assertEqual(changes.commits, 0)
        self.assertNotIn(_OUTSIDE, changes.files)

    def test_a_longer_package_number_is_a_different_package(self) -> None:
        _commit(_OUTSIDE, "TASK-wp-01-loopback")
        _commit("src/gzkit/other.py", "TASK-wp-011-loop")
        self.assertEqual(_changes().commits, 0)

    def test_a_bare_package_trailer_counts(self) -> None:
        _commit(_INSIDE, "TASK-wp-01-loop")
        self.assertEqual(_changes().commits, 1)

    def test_an_uncommitted_change_is_read_with_the_packages_commits(self) -> None:
        Path("src/gzkit").mkdir(parents=True, exist_ok=True)
        Path(_OUTSIDE).write_text("x = 1\n", encoding="utf-8")
        self.assertIn(_OUTSIDE, _changes().files)

    def test_a_committed_rename_shows_the_path_it_left(self) -> None:
        _commit(_OUTSIDE, "TASK-baseline")
        Path(_INSIDE).parent.mkdir(parents=True, exist_ok=True)
        _git("mv", _OUTSIDE, _INSIDE)
        _git("commit", "--no-verify", "-m", f"move\n\nTask: {_TRAILER}\n")
        files = _changes().files
        self.assertIn(_OUTSIDE, files)
        self.assertIn(_INSIDE, files)

    def test_a_staged_rename_shows_the_path_it_left(self) -> None:
        _commit(_OUTSIDE, "TASK-baseline")
        _git("mv", _OUTSIDE, _INSIDE)
        self.assertIn(_OUTSIDE, _changes().files)

    def test_a_non_ascii_path_reads_as_itself(self) -> None:
        name = "src/gzkit/na\u00efve.py"
        _commit(name, _TRAILER)
        self.assertIn(name, _changes().files)

    def test_outside_a_repository_nothing_is_observed(self) -> None:
        with tempfile.TemporaryDirectory() as plain:
            self.assertIsNone(package_changes(Path(plain).resolve(), _PACKAGE))

    def test_a_tree_git_cannot_read_observes_nothing(self) -> None:
        with mock.patch("gzkit.work_package_transit.read_changed_files", return_value=None):
            self.assertIsNone(package_changes(Path.cwd(), _PACKAGE))


class TestAccept(_AirlockCase):
    def test_a_package_inside_its_footprint_is_accepted_and_exits_clean(self) -> None:
        self._commence()
        _commit(_INSIDE, _TRAILER)
        self._wp("accept", _PACKAGE, "--evidence", "e")
        rows = self._rows("airlock_out")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["verdict"], "clean")
        self.assertEqual(rows[0]["observed_commits"], 1)
        self.assertEqual(rows[0]["observed_files"], 2)  # The file and the dirty ledger.

    def test_a_passed_exit_seals_the_files_it_read(self) -> None:
        self._commence()
        _commit(_INSIDE, _TRAILER)
        self._wp("accept", _PACKAGE, "--evidence", "e")
        self.assertIn(_INSIDE, self._rows("airlock_out")[0]["changed_files"])

    def test_a_file_outside_the_footprint_refuses_acceptance_and_names_it(self) -> None:
        self._commence()
        _commit(_OUTSIDE, _TRAILER)
        result = self.runner.invoke(main, ["wp", "accept", _PACKAGE, "--evidence", "e"])
        self.assertEqual(result.exit_code, 3, msg=result.output)
        self.assertIn(_OUTSIDE, result.output)
        self.assertIn("gz wp change", result.output)
        self.assertEqual(self._rows("airlock_out"), [])
        self.assertNotIn("accepted", self._wp("show", _PACKAGE))

    def test_a_defect_fix_under_its_own_trailer_does_not_refuse(self) -> None:
        self._commence()
        _commit(_OUTSIDE, "TASK-defect-fix-#9")
        self._wp("accept", _PACKAGE, "--evidence", "e")
        self.assertEqual(self._rows("airlock_out")[0]["verdict"], "clean")

    def test_gzkits_own_records_never_refuse(self) -> None:
        self._commence()
        ledger = Path(".gzkit") / "ledger.jsonl"
        _git("add", ledger.as_posix())
        _git("commit", "--no-verify", "-m", f"records\n\nTask: {_TRAILER}\n")
        self._wp("accept", _PACKAGE, "--evidence", "e")

    def test_the_order_that_adds_a_path_lets_the_package_be_accepted(self) -> None:
        self._commence()
        _commit(_OUTSIDE, _TRAILER)
        self._wp(
            "change",
            _PACKAGE,
            "--rung",
            "change_order",
            "--approver",
            "operator",
            "--change",
            "the fix reaches outside.py",
            "--superseded",
            "inside.py only",
            "--work-stopped",
            "--module",
            _OUTSIDE,
        )
        self.assertIn(_OUTSIDE, load_catalog(Path.cwd()).work_packages[0].modules)
        self._wp("accept", _PACKAGE, "--evidence", "e")
        self.assertEqual(self._rows("airlock_out")[0]["verdict"], "clean")

    def test_the_order_recovers_a_file_the_package_moved_away(self) -> None:
        _commit(_OUTSIDE, "TASK-baseline")
        self._commence()
        _git("mv", _OUTSIDE, _INSIDE)
        _git("commit", "--no-verify", "-m", f"move\n\nTask: {_TRAILER}\n")
        refused = self.runner.invoke(main, ["wp", "accept", _PACKAGE, "--evidence", "e"])
        self.assertEqual(refused.exit_code, 3, msg=refused.output)
        self.assertIn(_OUTSIDE, refused.output)
        order = self.runner.invoke(main, [*_CHANGE_ORDER, "--module", _OUTSIDE])
        self.assertEqual(order.exit_code, 0, msg=order.output)
        self._wp("accept", _PACKAGE, "--evidence", "e")

    def test_a_revert_does_not_clear_a_committed_file(self) -> None:
        self._commence()
        _commit(_OUTSIDE, _TRAILER)
        _git("revert", "--no-edit", "HEAD")
        result = self.runner.invoke(main, ["wp", "accept", _PACKAGE, "--evidence", "e"])
        self.assertEqual(result.exit_code, 3, msg=result.output)
        self.assertIn("a revert does not remove it", " ".join(result.output.split()))

    def test_a_stopped_package_is_excused_and_the_exit_still_names_the_file(self) -> None:
        self._commence()
        _commit(_OUTSIDE, _TRAILER)
        with mock.patch("gzkit.commands.wp.took_stopping_exit", return_value=True):
            self._wp("accept", _PACKAGE, "--evidence", "e")
        rows = self._rows("airlock_out")
        self.assertEqual(rows[0]["verdict"], "surface")
        self.assertIn(_OUTSIDE, rows[0]["drift"])

    def test_a_declared_footprint_with_no_way_to_read_changes_refuses(self) -> None:
        self._commence()
        with mock.patch("gzkit.work_package_transit.package_changes", return_value=None):
            result = self.runner.invoke(main, ["wp", "accept", _PACKAGE, "--evidence", "e"])
        self.assertEqual(result.exit_code, 3, msg=result.output)
        self.assertIn("git", result.output)

    def test_a_footprint_edited_by_hand_after_freeze_moves_nothing(self) -> None:
        self._commence()
        _commit(_OUTSIDE, _TRAILER)
        _seed_store(_record([_INSIDE, _OUTSIDE]))
        result = self.runner.invoke(main, ["wp", "accept", _PACKAGE, "--evidence", "e"])
        self.assertEqual(result.exit_code, 3, msg=result.output)
        self.assertIn(_OUTSIDE, result.output)

    def test_an_exit_that_cannot_read_changes_is_not_clean(self) -> None:
        self._commence()
        with (
            mock.patch("gzkit.work_package_transit.package_changes", return_value=None),
            mock.patch("gzkit.commands.wp.took_stopping_exit", return_value=True),
        ):
            self._wp("accept", _PACKAGE, "--evidence", "e")
        row = self._rows("airlock_out")[0]
        self.assertEqual(row["verdict"], "unobserved")
        self.assertNotIn("observed_files", row)


class TestUndeclared(_AirlockCase):
    modules = ()

    def test_an_undeclared_repair_package_cannot_freeze(self) -> None:
        self._wp("initiate", _PACKAGE, "--operator-text", "go")
        result = self.runner.invoke(
            main,
            ["wp", "freeze", _PACKAGE, "--risk-note", "r", "--review-receipt", "v", *_EVIDENCE],
        )
        self.assertEqual(result.exit_code, 3, msg=result.output)
        self.assertIn("gz wp change", result.output)
        states = [row["to_state"] for row in self._rows("work_package_transitioned")]
        self.assertNotIn("frozen", states)

    def test_an_undeclared_slice_reads_undeclared_and_never_clean(self) -> None:
        _commit(_OUTSIDE, _TRAILER)
        result = self.runner.invoke(
            main, ["airlock", "out", "--target", _PACKAGE, "--dry-run", "--json"]
        )
        report = json.loads(result.output)
        self.assertEqual(report["verdict"], "undeclared")
        self.assertEqual(report["drift"], [])

    def test_the_refusals_recovery_from_no_footprint_reaches_a_freeze(self) -> None:
        self._wp("initiate", _PACKAGE, "--operator-text", "go")
        result = self.runner.invoke(main, [*_CHANGE_ORDER, "--module", _MODULE])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self._wp("freeze", _PACKAGE, "--risk-note", "r", "--review-receipt", "v", *_EVIDENCE)

    def test_a_freeze_from_the_wrong_state_names_the_lifecycle(self) -> None:
        result = self.runner.invoke(
            main,
            ["wp", "freeze", _PACKAGE, "--risk-note", "r", "--review-receipt", "v", *_EVIDENCE],
        )
        self.assertEqual(result.exit_code, 3, msg=result.output)
        self.assertIn("lifecycle", result.output)

    def test_a_package_slice_with_no_modules_is_marked_undeclared(self) -> None:
        package = load_catalog(Path.cwd()).work_packages[0]
        self.assertTrue(package_slice(package).undeclared)


class TestFreeze(_AirlockCase):
    modules = ("src/gzkit/absent.py",)

    def _refused_freeze(self) -> str:
        self._wp("initiate", _PACKAGE, "--operator-text", "go")
        result = self.runner.invoke(
            main,
            ["wp", "freeze", _PACKAGE, "--risk-note", "r", "--review-receipt", "v", *_EVIDENCE],
        )
        self.assertEqual(result.exit_code, 3, msg=result.output)
        return result.output

    def test_a_module_that_does_not_exist_cannot_freeze(self) -> None:
        self.assertIn("src/gzkit/absent.py", self._refused_freeze())

    def test_a_change_order_cannot_add_a_path_that_does_not_exist(self) -> None:
        self._wp("initiate", _PACKAGE, "--operator-text", "go")
        result = self.runner.invoke(
            main,
            [*_CHANGE_ORDER, "--module", "no/such"],
        )
        self.assertEqual(result.exit_code, 3, msg=result.output)
        self.assertNotIn("no/such", load_catalog(Path.cwd()).work_packages[0].modules)

    def test_the_refusals_recovery_reaches_a_freeze(self) -> None:
        self._refused_freeze()
        result = self.runner.invoke(
            main, [*_CHANGE_ORDER, "--drop-module", self.modules[0], "--module", _MODULE]
        )
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self._wp("freeze", _PACKAGE, "--risk-note", "r", "--review-receipt", "v", *_EVIDENCE)

    def test_a_frozen_footprint_drops_nothing(self) -> None:
        _seed_store(_record([_MODULE]))
        self._commence()
        result = self.runner.invoke(main, [*_CHANGE_ORDER, "--drop-module", _MODULE])
        self.assertEqual(result.exit_code, 3, msg=result.output)
        self.assertIn(_MODULE, load_catalog(Path.cwd()).work_packages[0].modules)

    def test_a_directory_module_must_end_with_a_slash(self) -> None:
        _seed_store(_record(["src/gzkit/inside"]))
        self.assertIn("must end", self._refused_freeze())

    def test_a_store_edit_before_freeze_is_not_sealed(self) -> None:
        _seed_store(_record(["**"]))
        self.assertIn("names no literal path", " ".join(self._refused_freeze().split()))


class TestConfiguredLedger(_AirlockCase):
    def test_the_verbs_read_and_exempt_a_configured_ledger(self) -> None:
        config = Path(".gzkit.json")
        record = json.loads(config.read_text(encoding="utf-8"))
        record["paths"]["ledger"] = "custom/ledger.jsonl"
        config.write_text(json.dumps(record), encoding="utf-8")
        _git("add", config.as_posix())
        _git("commit", "--no-verify", "-m", "configure\n\nTask: TASK-baseline\n")
        Path("custom").mkdir()
        moved = Path("custom/ledger.jsonl")
        moved.write_text(
            (Path(".gzkit") / "ledger.jsonl").read_text(encoding="utf-8"), encoding="utf-8"
        )
        self._commence()
        _commit(_INSIDE, _TRAILER)
        self._wp("accept", _PACKAGE, "--evidence", "e")
        result = self.runner.invoke(
            main, ["airlock", "out", "--target", _PACKAGE, "--dry-run", "--json"]
        )
        self.assertEqual(json.loads(result.output)["verdict"], "clean", msg=result.output)
        self.assertIn('"airlock_out"', moved.read_text(encoding="utf-8"))


class TestFootprintOrders(_AirlockCase):
    def test_a_path_dropped_before_the_freeze_stays_out(self) -> None:
        self._wp("initiate", _PACKAGE, "--operator-text", "go")
        Path(_OUTSIDE).write_text("x = 1\n", encoding="utf-8")
        self._order("--module", _OUTSIDE)
        self._order("--drop-module", _OUTSIDE)
        self._wp("freeze", _PACKAGE, "--risk-note", "r", "--review-receipt", "v", *_EVIDENCE)
        self._wp("commence", _PACKAGE, "--evidence", "e")
        _commit(_OUTSIDE, _TRAILER)
        result = self.runner.invoke(main, ["wp", "accept", _PACKAGE, "--evidence", "e"])
        self.assertEqual(result.exit_code, 3, msg=result.output)

    def test_a_drop_before_initiation_names_the_state(self) -> None:
        result = self.runner.invoke(main, [*_CHANGE_ORDER, "--drop-module", _MODULE])
        self.assertEqual(result.exit_code, 3, msg=result.output)
        self.assertIn("not initiated", " ".join(result.output.split()))

    def _order(self, *args: str) -> None:
        result = self.runner.invoke(main, [*_CHANGE_ORDER, *args])
        self.assertEqual(result.exit_code, 0, msg=result.output)


class TestMirrors(_AirlockCase):
    modules = (".gzkit/skills/gz-wp/",)

    def setUp(self) -> None:
        super().setUp()
        Path(self.modules[0]).mkdir(parents=True, exist_ok=True)

    def test_a_mirror_of_a_file_inside_the_footprint_follows_it(self) -> None:
        self._commence()
        _commit(".gzkit/skills/gz-wp/SKILL.md", _TRAILER)
        _commit(".claude/skills/gz-wp/SKILL.md", _TRAILER)
        self._wp("accept", _PACKAGE, "--evidence", "e")
        self.assertEqual(self._rows("airlock_out")[0]["verdict"], "clean")

    def test_a_mirror_of_a_file_outside_the_footprint_is_refused(self) -> None:
        self._commence()
        mirror = ".claude/skills/gz-check/SKILL.md"
        _commit(mirror, _TRAILER)
        result = self.runner.invoke(main, ["wp", "accept", _PACKAGE, "--evidence", "e"])
        self.assertEqual(result.exit_code, 3, msg=result.output)
        self.assertIn(mirror, " ".join(result.output.split()))


class TestVendorMirror(_AirlockCase):
    modules = (".claude/skills/gz-wp/SKILL.md",)

    def test_a_generated_vendor_mirror_cannot_freeze(self) -> None:
        Path(self.modules[0]).parent.mkdir(parents=True, exist_ok=True)
        Path(self.modules[0]).write_text("x\n", encoding="utf-8")
        self._wp("initiate", _PACKAGE, "--operator-text", "go")
        result = self.runner.invoke(
            main,
            ["wp", "freeze", _PACKAGE, "--risk-note", "r", "--review-receipt", "v", *_EVIDENCE],
        )
        self.assertEqual(result.exit_code, 3, msg=result.output)


class TestDelivery(unittest.TestCase):
    def test_a_delivery_package_freezes_and_reads_undeclared_until_ro11(self) -> None:
        runner = CliRunner()
        self.enterContext(runner.isolated_filesystem())
        _quick_init()
        _seed([_delivery_record(_PACKAGE, kind="delivery")], [_req()])
        for args in (
            ["initiate", _PACKAGE, "--operator-text", "go"],
            [
                "freeze",
                _PACKAGE,
                "--baseline",
                "REQ-7@2",
                "--risk-note",
                "r",
                "--review-receipt",
                "v",
                *_EVIDENCE,
            ],
            ["commence", _PACKAGE, "--evidence", "e"],
        ):
            result = runner.invoke(main, ["wp", *args])
            self.assertEqual(result.exit_code, 0, msg=result.output)
        result = runner.invoke(
            main, ["airlock", "out", "--target", _PACKAGE, "--dry-run", "--json"]
        )
        self.assertEqual(json.loads(result.output)["verdict"], "undeclared")


class TestDirectoryFootprint(_AirlockCase):
    modules = ("src/gzkit/",)

    def test_a_directory_module_covers_its_tree(self) -> None:
        self._commence()
        _commit(_OUTSIDE, _TRAILER)
        self._wp("accept", _PACKAGE, "--evidence", "e")
        self.assertEqual(self._rows("airlock_out")[0]["verdict"], "clean")


class TestRecord(_AirlockCase):
    def test_new_declares_modules_on_a_repair_package(self) -> None:
        with mock.patch("gzkit.commands.wp.tag_issues"):
            self._wp(
                "new",
                "--kind",
                "repair",
                "--slug",
                "next",
                "--issue",
                "7",
                "--lane",
                "lite",
                "--module",
                _MODULE,
            )
        held = load_catalog(Path.cwd()).work_packages[1]
        self.assertEqual(held.modules, (_MODULE,))

    def test_a_delivery_package_holds_no_modules_of_its_own(self) -> None:
        result = self.runner.invoke(
            main, ["wp", "new", "--kind", "delivery", "--slug", "d", "--module", "src/a.py"]
        )
        self.assertEqual(result.exit_code, 3, msg=result.output)
        self.assertIn("reads from its outcome", result.output)

    def test_only_a_change_order_moves_the_footprint(self) -> None:
        self._commence()
        Path(_OUTSIDE).write_text("x = 1\n", encoding="utf-8")
        result = self.runner.invoke(
            main,
            [
                "wp",
                "change",
                _PACKAGE,
                "--rung",
                "attachment",
                "--approver",
                "operator",
                "--change",
                "c",
                "--module",
                _OUTSIDE,
            ],
        )
        self.assertEqual(result.exit_code, 3, msg=result.output)
        self.assertIn("does not move a footprint", result.output)
        self.assertNotIn(_OUTSIDE, load_catalog(Path.cwd()).work_packages[0].modules)

    def test_a_change_order_the_ladder_refuses_writes_neither_store_nor_ledger(self) -> None:
        self._commence()
        Path(_OUTSIDE).write_text("x = 1\n", encoding="utf-8")
        before = len(self._rows("work_package_changed"))
        result = self.runner.invoke(
            main,
            [
                "wp",
                "change",
                _PACKAGE,
                "--rung",
                "change_order",
                "--approver",
                "operator",
                "--change",
                "c",
                "--work-stopped",
                "--module",
                _OUTSIDE,
            ],
        )
        self.assertEqual(result.exit_code, 3, msg=result.output)
        self.assertNotIn(_OUTSIDE, load_catalog(Path.cwd()).work_packages[0].modules)
        self.assertEqual(len(self._rows("work_package_changed")), before)

    def test_a_module_that_names_no_path_is_refused_by_the_stores_rule(self) -> None:
        self._wp("initiate", _PACKAGE, "--operator-text", "go")
        for module in ("**", "*", "?*", "*/*", "**/*", "*\\*", "*.*", "*.py", "s*", "./src", "-x"):
            with self.subTest(module=module):
                result = self.runner.invoke(main, [*_CHANGE_ORDER, f"--module={module}"])
                self.assertEqual(result.exit_code, 3, msg=result.output)
                self.assertIn("names no literal path", " ".join(result.output.split()))

    def test_a_narrow_glob_is_a_path(self) -> None:
        self._wp("initiate", _PACKAGE, "--operator-text", "go")
        result = self.runner.invoke(main, [*_CHANGE_ORDER, "--module", "src/**/*.py"])
        self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_new_holds_a_module_to_the_path_check(self) -> None:
        result = self.runner.invoke(
            main,
            [
                "wp",
                "new",
                "--kind",
                "repair",
                "--slug",
                "n",
                "--issue",
                "7",
                "--lane",
                "lite",
                "--module",
                "no/such.py",
            ],
        )
        self.assertEqual(result.exit_code, 3, msg=result.output)
        self.assertEqual(len(load_catalog(Path.cwd()).work_packages), 1)

    def test_show_json_reads_the_ledgers_footprint(self) -> None:
        self._commence()
        _seed_store(_record([_MODULE, "elsewhere/"]))
        result = self.runner.invoke(main, ["wp", "show", _PACKAGE, "--json"])
        self.assertEqual(json.loads(result.output)["footprint"], [_MODULE])

    def test_show_states_the_footprint(self) -> None:
        self.assertIn(f"footprint: {_MODULE}", self._wp("show", _PACKAGE))


class TestGzAirlockOut(_AirlockCase):
    def test_the_verb_reports_a_package_and_never_refuses(self) -> None:
        _commit(_OUTSIDE, _TRAILER)
        result = self.runner.invoke(
            main, ["airlock", "out", "--target", _PACKAGE, "--dry-run", "--json"]
        )
        self.assertEqual(result.exit_code, 0, msg=result.output)
        report = json.loads(result.output)
        self.assertEqual(report["verdict"], "surface")
        self.assertIn(_OUTSIDE, report["drift"])
        self.assertEqual(self._rows("airlock_out"), [])

    def test_an_unknown_package_exits_1(self) -> None:
        result = self.runner.invoke(main, ["airlock", "out", "--target", "WP-99-none"])
        self.assertEqual(result.exit_code, 1, msg=result.output)


if __name__ == "__main__":
    unittest.main()
