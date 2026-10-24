"""Which production lines each test module executes, read in a commit's tree (GHI #1260).

``gz arb red --commit`` reverted every hunk against every test module its commit
touched. A module that never executes a hunk's lines cannot fail because of them,
so running it grades nothing and only costs time; RO-9 tranche 1's 57 hunks took
a 992 s serial run each and could not finish. This module records, once per
module, the lines that module executes, so each mutant runs against only the
modules that reach it.

Reach is read with :mod:`sys.monitoring` from a ``sitecustomize`` placed first on
``PYTHONPATH``, so a test that drives the code in a child interpreter (a hook, a
``python -m gzkit`` run) is counted too. Each location reports once and is then
disabled, which keeps the traced run close to an untraced one.

What it cannot see: a test that reads a function's source without running it, and a
child started with ``-I``, ``-S`` or an environment that drops ``PYTHONPATH``. Such a
module is left out of a hunk it would have killed, which reads as ``survived``,
never as a false kill.
"""

import json
import subprocess
import tempfile
from collections.abc import Callable, Sequence
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.unit_run_provenance import read_test_observations

_SITECUSTOMIZE = """\
import atexit, json, os, sys


def _install():
    root, out = os.environ.get("GZKIT_REACH_ROOT"), os.environ.get("GZKIT_REACH_OUT")
    if not root or not out:
        return
    mon = sys.monitoring
    tool = next((t for t in (3, 4) if mon.get_tool(t) is None), None)
    if tool is None:
        return
    mon.use_tool_id(tool, "gzkit-reach")
    prefix = os.path.realpath(root) + os.sep
    files, seen = {}, set()

    def line(code, number):
        name = code.co_filename
        rel = files.get(name, False)
        if rel is False:
            real = os.path.realpath(name)
            rel = real[len(prefix):].replace(os.sep, "/") if real.startswith(prefix) else None
            files[name] = rel
        if rel is not None:
            seen.add((rel, number))
        return mon.DISABLE

    def dump():
        path = os.path.join(out, f"{os.getpid()}-{id(seen)}.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(sorted(seen), handle)

    mon.register_callback(tool, mon.events.LINE, line)
    mon.set_events(tool, mon.events.LINE)
    atexit.register(dump)


_install()
"""

Runner = Callable[..., subprocess.CompletedProcess[str]]


class ModuleReach(BaseModel):
    """What one test module ran on the commit's tree."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    lines: frozenset[tuple[str, int]] = Field(..., description="(repo-relative path, line) run")
    tests: frozenset[str] = Field(..., description="Executed test IDs")


def trace_reach(
    worktree: Path, modules: Sequence[str], runner: Sequence[str], run: Runner
) -> dict[str, ModuleReach]:
    """Run each module once under the tracer and return what it reached.

    ``run`` is the sweep's own runner, so the hang bound applies here too: a module
    that does not return raises :class:`subprocess.TimeoutExpired` to the caller.
    """
    reach: dict[str, ModuleReach] = {}
    with tempfile.TemporaryDirectory() as tmp:
        hook = Path(tmp) / "hook"
        hook.mkdir()
        (hook / "sitecustomize.py").write_text(_SITECUSTOMIZE, encoding="utf-8")
        for module in modules:
            out = Path(tmp) / "out" / module
            out.mkdir(parents=True)
            env = {"GZKIT_REACH_ROOT": str(worktree), "GZKIT_REACH_OUT": str(out)}
            result = run(
                [*runner, module],
                worktree,
                Path(tmp) / "pyc",
                extra_env=env,
                pythonpath_prefix=str(hook),
            )
            executed, _, _ = read_test_observations((result.stdout or "") + (result.stderr or ""))
            lines = {
                (str(rel), int(number))
                for dump in out.glob("*.json")
                for rel, number in json.loads(dump.read_text(encoding="utf-8"))
            }
            reach[module] = ModuleReach(lines=frozenset(lines), tests=frozenset(executed))
    return reach


def reaching_modules(reach: dict[str, ModuleReach], path: str, first: int, last: int) -> list[str]:
    """Return the modules that executed any of ``path``'s lines ``first..last``.

    When none did, every module is returned: the trace may have missed a child it
    could not see, and grading against all of them is the witness's prior behavior.
    """
    span = {(path, n) for n in range(first, last + 1)}
    return sorted(m for m, r in reach.items() if r.lines & span) or sorted(reach)
