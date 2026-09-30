"""The commit-keyed falsifiability witness (GHI #927).

Each test builds a throwaway repository whose last commit is one shape of the
direct-fix route, and asserts the verdict the witness owes it. The fixture's
production code is a one-line clamp, so a reverted guard either changes what
`clamp(-1)` returns or it does not; the commit's own tests decide which.
"""

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.arb.validator import validate_receipts
from gzkit.cli.main import _build_parser
from gzkit.commands.arb import arb_red_cmd
from gzkit.commit_witness import (
    CommitWitness,
    HunkWitness,
    _behavior,
    run_commit_witness,
    statement_mutations,
)
from gzkit.ledger import Ledger
from tests.commands.common import _isolated_git_env

_RUNNER = (sys.executable, "-m", "unittest", "-v")
_BASE = "def clamp(x):\n    return x\n"
_GUARDED = "def clamp(x):\n    if x < 0:\n        return 0\n    return x\n"
_BASE_TEST = (
    "import unittest\n\nfrom pkg.mod import clamp\n\n\n"
    "class T(unittest.TestCase):\n    def test_identity(self):\n"
    "        self.assertEqual(clamp(1), 1)\n"
)


class _CommitRepo(unittest.TestCase):
    """A throwaway repository whose last commit is the shape under test."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self._git("init", "-q", "-b", "main")
        (self.root / "pkg").mkdir()
        (self.root / "tests").mkdir()
        (self.root / "pkg" / "__init__.py").write_text("", encoding="utf-8")
        (self.root / "tests" / "__init__.py").write_text("", encoding="utf-8")
        (self.root / "pkg" / "mod.py").write_text(_BASE, encoding="utf-8")
        (self.root / "tests" / "test_mod.py").write_text(_BASE_TEST, encoding="utf-8")
        self._commit("base")

    def tearDown(self):
        self._tmp.cleanup()

    def _git(self, *args: str) -> str:
        return subprocess.run(
            ["git", "-c", "user.email=t@example.com", "-c", "user.name=t", *args],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=_isolated_git_env(),
        ).stdout.strip()

    def _commit(self, message: str) -> str:
        self._git("add", "-A")
        self._git("commit", "-qm", message)
        return self._git("rev-parse", "HEAD")

    def _add_test(self, body: str) -> None:
        path = self.root / "tests" / "test_mod.py"
        path.write_text(path.read_text(encoding="utf-8") + body, encoding="utf-8")


class TestCommitWitness(_CommitRepo):
    """Verdicts for the four commit shapes the direct-fix route produces."""

    def test_a_guard_its_commit_tests_is_driven(self):
        """Reverting the guard fails the commit's own assertion: every hunk is killed."""
        (self.root / "pkg" / "mod.py").write_text(_GUARDED, encoding="utf-8")
        self._add_test("\n    def test_negative(self):\n        self.assertEqual(clamp(-1), 0)\n")
        result = run_commit_witness(self.root, self._commit("guard + test"), runner=_RUNNER)
        self.assertEqual(result.verdict, "driven", result)
        self.assertEqual({h.outcome for h in result.hunks}, {"killed"})

    def test_a_guard_beside_an_unrelated_test_is_undriven(self):
        """The #927 instance: the commit touches tests, none drives the guard."""
        (self.root / "pkg" / "mod.py").write_text(_GUARDED, encoding="utf-8")
        self._add_test("\n    def test_two(self):\n        self.assertEqual(clamp(2), 2)\n")
        result = run_commit_witness(self.root, self._commit("guard + other test"), runner=_RUNNER)
        self.assertEqual(result.verdict, "undriven", result)
        self.assertEqual([h.path for h in result.undriven], ["pkg/mod.py"])

    def test_a_guard_with_no_test_module_is_reported_not_graded(self):
        """No test module in the commit: nothing in it can fail, so no hunk is graded."""
        (self.root / "pkg" / "mod.py").write_text(_GUARDED, encoding="utf-8")
        result = run_commit_witness(self.root, self._commit("guard only"), runner=_RUNNER)
        self.assertEqual(result.verdict, "no-tests", result)
        self.assertEqual(result.hunks, [])

    def test_a_comment_only_hunk_is_not_a_guard(self):
        """Reverting a comment changes no behavior, so it must not read as undriven."""
        (self.root / "pkg" / "mod.py").write_text("# note\n" + _BASE, encoding="utf-8")
        self._add_test("\n    def test_two(self):\n        self.assertEqual(clamp(2), 2)\n")
        result = run_commit_witness(self.root, self._commit("comment + test"), runner=_RUNNER)
        self.assertEqual(result.verdict, "no-production-hunks", result)


