"""Cognitive complexity over CPython's own ``ast`` (drydock RO-9 tranche 4).

The operator ruled complexipy a poor replacement and selected a gzkit-owned scorer
(2026-10-22, *"gzkit-owned, stdlib ast (Rec.)"*). This module implements G. Ann
Campbell, *Cognitive Complexity: A new way of measuring understandability*
(SonarSource, 2016-2023), for Python:

- **Structural** (+1, plus the nesting level): ``if``, a conditional expression,
  ``for`` / ``async for`` / ``while``, each ``except`` clause, ``match``.
- **Hybrid** (+1, no nesting increment): ``elif``, ``else`` (on ``if``, a loop or
  ``try``).
- **Fundamental** (+1): each sequence of like boolean operators (``a and b and c``
  is one, ``a and b or c`` two); each comprehension ``if`` filter and each ``case``
  guard; direct recursion, once per function.
- **Nesting** rises inside the bodies of the structural increments, ``elif`` and
  ``else``, and inside a nested ``def``, ``lambda`` or class, whose complexity
  counts toward the function that encloses it (the spec's lambda and nested-method
  rule). ``try``, ``finally`` and ``with`` add nothing.

Python has no labelled ``break`` or ``continue`` and no ``goto``, so the spec's
jump increments never apply. Comprehension ``for`` clauses add nothing: the spec
ignores a structure that shorthands several statements readably into one.

Parsing is CPython's, so every syntax the running interpreter accepts is scored by
the grammar that defines it. The scored unit is a function with no enclosing
function: a module-level ``def`` or a method, named by its qualified name.
"""

from __future__ import annotations

import ast

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["CognitiveScore", "score_cognitive"]

_FunctionNode = ast.FunctionDef | ast.AsyncFunctionDef
_LOOPS = (ast.For, ast.AsyncFor, ast.While)


