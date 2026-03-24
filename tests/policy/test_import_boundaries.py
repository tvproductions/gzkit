"""Policy tests: architectural import boundary enforcement via AST scanning.

These tests NEVER import or execute application code. They parse source files
with the `ast` module to verify hexagonal architecture boundaries are respected.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SRC_ROOT = Path(__file__).parent.parent.parent / "src" / "gzkit"

CORE_DIR = SRC_ROOT / "core"
PORTS_DIR = SRC_ROOT / "ports"

# Modules that core/ must never import from
CORE_FORBIDDEN_PREFIXES = (
    "gzkit.cli",
    "gzkit.adapters",
    "gzkit.commands",
)
CORE_FORBIDDEN_TOP_LEVEL = ("rich", "argparse")

# Allowed top-level module names for ports/ (stdlib type annotation modules only)
PORTS_ALLOWED_MODULES = frozenset(
    {
        "__future__",
        "typing",
        "typing_extensions",
        "types",
        "pathlib",
        "collections",
        "collections.abc",
        "abc",
        "enum",
        "dataclasses",
        "re",
        "os",
        "sys",
    }
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _collect_py_files(directory: Path) -> list[Path]:
    """Return all .py files under *directory* (recursive)."""
    return sorted(directory.rglob("*.py"))


def _parse_file(path: Path) -> ast.Module:
    """Parse a Python source file and return its AST."""
    source = path.read_text(encoding="utf-8")
    return ast.parse(source, filename=str(path))


def _collect_imports(tree: ast.Module) -> list[tuple[str, str]]:
    """Return (import_kind, module_name) pairs for all import statements.

    import_kind is "import" for `import X` and "from" for `from X import Y`.
    module_name is the top-level dotted name being imported.
    """
    imports: list[tuple[str, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(("import", alias.name))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.append(("from", module))
    return imports


def _top_level_module(dotted_name: str) -> str:
    """Return the first component of a dotted module name."""
    return dotted_name.split(".")[0]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestCoreImportBoundaries(unittest.TestCase):
    """core/ must not import from CLI, adapters, commands, rich, or argparse."""

    def _assert_file_clean(self, path: Path) -> None:
        tree = _parse_file(path)
        imports = _collect_imports(tree)
        violations: list[str] = []

        for _kind, module in imports:
            # Check forbidden gzkit sub-package prefixes
            for forbidden_prefix in CORE_FORBIDDEN_PREFIXES:
                if module == forbidden_prefix or module.startswith(forbidden_prefix + "."):
                    violations.append(
                        f"{path.name}: imports '{module}' (forbidden prefix '{forbidden_prefix}')"
                    )

            # Check forbidden top-level modules
            if _top_level_module(module) in CORE_FORBIDDEN_TOP_LEVEL:
                violations.append(f"{path.name}: imports '{module}' (forbidden top-level module)")

        if violations:
            self.fail("core/ import boundary violations:\n" + "\n".join(violations))

    def test_core_files_exist(self) -> None:
        """Sanity check: core/ directory contains at least one .py file."""
        files = _collect_py_files(CORE_DIR)
        self.assertGreater(len(files), 0, f"No .py files found in {CORE_DIR}")

    def test_core_no_cli_imports(self) -> None:
        """core/ must not import from gzkit.cli."""
        for path in _collect_py_files(CORE_DIR):
            with self.subTest(file=path.name):
                tree = _parse_file(path)
                for _kind, module in _collect_imports(tree):
                    self.assertFalse(
                        module == "gzkit.cli" or module.startswith("gzkit.cli."),
                        f"{path.name}: forbidden import from gzkit.cli — '{module}'",
                    )

    def test_core_no_adapters_imports(self) -> None:
        """core/ must not import from gzkit.adapters."""
        for path in _collect_py_files(CORE_DIR):
            with self.subTest(file=path.name):
                tree = _parse_file(path)
                for _kind, module in _collect_imports(tree):
                    self.assertFalse(
                        module == "gzkit.adapters" or module.startswith("gzkit.adapters."),
                        f"{path.name}: forbidden import from gzkit.adapters — '{module}'",
                    )

    def test_core_no_commands_imports(self) -> None:
        """core/ must not import from gzkit.commands."""
        for path in _collect_py_files(CORE_DIR):
            with self.subTest(file=path.name):
                tree = _parse_file(path)
                for _kind, module in _collect_imports(tree):
                    self.assertFalse(
                        module == "gzkit.commands" or module.startswith("gzkit.commands."),
                        f"{path.name}: forbidden import from gzkit.commands — '{module}'",
                    )

    def test_core_no_rich_imports(self) -> None:
        """core/ must not import from rich (UI layer)."""
        for path in _collect_py_files(CORE_DIR):
            with self.subTest(file=path.name):
                tree = _parse_file(path)
                for _kind, module in _collect_imports(tree):
                    self.assertNotEqual(
                        _top_level_module(module),
                        "rich",
                        f"{path.name}: forbidden import from rich — '{module}'",
                    )

    def test_core_no_argparse_imports(self) -> None:
        """core/ must not import argparse (CLI layer)."""
        for path in _collect_py_files(CORE_DIR):
            with self.subTest(file=path.name):
                tree = _parse_file(path)
                for _kind, module in _collect_imports(tree):
                    self.assertNotEqual(
                        _top_level_module(module),
                        "argparse",
                        f"{path.name}: forbidden import from argparse — '{module}'",
                    )

    def test_core_all_files_pass_boundary_check(self) -> None:
        """Aggregate: all core/ files pass the full boundary check in one sweep."""
        for path in _collect_py_files(CORE_DIR):
            with self.subTest(file=path.name):
                self._assert_file_clean(path)


class TestPortsImportBoundaries(unittest.TestCase):
    """ports/ must import only stdlib type annotation modules."""

    def test_ports_files_exist(self) -> None:
        """Sanity check: ports/ directory contains at least one .py file."""
        files = _collect_py_files(PORTS_DIR)
        self.assertGreater(len(files), 0, f"No .py files found in {PORTS_DIR}")

    def test_ports_only_stdlib_type_modules(self) -> None:
        """ports/ must only import from allowed stdlib type annotation modules."""
        for path in _collect_py_files(PORTS_DIR):
            with self.subTest(file=path.name):
                tree = _parse_file(path)
                violations: list[str] = []

                for _kind, module in _collect_imports(tree):
                    if not module:
                        continue
                    # Allow intra-package re-exports (gzkit.ports.* -> gzkit.ports.*)
                    if module == "gzkit.ports" or module.startswith("gzkit.ports."):
                        continue
                    top = _top_level_module(module)
                    # Allow the full dotted name or the top-level name
                    if module not in PORTS_ALLOWED_MODULES and top not in PORTS_ALLOWED_MODULES:
                        violations.append(f"'{module}'")

                if violations:
                    self.fail(
                        f"{path.name}: ports/ imports non-allowed modules: "
                        + ", ".join(violations)
                        + f"\nAllowed: {sorted(PORTS_ALLOWED_MODULES)}"
                    )


class TestPolicyTestIsolation(unittest.TestCase):
    """Policy tests themselves must not import from src/gzkit/."""

    def test_this_module_imports_no_gzkit(self) -> None:
        """This test file must not import any gzkit application module."""
        this_file = Path(__file__)
        tree = _parse_file(this_file)
        for _kind, module in _collect_imports(tree):
            self.assertFalse(
                module == "gzkit" or module.startswith("gzkit."),
                f"Policy test file imports gzkit module: '{module}'",
            )


if __name__ == "__main__":
    unittest.main()
