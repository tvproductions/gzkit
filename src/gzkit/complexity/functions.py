"""Per-function cyclomatic scores bound to their AST nodes (RO-9 tranche 4, GHI #1183).

The advisor, the authoring guide and the auto-chain hook diagnose each function
whose cyclomatic score crosses a `lizard_ccn` band. Radon's ``cc_visit`` supplied
that score until Radon retired; Lizard's native score replaces it, through the
one adapter that imports Lizard. Lizard scores nested functions too, which
Radon's ``cc_visit`` listed only inside their enclosing function.

A function is named by its dotted path through the classes and functions that
enclose it (``Class.method``, ``outer.inner``), the form the intrinsic-complexity
ledger events record.

Lizard skips a function whose body sits on its ``def`` line (an inline suite).
:func:`unmeasured_functions` names those so a surface can say so rather than
pass over them in silence or invent a score (operator ruling 2026-10-22, "Name
it, don't guess (Rec.)"); a body that is ``...`` alone carries no decision and
is not named.
"""

import ast
from collections.abc import Callable

from gzkit.complexity.lizard_adapter import FunctionScore, score_functions

__all__ = [
    "METRIC_KEY",
    "FunctionNode",
    "ScoredFunction",
    "is_ellipsis_stub",
    "scored_functions",
    "unmeasured_functions",
    "unmeasured_note",
]

#: The threshold-table metric the per-function surfaces read.
METRIC_KEY = "lizard_ccn"

FunctionNode = ast.FunctionDef | ast.AsyncFunctionDef
ScoredFunction = tuple[str, FunctionNode, int]
Scorer = Callable[[str, str], list[FunctionScore]]


def _qualified_nodes(tree: ast.Module) -> dict[int, tuple[str, FunctionNode]]:
    """Map each function's ``def`` line to its dotted name and node."""
    found: dict[int, tuple[str, FunctionNode]] = {}

    def visit(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                name = f"{prefix}{child.name}"
                if not isinstance(child, ast.ClassDef):
                    found[child.lineno] = (name, child)
                visit(child, f"{name}.")
            else:
                visit(child, prefix)

    visit(tree, "")
    return found


def scored_functions(
    source: str, filename: str, tree: ast.Module, *, scorer: Scorer = score_functions
) -> list[ScoredFunction]:
    """Return ``(qualname, node, cyclomatic)`` for every function Lizard scores."""
    nodes = _qualified_nodes(tree)
    return [
        (*nodes[score.line], score.cyclomatic)
        for score in scorer(source, filename)
        if score.line in nodes
    ]


def is_ellipsis_stub(node: FunctionNode) -> bool:
    """Return True when the body is ``...`` alone, after an optional docstring."""
    body = node.body
    if len(body) == 2 and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant):
        body = body[1:]
    return (
        len(body) == 1
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and body[0].value.value is Ellipsis
    )


def unmeasured_functions(
    source: str, filename: str, tree: ast.Module, *, scorer: Scorer = score_functions
) -> list[tuple[str, FunctionNode]]:
    """Return ``(qualname, node)`` for each function Lizard did not score, stubs aside."""
    measured = {score.line for score in scorer(source, filename)}
    return [
        (name, node)
        for line, (name, node) in sorted(_qualified_nodes(tree).items())
        if line not in measured and not is_ellipsis_stub(node)
    ]


def unmeasured_note(file: str, node: FunctionNode, qualname: str) -> str:
    """Return the line a surface prints for a function Lizard did not measure."""
    return (
        f"not measured: {file}:{node.lineno} {qualname} -- Lizard skips a body written on "
        "its def line, so no score is inferred; move the body below the def to measure it"
    )
