"""Policy tests: every spawn takes its executable from ``gzkit.executables``.

``.gzkit/rules/cross-platform.md`` § Executable resolution: on Windows
``CreateProcess``, and ``shutil.which`` with it, try the current directory before
``PATH``, so a bare ``"git"`` in a repository gzkit runs inside can spawn a planted
``git.exe``. Ruff S607 sees only a literal argv; this scan reads every
``subprocess`` spawn's AST, so a variable argv that skips the resolver fails here
too. Three surfaces are read: the package, every generated hook script rendered
from its template, and the canonical skill and chore scripts. A surface that
cannot import gzkit carries the resolver verbatim, and the copy must equal the
package's source.
"""

import ast
import inspect
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

from gzkit import executables
from gzkit.hooks.scripts import ghi, mx, pipeline, quality, routing, session_exit, validation

if TYPE_CHECKING:
    from collections.abc import Iterator

REPO_ROOT = Path(__file__).parent.parent.parent
SRC_ROOT = REPO_ROOT / "src" / "gzkit"
CANONICAL_SCRIPT_GLOBS = (".gzkit/skills/*/scripts/*.py", ".gzkit/chores/**/*.py")
HOOK_TEMPLATE_MODULES = (ghi, mx, pipeline, quality, routing, session_exit, validation)

_SPAWNS = frozenset({"run", "Popen", "check_output", "check_call", "call"})
_RESOLVERS = frozenset({"find_executable", "resolve_executable"})


def _spawns(tree: ast.AST) -> Iterator[tuple[ast.Call, ast.expr | None]]:
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in _SPAWNS
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "subprocess"
        ):
            argv = node.args[0] if node.args else None
            argv = argv or next((k.value for k in node.keywords if k.arg == "args"), None)
            yield node, argv


def _resolved_names(tree: ast.AST) -> set[str]:
    """Return names assigned from ``find_executable`` or ``resolve_executable``.

    Returns:
        Every variable name bound to a resolver's result anywhere in ``tree``.
    """
    names: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id in _RESOLVERS
        ):
            names.update(t.id for t in node.targets if isinstance(t, ast.Name))
    return names


def _calls(node: ast.expr | None, name: str) -> bool:
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == name


def _is_resolved(argv: ast.expr | None, resolved: set[str]) -> bool:
    if _calls(argv, "resolve_argv"):
        return True
    if isinstance(argv, ast.IfExp):
        # The transcript replay: a list goes through resolve_argv, a shell string
        # runs under the shell replay_shell resolved with find_executable.
        return _calls(argv.body, "resolve_argv")
    if isinstance(argv, ast.List) and argv.elts:
        head = argv.elts[0]
        if _calls(head, "resolve_executable"):
            return True
        if isinstance(head, ast.Name) and head.id in resolved:
            return True
        return ast.unparse(head) == "sys.executable"
    return False


def _unresolved(source: str, label: str) -> list[str]:
    tree = ast.parse(source)
    resolved = _resolved_names(tree)
    return [
        f"{label}:{call.lineno} spawns {ast.unparse(argv) if argv else '?'}"
        for call, argv in _spawns(tree)
        if not _is_resolved(argv, resolved)
    ]


def _inlined_copies(source: str) -> dict[str, str]:
    tree = ast.parse(source)
    return {
        node.name: ast.get_source_segment(source, node) or ""
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in _RESOLVERS
    }


def _hook_scripts() -> Iterator[tuple[str, str]]:
    for module in HOOK_TEMPLATE_MODULES:
        for name, renderer in inspect.getmembers(module, inspect.isfunction):
            if renderer.__module__ == module.__name__ and name.endswith("_script"):
                yield f"{module.__name__}.{name}", renderer()


def _canonical_scripts() -> Iterator[Path]:
    for pattern in CANONICAL_SCRIPT_GLOBS:
        yield from sorted(REPO_ROOT.glob(pattern))


class TestEverySpawnIsResolved(unittest.TestCase):
    def test_package(self) -> None:
        findings = [
            finding
            for path in sorted(SRC_ROOT.rglob("*.py"))
            for finding in _unresolved(
                path.read_text(encoding="utf-8"), path.relative_to(REPO_ROOT).as_posix()
            )
        ]
        self.assertEqual(findings, [])

    def test_generated_hooks(self) -> None:
        scripts = list(_hook_scripts())
        self.assertTrue(scripts, "no hook template renders a script")
        findings = [f for label, source in scripts for f in _unresolved(source, label)]
        self.assertEqual(findings, [])

    def test_canonical_skill_and_chore_scripts(self) -> None:
        findings = [
            finding
            for path in _canonical_scripts()
            for finding in _unresolved(
                path.read_text(encoding="utf-8"), path.relative_to(REPO_ROOT).as_posix()
            )
        ]
        self.assertEqual(findings, [])


class TestInlinedResolverIsThePackages(unittest.TestCase):
    def test_every_inlined_copy_matches(self) -> None:
        expected = {name: inspect.getsource(getattr(executables, name)) for name in _RESOLVERS}
        sources = [(label, source) for label, source in _hook_scripts()]
        sources += [
            (path.relative_to(REPO_ROOT).as_posix(), path.read_text(encoding="utf-8"))
            for path in _canonical_scripts()
        ]
        copies = 0
        for label, source in sources:
            for name, copy in _inlined_copies(source).items():
                copies += 1
                with self.subTest(source=label, function=name):
                    self.assertEqual(copy.strip(), expected[name].strip())
        self.assertGreater(copies, 0, "no surface carries an inlined resolver")


class TestTheScanSeesABareExecutable(unittest.TestCase):
    """The scan's own controls: each shape it must refuse, and each it must admit."""

    def test_refuses_a_bare_literal(self) -> None:
        source = 'import subprocess\nsubprocess.run(["git", "status"])\n'
        self.assertEqual(len(_unresolved(source, "planted")), 1)

    def test_refuses_a_variable_argv(self) -> None:
        source = "import subprocess\ndef f(cmd):\n    subprocess.run(cmd)\n"
        self.assertEqual(len(_unresolved(source, "planted")), 1)

    def test_admits_the_resolver_shapes(self) -> None:
        source = (
            "import subprocess, sys\n"
            "def f(cmd):\n"
            '    subprocess.run([resolve_executable("git"), "status"])\n'
            "    subprocess.run(resolve_argv(cmd))\n"
            '    subprocess.run([sys.executable, "-c", "pass"])\n'
            '    tool = find_executable("codex")\n'
            '    subprocess.run([tool, "--version"])\n'
        )
        self.assertEqual(_unresolved(source, "planted"), [])


if __name__ == "__main__":
    unittest.main()
