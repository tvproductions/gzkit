"""Policy tests: env-var usage enforcement via AST scanning.

These tests NEVER import or execute application code. They parse source files
with the `ast` module to verify that `os.getenv()`, `os.environ.get()`, and
`os.environ[...]` are only used with explicitly allowed environment variable names.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SRC_ROOT = Path(__file__).parent.parent.parent / "src" / "gzkit"

# Environment variable names that may be read anywhere in the codebase.
ENV_VAR_ALLOWLIST: frozenset[str] = frozenset(
    {
        "NO_COLOR",
        "FORCE_COLOR",
        "TERM",
        "SKIP",  # CI/hook bypass detection (git_sync, cli/main)
        "CLAUDE_CODE",  # Agent identity resolution (obpi lock)
        "CLAUDE_SESSION_ID",  # Agent session identification (hooks, obpi lock)
        "CODEX_SANDBOX",  # Agent identity resolution (obpi lock)
        "COPILOT_SESSION_ID",  # Agent session identification (hooks)
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


def _collect_env_violations(tree: ast.Module) -> list[tuple[int, str, str]]:
    """Walk *tree* and return env-var violations outside the allowlist.

    Returns a list of (line_number, access_form, var_name) triples for each
    usage of an env var not in ENV_VAR_ALLOWLIST.

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
                if var_name is not None and var_name not in ENV_VAR_ALLOWLIST:
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
                if var_name is not None and var_name not in ENV_VAR_ALLOWLIST:
                    violations.append((node.lineno, "os.environ.get", var_name))

        # os.environ["VAR"] — ast.Subscript
        elif isinstance(node, ast.Subscript) and _is_os_attr(node.value, "environ"):
            var_name = _string_value(node.slice)
            if var_name is not None and var_name not in ENV_VAR_ALLOWLIST:
                violations.append((node.lineno, "os.environ[...]", var_name))

    return violations


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestEnvVarUsage(unittest.TestCase):
    """All env-var access in src/gzkit/ must use only allowlisted variable names."""

    def test_src_files_exist(self) -> None:
        """Sanity check: src/gzkit/ contains at least one .py file."""
        files = _collect_py_files(SRC_ROOT)
        self.assertGreater(len(files), 0, f"No .py files found in {SRC_ROOT}")

    def test_no_unapproved_env_vars(self) -> None:
        """Every os.getenv / os.environ.get / os.environ[...] call must use an allowlisted var."""
        all_violations: list[str] = []

        for path in _collect_py_files(SRC_ROOT):
            with self.subTest(file=str(path.relative_to(SRC_ROOT.parent.parent))):
                tree = _parse_file(path)
                violations = _collect_env_violations(tree)
                for lineno, form, var_name in violations:
                    rel = path.relative_to(SRC_ROOT.parent.parent)
                    all_violations.append(
                        f"{rel}:{lineno}: {form}({var_name!r}) — not in allowlist"
                    )

        if all_violations:
            self.fail(
                "Unapproved env-var access detected "
                f"(allowlist={sorted(ENV_VAR_ALLOWLIST)}):\n" + "\n".join(all_violations)
            )

    def test_allowlisted_vars_are_detectable(self) -> None:
        """Regression guard: allowlisted env vars are readable by the scanner."""
        # Construct a synthetic source that uses all allowlisted vars; none should
        # appear in violation output.
        lines = ["import os\n"]
        for var in sorted(ENV_VAR_ALLOWLIST):
            lines.append(f'os.environ.get("{var}")\n')
        source = "".join(lines)
        tree = ast.parse(source, filename="<synthetic>")
        violations = _collect_env_violations(tree)
        self.assertEqual(
            violations,
            [],
            f"Allowlisted vars produced unexpected violations: {violations}",
        )

    def test_unapproved_getenv_is_detected(self) -> None:
        """Scanner must flag os.getenv with a non-allowlisted var."""
        source = 'import os\nos.getenv("SECRET_KEY")\n'
        tree = ast.parse(source, filename="<synthetic>")
        violations = _collect_env_violations(tree)
        self.assertEqual(len(violations), 1)
        _lineno, form, var_name = violations[0]
        self.assertEqual(form, "os.getenv")
        self.assertEqual(var_name, "SECRET_KEY")

    def test_unapproved_environ_get_is_detected(self) -> None:
        """Scanner must flag os.environ.get with a non-allowlisted var."""
        source = 'import os\nos.environ.get("DATABASE_URL", "")\n'
        tree = ast.parse(source, filename="<synthetic>")
        violations = _collect_env_violations(tree)
        self.assertEqual(len(violations), 1)
        _lineno, form, var_name = violations[0]
        self.assertEqual(form, "os.environ.get")
        self.assertEqual(var_name, "DATABASE_URL")

    def test_unapproved_environ_subscript_is_detected(self) -> None:
        """Scanner must flag os.environ[...] with a non-allowlisted var."""
        source = 'import os\nvalue = os.environ["PATH"]\n'
        tree = ast.parse(source, filename="<synthetic>")
        violations = _collect_env_violations(tree)
        self.assertEqual(len(violations), 1)
        _lineno, form, var_name = violations[0]
        self.assertEqual(form, "os.environ[...]")
        self.assertEqual(var_name, "PATH")


class TestPolicyTestIsolation(unittest.TestCase):
    """This policy test file must not import from src/gzkit/."""

    def test_this_module_imports_no_gzkit(self) -> None:
        """This test file must not import any gzkit application module."""
        this_file = Path(__file__)
        source = this_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(this_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertFalse(
                        alias.name == "gzkit" or alias.name.startswith("gzkit."),
                        f"Policy test file imports gzkit module: '{alias.name}'",
                    )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                self.assertFalse(
                    module == "gzkit" or module.startswith("gzkit."),
                    f"Policy test file imports gzkit module: '{module}'",
                )


if __name__ == "__main__":
    unittest.main()