class CognitiveScore(BaseModel):
    """The cognitive complexity of one function with no enclosing function."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(..., description="Qualified name: `Class.method` or `function`")
    line: int = Field(..., description="Line of the `def`")
    score: int = Field(..., description="Cognitive complexity per the SonarSource spec")


class _Scorer:
    """Score one function; reads the source to tell ``elif`` from ``else: if``."""

    def __init__(self, lines: list[str], function: _FunctionNode) -> None:
        self._lines = lines
        self._function = function

    def total(self) -> int:
        body = self._block(self._function.body, 0)
        return body + self._recursion() + self._signature(self._function, 0)

    def _signature(self, node: _FunctionNode | ast.Lambda, nesting: int) -> int:
        """Score default values, which are evaluated outside the body."""
        return sum(self._node(d, nesting) for d in node.args.defaults + node.args.kw_defaults if d)

    def _block(self, statements: list[ast.stmt], nesting: int) -> int:
        return sum(self._node(statement, nesting) for statement in statements)

    def _children(self, node: ast.AST, nesting: int) -> int:
        return sum(self._node(child, nesting) for child in ast.iter_child_nodes(node))

    def _node(self, node: ast.AST, nesting: int) -> int:
        if isinstance(node, ast.If):
            return 1 + nesting + self._if(node, nesting)
        if isinstance(node, _LOOPS):
            return self._loop(node, nesting)
        if isinstance(node, ast.Try | ast.TryStar):
            return self._try(node, nesting)
        if isinstance(node, ast.Match):
            return self._match(node, nesting)
        if isinstance(node, ast.IfExp):
            branches = self._node(node.body, nesting + 1) + self._node(node.orelse, nesting + 1)
            return 1 + nesting + self._node(node.test, nesting) + branches
        if isinstance(node, ast.BoolOp):
            return self._bool_op(node, nesting)
        if isinstance(node, ast.comprehension):
            return len(node.ifs) + self._children(node, nesting)
        if isinstance(node, _FunctionNode | ast.Lambda):
            return self._nested_function(node, nesting)
        if isinstance(node, ast.ClassDef):
            return self._children(node, nesting + 1)
        return self._children(node, nesting)

    def _if(self, node: ast.If, nesting: int) -> int:
        """Score an ``if`` after its own increment: test, body and the chain below it."""
        score = self._node(node.test, nesting) + self._block(node.body, nesting + 1)
        if not node.orelse:
            return score
        if (elif_node := self._elif(node.orelse)) is not None:
            return score + 1 + self._if(elif_node, nesting)
        return score + 1 + self._block(node.orelse, nesting + 1)

    def _elif(self, orelse: list[ast.stmt]) -> ast.If | None:
        """Return the ``elif`` an ``else`` branch spells, or None for a plain ``else``.

        The AST spells ``elif`` and ``else: if`` alike, as a lone nested ``If``; only
        the source at the node's position tells them apart.
        """
        node = orelse[0]
        spelled = self._lines[node.lineno - 1].startswith("elif", node.col_offset)
        return node if isinstance(node, ast.If) and spelled else None

    def _loop(self, node: ast.For | ast.AsyncFor | ast.While, nesting: int) -> int:
        head = (
            self._node(node.test, nesting)
            if isinstance(node, ast.While)
            else self._node(node.target, nesting) + self._node(node.iter, nesting)
        )
        score = 1 + nesting + head + self._block(node.body, nesting + 1)
        if node.orelse:
            score += 1 + self._block(node.orelse, nesting + 1)
        return score

    def _try(self, node: ast.Try | ast.TryStar, nesting: int) -> int:
        score = self._block(node.body, nesting) + self._block(node.finalbody, nesting)
        for handler in node.handlers:
            handled = self._node(handler.type, nesting) if handler.type else 0
            score += 1 + nesting + handled + self._block(handler.body, nesting + 1)
        if node.orelse:
            score += 1 + self._block(node.orelse, nesting + 1)
        return score

    def _match(self, node: ast.Match, nesting: int) -> int:
        score = 1 + nesting + self._node(node.subject, nesting)
        for case in node.cases:
            if case.guard is not None:
                score += 1 + self._node(case.guard, nesting + 1)
            score += self._block(case.body, nesting + 1)
        return score

    def _bool_op(self, node: ast.BoolOp, nesting: int) -> int:
        """+1 for this sequence; an operand continuing the same operator adds nothing."""
        score = 1
        for value in node.values:
            if isinstance(value, ast.BoolOp) and isinstance(value.op, type(node.op)):
                score += self._bool_op(value, nesting) - 1
            else:
                score += self._node(value, nesting)
        return score

    def _nested_function(self, node: _FunctionNode | ast.Lambda, nesting: int) -> int:
        decorators = (
            0
            if isinstance(node, ast.Lambda)
            else sum(self._node(d, nesting) for d in node.decorator_list)
        )
        body = (
            self._node(node.body, nesting + 1)
            if isinstance(node, ast.Lambda)
            else self._block(node.body, nesting + 1)
        )
        return decorators + self._signature(node, nesting) + body

    def _recursion(self) -> int:
        """+1 when the function calls itself by name, or as ``self.``/``cls.`` for a method."""
        name = self._function.name
        for node in ast.walk(self._function):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if isinstance(func, ast.Name) and func.id == name:
                return 1
            if (
                isinstance(func, ast.Attribute)
                and func.attr == name
                and isinstance(func.value, ast.Name)
                and func.value.id in {"self", "cls"}
            ):
                return 1
        return 0


def _scored_functions(tree: ast.Module) -> list[tuple[str, _FunctionNode]]:
    """Return (qualname, node) for each function with no enclosing function."""
    found: list[tuple[str, _FunctionNode]] = []

    def visit(body: list[ast.stmt], prefix: str) -> None:
        for statement in body:
            if isinstance(statement, _FunctionNode):
                found.append((f"{prefix}{statement.name}", statement))
            elif isinstance(statement, ast.ClassDef):
                visit(statement.body, f"{prefix}{statement.name}.")
            elif isinstance(statement, ast.If | ast.Try | ast.TryStar | ast.With | ast.AsyncWith):
                # Conditional and guarded definitions at module or class level.
                for field in ("body", "orelse", "finalbody"):
                    visit(getattr(statement, field, []), prefix)
                for handler in getattr(statement, "handlers", []):
                    visit(handler.body, prefix)

    visit(tree.body, "")
    return found


def score_cognitive(source: str, filename: str = "<source>") -> list[CognitiveScore]:
    """Score every function in *source* with no enclosing function.

    Raises ``SyntaxError`` when *source* does not parse; the caller decides how a
    module that cannot be measured is reported.
    """
    tree = ast.parse(source, filename=filename)
    lines = source.splitlines()
    return [
        CognitiveScore(name=name, line=node.lineno, score=_Scorer(lines, node).total())
        for name, node in _scored_functions(tree)
    ]
