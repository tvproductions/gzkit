"""AST predicate: which test files spawn ``git`` with the inherited environment (GHI #977).

A test that runs ``subprocess.run(["git", ...])`` without an ``env=`` built by the
fixture boundary inherits whatever repository-selection state the process was
started with. A git hook exports an absolute ``GIT_DIR`` — from a linked worktree,
``<repo>/.git/worktrees/<name>`` — so ``git init`` in a temp dir re-initialises the
HOSTING repository (guessing bare, because that gitdir's basename is not ``.git``)
and ``git config`` writes the fixture identity into its shared config. Measured
2026-09-07 from the pre-push ``gz check`` gate.

Two layers, one definition of "repo-local" (:data:`GIT_REPO_LOCAL_ENV`):

* :func:`scrub_repo_local_git_env` — the process chokepoint ``tests/__init__.py``
  applies once, so every child process a test or the code it drives spawns
  starts clean.
* :func:`isolated_git_env` — the per-call ``env=`` every ``git`` a test spawns
  passes, the explicit local statement of the same boundary, fenced by
  :func:`git_spawns_outside_boundary`.

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
from collections.abc import Mapping, MutableMapping
from pathlib import Path

#: Git's own list of the environment variables that are LOCAL TO ONE REPOSITORY —
#: ``local_repo_env`` in git's ``environment.c``, the set git itself clears before
#: running a child git against a *different* repository (a submodule). Deliberately
#: NOT here: ``GIT_CONFIG_GLOBAL`` / ``GIT_CONFIG_SYSTEM`` / ``GIT_CONFIG_NOSYSTEM``
#: (they route the USER's own config, which a fixture inherits by design),
#: ``GIT_AUTHOR_*`` / ``GIT_COMMITTER_*`` (identity), ``GIT_SSH*`` / ``GIT_ASKPASS`` /
#: ``GIT_TERMINAL_PROMPT`` (auth and transport), ``GIT_EXEC_PATH`` / ``GIT_EDITOR`` /
#: ``GIT_TRACE*`` (toolchain and diagnostics), and the discovery modifiers
#: ``GIT_CEILING_DIRECTORIES`` / ``GIT_DISCOVERY_ACROSS_FILESYSTEM`` / ``GIT_NAMESPACE``,
#: which git does not classify as repo-local either.
GIT_REPO_LOCAL_ENV: frozenset[str] = frozenset(
    {
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_CONFIG",
        "GIT_CONFIG_PARAMETERS",
        "GIT_CONFIG_COUNT",
        "GIT_OBJECT_DIRECTORY",
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_IMPLICIT_WORK_TREE",
        "GIT_GRAFT_FILE",
        "GIT_INDEX_FILE",
        "GIT_NO_REPLACE_OBJECTS",
        "GIT_REPLACE_REF_BASE",
        "GIT_PREFIX",
        "GIT_SHALLOW_FILE",
        "GIT_COMMON_DIR",
    }
)

#: ``GIT_CONFIG_KEY_<n>`` / ``GIT_CONFIG_VALUE_<n>`` inject config values and are read
#: only under ``GIT_CONFIG_COUNT``; dropped with it so no half-pair lingers.
GIT_CONFIG_INJECTION_PREFIXES: tuple[str, ...] = ("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_")


def is_repo_local_git_var(name: str) -> bool:
    """Return True when *name* selects a repository or injects config for git."""
    return name in GIT_REPO_LOCAL_ENV or name.startswith(GIT_CONFIG_INJECTION_PREFIXES)


#: Config a fixture git is PINNED to, injected after the inherited injection is
#: scrubbed. ``core.autocrlf`` is the one that bites: Git for Windows defaults it
#: to ``true``, so ``git checkout -- <surface>`` rewrites LF to CRLF and a
#: BYTE-MEASURED surface gains a byte per line. Measured 2026-09-07 on
#: ``windows-latest``: a fixture seeded a declaration at floor 26 from the
#: in-memory text, checked the surface back out through git, and the loader then
#: refused — ``summed byte span ... is 28, which exceeds it`` (GHI #982). The
#: fixtures already write surfaces with ``write_bytes`` for exactly this reason
#: (GHI #958); git was the remaining translation point, and it sat outside every
#: guard because it is not a Python write.
PINNED_FIXTURE_GIT_CONFIG: tuple[tuple[str, str], ...] = (
    ("core.autocrlf", "false"),
    ("core.eol", "lf"),
)


def isolated_git_env(base: Mapping[str, str]) -> dict[str, str]:
    """Return a copy of *base* minus git's repo-local variables, plus pinned config.

    Pass the result as ``env=`` to a ``git`` spawned against a temporary
    repository, so it operates on the repository its ``cwd`` (or ``-C``) names
    regardless of what the process inherited — from a git hook, an IDE task,
    ``git bisect run``, or a ``GIT_DIR=`` shell. Run INSIDE a checkout, a
    scrubbed ``git`` still discovers that same checkout — the main one through
    ``.git/``, a linked worktree through its gitfile — so a command that means
    to inspect its hosting repository is not redirected.

    ISOLATION IS FROM THE PLATFORM, NOT ONLY FROM THE REPOSITORY. Scrubbing
    answers *which repository* a fixture git operates on; it said nothing about
    *what bytes* that git writes, and on Windows the answer differs from POSIX
    by default. :data:`PINNED_FIXTURE_GIT_CONFIG` is therefore injected here
    rather than repeated at each ``git init`` — the same one-authority argument
    the scrub list makes, and the reason a per-fixture ``git config`` call would
    have closed one instance of the failure rather than its class.

    The injection uses ``GIT_CONFIG_COUNT``/``GIT_CONFIG_KEY_<n>``, which the
    scrub above removes from the inherited environment; these are written AFTER
    that filter, so a fixture's pins can never be a caller's leftovers.
    """
    env = {key: value for key, value in base.items() if not is_repo_local_git_var(key)}
    for index, (key, value) in enumerate(PINNED_FIXTURE_GIT_CONFIG):
        env[f"GIT_CONFIG_KEY_{index}"] = key
        env[f"GIT_CONFIG_VALUE_{index}"] = value
    env["GIT_CONFIG_COUNT"] = str(len(PINNED_FIXTURE_GIT_CONFIG))
    return env


def scrub_repo_local_git_env(environ: MutableMapping[str, str]) -> list[str]:
    """Remove git's repo-local variables from *environ* in place; return what was removed.

    The process-level form of :func:`isolated_git_env`, for a chokepoint every
    child process descends from — the test package's ``__init__``. Per-call
    ``env=`` covers the git a test spawns itself; it cannot cover the git that
    PRODUCTION code spawns when a test drives it against a temp root (the
    merge-driver installer, the commit-locus recorder, ``git_cmd``), and
    production code honouring ``GIT_DIR`` is correct git-tool behaviour. Measured
    2026-09-07: with every fixture site guarded, a linked-worktree push still
    left the hosting clone bare with three foreign commits on its branch.
    """
    removed = sorted(key for key in environ if is_repo_local_git_var(key))
    for key in removed:
        del environ[key]
    return removed


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
