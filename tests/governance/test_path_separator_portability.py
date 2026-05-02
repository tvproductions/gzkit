"""Regression test for non-POSIX ``relative_to`` rendering (GHI #383).

``str(<Path>.relative_to(<root>))`` and ``f"{<Path>.relative_to(<root>)}"``
both call ``Path.__str__``, which emits backslash separators on Windows.
Downstream code that compares those strings against forward-slash literals
(``startswith("tests/")``, ``"docs/design/adr/pool" in str(...)``, JSON
artifacts read cross-platform, markdown links) silently fails on Windows
while POSIX CI stays green. ``.as_posix()`` produces forward slashes on
every platform and is the binding rendering shape for relative paths in
gzkit code per ``.gzkit/rules/cross-platform.md`` § File Paths.

This test fail-closes both shapes of the regression under ``src/gzkit/``.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src" / "gzkit"


def _is_relative_to_call(node: ast.AST) -> bool:
    """Return True if ``node`` is an ``X.relative_to(...)`` Call."""
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "relative_to"
    )


def _is_str_of_relative_to(node: ast.AST) -> bool:
    """Return True if ``node`` is ``str(<expr>.relative_to(<expr>))``."""
    if not (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "str"
        and len(node.args) == 1
        and not node.keywords
    ):
        return False
    return _is_relative_to_call(node.args[0])


def _is_naked_relative_to_in_fstring(node: ast.AST) -> bool:
    """Return True if ``node`` is an f-string ``{<expr>.relative_to(<expr>)}`` slot.

    Detects ``FormattedValue`` AST nodes whose value is a ``relative_to`` Call
    with no chained ``.as_posix()`` — i.e. the f-string would render via
    ``Path.__str__`` and emit native separators.
    """
    if not isinstance(node, ast.FormattedValue):
        return False
    return _is_relative_to_call(node.value)


def _scan_file(path: Path) -> list[tuple[int, str, str]]:
    """Return [(lineno, kind, source_line)] for every offending site."""
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    lines = source.splitlines()
    hits: list[tuple[int, str, str]] = []
    for node in ast.walk(tree):
        kind = ""
        if _is_str_of_relative_to(node):
            kind = "str()"
        elif _is_naked_relative_to_in_fstring(node):
            kind = "f-string"
        if not kind:
            continue
        lineno = node.lineno
        line = lines[lineno - 1] if 0 < lineno <= len(lines) else ""
        hits.append((lineno, kind, line.strip()))
    return hits


class PathSeparatorPortabilityTests(unittest.TestCase):
    """Backslash-emitting ``relative_to`` sites are forbidden under ``src/gzkit/`` (GHI #383).

    Downstream consumers (validator artifact fields, JSON output, markdown
    links, prefix comparisons against forward-slash literals) require POSIX
    separators on every platform. Both shapes — ``str(<>.relative_to(<>))``
    and f-string ``{<>.relative_to(<>)}`` — call ``Path.__str__`` and emit
    backslashes on Windows. Use ``.as_posix()`` instead.
    """

    def test_no_native_separator_relative_to_renderings_under_src(self) -> None:
        violations: list[str] = []
        for py_file in sorted(SRC_ROOT.rglob("*.py")):
            for lineno, kind, line in _scan_file(py_file):
                rel = py_file.relative_to(REPO_ROOT).as_posix()
                violations.append(f"{rel}:{lineno} [{kind}]: {line}")
        self.assertEqual(
            violations,
            [],
            msg=(
                "Found backslash-emitting `<expr>.relative_to(<expr>)` renderings "
                "under src/gzkit/. These emit native separators on Windows and break "
                "downstream forward-slash comparisons (GHI #383). Append `.as_posix()` "
                "to each. Sites:\n  " + "\n  ".join(violations)
            ),
        )


if __name__ == "__main__":
    unittest.main()
