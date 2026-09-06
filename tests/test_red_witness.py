"""Tests for the base-tree RED falsifiability witness (GHI #642).

Assertions derive from the requirement — a BEHAVIOR test must demonstrate it can fail
in the absence of its implementation — not from a run of the implementation.

The three failure classes are tested apart because collapsing them is the specific
defect GHI #642 forbids: an ImportError against a not-yet-existing symbol is a *weak*
RED and must never be recorded as an assertion RED.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from gzkit.red_witness import (
    RedWitness,
    changed_test_files,
    classify_failure,
    resolve_base_commit,
    resolve_introducing_base,
    run_red_witness,
)

# Hermetic runner: the temp fixtures have no pyproject.toml, so `uv run` would build
# an env (slow) or fail (an "error" class that would mask the assertion RED we assert).
_RUNNER = [sys.executable, "-m", "unittest"]


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


class TestClassifyFailure(unittest.TestCase):
    """`failure_class` is the verdict, not decoration."""

    def test_exit_zero_is_no_red(self) -> None:
        """A test that passes without its implementation cannot fail (Rule 6)."""
        self.assertEqual(classify_failure(0, "Ran 1 test\n\nOK"), "none")

    def test_assertion_failure_is_strong_red(self) -> None:
        self.assertEqual(classify_failure(1, "FAILED (failures=1)"), "assertion")

    def test_error_is_weak_red(self) -> None:
        self.assertEqual(classify_failure(1, "FAILED (errors=1)"), "error")

    def test_errors_dominate_failures(self) -> None:
        """A run that raised failed for the wrong reason, whatever else also failed.

        Collapsing this to `assertion` would launder a weak RED into a strong one.
        """
        self.assertEqual(classify_failure(1, "FAILED (failures=2, errors=1)"), "error")

    def test_nonzero_without_a_unittest_summary_is_an_error(self) -> None:
        """A crash, a collection failure, or a timeout is never an assertion RED."""
        self.assertEqual(classify_failure(1, "Segmentation fault"), "error")

    def test_zero_failures_and_zero_errors_but_nonzero_exit_is_an_error(self) -> None:
        self.assertEqual(classify_failure(1, "FAILED (failures=0, errors=0)"), "error")


class _GitFixture(unittest.TestCase):
    """A real git repo: a base commit, then working-tree changes on top."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        _git(["init", "-q", "-b", "main"], self.root)
        _git(["config", "user.email", "t@example.invalid"], self.root)
        _git(["config", "user.name", "t"], self.root)
        (self.root / "tests").mkdir()
        (self.root / "tests" / "__init__.py").write_text("", encoding="utf-8")

    def _commit(self, message: str) -> None:
        _git(["add", "-A"], self.root)
        _git(["commit", "-q", "-m", message], self.root)


class TestChangedTestFiles(_GitFixture):
    """Both arms matter: modified files AND brand-new untracked ones."""

    def test_modified_test_file_is_detected(self) -> None:
        (self.root / "tests" / "test_a.py").write_text("x = 1\n", encoding="utf-8")
        self._commit("base")
        (self.root / "tests" / "test_a.py").write_text("x = 2\n", encoding="utf-8")
        base = resolve_base_commit(self.root)
        self.assertEqual(changed_test_files(self.root, base), [Path("tests/test_a.py")])

    def test_untracked_new_test_file_is_detected(self) -> None:
        """A brand-new test module appears only in `ls-files --others`.

        Missing this arm would silently witness nothing for every new test file —
        the common case for a REQ's first covering test.
        """
        (self.root / "tests" / "test_a.py").write_text("x = 1\n", encoding="utf-8")
        self._commit("base")
        (self.root / "tests" / "test_new.py").write_text("y = 1\n", encoding="utf-8")
        base = resolve_base_commit(self.root)
        self.assertIn(Path("tests/test_new.py"), changed_test_files(self.root, base))

    def test_non_python_files_are_ignored(self) -> None:
        (self.root / "tests" / "test_a.py").write_text("x = 1\n", encoding="utf-8")
        self._commit("base")
        (self.root / "tests" / "fixture.txt").write_text("data\n", encoding="utf-8")
        base = resolve_base_commit(self.root)
        self.assertEqual(changed_test_files(self.root, base), [])


