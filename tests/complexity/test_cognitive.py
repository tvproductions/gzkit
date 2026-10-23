"""Cognitive complexity over CPython's ``ast`` (drydock RO-9 tranche 4).

Expected scores come from the worked examples in G. Ann Campbell, *Cognitive
Complexity* (SonarSource), translated to Python, and from the spec's increment
rules applied by hand. Python has no labelled ``continue``, so ``sum_of_primes``
scores 6 where the spec's Java scores 7 with its ``continue OUT`` (+1).
"""

from __future__ import annotations

import contextlib
import io
import json
import runpy
import sys
import tempfile
import textwrap
import unittest
import warnings
from pathlib import Path
from unittest import mock

from gzkit.complexity.cognitive import main, score_cognitive


def _score(source: str) -> dict[str, int]:
    return {s.name: s.score for s in score_cognitive(textwrap.dedent(source))}


class TestTheSpecWorkedExamples(unittest.TestCase):
    """The paper's own examples, translated."""

    def test_sum_of_primes_nests_three_deep(self) -> None:
        # for +1; for +2 (nesting 1); if +3 (nesting 2)
        source = """
            def sum_of_primes(limit):
                total = 0
                for i in range(1, limit + 1):
                    for j in range(2, i):
                        if i % j == 0:
                            break
                    total += i
                return total
        """
        self.assertEqual(_score(source), {"sum_of_primes": 6})

    def test_a_flat_match_costs_one(self) -> None:
        # The spec's getWords: one switch, whatever its case count.
        source = """
            def get_words(number):
                match number:
                    case 1:
                        return "one"
                    case 2:
                        return "a couple"
                    case _:
                        return "lots"
        """
        self.assertEqual(_score(source), {"get_words": 1})

    def test_try_adds_no_nesting_and_except_does(self) -> None:
        # if +1; for +2; while +3; except +1; if +2 (nesting 1): 9.
        source = """
            def my_method(condition1, condition2):
                try:
                    if condition1:
                        for i in range(10):
                            while condition2:
                                pass
                except (ValueError, KeyError):
                    if condition2:
                        pass
        """
        self.assertEqual(_score(source), {"my_method": 9})

    def test_a_nested_function_raises_nesting_and_counts_toward_its_enclosure(self) -> None:
        # The spec's myMethod2: the lambda/nested method adds nothing itself; if +2.
        source = """
            def my_method2(condition1):
                def runnable():
                    if condition1:
                        pass
                return runnable
        """
        self.assertEqual(_score(source), {"my_method2": 2})

    def test_mixed_boolean_operators_cost_one_per_sequence(self) -> None:
        # The spec's `a && b && c || d || e && f`: if +1, three sequences +3.
        source = """
            def f(a, b, c, d, e, g):
                if a and b and c or d or e and g:
                    pass
        """
        self.assertEqual(_score(source), {"f": 4})


class TestTheIncrementRules(unittest.TestCase):
    """Each increment rule, isolated so removing it changes one score."""

    def test_elif_and_else_are_hybrid_increments(self) -> None:
        source = """
            def f(a):
                if a > 1:
                    pass
                elif a > 0:
                    pass
                else:
                    pass
        """
        self.assertEqual(_score(source), {"f": 3})

    def test_else_if_is_a_nested_if_not_an_elif(self) -> None:
        # if +1; else +1; the inner if is structural at nesting 1: +2.
        source = """
            def f(a):
                if a > 1:
                    pass
                else:
                    if a > 0:
                        pass
        """
        self.assertEqual(_score(source), {"f": 4})

    def test_each_conditional_expression_is_structural(self) -> None:
        # Nine flat conditional expressions in one call, as in
        # plan.py:_build_scorecard_and_checklist, which complexipy 8.1.0 scored 0.
        args = ", ".join(f"x{i} if c{i} else y{i}" for i in range(9))
        self.assertEqual(_score(f"def f():\n    return g({args})\n"), {"f": 9})

    def test_a_conditional_expression_nests(self) -> None:
        # Outer +1; the inner one sits in a branch: +2.
        self.assertEqual(_score("def f(a, b):\n    return 1 if a else (2 if b else 3)\n"), {"f": 3})

    def test_a_like_operator_continued_in_parentheses_is_one_sequence(self) -> None:
        self.assertEqual(_score("def f(a, b, c):\n    return a and (b and c)\n"), {"f": 1})

    def test_negation_does_not_break_or_add_a_sequence(self) -> None:
        self.assertEqual(_score("def f(a, b):\n    return not (a and b)\n"), {"f": 1})

    def test_loop_else_and_try_else_are_hybrid(self) -> None:
        # for +1, for-else +1, except +1, try-else +1.
        source = """
            def f(items):
                for item in items:
                    pass
                else:
                    pass
                try:
                    pass
                except OSError:
                    pass
                else:
                    pass
        """
        self.assertEqual(_score(source), {"f": 4})

    def test_with_and_finally_add_nothing(self) -> None:
        source = """
            def f(path):
                with open(path) as handle:
                    try:
                        return handle.read()
                    finally:
                        handle.close()
        """
        self.assertEqual(_score(source), {"f": 0})

    def test_comprehension_filters_count_and_their_for_clauses_do_not(self) -> None:
        source = "def f(rows):\n    return [c for r in rows if r for c in r if c if c > 1]\n"
        self.assertEqual(_score(source), {"f": 3})

    def test_a_case_guard_is_fundamental(self) -> None:
        # match +1; guard +1.
        source = """
            def f(point):
                match point:
                    case (x, y) if x == y:
                        return "diagonal"
                    case _:
                        return "off"
        """
        self.assertEqual(_score(source), {"f": 2})

    def test_direct_recursion_costs_one_and_a_method_recurses_through_self(self) -> None:
        source = """
            def fact(n):
                return 1 if n < 2 else n * fact(n - 1)

            class Tree:
                def depth(self, node):
                    return 1 + max(self.depth(c) for c in node)
        """
        self.assertEqual(_score(source), {"fact": 2, "Tree.depth": 1})

    def test_a_default_value_is_scored_where_it_is_evaluated(self) -> None:
        # Defaults evaluate outside the body: the conditional expression is at nesting 0.
        self.assertEqual(_score("def f(a=1 if X else 2, *, b=Y or Z):\n    pass\n"), {"f": 2})

    def test_a_nested_function_decorator_is_scored_in_the_enclosure(self) -> None:
        # The decorator evaluates in the enclosing body (nesting 0); `inner` adds nothing.
        source = """
            def outer(flag):
                @register(1 if flag else 2)
                def inner():
                    pass
        """
        self.assertEqual(_score(source), {"outer": 1})

    def test_a_lambda_body_nests(self) -> None:
        # The lambda adds nothing itself; its conditional expression sits at nesting 1.
        self.assertEqual(_score("def f(c):\n    return lambda: 1 if c else 2\n"), {"f": 2})


