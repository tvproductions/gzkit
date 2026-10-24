"""Per-function Lizard scores bound to AST nodes (RO-9 tranche 4, GHI #1183).

``gzkit.complexity.functions`` is the one place the advisor, the guide and the
auto-chain hook read cyclomatic scores from. A function Lizard skips (a body on
its ``def`` line) is named, never scored by guess (operator ruling 2026-10-22,
"Name it, don't guess (Rec.)"); a body of ``...`` alone carries no decision.
"""

import ast
import unittest

from gzkit.complexity.functions import (
    is_ellipsis_stub,
    scored_functions,
    unmeasured_functions,
    unmeasured_note,
)

_NESTED = """\
class C:
    def method(self, x):
        if x:
            return 1

        def inner():
            return 2

        return inner


async def free(y):
    return y
"""


def _function(source: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
    node = ast.parse(source).body[0]
    if isinstance(node, ast.ClassDef):
        node = node.body[0]
    assert isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
    return node


class ScoredFunctionsTest(unittest.TestCase):
    def test_names_follow_the_enclosing_classes_and_functions(self) -> None:
        names = {
            name for name, _node, _score in scored_functions(_NESTED, "m.py", ast.parse(_NESTED))
        }
        self.assertEqual(names, {"C.method", "C.method.inner", "free"})

    def test_each_score_is_lizards_cyclomatic_number(self) -> None:
        scores = {
            name: score
            for name, _node, score in scored_functions(_NESTED, "m.py", ast.parse(_NESTED))
        }
        self.assertEqual(scores["C.method"], 2)
        self.assertEqual(scores["free"], 1)


class EllipsisStubTest(unittest.TestCase):
    def test_a_bare_ellipsis_body_is_a_stub(self) -> None:
        self.assertTrue(is_ellipsis_stub(_function("def f(): ...\n")))

    def test_a_documented_ellipsis_body_is_a_stub(self) -> None:
        self.assertTrue(is_ellipsis_stub(_function('def f():\n    """Doc."""\n    ...\n')))

    def test_a_docstring_alone_is_not_a_stub(self) -> None:
        self.assertFalse(is_ellipsis_stub(_function('def f():\n    """Doc."""\n')))

    def test_a_real_body_is_not_a_stub(self) -> None:
        self.assertFalse(is_ellipsis_stub(_function("def f():\n    return 1\n")))


class UnmeasuredFunctionsTest(unittest.TestCase):
    def test_an_inline_body_is_unmeasured_and_named(self) -> None:
        source = "def one(x): return x\n"
        (found,) = unmeasured_functions(source, "m.py", ast.parse(source))
        self.assertEqual(found[0], "one")

    def test_an_inline_stub_is_not_named(self) -> None:
        source = "class P:\n    def f(self) -> None: ...\n"
        self.assertEqual(unmeasured_functions(source, "m.py", ast.parse(source)), [])

    def test_the_note_names_the_file_line_and_function(self) -> None:
        source = "\n\ndef one(x): return x\n"
        ((name, node),) = unmeasured_functions(source, "m.py", ast.parse(source))
        note = unmeasured_note("pkg/m.py", node, name)
        self.assertTrue(note.startswith("not measured: pkg/m.py:3 one "))


if __name__ == "__main__":
    unittest.main()
