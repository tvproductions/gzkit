"""The production-write fence on a work package (RO-14 act 4, GHI #1206).

A control that holds at launch must hold at re-entry. The fence has to refuse a
blocked, accepted or stopped package, or `gz wp dispatch` refusing it is a
sentence: an agent would simply write the code without a dispatch. Operator
ruling 2026-11-01, by selection: "Fence on the WP surface (Recommended)".

The generated hook runs as a real process here, because a hook whose import or
ordering is wrong fails open silently.
"""

import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.cli import main
from gzkit.hooks import guards
from gzkit.hooks.scripts.routing import _pipeline_gate_script
from gzkit.work_package_fence import (
    FencedPackage,
    fenced_packages,
    work_package_write_message,
)
from tests.commands.common import CliRunner, _quick_init

_PACKAGE = "WP-01-loop"
_OTHER = "WP-02-other"
_SOURCE = "src/gzkit/example.py"
_TEST = "tests/test_example.py"
_BOTH_STAGED = f"M\t{_SOURCE}\nM\t{_TEST}\n"
_REQ = "REQ-7"
_OUTCOME = {
    "code": "H1.1",
    "statement": "s",
    "owner": "o",
    "user_facing": False,
    "governed_by": [],
    "depends_on": [],
    "feature": None,
    "retired": False,
}
_CATALOG_REQ = {
    "id": _REQ,
    "specialization": "catalog",
    "member_of": "H1.1",
    "statement": "The package carries its frozen requirement.",
    "criteria": [{"state_or_input": "i", "required_outcome": "o", "evidence": "e"}],
    "kind": "BEHAVIOR",
    "revision": 2,
    "derives_from": [],
    "applies_to": [],
}


def _record(package: str) -> dict[str, object]:
    """A delivery package: a repair package's run is its orders' (RP-12 ruling 44)."""
    return {
        "id": package,
        "kind": "delivery",
        "outcome": "H1.1",
        "issues": [],
        "lane": None,
        "aliases": [],
        "modules": [],
        "initial_conditions": "NA",
        "procedure": "NA",
        "test_and_inspection": "NA",
        "system_restoration": "NA",
        "oqe": [],
        "alterations": [],
        "departures": [],
    }


def _seed_store() -> None:
    catalog = Path("data") / "catalog"
    catalog.mkdir(parents=True, exist_ok=True)
    for kind, entries in (
        ("families", []),
        ("outcomes", [_OUTCOME]),
        ("reqs", [_CATALOG_REQ]),
        ("externals", []),
        ("work_packages", [_record(_PACKAGE), _record(_OTHER)]),
        ("orders", []),
    ):
        text = json.dumps({"_doc": "Fixture catalog.", kind: entries})
        (catalog / f"{kind}.json").write_text(text, encoding="utf-8")


class _FenceCase(unittest.TestCase):
    def setUp(self) -> None:
        # Acceptance is not this suite's subject: tests/commands/test_wp_acceptance.py is.
        gate = mock.patch("gzkit.commands.wp.acceptance_blockers", return_value=[])
        gate.start()
        self.addCleanup(gate.stop)
        # Nor is the footprint: tests/commands/test_wp_airlock.py is, in a real repository.
        scope = mock.patch("gzkit.commands.wp.footprint_refusal", return_value=None)
        scope.start()
        self.addCleanup(scope.stop)
        self.runner = CliRunner()
        self.enterContext(self.runner.isolated_filesystem())
        _quick_init()
        _seed_store()

    def _wp(self, *args: str) -> None:
        result = self.runner.invoke(main, ["wp", *args])
        self.assertEqual(result.exit_code, 0, msg=result.output)

    def _commence(self, package: str = _PACKAGE) -> None:
        self._wp("initiate", package, "--operator-text", "go")
        self._wp(
            "freeze", package, "--risk-note", "r", "--review-receipt", "v", "--evidence", "e",
            "--baseline", f"{_REQ}@2",
        )  # fmt: skip
        self._wp("commence", package, "--evidence", "e")

    def _block(self) -> None:
        self._wp("block", _PACKAGE, "--reason", "stuck", "--next-action", "rule")

    def _unblock(self) -> None:
        self._wp("unblock", _PACKAGE, "--ruling", "go on", "--operator", "g0")

    def _accept(self) -> None:
        self._wp("accept", _PACKAGE, "--evidence", "e")

    def _close(self) -> None:
        self._wp(
            "close", _PACKAGE, "--decision", "proceed", "--attestor", "g0",
            "--residual-risk", "none", "--evidence", "e",
        )  # fmt: skip

    def _reasons(self) -> dict[str, str]:
        return {fence.work_package: fence.reason for fence in fenced_packages(Path())}