_HELPER = (
    "def _floor(value):\n    if value < 0:\n        return 0\n    return value\n\n\n"
    "def clamp(x):\n    return _floor(x)\n"
)
_CALLER_BASE = (
    'def clamp(x):\n    """Clamp."""\n    return x\n\n\ndef use(x):\n    return clamp(x)\n'
)
_CALLER_NEW = (
    'def clamp(x, floor):\n    """Clamp."""\n    if x < floor:\n        return floor\n'
    "    return x\n\n\ndef use(x):\n    return clamp(x, 0)\n"
)


class TestDependentHunks(_CommitRepo):
    """GHI #1153: a fix whose hunks depend on each other still gets its guards graded.

    Reverting a new helper's definition alone, or a signature without its callers,
    raises rather than asserts. The witness falls back to one guard statement at a
    time, and a hunk with no guard statement is a declaration, not an ungraded guard.
    """

    def _use_test(self, arg: int, expected: int) -> None:
        """Replace the module's tests: the new signature breaks the base ``clamp(1)``."""
        (self.root / "tests" / "test_mod.py").write_text(
            "import unittest\n\nfrom pkg.mod import use\n\n\nclass T(unittest.TestCase):\n"
            f"    def test_use(self):\n        self.assertEqual(use({arg}), {expected})\n",
            encoding="utf-8",
        )

    def test_a_helper_its_test_drives_is_driven(self):
        (self.root / "pkg" / "mod.py").write_text(_HELPER, encoding="utf-8")
        self._add_test("\n    def test_negative(self):\n        self.assertEqual(clamp(-1), 0)\n")
        result = run_commit_witness(self.root, self._commit("helper + call"), runner=_RUNNER)
        self.assertEqual(result.verdict, "driven", result)
        self.assertIn("statement", {h.unit for h in result.hunks})

    def test_a_helper_guard_no_test_drives_is_undriven(self):
        (self.root / "pkg" / "mod.py").write_text(_HELPER, encoding="utf-8")
        self._add_test("\n    def test_two(self):\n        self.assertEqual(clamp(2), 2)\n")
        result = run_commit_witness(
            self.root, self._commit("helper, no guard test"), runner=_RUNNER
        )
        self.assertEqual(result.verdict, "undriven", result)
        self.assertIn("statement", {h.unit for h in result.undriven}, result)

    def _signature_change(self) -> None:
        (self.root / "pkg" / "mod.py").write_text(_CALLER_BASE, encoding="utf-8")
        self._commit("caller base")
        (self.root / "pkg" / "mod.py").write_text(_CALLER_NEW, encoding="utf-8")

    def test_a_signature_change_its_test_drives_is_driven(self):
        self._signature_change()
        self._use_test(-1, 0)
        result = run_commit_witness(self.root, self._commit("signature + caller"), runner=_RUNNER)
        self.assertEqual(result.verdict, "driven", result)
        self.assertIn("declaration", {h.unit for h in result.hunks})

    def test_a_signature_change_no_test_drives_is_undriven(self):
        self._signature_change()
        self._use_test(2, 2)
        result = run_commit_witness(self.root, self._commit("signature, no test"), runner=_RUNNER)
        self.assertEqual(result.verdict, "undriven", result)

    def test_a_red_baseline_stays_inconclusive(self):
        """A run that cannot be graded is not rescued by statement fallback."""
        (self.root / "pkg" / "mod.py").write_text(_HELPER, encoding="utf-8")
        self._add_test("\n    def test_wrong(self):\n        self.assertEqual(clamp(-1), 5)\n")
        result = run_commit_witness(self.root, self._commit("red baseline"), runner=_RUNNER)
        self.assertEqual(result.verdict, "inconclusive", result)
        self.assertEqual({h.unit for h in result.hunks}, {"hunk"})


