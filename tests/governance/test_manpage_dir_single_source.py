"""Regression test for hardcoded manpage path construction (GHI #425).

The manpage surface root (``docs/user/manpages``) is canonicalized as
``MANPAGE_DIR`` in :mod:`gzkit.doc_coverage.manifest`. Future surface
migrations (the GHI #418 ``commands`` -> ``manpages`` migration was the
canonical trigger) succeed only when every site that names the surface
imports the constant rather than spelling the path inline.

This test fail-closes any source-level reuse of the literal
``docs/user/manpages`` substring outside the constant's home module,
except where the substring appears in a module/function/class docstring
(documentation prose is not a runtime construction site).
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src" / "gzkit"
ALLOWLIST = {SRC_ROOT / "doc_coverage" / "manifest.py"}
SURFACE = "docs/user/manpages"


def _docstring_node_ids(tree: ast.AST) -> set[int]:
    """Return id() of every ast.Constant node that is a docstring.

    A docstring is the first statement of a module/function/class body
    when that statement is an ``Expr`` wrapping a string ``Constant``.
    """
    ids: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if not isinstance(body, list) or not body:
            continue
        first = body[0]
        if not isinstance(first, ast.Expr):
            continue
        value = first.value
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            ids.add(id(value))
    return ids


def _binop_chain_string_parts(node: ast.AST) -> list[str | None]:
    """Return the leaf-string parts of a chained ``/`` BinOp expression.

    A non-string operand (variable, call, etc.) is recorded as ``None`` so the
    surrounding caller can detect ``docs``/``user``/``manpages`` substrings
    inside a chain whose root is a non-Path expression like
    ``project_root / "docs" / "user" / "manpages"``.
    """
    if not (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div)):
        return []
    parts: list[str | None] = []
    current: ast.AST = node
    while isinstance(current, ast.BinOp) and isinstance(current.op, ast.Div):
        right = current.right
        if isinstance(right, ast.Constant) and isinstance(right.value, str):
            parts.insert(0, right.value)
        else:
            parts.insert(0, None)
        current = current.left
    if isinstance(current, ast.Constant) and isinstance(current.value, str):
        parts.insert(0, current.value)
    else:
        parts.insert(0, None)
    return parts


def _chain_spells_surface(parts: list[str | None]) -> bool:
    """Return True if the chain spells ``docs/user/manpages`` consecutively."""
    target = ("docs", "user", "manpages")
    return any(tuple(parts[i : i + 3]) == target for i in range(len(parts) - 2))


def _scan_file(path: Path) -> list[tuple[int, str]]:
    """Return [(lineno, source_excerpt)] for every offending site."""
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    docstring_ids = _docstring_node_ids(tree)
    lines = source.splitlines()
    hits: dict[int, str] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) in docstring_ids:
                continue
            if SURFACE not in node.value:
                continue
            hits.setdefault(node.lineno, lines[node.lineno - 1].strip())
            continue
        if isinstance(node, ast.JoinedStr):
            for value in node.values:
                if (
                    isinstance(value, ast.Constant)
                    and isinstance(value.value, str)
                    and SURFACE in value.value
                ):
                    hits.setdefault(node.lineno, lines[node.lineno - 1].strip())
                    break
            continue
        parts = _binop_chain_string_parts(node)
        if parts and _chain_spells_surface(parts):
            hits.setdefault(node.lineno, lines[node.lineno - 1].strip())

    return sorted(hits.items())


class ManpageDirSingleSourceTests(unittest.TestCase):
    """GHI #425 -- ``MANPAGE_DIR`` is the single source of truth."""

    def test_constant_is_canonical(self) -> None:
        from gzkit.doc_coverage.manifest import MANPAGE_DIR, MANPAGE_INDEX

        self.assertEqual(MANPAGE_DIR, Path("docs") / "user" / "manpages")
        self.assertEqual(MANPAGE_INDEX, MANPAGE_DIR / "index.md")

    def test_manpage_path_for_uses_constant(self) -> None:
        from gzkit.doc_coverage.manifest import MANPAGE_DIR, manpage_path_for

        derived = manpage_path_for("plan create")
        self.assertEqual(derived.parent, MANPAGE_DIR)
        self.assertEqual(derived.name, "plan-create.md")

    def test_no_hardcoded_manpage_surface_literals(self) -> None:
        violations: list[str] = []
        for py_file in sorted(SRC_ROOT.rglob("*.py")):
            if py_file in ALLOWLIST:
                continue
            for lineno, line in _scan_file(py_file):
                rel = py_file.relative_to(REPO_ROOT).as_posix()
                violations.append(f"  {rel}:{lineno}  {line}")
        if violations:
            self.fail(
                "Hardcoded `docs/user/manpages` literal outside the constant home "
                "(GHI #425). Import MANPAGE_DIR / MANPAGE_INDEX from "
                "gzkit.doc_coverage.manifest:\n" + "\n".join(violations)
            )


if __name__ == "__main__":
    unittest.main()
