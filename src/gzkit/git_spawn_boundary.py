"""AST predicate: which test files spawn ``git`` with the inherited environment (GHI #977).

A test that runs ``subprocess.run(["git", ...])`` without an ``env=`` built by the
fixture boundary inherits whatever repository-selection state the process was
started with. A git hook exports an absolute ``GIT_DIR`` — from a linked worktree,
``<repo>/.git/worktrees/<name>`` — so ``git init`` in a temp dir re-initialises the
HOSTING repository (guessing bare, because that gitdir's basename is not ``.git``)
and ``git config`` writes the fixture identity into its shared config. Measured
2026-09-07 from the pre-push ``gz check`` gate.

The predicate is production code so the enforcement floor can drive it against a
planted violation (claim ``git-fixture-isolation``); the fail-closed gate is the
suite itself, through ``tests/commands/test_common_fixtures.py``, which fails on
any offender this function reports.

Scope, declared: literal ``git`` argv only — ``subprocess.<spawner>(["git", ...])``
where ``spawner`` is ``run``, ``check_output``, ``check_call``, ``call`` or ``Popen``.
A helper whose argv arrives as a parameter is outside the fence and must be read.
"""

from __future__ import annotations

import ast
from pathlib import Path

#: ``subprocess`` attributes that start a child process.
SPAWNERS: frozenset[str] = frozenset({"run", "check_output", "check_call", "call", "Popen"})

#: The boundary helper a ``git`` spawn's ``env=`` must come from.
BOUNDARY_NAME = "_isolated_git_env"


def _spawns_git(node: ast.Call) -> bool:
    """Return True when *node* is ``subprocess.<spawner>(["git", ...], ...)``."""
    func = node.func
    if not (
        isinstance(func, ast.Attribute)
        and isinstance(func.value, ast.Name)
        and func.value.id == "subprocess"
        and func.attr in SPAWNERS
        and node.args
    ):
        return False
    argv = node.args[0]
    return (
        isinstance(argv, ast.List)
        and bool(argv.elts)
        and isinstance(argv.elts[0], ast.Constant)
        and argv.elts[0].value == "git"
    )


def _inside_boundary(node: ast.Call) -> bool:
    """Return True when the call's ``env=`` is the boundary call or a local name bound from it."""
    env = next((kw.value for kw in node.keywords if kw.arg == "env"), None)
    if isinstance(env, ast.Name):
        return True
    return (
        isinstance(env, ast.Call)
        and isinstance(env.func, ast.Name)
        and env.func.id == BOUNDARY_NAME
    )


def git_spawns_outside_boundary(tests_root: Path) -> list[str]:
    """Return ``<path>:<line>`` for every unguarded literal ``git`` spawn under *tests_root*.

    Paths are relative to *tests_root*'s parent (the project root). Files that do
    not parse are reported as offenders too: a fence that skips what it cannot
    read is a fence with a hole shaped like a syntax error.
    """
    offenders: list[str] = []
    base = tests_root.parent
    for path in sorted(tests_root.rglob("*.py")):
        rel = path.relative_to(base).as_posix()
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError):
            offenders.append(f"{rel}:0 (unparseable)")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and _spawns_git(node) and not _inside_boundary(node):
                offenders.append(f"{rel}:{node.lineno}")
    return offenders