class TestTheScoredUnits(unittest.TestCase):
    """Which functions are reported, and under what name."""

    def test_methods_carry_their_qualified_name_and_nested_defs_fold_in(self) -> None:
        source = """
            def top():
                def inner():
                    pass

            class Outer:
                class Inner:
                    def method(self):
                        pass

            if True:
                def guarded():
                    pass

            try:
                from fast import parse
            except ImportError:
                def parse():
                    pass
        """
        names = [s.name for s in score_cognitive(textwrap.dedent(source))]
        self.assertEqual(names, ["top", "Outer.Inner.method", "guarded", "parse"])

    def test_a_class_inside_a_function_raises_nesting_for_its_methods(self) -> None:
        # class +1 nesting, method +1 nesting: the if sits at nesting 2, +3.
        source = """
            def factory(flag):
                class Local:
                    def method(self):
                        if flag:
                            pass
                return Local
        """
        self.assertEqual(_score(source), {"factory": 3})

    def test_async_constructs_score_as_their_sync_forms(self) -> None:
        source = """
            async def f(stream):
                async for item in stream:
                    if item:
                        pass
        """
        self.assertEqual(_score(source), {"f": 3})

    def test_a_module_that_does_not_parse_raises(self) -> None:
        with self.assertRaises(SyntaxError):
            score_cognitive("def f(:\n")


class TestTheEntryPoint(unittest.TestCase):
    """`python -m gzkit.complexity.cognitive`: the chores' worklist and evidence."""

    def _run(self, files: dict[str, str], *args: str) -> tuple[int, str, str]:
        handle = tempfile.TemporaryDirectory()
        self.addCleanup(handle.cleanup)
        root = Path(handle.name)
        for name, source in files.items():
            (root / name).write_text(textwrap.dedent(source), encoding="utf-8")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main([root.as_posix(), *args])
        return code, out.getvalue(), err.getvalue()

    _FILES = {
        "a.py": "def low(x):\n    if x:\n        pass\n",
        "b.py": "def high(x, y):\n    if x:\n        if y:\n            pass\n",
    }

    def test_scores_print_highest_first_and_top_truncates(self) -> None:
        code, out, _ = self._run(self._FILES, "--json", "--top", "1")
        self.assertEqual(code, 0)
        rows = json.loads(out)
        self.assertEqual([(r["function"], r["score"]) for r in rows], [("high", 3)])
        self.assertEqual(set(rows[0]), {"file", "function", "line", "score"})

    def test_plain_output_is_one_function_per_line_in_score_order(self) -> None:
        code, out, _ = self._run(self._FILES)
        self.assertEqual(code, 0)
        self.assertEqual([line.split()[-1] for line in out.splitlines()], ["high", "low"])

    def test_running_the_module_exits_with_mains_code(self) -> None:
        handle = tempfile.TemporaryDirectory()
        self.addCleanup(handle.cleanup)
        bad = Path(handle.name) / "bad.py"
        bad.write_text("def f(:\n", encoding="utf-8")
        argv = ["gzkit.complexity.cognitive", bad.as_posix()]
        with (
            mock.patch.object(sys, "argv", argv),
            contextlib.redirect_stderr(io.StringIO()),
            warnings.catch_warnings(),
            self.assertRaises(SystemExit) as raised,
        ):
            warnings.simplefilter("ignore", RuntimeWarning)  # already imported by this test
            runpy.run_module("gzkit.complexity.cognitive", run_name="__main__")
        self.assertEqual(raised.exception.code, 1)

    def test_a_file_that_does_not_parse_fails_naming_it(self) -> None:
        code, out, err = self._run({"bad.py": "def f(:\n"})
        self.assertEqual((code, out), (1, ""))
        self.assertIn("bad.py: does not parse", err)


if __name__ == "__main__":
    unittest.main()
