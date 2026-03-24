"""Policy tests: snake_case naming convention enforcement.

These tests NEVER import or execute application code. They use pathlib to
inspect file and directory names under src/gzkit/ and verify all module
and package names conform to snake_case conventions.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SRC_ROOT = Path(__file__).parent.parent.parent / "src" / "gzkit"

# Valid snake_case: lowercase letters, digits, underscores; no leading digit.
# Dunder names like __init__ and __main__ are valid by this pattern.
SNAKE_CASE_RE = re.compile(r"^[a-z_][a-z0-9_]*$")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _collect_py_files(directory: Path) -> list[Path]:
    """Return all .py files under *directory* (recursive), sorted."""
    return sorted(directory.rglob("*.py"))


def _collect_package_dirs(directory: Path) -> list[Path]:
    """Return all subdirectories under *directory* (recursive), sorted.

    Only returns directories that contain an __init__.py (i.e., packages),
    plus the root directory itself.
    """
    dirs: list[Path] = [directory]
    for d in sorted(directory.rglob("*")):
        if d.is_dir() and not d.name.startswith(".") and d.name != "__pycache__":
            dirs.append(d)
    return dirs


def _is_snake_case(name: str) -> bool:
    """Return True if *name* matches the snake_case pattern."""
    return bool(SNAKE_CASE_RE.match(name))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestModuleNamingConventions(unittest.TestCase):
    """All .py module stems under src/gzkit/ must use snake_case."""

    def test_src_root_exists(self) -> None:
        """Sanity check: src/gzkit/ directory exists."""
        self.assertTrue(SRC_ROOT.is_dir(), f"Expected src/gzkit/ at {SRC_ROOT}")

    def test_py_files_exist(self) -> None:
        """Sanity check: at least one .py file exists under src/gzkit/."""
        files = _collect_py_files(SRC_ROOT)
        self.assertGreater(len(files), 0, f"No .py files found under {SRC_ROOT}")

    def test_all_module_names_are_snake_case(self) -> None:
        """Every .py file stem under src/gzkit/ must be snake_case."""
        violations: list[str] = []
        for path in _collect_py_files(SRC_ROOT):
            stem = path.stem
            if not _is_snake_case(stem):
                rel = path.relative_to(SRC_ROOT.parent.parent)
                violations.append(f"{rel}: module name '{stem}' is not snake_case")

        if violations:
            self.fail("Module naming violations:\n" + "\n".join(violations))


class TestPackageNamingConventions(unittest.TestCase):
    """All package directory names under src/gzkit/ must use snake_case."""

    def test_all_package_dirs_are_snake_case(self) -> None:
        """Every package directory under src/gzkit/ must be snake_case."""
        violations: list[str] = []
        for d in _collect_package_dirs(SRC_ROOT):
            name = d.name
            if not _is_snake_case(name):
                rel = d.relative_to(SRC_ROOT.parent.parent)
                violations.append(f"{rel}: directory name '{name}' is not snake_case")

        if violations:
            self.fail("Package directory naming violations:\n" + "\n".join(violations))


class TestNamingConventionTestIsolation(unittest.TestCase):
    """This test file must not import any module from src/gzkit/."""

    def test_this_module_imports_no_gzkit(self) -> None:
        """Verify this policy test file itself imports zero gzkit modules."""
        import ast

        this_file = Path(__file__)
        source = this_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(this_file))

        violations: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "gzkit" or alias.name.startswith("gzkit."):
                        violations.append(f"import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module == "gzkit" or module.startswith("gzkit."):
                    violations.append(f"from {module} import ...")

        if violations:
            self.fail("Policy test file must not import gzkit modules:\n" + "\n".join(violations))


if __name__ == "__main__":
    unittest.main()