class TestStatementMutations(unittest.TestCase):
    """GHI #1153: which guards the statement unit builds, and that each is a valid program."""

    _SOURCE = (
        "def f(x):\n"
        "    if x < 0: return 0\n"
        "    if x > 9:\n        return 9\n    elif x == 5:\n        raise ValueError\n"
        "    return x\n"
    )

    def _mutants(self, first: int, last: int) -> dict[str, str]:
        return {
            m.label: self._SOURCE.replace(m.find, m.replace, 1)
            for m in statement_mutations(self._SOURCE, "m.py", first, last)
        }

    def test_each_guard_in_range_is_one_parseable_mutant(self):
        mutants = self._mutants(1, 8)
        self.assertEqual(
            sorted(mutants),
            ["m.py:2-2", "m.py:3-6", "m.py:4-4", "m.py:5-6", "m.py:6-6", "m.py:7-7"],
        )
        for label, source in mutants.items():
            with self.subTest(label=label):
                self.assertIsNotNone(_behavior(source))

    def test_an_elif_mutant_removes_only_its_branch(self):
        mutants = self._mutants(5, 5)
        self.assertEqual(list(mutants), ["m.py:5-6"])
        namespace: dict = {}
        exec(compile(mutants["m.py:5-6"], "m.py", "exec"), namespace)  # noqa: S102
        self.assertEqual((namespace["f"](5), namespace["f"](10)), (5, 9))

    def test_only_guards_starting_in_range_are_mutated(self):
        self.assertEqual(sorted(self._mutants(4, 4)), ["m.py:4-4"])

    def test_source_that_does_not_parse_builds_no_mutant(self):
        self.assertEqual(statement_mutations("def f(:\n", "m.py", 1, 1), [])


class TestAnnotationOnlyHunks(unittest.TestCase):
    """Which annotation changes are behavior (the 92f64debc false positive)."""

    _FUTURE = "from __future__ import annotations\n\n"

    def _neutral(self, before: str, after: str) -> bool:
        """True when reverting ``after`` to ``before`` changes no behavior."""
        return _behavior(after) == _behavior(before)

    def test_a_signature_annotation_under_the_future_import_is_not_behavior(self):
        """Under PEP 563 a signature annotation is a string nothing in gzkit reads."""
        before = self._FUTURE + "def f(x):\n    return x\n"
        after = self._FUTURE + "def f(x: int) -> tuple[int, str]:\n    return x\n"
        self.assertTrue(self._neutral(before, after))

    def test_a_signature_annotation_without_the_future_import_is_behavior(self):
        """Evaluated at definition time: a changed annotation can fail the import."""
        before = "def f(x):\n    return x\n"
        after = "def f(x: int) -> int:\n    return x\n"
        self.assertFalse(self._neutral(before, after))

    def test_a_class_field_annotation_is_behavior(self):
        """Pydantic builds its fields from class annotations."""
        before = self._FUTURE + "class M(BaseModel):\n    x: int\n"
        after = self._FUTURE + "class M(BaseModel):\n    x: str\n"
        self.assertFalse(self._neutral(before, after))

    def test_an_annotation_read_by_its_decorator_is_behavior(self):
        """A decorator outside the known annotation-blind set may read the signature."""
        before = self._FUTURE + "@validate_call\ndef f(x: int):\n    return x\n"
        after = self._FUTURE + "@validate_call\ndef f(x: str):\n    return x\n"
        self.assertFalse(self._neutral(before, after))

    def test_a_staticmethod_signature_annotation_is_not_behavior(self):
        """staticmethod never reads annotations, so its methods stay neutral."""
        before = self._FUTURE + "class C:\n    @staticmethod\n    def f(x):\n        return x\n"
        after = (
            self._FUTURE
            + "class C:\n    @staticmethod\n    def f(x: int) -> int:\n        return x\n"
        )
        self.assertTrue(self._neutral(before, after))


