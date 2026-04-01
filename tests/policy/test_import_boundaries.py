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

COMMANDS_DIR = SRC_ROOT / "commands"

# Commands are allowed to import from these gzkit sub-packages
COMMANDS_ALLOWED_GZKIT_PREFIXES = (
    "gzkit.commands",  # intra-package
    "gzkit.core",  # domain layer
    "gzkit.cli",  # CLI helpers
    "gzkit.ports",  # port interfaces
    "gzkit.ledger",  # ledger access
    "gzkit.quality",  # quality checks
    "gzkit.skills",  # skill utilities
)

# Commands must NOT import from these
COMMANDS_FORBIDDEN_PREFIXES = ("gzkit.adapters",)  # adapter layer (should go through ports)

# Env vars permitted anywhere in commands/
COMMAND_ENV_ALLOWLIST: frozenset[str] = frozenset({"NO_COLOR", "FORCE_COLOR"})

# Per-file exceptions for env-var access beyond COMMAND_ENV_ALLOWLIST.
# Each entry maps filename -> frozenset of additionally-allowed var names,
# with a comment explaining the rationale.
COMMAND_ENV_EXCEPTIONS: dict[str, frozenset[str]] = {
    # sync.py reads SKIP to detect CI/hook bypass tokens, mirroring the same
    # guard used in git_sync; this is a deliberate policy-enforcement read,
    # not a configuration lookup that should move to core.
    "sync.py": frozenset({"SKIP"}),
    # obpi_lock_cmd.py reads agent identity env vars for lock ownership.
    "obpi_lock_cmd.py": frozenset({"CLAUDE_CODE", "CODEX_SANDBOX", "CLAUDE_SESSION_ID"}),
}


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


def _is_os_attr(node: ast.expr, attr: str) -> bool:
    """Return True if *node* is `os.<attr>` (Attribute access on bare `os` name)."""
    return (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "os"
        and node.attr == attr
    )


def _string_value(node: ast.expr) -> str | None:
    """Return the string value of a Constant string node, or None."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _collect_command_env_violations(
    tree: ast.Module, allowlist: frozenset[str]
) -> list[tuple[int, str, str]]:
    """Walk *tree* and return env-var violations outside *allowlist*.

    Returns a list of (line_number, access_form, var_name) triples for each
    usage of an env var not in *allowlist*.

    Detected patterns:
    - ``os.getenv("VAR")``
    - ``os.environ.get("VAR")``
    - ``os.environ["VAR"]``
    """
    violations: list[tuple[int, str, str]] = []

    for node in ast.walk(tree):
        # os.getenv("VAR", ...) — ast.Call
        if isinstance(node, ast.Call) and _is_os_attr(node.func, "getenv"):
            if node.args:
                var_name = _string_value(node.args[0])
                if var_name is not None and var_name not in allowlist:
                    violations.append((node.lineno, "os.getenv", var_name))

        # os.environ.get("VAR", ...) — ast.Call on a chained Attribute
        elif isinstance(node, ast.Call):
            func = node.func
            if (
                isinstance(func, ast.Attribute)
                and func.attr == "get"
                and _is_os_attr(func.value, "environ")
                and node.args
            ):
                var_name = _string_value(node.args[0])
                if var_name is not None and var_name not in allowlist:
                    violations.append((node.lineno, "os.environ.get", var_name))

        # os.environ["VAR"] — ast.Subscript
        elif isinstance(node, ast.Subscript) and _is_os_attr(node.value, "environ"):
            var_name = _string_value(node.slice)
            if var_name is not None and var_name not in allowlist:
                violations.append((node.lineno, "os.environ[...]", var_name))

    return violations


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


class TestCommandImportBoundaries(unittest.TestCase):
    """commands/ must not import from gzkit.adapters directly.

    Commands should go through core/ports, not reach into the adapters layer.
    """

    def test_commands_files_exist(self) -> None:
        """Sanity check: commands/ directory contains at least one .py file."""
        files = _collect_py_files(COMMANDS_DIR)
        self.assertGreater(len(files), 0, f"No .py files found in {COMMANDS_DIR}")

    def test_commands_no_adapter_imports(self) -> None:
        """command files must not import from gzkit.adapters."""
        for path in _collect_py_files(COMMANDS_DIR):
            with self.subTest(file=path.name):
                tree = _parse_file(path)
                violations: list[str] = []
                for _kind, module in _collect_imports(tree):
                    for forbidden_prefix in COMMANDS_FORBIDDEN_PREFIXES:
                        if module == forbidden_prefix or module.startswith(forbidden_prefix + "."):
                            violations.append(
                                f"imports '{module}' (forbidden prefix '{forbidden_prefix}')"
                            )
                if violations:
                    self.fail(
                        f"{path.name}: commands/ import boundary violations "
                        f"(commands must not reach into gzkit.adapters directly — "
                        f"use core/ports instead):\n" + "\n".join(violations)
                    )


class TestCommandEnvUsage(unittest.TestCase):
    """Command handlers must not call os.getenv() outside a narrow allowlist.

    Only terminal-color env vars (NO_COLOR, FORCE_COLOR) are permitted in the
    commands layer.  Any additional env-var reads indicate configuration that
    should be routed through core services or explicit CLI flags instead.

    Known exceptions are listed in COMMAND_ENV_EXCEPTIONS with explanations.
    """

    def test_commands_no_unapproved_env_access(self) -> None:
        """Scan all files in src/gzkit/commands/ for unapproved env-var reads."""
        all_violations: list[str] = []

        for path in _collect_py_files(COMMANDS_DIR):
            # Per-file exceptions: {filename: frozenset of allowed extra var names}
            extra_allowed = COMMAND_ENV_EXCEPTIONS.get(path.name, frozenset())
            effective_allowlist = COMMAND_ENV_ALLOWLIST | extra_allowed

            with self.subTest(file=path.name):
                tree = _parse_file(path)
                violations = _collect_command_env_violations(tree, effective_allowlist)
                for lineno, form, var_name in violations:
                    rel = path.relative_to(COMMANDS_DIR.parent.parent)
                    all_violations.append(
                        f"{rel}:{lineno}: {form}({var_name!r}) — not in allowlist "
                        f"(allowlist for this file: {sorted(effective_allowlist)})"
                    )

        if all_violations:
            self.fail(
                "Unapproved env-var access in commands/ detected:\n" + "\n".join(all_violations)
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
