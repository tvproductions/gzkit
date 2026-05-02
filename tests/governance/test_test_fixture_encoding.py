"""Regression test for fixture I/O without ``encoding="utf-8"`` (GHI #384).

``Path.write_text(content)`` and ``Path.read_text()`` without an explicit
``encoding=`` kwarg defer to the system locale. On Windows that is cp1252;
on POSIX it is usually UTF-8. A test fixture that writes em-dash / smart
quotes / arrows under cp1252 and is then read back as UTF-8 (or vice
versa) raises ``UnicodeDecodeError``. POSIX CI never sees the bug; Windows
does.

``.gzkit/rules/cross-platform.md`` § Encoding binds: *"All file I/O
specifies encoding=\"utf-8\""*. The rule applies to ``src/**`` and
``tests/**``. This test fail-closes any regression of the pattern under
``tests/**``.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TESTS_ROOT = REPO_ROOT / "tests"

# Path.read_text() takes 0 positional args (encoding is positional[0] OR kwarg).
# Path.write_text(data) takes 1 positional arg (encoding is positional[1] OR kwarg).
# The Filesystem port at src/gzkit/ports/interfaces.py declares
# read_text(self, path) and write_text(self, path, content) — those calls
# carry one extra positional arg in source-form (read_text(path),
# write_text(path, data)) and are correctly skipped by the positional-count
# heuristic below.
_PATH_TEXT_IO_ARITY = {"read_text": 0, "write_text": 1}


def _is_text_io_call_missing_encoding(node: ast.AST) -> bool:
    """Return True for ``<Path>.write_text(data)`` / ``.read_text()`` lacking encoding."""
    if not (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in _PATH_TEXT_IO_ARITY
    ):
        return False
    expected_arity = _PATH_TEXT_IO_ARITY[node.func.attr]
    if len(node.args) != expected_arity:
        # Either positional encoding is supplied (covered) or the call is a
        # port-API method with extra positional args (out of scope).
        return False
    return all(kw.arg != "encoding" for kw in node.keywords)


def _scan_file(path: Path) -> list[tuple[int, str, str]]:
    """Return [(lineno, method, source_line)] for every offending site."""
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    lines = source.splitlines()
    hits: list[tuple[int, str, str]] = []
    for node in ast.walk(tree):
        if _is_text_io_call_missing_encoding(node):
            assert isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            lineno = node.lineno
            line = lines[lineno - 1] if 0 < lineno <= len(lines) else ""
            hits.append((lineno, node.func.attr, line.strip()))
    return hits


class TestFixtureEncodingTests(unittest.TestCase):
    """Default-encoding ``write_text`` / ``read_text`` is forbidden under tests/ (GHI #384).

    Default-encoding I/O is the cp1252-vs-UTF-8 hazard on Windows: a fixture
    write containing an em-dash (``—``, U+2014) under cp1252 emits byte
    ``0x97``, which fails UTF-8 decode when the test reads it back.
    """

    def test_no_default_encoding_text_io_under_tests(self) -> None:
        violations: list[str] = []
        for py_file in sorted(TESTS_ROOT.rglob("*.py")):
            for lineno, method, line in _scan_file(py_file):
                rel = py_file.relative_to(REPO_ROOT).as_posix()
                violations.append(f"{rel}:{lineno} [{method}]: {line}")
        self.assertEqual(
            violations,
            [],
            msg=(
                "Found `write_text(...)` / `read_text(...)` call sites under tests/ "
                "without an explicit `encoding=` kwarg. These default to the system "
                "locale (cp1252 on Windows) and silently break on any non-ASCII "
                'fixture content (GHI #384). Add `encoding="utf-8"` to each. '
                "Sites:\n  " + "\n  ".join(violations)
            ),
        )


if __name__ == "__main__":
    unittest.main()