class TestRunRedWitness(_GitFixture):
    """The end-to-end experiment: test hunks graft onto the base tree, production does not."""

    def _seed_base(self) -> None:
        (self.root / "impl.py").write_text("", encoding="utf-8")
        self._commit("base")

    def test_new_symbol_yields_a_weak_error_red(self) -> None:
        """The GHI's named edge: a not-yet-existing symbol is an ImportError.

        Non-zero, but for the wrong reason. It must be classed `error`, never
        silently equated with an assertion RED.
        """
        self._seed_base()
        (self.root / "impl.py").write_text("def added():\n    return 1\n", encoding="utf-8")
        (self.root / "tests" / "test_impl.py").write_text(
            "import unittest\nfrom impl import added\n\n"
            "class T(unittest.TestCase):\n"
            "    def test_added(self):\n        self.assertEqual(added(), 1)\n",
            encoding="utf-8",
        )
        witness = run_red_witness(
            project_root=self.root,
            req_id="REQ-1.2.3-01-01",
            test_names=["tests.test_impl"],
            test_runner=_RUNNER,
        )
        self.assertEqual(witness.failure_class, "error")
        self.assertNotEqual(witness.exit_status, 0)
        self.assertTrue(witness.is_red, "a weak RED still witnesses falsifiability")

    def test_changed_behavior_yields_a_strong_assertion_red(self) -> None:
        """The symbol exists at base but behaves differently: a real assertion RED."""
        (self.root / "impl.py").write_text("def value():\n    return 1\n", encoding="utf-8")
        self._commit("base")
        (self.root / "impl.py").write_text("def value():\n    return 2\n", encoding="utf-8")
        (self.root / "tests" / "test_impl.py").write_text(
            "import unittest\nfrom impl import value\n\n"
            "class T(unittest.TestCase):\n"
            "    def test_value(self):\n        self.assertEqual(value(), 2)\n",
            encoding="utf-8",
        )
        witness = run_red_witness(
            project_root=self.root,
            req_id="REQ-1.2.3-01-01",
            test_names=["tests.test_impl"],
            test_runner=_RUNNER,
        )
        self.assertEqual(witness.failure_class, "assertion")
        self.assertTrue(witness.is_red)

    def test_test_that_passes_without_its_implementation_is_not_red(self) -> None:
        """The defect this whole module exists to surface.

        The test asserts nothing about the production change, so it passes against
        the base tree — it cannot fail when the business logic changes.
        """
        self._seed_base()
        (self.root / "impl.py").write_text("def added():\n    return 1\n", encoding="utf-8")
        (self.root / "tests" / "test_impl.py").write_text(
            "import unittest\n\nclass T(unittest.TestCase):\n"
            "    def test_tautology(self):\n        self.assertTrue(True)\n",
            encoding="utf-8",
        )
        witness = run_red_witness(
            project_root=self.root,
            req_id="REQ-1.2.3-01-01",
            test_names=["tests.test_impl"],
            test_runner=_RUNNER,
        )
        self.assertEqual(witness.failure_class, "none")
        self.assertEqual(witness.exit_status, 0)
        self.assertFalse(witness.is_red, "a test that passes without the code proves nothing")

    def test_production_hunks_are_never_grafted(self) -> None:
        """The asymmetry IS the experiment.

        If production files were copied in too, the test would pass and every REQ
        would report `none` — the witness would be inverted into a rubber stamp.
        """
        self._seed_base()
        (self.root / "impl.py").write_text("def added():\n    return 1\n", encoding="utf-8")
        (self.root / "tests" / "test_impl.py").write_text(
            "import unittest, pathlib\n\nclass T(unittest.TestCase):\n"
            "    def test_base_impl_is_empty(self):\n"
            "        self.assertEqual(pathlib.Path('impl.py').read_text(), '')\n",
            encoding="utf-8",
        )
        witness = run_red_witness(
            project_root=self.root,
            req_id="REQ-1.2.3-01-01",
            test_names=["tests.test_impl"],
            test_runner=_RUNNER,
        )
        # The test asserts impl.py is EMPTY in the worktree; it passes => not grafted.
        self.assertEqual(witness.exit_status, 0, "production hunks leaked into the base tree")

    def test_no_covering_tests_raises(self) -> None:
        self._seed_base()
        with self.assertRaises(ValueError):
            run_red_witness(project_root=self.root, req_id="REQ-1.2.3-01-01", test_names=[])

    def test_witness_records_the_base_commit_it_ran_against(self) -> None:
        self._seed_base()
        base = resolve_base_commit(self.root)
        (self.root / "tests" / "test_impl.py").write_text(
            "import unittest\n\nclass T(unittest.TestCase):\n"
            "    def test_ok(self):\n        self.assertTrue(True)\n",
            encoding="utf-8",
        )
        witness = run_red_witness(
            project_root=self.root,
            req_id="REQ-1.2.3-01-01",
            test_names=["tests.test_impl"],
            test_runner=_RUNNER,
        )
        self.assertEqual(witness.base_commit, base)

    def test_worktree_is_removed_after_the_run(self) -> None:
        """A leaked worktree would poison every later `git worktree` operation."""
        self._seed_base()
        (self.root / "tests" / "test_impl.py").write_text(
            "import unittest\n\nclass T(unittest.TestCase):\n"
            "    def test_ok(self):\n        self.assertTrue(True)\n",
            encoding="utf-8",
        )
        run_red_witness(
            project_root=self.root,
            req_id="REQ-1.2.3-01-01",
            test_names=["tests.test_impl"],
            test_runner=_RUNNER,
        )
        listing = subprocess.run(
            ["git", "worktree", "list"],
            cwd=self.root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        self.assertEqual(
            len(listing.stdout.strip().splitlines()), 1, "the throwaway worktree leaked"
        )


if __name__ == "__main__":
    unittest.main()


class TestResolveIntroducingBase(_GitFixture):
    """The base for LANDED work is the parent of the commit that introduced the test.

    `resolve_base_commit` returns HEAD, which is correct while work is in flight and
    vacuous once it lands: HEAD already carries the implementation, so nothing is
    withheld and the experiment has no premise (GHI #839). `--from=verify` — the
    pipeline's supported entry point for already-implemented work — runs entirely on
    that path, so the falsifiability check it mandates could never execute there
    (GHI #849).
    """

    def _land_a_covering_test(self, req: str) -> None:
        (self.root / "impl.py").write_text("", encoding="utf-8")
        self._commit("base")
        (self.root / "impl.py").write_text("def added():\n    return 1\n", encoding="utf-8")
        (self.root / "tests" / "test_impl.py").write_text(
            "import unittest\nfrom impl import added\n\n"
            "class T(unittest.TestCase):\n"
            f'    @covers("{req}")\n'
            "    def test_added(self):\n        self.assertEqual(added(), 1)\n",
            encoding="utf-8",
        )
        self._commit("land the REQ and its covering test")

    def test_it_resolves_the_parent_of_the_introducing_commit(self) -> None:
        req = "REQ-1.2.3-01-01"
        self._land_a_covering_test(req)
        introducing = subprocess.run(
            ["git", "log", "-S", f'@covers("{req}")', "--format=%H", "--reverse", "--", "tests"],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        ).stdout.split()[0]
        expected = subprocess.run(
            ["git", "rev-parse", f"{introducing}^"],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="replace",
        ).stdout.strip()
        self.assertEqual(resolve_introducing_base(self.root, req), expected)

    def test_a_req_that_never_appears_resolves_to_nothing(self) -> None:
        # Must return None rather than guess. A wrong base is worse than no base:
        # it would run the experiment against a tree with no relationship to the REQ
        # and report a confident class for it.
        self._land_a_covering_test("REQ-1.2.3-01-01")
        self.assertIsNone(resolve_introducing_base(self.root, "REQ-9.9.9-99-99"))

    def test_an_introducing_root_commit_resolves_to_nothing(self) -> None:
        # A root commit has no parent, so there is no tree that predates the test.
        req = "REQ-1.2.3-01-01"
        (self.root / "tests" / "test_impl.py").write_text(f'@covers("{req}")\n', encoding="utf-8")
        self._commit("root commit carries the covering test")
        self.assertIsNone(resolve_introducing_base(self.root, req))


class TestLandedWorkStillWitnesses(_GitFixture):
    """`--from=verify` must actually run the witness, not report `not-applicable`."""

    def _land(self, req: str, *, test_body: str) -> None:
        (self.root / "impl.py").write_text("", encoding="utf-8")
        self._commit("base")
        (self.root / "impl.py").write_text("def value():\n    return 2\n", encoding="utf-8")
        (self.root / "tests" / "test_impl.py").write_text(test_body, encoding="utf-8")
        self._commit("land the REQ and its covering test")

    def test_a_landed_req_falls_back_to_the_reconstructed_base(self) -> None:
        req = "REQ-1.2.3-01-01"
        self._land(
            req,
            test_body=(
                "import unittest\nfrom impl import value\n\n"
                "class T(unittest.TestCase):\n"
                f'    @covers("{req}")\n'
                "    def test_value(self):\n        self.assertEqual(value(), 2)\n"
            ),
        )
        witness = run_red_witness(
            project_root=self.root,
            req_id=req,
            test_names=["tests.test_impl"],
            test_runner=_RUNNER,
        )
        self.assertNotEqual(
            witness.failure_class,
            "not-applicable",
            "the witness must RUN on landed work, not merely be honest about not running",
        )
        self.assertEqual(witness.base_provenance, "reconstructed")
        # And this is the fail-open hole closed in the same breath: the module dies on
        # `from impl import value` against the old tree, which is an `error` — real
        # evidence in flight, and no evidence at all here, so the run reports that it
        # could not tell rather than banking a weak RED it did not earn.
        self.assertEqual(witness.failure_class, "error")
        self.assertFalse(witness.is_red)
        self.assertFalse(witness.is_conclusive)

    def test_a_hollow_test_is_still_caught_on_a_reconstructed_base(self) -> None:
        # The accusation that MUST survive the change. A test that passes against a
        # tree without its implementation cannot fail — reconstructing the base does
        # not soften that, it is what finally makes it observable for landed work.
        req = "REQ-1.2.3-01-02"
        # Imports nothing from `impl`, so the module loads cleanly against the old
        # tree and the test actually RUNS there — which is what makes its passing a
        # finding rather than an import accident.
        self._land(
            req,
            test_body=(
                "import unittest\n\n"
                "def covers(req):\n    return lambda fn: fn\n\n"
                "class T(unittest.TestCase):\n"
                f'    @covers("{req}")\n'
                "    def test_tautology(self):\n        self.assertTrue(True)\n"
            ),
        )
        witness = run_red_witness(
            project_root=self.root,
            req_id=req,
            test_names=["tests.test_impl"],
            test_runner=_RUNNER,
        )
        self.assertEqual(witness.failure_class, "none")
        self.assertFalse(witness.is_red)
        self.assertTrue(witness.is_conclusive, "a `none` on a reconstructed base is a real finding")

    def test_in_flight_work_still_uses_the_working_tree_base(self) -> None:
        # The fallback must not displace the in-flight path: while the production
        # change is uncommitted, HEAD is the right base and the provenance says so.
        (self.root / "impl.py").write_text("", encoding="utf-8")
        self._commit("base")
        (self.root / "impl.py").write_text("def added():\n    return 1\n", encoding="utf-8")
        (self.root / "tests" / "test_impl.py").write_text(
            "import unittest\nfrom impl import added\n\n"
            "class T(unittest.TestCase):\n"
            "    def test_added(self):\n        self.assertEqual(added(), 1)\n",
            encoding="utf-8",
        )
        witness = run_red_witness(
            project_root=self.root,
            req_id="REQ-1.2.3-01-03",
            test_names=["tests.test_impl"],
            test_runner=_RUNNER,
        )
        self.assertEqual(witness.base_provenance, "working-tree")
        self.assertEqual(witness.failure_class, "error")
        self.assertTrue(witness.is_red, "an ImportError in flight is a legitimate weak RED")


class TestErrorMeansDifferentThingsByProvenance(unittest.TestCase):
    """THE FAIL-OPEN HOLE the reconstruction opens, and the reason it is not bundled.

    A reconstructed base can be months old, so a grafted modern test meets an old tree
    and dies on an unrelated `ImportError`. `classify_failure` calls that `error`, and
    `error` counts as a weak RED — so a genuinely hollow test in old code would clear
    the gate. On a reconstructed base an `error` therefore witnesses NOTHING; in flight
    it remains a legitimate weak RED, because there the withheld hunk is the only thing
    that changed.
    """

    def _witness(self, failure_class: str, provenance: str) -> RedWitness:
        return RedWitness(
            req_id="REQ-1.2.3-01-01",
            base_commit="a" * 40,
            test_names=["t"],
            exit_status=1 if failure_class != "none" else 0,
            failure_class=failure_class,
            base_provenance=provenance,
        )

    def test_an_error_in_flight_is_a_weak_red(self) -> None:
        witness = self._witness("error", "working-tree")
        self.assertTrue(witness.is_red)
        self.assertTrue(witness.is_conclusive)

    def test_an_error_on_a_reconstructed_base_is_void_not_red(self) -> None:
        witness = self._witness("error", "reconstructed")
        self.assertFalse(witness.is_red, "an unrelated ImportError is not falsifiability")
        self.assertFalse(
            witness.is_conclusive,
            "and it is not an accusation either — the run simply could not tell",
        )

    def test_an_assertion_is_a_strong_red_on_either_base(self) -> None:
        # The assertion class is unaffected: the test reached its assertion and it
        # failed, which is the same evidence whichever tree it ran against.
        for provenance in ("working-tree", "reconstructed"):
            with self.subTest(provenance=provenance):
                witness = self._witness("assertion", provenance)
                self.assertTrue(witness.is_red)
                self.assertTrue(witness.is_conclusive)

    def test_a_not_applicable_run_is_never_conclusive(self) -> None:
        witness = self._witness("not-applicable", "working-tree")
        self.assertFalse(witness.is_red)
        self.assertFalse(witness.is_conclusive)


class TestUnrelatedDirtDoesNotFakeThePremise(_GitFixture):
    """A dirty tree must not manufacture a premise for a REQ it has nothing to do with.

    `withheld_production_files` asks *"is ANY production file uncommitted"*, never
    *"is THIS REQ's implementation withheld"*. So while any unrelated production edit
    sits in the tree, a landed REQ's covering test is grafted onto a HEAD that already
    contains its implementation, passes, and is classed `none` — a confident accusation
    against a test that was never actually tested. That is GHI #839's own class
    (*"an experiment that silently degenerates while reporting a confident verdict"*)
    surviving in a second guise.

    Observed on this repository 2026-09-06 during the GHI #849 fix, with a receipt:
    `arb red --req REQ-0.35.0-09-01` returned `failure_class=none`,
    `base_provenance=working-tree`, base `77402bdf8848` — while the only dirty
    production files were this fix's own, none of them that REQ's implementation.

    The discriminator is exact and needs no heuristic: a REQ whose `@covers` string is
    ABSENT from the test tree's history is in flight, and HEAD is its base; a REQ whose
    string is present has landed, and the reconstructed base is the only tree that
    genuinely predates it.
    """

    REQ = "REQ-1.2.3-01-09"

    def _land_then_dirty_something_unrelated(self) -> None:
        (self.root / "impl.py").write_text("def value():\n    return 1\n", encoding="utf-8")
        self._commit("base: value() returns 1")
        (self.root / "impl.py").write_text("def value():\n    return 2\n", encoding="utf-8")
        (self.root / "tests" / "test_impl.py").write_text(
            "import unittest\nfrom impl import value\n\n"
            "def covers(req):\n    return lambda fn: fn\n\n"
            "class T(unittest.TestCase):\n"
            f'    @covers("{self.REQ}")\n'
            "    def test_value(self):\n        self.assertEqual(value(), 2)\n",
            encoding="utf-8",
        )
        self._commit("land the REQ and its covering test")
        # Unrelated in-flight work — the whole point: it touches nothing this REQ owns.
        (self.root / "unrelated.py").write_text("SOMETHING = 1\n", encoding="utf-8")

    def test_a_landed_req_ignores_unrelated_dirt_and_reconstructs(self) -> None:
        self._land_then_dirty_something_unrelated()
        witness = run_red_witness(
            project_root=self.root,
            req_id=self.REQ,
            test_names=["tests.test_impl"],
            test_runner=_RUNNER,
        )
        self.assertEqual(
            witness.base_provenance,
            "reconstructed",
            "an unrelated uncommitted file is not this REQ's withheld implementation",
        )
        self.assertNotEqual(
            witness.failure_class,
            "none",
            "the test DOES depend on its implementation; a `none` here is a false accusation",
        )
        self.assertEqual(witness.failure_class, "assertion")
        self.assertTrue(witness.is_red)

    def test_an_in_flight_req_whose_test_is_unlanded_still_uses_head(self) -> None:
        # The other side, so the ordering cannot be over-applied. A REQ whose `@covers`
        # has never been committed IS in flight, HEAD is the tree that lacks its
        # implementation, and an ImportError there is a legitimate weak RED.
        (self.root / "impl.py").write_text("", encoding="utf-8")
        self._commit("base")
        (self.root / "impl.py").write_text("def added():\n    return 1\n", encoding="utf-8")
        (self.root / "tests" / "test_impl.py").write_text(
            "import unittest\nfrom impl import added\n\n"
            "def covers(req):\n    return lambda fn: fn\n\n"
            "class T(unittest.TestCase):\n"
            '    @covers("REQ-1.2.3-01-10")\n'
            "    def test_added(self):\n        self.assertEqual(added(), 1)\n",
            encoding="utf-8",
        )
        witness = run_red_witness(
            project_root=self.root,
            req_id="REQ-1.2.3-01-10",
            test_names=["tests.test_impl"],
            test_runner=_RUNNER,
        )
        self.assertEqual(witness.base_provenance, "working-tree")
        self.assertTrue(witness.is_red)


class TestReconstructedPremiseIsRecheckedNotAssumed(_GitFixture):
    """A reconstructed base that withholds NOTHING is as vacuous as HEAD was.

    Surfaced by a mutation sweep: deleting the premise re-check on the reconstructed
    base survived every other test. The case it guards is real — a covering test added
    for code that already existed, in a commit touching only `tests/`. The parent of
    that commit carries the SAME production tree, so grafting the test there proves
    nothing about it, and without the re-check the run would class the pass as `none`:
    a confident accusation manufactured entirely by reconstructing a base.

    Reconstruction widens where the witness can run; it must not widen what it is
    willing to accuse.
    """

    REQ = "REQ-1.2.3-01-11"

    def test_a_test_only_commit_yields_no_verdict_rather_than_a_false_none(self) -> None:
        (self.root / "impl.py").write_text("def value():\n    return 2\n", encoding="utf-8")
        self._commit("production, complete and unchanged hereafter")
        (self.root / "tests" / "test_impl.py").write_text(
            "import unittest\nfrom impl import value\n\n"
            "def covers(req):\n    return lambda fn: fn\n\n"
            "class T(unittest.TestCase):\n"
            f'    @covers("{self.REQ}")\n'
            "    def test_value(self):\n        self.assertEqual(value(), 2)\n",
            encoding="utf-8",
        )
        self._commit("add the covering test only — no production change")

        witness = run_red_witness(
            project_root=self.root,
            req_id=self.REQ,
            test_names=["tests.test_impl"],
            test_runner=_RUNNER,
        )
        self.assertEqual(
            witness.failure_class,
            "not-applicable",
            "nothing was withheld against EITHER base, so there is no experiment to report",
        )
        self.assertFalse(witness.is_conclusive)
