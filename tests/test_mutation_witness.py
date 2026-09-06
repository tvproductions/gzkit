"""Mutation-sweep witness with a four-way verdict (GHI #963).

A sweep's per-guard verdict must be produced by executing the tree with that
guard — and only that guard — removed. G12 of an OBPI-0.35.0-04 sweep reported
PASSED because CPython validates a cached `.pyc` on `(mtime-seconds, size)`:
G11 and G12 deleted byte-identical text within the same clock second, so the
second subprocess imported the first mutation's bytecode.

It cuts both ways, and that is the correction this module exists to encode. A
failing run does NOT prove the mutation took effect or that a relevant assertion
caught it — an absent target, a no-op edit, a mutant that cannot import, an
unrelated failure, or a red baseline all produce a non-zero exit that looks like
a kill. A surviving run can equally conceal a mutation that never activated.

So `killed` and `survived` are claims about the guard, while `invalid` and
`inconclusive` are claims about the RUN, and the four are reported separately.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.mutation_witness import Mutation, run_mutation_sweep

_MODULE = '''"""Subject under mutation."""


def guard(value: int) -> bool:
    """Return True only for positive values."""
    if value <= 0:
        return False
    return True
'''

_TESTS = """import unittest

from subject import guard


class TestGuard(unittest.TestCase):
    def test_rejects_zero(self) -> None:
        self.assertFalse(guard(0))

    def test_accepts_one(self) -> None:
        self.assertTrue(guard(1))
