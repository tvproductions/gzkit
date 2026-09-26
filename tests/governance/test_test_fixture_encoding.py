"""Regression test for text I/O without ``encoding="utf-8"`` (GHI #384).

``Path.write_text(content)``, ``Path.read_text()`` and a text-mode
``open()`` / ``Path.open()`` without an explicit ``encoding=`` defer to the
system locale. On Windows that is cp1252; on POSIX it is usually UTF-8. A
file written with em-dash / smart quotes / arrows under cp1252 and read back
as UTF-8 (or vice versa) raises ``UnicodeDecodeError`` or reads mojibake.
POSIX CI never sees the bug; Windows does.

``.gzkit/rules/cross-platform.md`` § Encoding binds: *"All file I/O
specifies encoding=\"utf-8\""*. The rule applies to ``src/**`` and
``tests/**``, and this test fail-closes the pattern under both. It first
covered only ``read_text`` / ``write_text`` under ``tests/**``, which let
``GzkitConfig.load``'s bare ``config_path.open()`` ship in ``src/``.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TESTS_ROOT = REPO_ROOT / "tests"
SRC_ROOT = REPO_ROOT / "src" / "gzkit"

# Path.read_text() takes 0 positional args (encoding is positional[0] OR kwarg).
# Path.write_text(data) takes 1 positional arg (encoding is positional[1] OR kwarg).
# The Filesystem port at src/gzkit/ports/interfaces.py declares
# read_text(self, path) and write_text(self, path, content) — those calls
# carry one extra positional arg in source-form (read_text(path),
# write_text(path, data)) and are correctly skipped by the positional-count
# heuristic below.
_PATH_TEXT_IO_ARITY = {"read_text": 0, "write_text": 1}

# Positional index of (mode, encoding): builtin open(file, mode, buffering,
# encoding) and Path.open(mode, buffering, encoding).
_BUILTIN_OPEN_POSITIONS = (1, 3)
_PATH_OPEN_POSITIONS = (0, 2)

# `<module>.open(...)` receivers whose open is not a locale-defaulting text open.
_NON_TEXT_OPEN_MODULES = frozenset(
    {"os", "tarfile", "zipfile", "gzip", "bz2", "lzma", "webbrowser", "shelve", "dbm", "wave"}
)


def _open_positions(func: ast.expr) -> tuple[int, int] | None:
    if isinstance(func, ast.Name) and func.id == "open":
        return _BUILTIN_OPEN_POSITIONS
    if isinstance(func, ast.Attribute) and func.attr == "open":
        receiver = func.value
        if isinstance(receiver, ast.Name) and receiver.id in _NON_TEXT_OPEN_MODULES:
            return None
        return _PATH_OPEN_POSITIONS
    return None


def _is_text_open_missing_encoding(node: ast.Call) -> bool:
    """Return True for a text-mode ``open()`` / ``<Path>.open()`` lacking encoding."""
    positions = _open_positions(node.func)
    if positions is None:
        return False
    mode_index, encoding_index = positions
    if len(node.args) > encoding_index or any(kw.arg == "encoding" for kw in node.keywords):
        return False
    mode: ast.expr | None = node.args[mode_index] if len(node.args) > mode_index else None
    for kw in node.keywords:
        if kw.arg == "mode":
            mode = kw.value
    if mode is None:
        return True  # default mode "r" is text
    if not (isinstance(mode, ast.Constant) and isinstance(mode.value, str)):
        return False  # a computed mode cannot be judged statically
    return "b" not in mode.value


def _is_text_io_call_missing_encoding(node: ast.AST) -> bool:
    """Return True for any locale-defaulting text I/O call lacking encoding."""
    if not isinstance(node, ast.Call):
        return False
    if isinstance(node.func, ast.Attribute) and node.func.attr in _PATH_TEXT_IO_ARITY:
        expected_arity = _PATH_TEXT_IO_ARITY[node.func.attr]
        if len(node.args) != expected_arity:
            # Either positional encoding is supplied (covered) or the call is a
            # port-API method with extra positional args (out of scope).
            return False
        return all(kw.arg != "encoding" for kw in node.keywords)
    return _is_text_open_missing_encoding(node)


def _scan_source(source: str) -> list[tuple[int, str, str]]:
    """Return [(lineno, method, source_line)] for every offending site."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    lines = source.splitlines()
    hits: list[tuple[int, str, str]] = []
    for node in ast.walk(tree):
        if _is_text_io_call_missing_encoding(node):
            assert isinstance(node, ast.Call)
            func = node.func
            method = func.attr if isinstance(func, ast.Attribute) else "open"
            lineno = node.lineno
            line = lines[lineno - 1] if 0 < lineno <= len(lines) else ""
            hits.append((lineno, method, line.strip()))
    return hits


def _violations_under(root: Path) -> list[str]:
    violations: list[str] = []
    for py_file in sorted(root.rglob("*.py")):
        for lineno, method, line in _scan_source(py_file.read_text(encoding="utf-8")):
            rel = py_file.relative_to(REPO_ROOT).as_posix()
            violations.append(f"{rel}:{lineno} [{method}]: {line}")
    return violations


def _failure_message(tree: str, violations: list[str]) -> str:
    return (
        f"Found text I/O call sites under {tree} without an explicit `encoding=`. "
        "These default to the system locale (cp1252 on Windows) and silently break "
        'on any non-ASCII content (GHI #384). Add `encoding="utf-8"` to each. '
        "Sites:\n  " + "\n  ".join(violations)
    )


class TestFixtureEncodingTests(unittest.TestCase):
    """Default-encoding text I/O is forbidden under tests/ and src/gzkit/ (GHI #384).

    Default-encoding I/O is the cp1252-vs-UTF-8 hazard on Windows: a fixture
    write containing an em-dash (``—``, U+2014) under cp1252 emits byte
    ``0x97``, which fails UTF-8 decode when the test reads it back.
    """

    def test_no_default_encoding_text_io_under_tests(self) -> None:
        violations = _violations_under(TESTS_ROOT)
        self.assertEqual(violations, [], msg=_failure_message("tests/", violations))

    def test_no_default_encoding_text_io_under_src(self) -> None:
        violations = _violations_under(SRC_ROOT)
        self.assertEqual(violations, [], msg=_failure_message("src/gzkit/", violations))


class TestEncodingDetector(unittest.TestCase):
    """The detector flags locale-defaulting text I/O and passes explicit or binary I/O."""

    def _flagged(self, source: str) -> bool:
        return bool(_scan_source(source))

    def test_flags_locale_defaulting_calls(self) -> None:
        for source in (
            "p.read_text()",
            "p.write_text(data)",
            "p.open()",
            "p.open('w')",
            "p.open(mode='a')",
            "open(name)",
            "open(name, 'w')",
        ):
            with self.subTest(source=source):
                self.assertTrue(self._flagged(source))

    def test_passes_explicit_encoding_and_binary_calls(self) -> None:
        for source in (
            "p.read_text(encoding='utf-8')",
            "p.read_text('utf-8')",
            "p.write_text(data, encoding='utf-8')",
            "p.open(encoding='utf-8')",
            "p.open('w', -1, 'utf-8')",
            "p.open('rb')",
            "p.open(mode='wb')",
            "open(name, 'rb')",
            "open(name, 'r', -1, 'utf-8')",
            "open(name, encoding='utf-8')",
            "os.open(name, flags)",
            "tarfile.open(name)",
            "fs.read_text(path)",
        ):
            with self.subTest(source=source):
                self.assertFalse(self._flagged(source))


if __name__ == "__main__":
    unittest.main()
