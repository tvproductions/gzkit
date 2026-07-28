"""The tautological audit exempts fences over shipped executables (GHI #730).

`_reads_project_source` keys its static-analysis-fence exemption on Python-ness
(`ast.parse`, a `*.py` glob), so an identical structural assertion over a shell
script gzkit ships and runs scored as a governance-doc content echo. Both are
production code. `_asserts_shipped_executable` closes that gap.

The negative control is the load-bearing test here: the sibling predicate's
docstring commits to being *"deliberately narrow, so real tautologies are not
laundered"*, and an exemption keyed on a path prefix is exactly the shape that
goes broad by accident.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

from gzkit.tautological_tests import (
    _SHIPPED_EXECUTABLE_ROOTS,
    _asserts_shipped_executable,
)


def _func(source: str) -> ast.FunctionDef:
    """Parse a single function definition out of a source snippet."""
    node = ast.parse(source).body[0]
    assert isinstance(node, ast.FunctionDef)
    return node


class TestShippedExecutableFence(unittest.TestCase):
    """Only literal paths under a shipped-executable root are exempt."""

    def test_hook_path_assertion_is_a_fence(self) -> None:
        node = _func(
            "def test_x(self):\n"
            "    p = Path('.gzkit/hooks/pre-commit-complexity-advisor')\n"
            "    self.assertTrue(p.exists())\n"
        )
        self.assertTrue(_asserts_shipped_executable(node))

    def test_governance_doc_assertion_is_not_a_fence(self) -> None:
        """The laundering guard: reading a doc and echoing its text stays flagged."""
        node = _func(
            "def test_x(self):\n"
            "    p = Path('docs/governance/state-doctrine.md')\n"
            "    self.assertIn('Layer 3', p.read_text())\n"
        )
        self.assertFalse(_asserts_shipped_executable(node))

    def test_bare_gzkit_path_is_not_a_fence(self) -> None:
        """`.gzkit/` alone is far too broad — only the hooks root counts."""
        node = _func(
            "def test_x(self):\n"
            "    p = Path('.gzkit/ledger.jsonl')\n"
            "    self.assertTrue(p.exists())\n"
        )
        self.assertFalse(_asserts_shipped_executable(node))

    def test_partial_prefix_does_not_match(self) -> None:
        """A sibling directory sharing a prefix must not inherit the exemption."""
        node = _func(
            "def test_x(self):\n"
            "    p = Path('.gzkit/hooks-archive/old-script')\n"
            "    self.assertTrue(p.exists())\n"
        )
        self.assertFalse(_asserts_shipped_executable(node))

    def test_function_with_no_string_constants_is_not_a_fence(self) -> None:
        node = _func("def test_x(self):\n    self.assertTrue(True)\n")
        self.assertFalse(_asserts_shipped_executable(node))


def _roots_missing_from_disk() -> list[str]:
    """Return the declared roots that are not directories in this repo."""
    repo_root = Path(__file__).resolve().parents[2]
    return [root for root in _SHIPPED_EXECUTABLE_ROOTS if not (repo_root / root).is_dir()]


class TestShippedExecutableRootsAreReal(unittest.TestCase):
    """The roots tuple must name surfaces that exist, or the fence is dead code."""

    def test_no_root_is_missing_from_disk(self) -> None:
        """A renamed or deleted root would make the exemption silently inert."""
        self.assertEqual(_roots_missing_from_disk(), [])

    def test_roots_are_directory_prefixes(self) -> None:
        """A root missing its trailing slash would match sibling paths by prefix."""
        for root in _SHIPPED_EXECUTABLE_ROOTS:
            with self.subTest(root=root):
                self.assertTrue(root.endswith("/"), f"{root} must end with '/'")


if __name__ == "__main__":
    unittest.main()