"""


def _fixture(root: Path) -> Path:
    (root / "subject.py").write_text(_MODULE, encoding="utf-8")
    (root / "test_subject.py").write_text(_TESTS, encoding="utf-8")
    return root / "subject.py"


_TEST_CMD = ["python3", "-m", "unittest", "test_subject", "-v"]


class TestBaseline(unittest.TestCase):
    def test_a_red_baseline_makes_every_mutation_inconclusive(self) -> None:
        # Without a green baseline nothing downstream means anything: every
        # mutant "fails", and none of those failures is evidence about a guard.
        with TemporaryDirectory() as td:
            root = Path(td)
            source = _fixture(root)
            (root / "test_subject.py").write_text(
                "import unittest\n\n\nclass T(unittest.TestCase):\n"
                "    def test_broken(self):\n        self.fail('red baseline')\n",
                encoding="utf-8",
            )
            sweep = run_mutation_sweep(
                root,
                source,
                [Mutation(find="if value <= 0:", replace="if False:", label="g")],
                _TEST_CMD,
            )
        self.assertFalse(sweep.baseline_green)
        self.assertEqual([w.outcome for w in sweep.witnesses], ["inconclusive"])
        self.assertIn("baseline", sweep.witnesses[0].reason.lower())


class TestActivation(unittest.TestCase):
    def test_an_absent_target_is_invalid_never_a_kill(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            source = _fixture(root)
            sweep = run_mutation_sweep(
                root,
                source,
                [Mutation(find="no such text anywhere", replace="x", label="absent")],
                _TEST_CMD,
            )
        self.assertEqual(sweep.witnesses[0].outcome, "invalid")
        self.assertFalse(sweep.witnesses[0].target_present)

    def test_a_no_op_mutation_is_invalid(self) -> None:
        # Replacing text with itself leaves the tree untested; a green run here
        # would otherwise be recorded as a surviving mutant.
        with TemporaryDirectory() as td:
            root = Path(td)
            source = _fixture(root)
            sweep = run_mutation_sweep(
                root,
                source,
                [Mutation(find="return True", replace="return True", label="noop")],
                _TEST_CMD,
            )
        self.assertEqual(sweep.witnesses[0].outcome, "invalid")
        self.assertFalse(sweep.witnesses[0].source_changed)

    def test_a_mutant_that_cannot_import_is_invalid_never_a_kill(self) -> None:
        # The operator's named false-kill: a syntax error fails every test, and
        # that failure is about the edit, not about any guard being load-bearing.
        with TemporaryDirectory() as td:
            root = Path(td)
            source = _fixture(root)
            sweep = run_mutation_sweep(
                root,
                source,
                [Mutation(find="return True", replace="return ((", label="broken")],
                _TEST_CMD,
            )
        self.assertEqual(sweep.witnesses[0].outcome, "invalid")
        self.assertFalse(sweep.witnesses[0].imports)


class TestFailureCause(unittest.TestCase):
    def test_a_kill_names_the_tests_that_failed(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            source = _fixture(root)
            sweep = run_mutation_sweep(
                root,
                source,
                [Mutation(find="if value <= 0:", replace="if False:", label="guard")],
                _TEST_CMD,
            )
        w = sweep.witnesses[0]
        self.assertEqual(w.outcome, "killed")
        self.assertIn("test_rejects_zero", " ".join(w.failing_tests))

    def test_a_kill_by_unrelated_tests_is_inconclusive(self) -> None:
        # A kill must be attributed. If the only failures are outside the tests
        # said to cover this guard, the sweep witnessed collateral, not coverage.
        with TemporaryDirectory() as td:
            root = Path(td)
            source = _fixture(root)
            sweep = run_mutation_sweep(
                root,
                source,
                [
                    Mutation(
                        find="if value <= 0:",
                        replace="if False:",
                        label="guard",
                        expected_tests=["test_accepts_one"],
                    )
                ],
                _TEST_CMD,
            )
        w = sweep.witnesses[0]
        self.assertEqual(w.outcome, "inconclusive")
        self.assertIn("test_rejects_zero", " ".join(w.failing_tests))

    def test_a_surviving_mutation_is_reported_as_survived(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            source = _fixture(root)
            sweep = run_mutation_sweep(
                root,
                source,
                [Mutation(find='"""Subject under mutation."""', replace='"""x."""', label="doc")],
                _TEST_CMD,
            )
        self.assertEqual(sweep.witnesses[0].outcome, "survived")


class TestIsolation(unittest.TestCase):
    def test_each_mutation_runs_with_its_own_bytecode_cache(self) -> None:
        # GHI #963's root cause. Two mutations of EQUAL LENGTH applied within the
        # same clock second leave `(mtime-seconds, size)` unchanged, so a stale
        # .pyc validates and the second run imports the first mutant's bytecode.
        #
        # This asserts what the SUBPROCESS actually saw, not what the witness
        # recorded. The first version of this test read `w.pycache_prefix` — a
        # field populated from the TemporaryDirectory regardless of whether the
        # environment was ever set — and it survived deleting the assignment that
        # does the isolating. The sweep caught that hollowness in its own guard.
        probe = (
            "import os, pathlib; "
            "pathlib.Path('seen.txt').open('a', encoding='utf-8')"
            ".write(os.environ.get('PYTHONPYCACHEPREFIX', 'UNSET') + chr(10))"
        )
        with TemporaryDirectory() as td:
            root = Path(td)
            source = _fixture(root)
            run_mutation_sweep(
                root,
                source,
                [
                    Mutation(find="if value <= 0:", replace="if value <= 9:", label="a"),
                    Mutation(find="if value <= 0:", replace="if value <= 8:", label="b"),
                ],
                ["python3", "-c", probe],
            )
            seen = (root / "seen.txt").read_text(encoding="utf-8").split()
        self.assertNotIn("UNSET", seen, "the subprocess ran with no isolated bytecode cache")
        self.assertEqual(len(set(seen)), len(seen), "two runs shared a bytecode cache")

    def test_the_source_is_restored_after_the_sweep(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            source = _fixture(root)
            original = source.read_text(encoding="utf-8")
            run_mutation_sweep(
                root,
                source,
                [Mutation(find="return True", replace="return ((", label="broken")],
                _TEST_CMD,
            )
            self.assertEqual(source.read_text(encoding="utf-8"), original)


class TestSweepReporting(unittest.TestCase):
    def test_the_summary_separates_run_verdicts_from_guard_verdicts(self) -> None:
        # "Report invalid or inconclusive runs separately from killed and
        # survived mutations" — a sweep that lumps them reports coverage it
        # never observed.
        with TemporaryDirectory() as td:
            root = Path(td)
            source = _fixture(root)
            sweep = run_mutation_sweep(
                root,
                source,
                [
                    Mutation(find="if value <= 0:", replace="if False:", label="killed"),
                    Mutation(
                        find='"""Subject under mutation."""', replace='"""x."""', label="survived"
                    ),
                    Mutation(find="nope", replace="x", label="invalid"),
                ],
                _TEST_CMD,
            )
        self.assertEqual(sweep.killed, 1)
        self.assertEqual(sweep.survived, 1)
        self.assertEqual(sweep.invalid, 1)
        self.assertEqual(sweep.inconclusive, 0)
        self.assertFalse(sweep.is_conclusive)