class TestWhoIsFenced(_FenceCase):
    def test_a_commenced_package_is_not_fenced(self) -> None:
        self._commence()
        self.assertEqual(self._reasons(), {})

    def test_a_blocked_package_is_fenced_until_the_operator_clears_it(self) -> None:
        self._commence()
        self._block()
        self.assertEqual(self._reasons(), {_PACKAGE: "blocked"})
        self._unblock()
        self.assertEqual(self._reasons(), {})

    def test_a_block_before_commencement_fences_too(self) -> None:
        self._wp("initiate", _PACKAGE, "--operator-text", "go")
        self._block()
        self.assertEqual(self._reasons(), {_PACKAGE: "blocked"})

    def test_an_accepted_package_is_fenced_until_it_closes(self) -> None:
        self._commence()
        self._accept()
        self.assertEqual(self._reasons(), {_PACKAGE: "accepted"})
        self._close()
        self.assertEqual(self._reasons(), {})

    def test_one_blocked_package_fences_beside_a_working_one(self) -> None:
        self._commence()
        self._commence(_OTHER)
        self._block()
        self.assertEqual(self._reasons(), {_PACKAGE: "blocked"})

    def test_a_damaged_catalog_lifts_no_block(self) -> None:
        self._commence()
        self._block()
        Path("data/catalog/work_packages.json").write_text("{", encoding="utf-8")
        self.assertEqual(self._reasons(), {_PACKAGE: "blocked"})

    def test_an_unreadable_ledger_fences_the_tree(self) -> None:
        self._commence()
        with Path(".gzkit/ledger.jsonl").open("a", encoding="utf-8") as ledger:
            ledger.write("{not a row\n{}\n")
        self.assertEqual(set(self._reasons().values()), {"unreadable"})

    def test_a_transition_row_missing_its_state_fences_the_tree(self) -> None:
        row = {"schema": "gzkit.ledger.v1", "event": "work_package_transitioned"}
        row |= {"id": _PACKAGE, "ts": "2026-11-01T00:00:00+00:00", "work_package": _PACKAGE}
        with Path(".gzkit/ledger.jsonl").open("a", encoding="utf-8") as ledger:
            ledger.write(json.dumps(row) + "\n")
        self.assertEqual(set(self._reasons().values()), {"unreadable"})

    def test_a_missing_ledger_is_a_project_with_no_package(self) -> None:
        Path(".gzkit/ledger.jsonl").unlink()
        self.assertEqual(self._reasons(), {})

    def test_a_torn_final_line_does_not_fence_a_healthy_tree(self) -> None:
        self._commence()
        with Path(".gzkit/ledger.jsonl").open("a", encoding="utf-8") as ledger:
            ledger.write('{"schema": "gzkit.le')
        self.assertEqual(self._reasons(), {})

    def test_a_project_with_no_package_fences_nothing(self) -> None:
        self.assertEqual(self._reasons(), {})


class TestTheExits(_FenceCase):
    """The states `gz wp dispatch` refuses after, or without, a block."""

    def _to_the_bound(self) -> None:
        self._commence()
        self._dispatch("Implementer")
        self._dispatch("SpecReviewer")
        self._dispatch("Implementer")
        self._dispatch("Implementer")

    def _dispatch(self, role: str) -> None:
        self._wp("dispatch", _PACKAGE, "--role", role, "--model", "m", "--req", _REQ)

    def _exit(self, name: str) -> None:
        self._block()
        self._wp("unblock", _PACKAGE, "--ruling", name, "--operator", "g0", "--exit", name)

    def _refused(self) -> bool:
        args = ["wp", "dispatch", _PACKAGE, "--role", "Implementer", "--model", "m"]
        return self.runner.invoke(main, [*args, "--req", _REQ]).exit_code != 0

    def test_the_last_admitted_cycle_is_not_fenced(self) -> None:
        self._to_the_bound()
        self.assertTrue(self._refused())
        self.assertEqual(self._reasons(), {})

    def test_terminate_fences_until_the_package_closes(self) -> None:
        self._to_the_bound()
        self._exit("terminate")
        self.assertTrue(self._refused())
        self.assertEqual(self._reasons(), {_PACKAGE: "stopped"})
        self._accept()
        self.assertEqual(self._reasons(), {_PACKAGE: "accepted"})
        self._close()
        self.assertEqual(self._reasons(), {})

    def test_a_hold_leaves_the_package_open(self) -> None:
        self._to_the_bound()
        self._exit("hold")
        self.assertEqual(self._reasons(), {})

    def test_an_accepted_package_refuses_a_block_and_keeps_its_fence(self) -> None:
        """RP-12 ruling 69: an accepted run takes no block; ruling 58 still fences it."""
        self._commence()
        self._accept()
        result = self.runner.invoke(
            main, ["wp", "block", _PACKAGE, "--reason", "stuck", "--next-action", "rule"]
        )
        self.assertEqual(result.exit_code, 3, msg=result.output)
        self.assertEqual(self._reasons(), {_PACKAGE: "accepted"})