class TestArbRedCommitCli(unittest.TestCase):
    """`gz arb red --commit`: its argument contract and the exit code each verdict owes."""

    def _parse(self, *argv: str):
        with contextlib.redirect_stderr(io.StringIO()):
            return _build_parser().parse_args(["arb", "red", *argv])

    def test_commit_alone_parses_without_a_req(self):
        args = self._parse("--commit", "HEAD")
        self.assertEqual((args.commit, args.req), ("HEAD", None))

    def test_req_and_commit_together_are_refused(self):
        with self.assertRaises(SystemExit):
            self._parse("--req", "REQ-0.1.0-01-01", "--commit", "HEAD")

    def test_neither_target_is_refused(self):
        with self.assertRaises(SystemExit):
            self._parse()

    def test_the_parsed_command_routes_commit_to_the_witness(self):
        """Dispatch through the parser, not the function: the lambda must pass --commit on."""
        witness = CommitWitness(commit="a" * 40, verdict="no-tests", detail="d")
        with (
            tempfile.TemporaryDirectory() as tmp,
            mock.patch("gzkit.commit_witness.run_commit_witness", return_value=witness) as run,
            mock.patch("gzkit.commands.common.get_project_root", return_value=Path(tmp)),
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            args = self._parse("--commit", "abc123")
            with self.assertRaises(SystemExit) as exited:  # _arb propagates the status
                args.func(args)
        self.assertEqual(exited.exception.code, 1)
        self.assertEqual(run.call_args.args[1], "abc123")

    def _exit_for(self, verdict: str, outcome: str = "killed") -> tuple[int, str]:
        hunks = [HunkWitness(path="p.py", label="p.py:1-2", outcome=outcome)]
        witness = CommitWitness(commit="a" * 40, verdict=verdict, hunks=hunks, detail="d")
        err = io.StringIO()
        with (
            tempfile.TemporaryDirectory() as tmp,
            mock.patch("gzkit.commit_witness.run_commit_witness", return_value=witness),
            mock.patch("gzkit.commands.common.get_project_root", return_value=Path(tmp)),
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(err),
        ):
            return arb_red_cmd(commit="HEAD"), err.getvalue()

    def test_a_driven_commit_exits_zero(self):
        self.assertEqual(self._exit_for("driven")[0], 0)

    def test_an_undriven_hunk_exits_one_and_names_it(self):
        code, err = self._exit_for("undriven", outcome="survived")
        self.assertEqual(code, 1)
        self.assertIn("p.py:1-2", err)

    def test_a_commit_without_tests_exits_one(self):
        self.assertEqual(self._exit_for("no-tests")[0], 1)

    def test_an_inconclusive_run_is_not_a_failure_but_says_so(self):
        code, err = self._exit_for("inconclusive", outcome="inconclusive")
        self.assertEqual(code, 0)
        self.assertIn("INCONCLUSIVE", err)

    def test_a_witness_that_cannot_run_is_an_internal_error(self):
        with (
            tempfile.TemporaryDirectory() as tmp,
            mock.patch("gzkit.commit_witness.run_commit_witness", side_effect=RuntimeError("x")),
            mock.patch("gzkit.commands.common.get_project_root", return_value=Path(tmp)),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            self.assertEqual(arb_red_cmd(commit="HEAD"), 2)


class TestCommitModeRecordsItsVerdict(unittest.TestCase):
    """GHI #1152: a commit-mode verdict is cited at GHI close, so it must be resolvable."""

    def _run(self, verdict: str, outcome: str) -> tuple[int, Path]:
        hunks = [
            HunkWitness(path="p.py", label="p.py:1-2", outcome=outcome, reason="r"),
            HunkWitness(path="p.py", label="p.py:9-9", outcome="killed"),
        ]
        witness = CommitWitness(
            commit="b" * 40, verdict=verdict, hunks=hunks, test_modules=["tests.t"], detail="d"
        )
        root = Path(self._tmp.name)
        self.stdout = io.StringIO()
        with (
            mock.patch("gzkit.commit_witness.run_commit_witness", return_value=witness),
            mock.patch("gzkit.commands.common.get_project_root", return_value=root),
            contextlib.redirect_stdout(self.stdout),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            return arb_red_cmd(commit="HEAD"), root

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def _receipts(self, root: Path) -> list[dict]:
        return [
            json.loads(p.read_text(encoding="utf-8"))
            for p in sorted((root / "artifacts" / "receipts").glob("arb-red-commit-*.json"))
        ]

    def test_the_receipt_records_what_the_run_found(self):
        code, root = self._run("undriven", "survived")
        (receipt,) = self._receipts(root)
        self.assertEqual(receipt["commit"], "b" * 40)
        self.assertEqual(receipt["verdict"], "undriven")
        self.assertEqual(receipt["exit_status"], code)
        self.assertEqual(
            [(h["label"], h["outcome"]) for h in receipt["hunks"]],
            [("p.py:1-2", "survived"), ("p.py:9-9", "killed")],
        )

    def test_the_receipt_satisfies_its_schema(self):
        _, root = self._run("driven", "killed")
        result = validate_receipts(root=root / "artifacts" / "receipts", limit=-1)
        self.assertEqual((result.scanned, result.invalid), (1, 0), result.errors)

    def test_the_ledger_names_the_receipt(self):
        _, root = self._run("inconclusive", "inconclusive")
        (receipt,) = self._receipts(root)
        events = [
            e
            for e in Ledger(root / ".gzkit" / "ledger.jsonl").read_all()
            if e.event == "red_commit_receipt_emitted"
        ]
        self.assertEqual([e.id for e in events], [receipt["run_id"]])
        self.assertEqual(events[0].extra["verdict"], "inconclusive")

    def test_the_printed_receipt_id_resolves_to_the_receipt(self):
        """ghi-close cites the id the run prints, so that id must name the file written."""
        _, root = self._run("driven", "killed")
        (receipt,) = self._receipts(root)
        printed = dict(
            field.split("=", 1) for field in self.stdout.getvalue().split() if "=" in field
        )
        self.assertEqual(printed.get("receipt"), receipt["run_id"])

    def test_a_commit_without_tests_is_recorded_too(self):
        code, root = self._run("no-tests", "killed")
        self.assertEqual(code, 1)
        self.assertEqual([r["verdict"] for r in self._receipts(root)], ["no-tests"])


class TestArbRedHelpOutputForm(unittest.TestCase):
    """The operator-facing help names both modes (output-contract: help text is the contract)."""

    def _help(self, *argv: str) -> str:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit):
            _build_parser().parse_args([*argv, "--help"])
        return out.getvalue()

    def test_red_help_describes_both_modes_and_an_example(self):
        text = " ".join(self._help("arb", "red").split())
        self.assertIn("--req: reconstruct the base tree", text)
        self.assertIn("direct-fix route", text)
        self.assertIn("gz arb red --commit HEAD", text)

    def test_arb_listing_summarizes_red_as_req_or_commit(self):
        self.assertIn("by REQ or by commit", " ".join(self._help("arb").split()))


if __name__ == "__main__":
    unittest.main()
