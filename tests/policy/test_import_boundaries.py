"""Policy tests: architectural import boundary enforcement via AST scanning.

These tests NEVER import or execute application code. They parse source files
with the `ast` module to verify hexagonal architecture boundaries are respected.
"""

from __future__ import annotations

import ast
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SRC_ROOT = Path(__file__).parent.parent.parent / "src" / "gzkit"

CORE_DIR = SRC_ROOT / "core"

# Modules that core/ must never import from. `gzkit.adapters` is retained as a
# forward-fence: the ports/adapters facade was retired (2026-07-06 ruling — see
# docs/governance/hexagonal-architecture.md), but the deps-behind-adapters
# directive keeps `adapters` a live architectural concept, so core purity from
# any future adapter package still holds.
CORE_FORBIDDEN_PREFIXES = (
    "gzkit.cli",
    "gzkit.adapters",
    "gzkit.commands",
)
#: Top-level modules core/ may import despite not being stdlib.
#:
#: `.gzkit/rules/hexagonal-architecture.md` rule 1 says core imports "stdlib +
#: Pydantic ONLY", and rule 2 names Pydantic the single ratified exception. That
#: is an ALLOWLIST, and it cannot be expressed as a denylist: the previous
#: `("rich", "argparse")` pair enforced "not these two", so every third-party
#: dependency the project has added since — networkx, radon, lizard, cohesion —
#: was free to enter core, and a dependency added tomorrow would be too. A check
#: whose subject is narrower than its name is the validator-side arm of the
#: doctrine-declared-without-mechanism family (GHI #537).
CORE_ALLOWED_THIRD_PARTY = frozenset({"pydantic"})

#: Stdlib modules core/ must still refuse. `argparse` is stdlib, so the
#: stdlib test admits it — but it is the CLI layer's technology, and rule 4
#: ("never name the technology in the core") fences it regardless of who ships it.
CORE_FORBIDDEN_STDLIB = frozenset({"argparse"})

COMMANDS_DIR = SRC_ROOT / "commands"

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
    # gz content edit (OBPI-0.0.34-04) resolves the operator's preferred
    # editor via $VISUAL / $EDITOR. This is the standard POSIX editor-
    # invocation contract; routing it through core/ports would be a
    # premature abstraction over a stable shell convention.
    "edit.py": frozenset({"EDITOR", "VISUAL"}),
    # validate_cmd.py reads CI to decide whether the session-green gate's
    # delivery arm binds: a developer worktree must have the pre-push hook
    # installed, a fresh CI checkout legitimately has none (CI *is* the gate
    # there and does not push). Like SKIP above, this is a policy-enforcement
    # read of the execution context, not a configuration lookup — there is no
    # value for core to supply, only a fact about where the process is running
    # (GHI #715).
    "validate_cmd.py": frozenset({"CI"}),
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


def _core_violations(path: Path) -> list[str]:
    """Return every core/ import-boundary violation in *path*.

    Extracted from the assertion so the predicate can be exercised against a
    synthetic module. A boundary check that is only ever run over a tree that
    already satisfies it cannot distinguish "enforces the rule" from "returns
    the empty list" -- and the denylist this replaced had been in exactly that
    state, admitting four third-party dependencies while passing every run.
    """
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

        # Core purity, stated as the allowlist the rule actually declares:
        # stdlib + Pydantic + gzkit internals, and nothing else.
        top = _top_level_module(module)
        if top in CORE_FORBIDDEN_STDLIB:
            violations.append(f"{path.name}: imports '{module}' (forbidden top-level module)")
        elif not (
            top in sys.stdlib_module_names or top in CORE_ALLOWED_THIRD_PARTY or top == "gzkit"
        ):
            violations.append(
                f"{path.name}: imports '{module}' — core/ is stdlib + Pydantic ONLY "
                "(.gzkit/rules/hexagonal-architecture.md rules 1-2); put the dependency "
                "behind an adapter and take it as a parameter"
            )

    return violations


class CorePurityIsAnAllowlist(unittest.TestCase):
    """The core-purity check refuses any non-stdlib import, not a fixed pair.

    These exercise the predicate against synthetic modules because `core/` is
    clean: a test that only reads the real tree passes identically whether the
    check enforces the rule or returns nothing.
    """

    def _violations(self, source: str) -> list[str]:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.py"
            path.write_text(source, encoding="utf-8")
            return _core_violations(path)

    def test_every_declared_runtime_dependency_is_refused(self) -> None:
        """The four deps added after the denylist was written are now fenced.

        `networkx`, `radon`, `lizard` and `cohesion` all entered `pyproject.toml`
        while `CORE_FORBIDDEN_TOP_LEVEL` still read `("rich", "argparse")`, so
        each could have been imported into core without failing a single test.
        """
        for dep in ("networkx", "radon", "lizard", "cohesion", "jinja2", "structlog"):
            with self.subTest(dependency=dep):
                self.assertTrue(self._violations(f"import {dep}\n"))

    def test_a_dependency_nobody_has_added_yet_is_refused(self) -> None:
        """The allowlist binds by construction, so it needs no upkeep.

        This is the property a denylist cannot have: enforcement must not depend
        on someone remembering to add a name when a dependency lands.
        """
        self.assertTrue(self._violations("import some_future_dependency\n"))

    def test_stdlib_pydantic_and_gzkit_are_admitted(self) -> None:
        clean = "import enum\nimport re\nfrom typing import Any\nfrom pydantic import BaseModel\n"
        self.assertEqual(self._violations(clean), [])

    def test_argparse_stays_refused_although_it_is_stdlib(self) -> None:
        """Rule 4 fences the CLI's technology out of core regardless of shipper."""
        self.assertTrue(self._violations("import argparse\n"))

    def test_the_message_names_the_rule_and_the_recovery(self) -> None:
        """Three-part recovery prose (`.gzkit/rules/guardrail-feedback-prose.md`)."""
        message = self._violations("import networkx\n")[0]
        self.assertIn("networkx", message)
        self.assertIn("hexagonal-architecture.md", message)
        self.assertIn("behind an adapter", message)


class TestCoreImportBoundaries(unittest.TestCase):
    """core/ imports stdlib + Pydantic only, and never the CLI/commands layers."""

    def _assert_file_clean(self, path: Path) -> None:
        violations = _core_violations(path)
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


class TestCommandLayerSanity(unittest.TestCase):
    """commands/ presence sanity.

    The former "commands must not import gzkit.adapters" rule was retired
    (2026-07-06 injection-seam ruling): the command layer IS gzkit's
    configurator (Cockburn Fig 2.1), so it is precisely where driven adapters
    are instantiated — forbidding that import contradicts the blessed pattern.
    Core purity from any adapter package is still enforced by
    TestCoreImportBoundaries.
    """

    def test_commands_files_exist(self) -> None:
        """Sanity check: commands/ directory contains at least one .py file."""
        files = _collect_py_files(COMMANDS_DIR)
        self.assertGreater(len(files), 0, f"No .py files found in {COMMANDS_DIR}")


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
