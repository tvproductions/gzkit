"""Import-cost guard for the ``gz --help`` path (GHI #180).

``gzkit.cli.main`` states the invariant this guard enforces, at module scope:
resolving handler attributes at import time pulls
``gzkit.commands.common -> gzkit.sync -> yaml`` into *every* ``gz --help``
invocation, so those attributes are deferred behind a PEP 562 ``__getattr__``.

That guard defends one door. Two others stood open, and both were found by
measurement rather than by reading:

  1. ``gzkit.commands.insights`` — one of two ``register_*_parsers`` functions
     living under ``gzkit.commands.`` instead of ``gzkit.cli.parser_*``, so
     ``main.py`` imports it eagerly to build the parser — pulled
     ``gzkit.commands.common`` at module scope for symbols only its *handler*
     needs.
  2. ``gzkit.cli.helpers.durations`` imported ``console`` from the same module at
     module scope, for use on two error branches. Every registrar was
     individually clean; the parser tree pulled ``common`` through the helpers
     package instead.

Door 2 is why this guard is a **transitive reachability** check and not a
per-module one. A check scoped to the registrars passes while a helper three
edges away re-opens the same path, which is precisely what happened.

**Why static AST rather than observing ``sys.modules``.** The first version of
this guard evicted ``gzkit.*`` from ``sys.modules``, rebuilt the parser, and
asserted on what got imported. It measured the right thing and broke a sibling:
``tests/test_closeout_migration.py`` reads ``gzkit.commands.closeout.__file__``,
and a submodule first imported *during* the eviction window binds its attribute
to the fresh parent package, which teardown then discards — so the attribute
vanished for every later test in the process. Import-time state is global, and a
unit test must not mutate it. The unit-tier contract also forbids the subprocess
that would isolate it properly (`.gzkit/rules/tests.md` § Unit-tier contract).

So the assertion is computed from source: build the module-level import graph by
AST and ask whether the forbidden module is reachable from the CLI entry point.
Module-level means import-time — imports inside a function body are deferred and
are exactly the fix this guard protects, so function bodies are not traversed.
"""

from __future__ import annotations

import ast
import unittest
from collections import deque
from pathlib import Path

_SRC = Path("src")
_PACKAGE_ROOT = _SRC / "gzkit"

# Entry point whose import cost every `gz` invocation pays, `--help` included.
_ENTRY_MODULE = "gzkit.cli.main"

# Modules that must not be reachable at module scope from the entry point.
#
# SCOPE — read before adding to this tuple. ``yaml`` and ``pydantic`` are NOT
# listed, and their absence is deliberate rather than an oversight: a third door
# is still open. ``gzkit.cli.parser_obpi`` imports ``DEFAULT_LOCK_TTL_MINUTES``
# from ``gzkit.lock_manager`` (which imports yaml and pydantic at module scope)
# and uses it as an argparse ``default=`` — a *registration-time* value, so
# deferring the import into the register function would change nothing, because
# registration IS the parser build. Closing it means relocating that constant
# into a dependency-free module: a structural change to a domain module, past
# AGENTS.md § Defect-fix routing's thresholds for the direct fix that produced
# this guard. Listing them today would make this test RED with no in-scope fix,
# so the tuple states the doors actually closed. Add them in the same change that
# relocates the constant — not before.
_FORBIDDEN_AT_IMPORT_TIME = ("gzkit.commands.common",)


def _module_name(path: Path) -> str:
    """``src/gzkit/cli/main.py`` -> ``gzkit.cli.main`` (packages drop ``__init__``)."""
    parts = path.relative_to(_SRC).with_suffix("").parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _module_level_imports(tree: ast.Module, module: str) -> set[str]:
    """Every ``gzkit.*`` module imported at import time by *module*.

    Function bodies are skipped: an import inside a function is deferred to call
    time and costs the help path nothing. Class bodies ARE traversed — they
    execute on import.
    """
    found: set[str] = set()

    def visit(node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            if isinstance(child, ast.Import):
                found.update(a.name for a in child.names if a.name.startswith("gzkit"))
            elif isinstance(child, ast.ImportFrom):
                found.update(_resolve_import_from(child, module))
            visit(child)

    visit(tree)
    return found


def _resolve_import_from(node: ast.ImportFrom, module: str) -> set[str]:
    """Resolve ``from X import a, b`` to candidate ``gzkit.*`` module names."""
    if node.level:  # relative import — resolve against the importing package
        base_parts = module.split(".")[: -node.level] if node.level else module.split(".")
        base = ".".join([*base_parts, node.module] if node.module else base_parts)
    else:
        base = node.module or ""
    if not base.startswith("gzkit"):
        return set()
    # ``from gzkit.commands import common`` names a module via the alias list, so
    # both the package and each ``package.alias`` are candidate modules.
    return {base} | {f"{base}.{a.name}" for a in node.names}


def _import_graph() -> dict[str, set[str]]:
    """Module-level ``gzkit.*`` import edges for every module under ``src/gzkit``."""
    graph: dict[str, set[str]] = {}
    for path in _PACKAGE_ROOT.rglob("*.py"):
        module = _module_name(path)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        graph[module] = _module_level_imports(tree, module)
    return graph


class TestHelpPathImports(unittest.TestCase):
    """Handler-only dependencies must be unreachable at import time from the CLI."""

    def test_entry_point_does_not_reach_handler_dependencies(self) -> None:
        graph = _import_graph()
        self.assertIn(_ENTRY_MODULE, graph, "entry module not found under src/gzkit")

        # BFS over module-level edges, recording one shortest path per node so a
        # failure names the chain to fix rather than only its endpoint.
        paths: dict[str, list[str]] = {_ENTRY_MODULE: [_ENTRY_MODULE]}
        queue = deque([_ENTRY_MODULE])
        while queue:
            current = queue.popleft()
            for imported in graph.get(current, set()):
                if imported in paths or imported not in graph:
                    continue
                paths[imported] = [*paths[current], imported]
                queue.append(imported)

        for forbidden in _FORBIDDEN_AT_IMPORT_TIME:
            with self.subTest(forbidden=forbidden):
                # Assert on the chain, never on ``paths``: unittest renders the
                # whole container on failure, and that dict is every reachable
                # module with its route — kilobytes of noise around the one chain
                # the failure is about.
                chain = paths.get(forbidden)
                self.assertIsNone(
                    chain,
                    f"{forbidden} is reachable at import time from {_ENTRY_MODULE} "
                    f"via {' -> '.join(chain or [])}. Every `gz --help` pays that "
                    f"import (GHI #180) — defer it into the function that uses it.",
                )
