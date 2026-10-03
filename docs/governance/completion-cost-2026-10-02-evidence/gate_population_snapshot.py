"""Re-apply HEAD's gate_population membership definition to a snapshot's src tree."""

import dis
import importlib
import json
import re
import sys
import types

sys.setrecursionlimit(10000)
_REFUSALS = frozenset({"SystemExit", "GzCliError", "PolicyBreachError"})
_REFUSAL_HELPERS = frozenset({"_fail", "_abort_closeout_with_blockers"})
_COMMAND_ENTRIES = (
    ("complete-refusal", "gzkit.commands.obpi_complete", "obpi_complete_cmd"),
    ("closeout-gate", "gzkit.commands.closeout", "closeout_cmd"),
    ("closeout-gate", "gzkit.commands.closeout_ceremony", "ceremony_cmd"),
)
_VALIDATE_COMMAND = re.compile(r"(?:uv\s+run\s+)?gz\s+validate(?:\s+--[a-z0-9-]+)*")


def _code_objects(code):
    yield code
    for c in code.co_consts:
        if isinstance(c, types.CodeType):
            yield from _code_objects(c)


def _imported(m, n):
    try:
        return getattr(importlib.import_module(m), n, None)
    except ImportError:
        return None


def _loaded(fn):
    found = {}
    for code in _code_objects(fn.__code__):
        module = None
        for ins in dis.get_instructions(code):
            t = None
            if ins.opname == "IMPORT_NAME":
                module = str(ins.argval)
            elif ins.opname == "IMPORT_FROM" and module is not None:
                t = _imported(module, str(ins.argval))
            elif ins.opname == "LOAD_GLOBAL":
                t = fn.__globals__.get(str(ins.argval))
            if isinstance(t, types.FunctionType) and t.__module__.startswith("gzkit."):
                found[f"{t.__module__}.{t.__qualname__}"] = t
    return found


def _names(fn):
    return {str(i.argval) for c in _code_objects(fn.__code__) for i in dis.get_instructions(c)}


def _refusing(entry):
    seen = {entry.__qualname__}
    frontier, members = [entry], []
    while frontier:
        fn = frontier.pop()
        if _names(fn) & (_REFUSALS | _REFUSAL_HELPERS):
            members.append(fn)
        for local in _loaded(fn).values():
            if (
                local.__module__ == entry.__module__
                and local.__qualname__ not in seen | _REFUSAL_HELPERS
            ):
                seen.add(local.__qualname__)
                frontier.append(local)
    return members


out = {}
for pop, mod, entry in _COMMAND_ENTRIES:
    try:
        e = getattr(importlib.import_module(mod), entry)
    except Exception as exc:  # noqa: BLE001
        out.setdefault("errors", []).append(f"{mod}.{entry}: {exc!r}")
        continue
    for fn in _refusing(e):
        out.setdefault(pop, []).append(fn.__name__)
try:
    from gzkit.commands import obpi_precomplete as p

    out["precomplete-check"] = sorted(
        f.__name__
        for f in _loaded(p._run_all_checks).values()
        if f.__module__ == p.__name__ and f.__name__.startswith("_check_")
    )
except Exception as exc:  # noqa: BLE001
    out.setdefault("errors", []).append(f"precomplete: {exc!r}")
try:
    from gzkit.commands import quality as q

    steps = list(q._build_check_steps())
    if hasattr(q, "_run_changed_tests"):
        steps.append(("Test (changed)", q._run_changed_tests))
    allsteps, nonval, val = [], [], []
    for name, runner in steps:
        allsteps.append(name)
        if isinstance(runner, types.FunctionType):
            is_val = any(
                isinstance(c, str)
                and c != runner.__doc__
                and _VALIDATE_COMMAND.fullmatch(c.strip())
                for n in _code_objects(runner.__code__)
                for c in n.co_consts
            )
            (val if is_val else nonval).append(name)
    out["check-steps-all"] = allsteps
    out["check-step"] = nonval
    out["check-step-validate"] = val
except Exception as exc:  # noqa: BLE001
    out.setdefault("errors", []).append(f"quality: {exc!r}")
for k in list(out):
    if isinstance(out[k], list) and k != "errors":
        out[k] = sorted(set(out[k]))
print(json.dumps(out, indent=1))