class TestTheRecoveryProse(unittest.TestCase):
    """Each refusal gives the next step with the flags its verb requires."""

    def _refusal(self, reason: str) -> str:
        fence = FencedPackage.model_validate({"work_package": _PACKAGE, "reason": reason})
        return work_package_write_message(fence, _SOURCE)

    def test_each_reason_names_a_runnable_recovery(self) -> None:
        for reason, *needed in (
            ("blocked", f"gz wp unblock {_PACKAGE}", "--ruling", "--operator", "--exit"),
            ("accepted", f"gz wp close {_PACKAGE}", "--decision", "--attestor", "--residual-risk"),
            ("stopped", f"gz wp accept {_PACKAGE}", "--evidence", f"gz wp close {_PACKAGE}"),
            ("unreadable", "gz validate --ledger"),
        ):
            with self.subTest(reason=reason):
                message = self._refusal(reason)
                self.assertIn(_SOURCE, message)
                for text in needed:
                    self.assertIn(text, message)


class TestTheCommitGuard(_FenceCase):
    """The arm no tool choice evades: it reads the staged diff."""

    def _guard(self, staged: str = _BOTH_STAGED) -> int:
        with mock.patch.object(guards, "_run_git", return_value=staged):
            return guards.forbid_post_authoring_src_commits(Path.cwd())

    def test_a_blocked_package_refuses_a_production_commit(self) -> None:
        self._commence()
        self._block()
        with contextlib.redirect_stdout(io.StringIO()) as printed:
            self.assertEqual(self._guard(), 1)
        self.assertIn(_SOURCE, printed.getvalue())
        self.assertIn(f"{_PACKAGE} is blocked", printed.getvalue())
        self.assertIn(f"gz wp unblock {_PACKAGE}", printed.getvalue())

    def test_a_rename_into_production_is_refused(self) -> None:
        self._commence()
        self._block()
        self.assertEqual(self._guard(f"R100\t{_TEST}\t{_SOURCE}\n"), 1)

    def test_an_unreadable_ledger_refuses_the_commit(self) -> None:
        self._commence()
        with Path(".gzkit/ledger.jsonl").open("a", encoding="utf-8") as ledger:
            ledger.write("{not a row\n{}\n")
        self.assertEqual(self._guard(), 1)

    def test_an_accepted_package_refuses_a_production_commit(self) -> None:
        self._commence()
        self._accept()
        self.assertEqual(self._guard(), 1)

    def test_a_commenced_package_admits_it(self) -> None:
        self._commence()
        self.assertEqual(self._guard(), 0)

    def test_tests_stay_committable_under_a_block(self) -> None:
        self._commence()
        self._block()
        self.assertEqual(self._guard(f"M\t{_TEST}\n"), 0)

    def test_a_deletion_is_not_authoring(self) -> None:
        self._commence()
        self._block()
        self.assertEqual(self._guard(f"D\t{_SOURCE}\n"), 0)

    def test_it_binds_with_no_plans_directory(self) -> None:
        self._commence()
        self._block()
        shutil.rmtree(".claude/plans", ignore_errors=True)
        self.assertEqual(self._guard(), 1)


class TestTheGeneratedHook(_FenceCase):
    """The write arm, run as the process Claude Code runs."""

    def _hook(self, rel_path: str) -> subprocess.CompletedProcess[str]:
        payload = {
            "cwd": str(Path.cwd()),
            "tool_input": {"file_path": str(Path.cwd() / rel_path)},
        }
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "pipeline-gate.py"
            script.write_text(_pipeline_gate_script(), encoding="utf-8")
            return subprocess.run(  # noqa: S603 - this interpreter and a script the test wrote
                [sys.executable, str(script)],
                input=json.dumps(payload),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

    def test_a_blocked_package_refuses_the_write_and_says_how_to_recover(self) -> None:
        self._commence()
        self._block()
        result = self._hook(_SOURCE)
        self.assertEqual(result.returncode, 2, msg=result.stderr)
        self.assertIn(f"{_PACKAGE} is blocked", result.stderr)
        self.assertIn(f"gz wp unblock {_PACKAGE}", result.stderr)

    def test_an_accepted_package_refuses_the_write_and_says_how_to_recover(self) -> None:
        self._commence()
        self._accept()
        result = self._hook(_SOURCE)
        self.assertEqual(result.returncode, 2, msg=result.stderr)
        self.assertIn("gz wp close", result.stderr)

    def test_tests_stay_writable_under_a_block(self) -> None:
        self._commence()
        self._block()
        self.assertEqual(self._hook(_TEST).returncode, 0)

    def test_a_commenced_package_admits_the_write(self) -> None:
        self._commence()
        result = self._hook(_SOURCE)
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_clearing_the_block_reopens_the_write(self) -> None:
        self._commence()
        self._block()
        self._unblock()
        self.assertEqual(self._hook(_SOURCE).returncode, 0)


if __name__ == "__main__":
    unittest.main()
