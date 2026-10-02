"""Gate-population enrollment beyond the validate scopes (GHI #1155 acceptance (a)).

``gate_enrollment`` inventories the ``gz validate`` scopes. The issue names four more
populations whose verdict can refuse completion, attestation or a push, and nothing
enumerated them: ``gz obpi precomplete`` checks, ``gz obpi complete`` refusals, ``gz
closeout`` gates, and the ``gz check`` steps that run no ``gz validate`` (the ones that do
are members of the scope population already). This module reads each from code and holds
it to the same contract: a member is named by a registered claim, or it is disclosed on the
shrink-only list ``data/gate_population_grandfather.json``.

**Members.** A precomplete check is a ``_check_*`` function ``_run_all_checks`` loads. A
complete refusal or closeout gate is a function in the command's module, reachable from its
entry point within that module, that refuses: it raises ``SystemExit``, ``GzCliError`` or
``PolicyBreachError``, or calls a refusal helper (``_fail``,
``_abort_closeout_with_blockers``), which are mechanisms rather than members. A check step is
a ``_build_check_steps`` entry, plus the ``Test (changed)`` step ``--fast`` substitutes,
whose runner holds no string that IS a ``gz validate`` command.

**Deciding functions.** A member's subject is the member itself plus the gzkit functions it
loads from other modules, lazy imports included, one level: a claim on a function several
calls below a member does not enroll it, the conservative direction (GHI #1155 increment 1
found that a recursive resolver mistook a claim on a helper for enrollment). An entry point
is its own subject only: its refusals are inline, and the functions it calls are the other
members' subjects. A member resolves at function granularity, so one claimed refusal enrolls
a function that holds several; the inventory says which claim enrolled it.

The issue names these populations as the starting set, not a claim of completeness: CLI
handlers outside them (``gz tidy``, ``gz validate --json``) carry claims of their own.
"""

from __future__ import annotations

import dis
import importlib
import re
import types
from collections.abc import Iterator, Mapping
from pathlib import Path

from gzkit.core.validation_rules import ValidationError
from gzkit.governance.trust_audits.gate_enrollment import claimed_functions, enrolled_claims
from gzkit.registries import RegistryError, load_registry

ACCEPTED_NAME = "gate_population_grandfather.json"
ACCEPTED_DISPLAY = f"data/{ACCEPTED_NAME}"
ENTRIES_KEY = "accepted_gates"
_RECOVER = "uv run gz validate --gate-enrollment"
_GATE_PREFIX = "gzkit."

#: Names whose presence in a function's bytecode marks it as refusing.
_REFUSALS = frozenset({"SystemExit", "GzCliError", "PolicyBreachError"})
#: Refusal helpers: they refuse on their caller's decision, so they mark and never join.
_REFUSAL_HELPERS = frozenset({"_fail", "_abort_closeout_with_blockers"})
#: (population, module, entry point) for the populations read as refusal reachability.
_COMMAND_ENTRIES: tuple[tuple[str, str, str], ...] = (
    ("complete-refusal", "gzkit.commands.obpi_complete", "obpi_complete_cmd"),
    ("closeout-gate", "gzkit.commands.closeout", "closeout_cmd"),
    ("closeout-gate", "gzkit.commands.closeout_ceremony", "ceremony_cmd"),
)
_VALIDATE_COMMAND = re.compile(r"(?:uv\s+run\s+)?gz\s+validate(?:\s+--[a-z0-9-]+)*")


def _err(artifact: str, message: str) -> ValidationError:
    return ValidationError(type="gate-enrollment", artifact=artifact, message=message)


def _code_objects(code: types.CodeType) -> Iterator[types.CodeType]:
    """Yield *code* and every code object nested in it (lambdas, comprehensions)."""
    yield code
    for const in code.co_consts:
        if isinstance(const, types.CodeType):
            yield from _code_objects(const)


def _imported(module: str, name: str) -> object:
    try:
        return getattr(importlib.import_module(module), name, None)
    except ImportError:
        return None


def _loaded(fn: types.FunctionType) -> dict[str, types.FunctionType]:
    """Return ``{module.qualname: function}`` for the gzkit functions *fn* loads."""
    found: dict[str, types.FunctionType] = {}
    for code in _code_objects(fn.__code__):
        module: str | None = None
        for ins in dis.get_instructions(code):
            target: object = None
            if ins.opname == "IMPORT_NAME":
                module = str(ins.argval)
            elif ins.opname == "IMPORT_FROM" and module is not None:
                target = _imported(module, str(ins.argval))
            elif ins.opname == "LOAD_GLOBAL":
                target = fn.__globals__.get(str(ins.argval))
            if isinstance(target, types.FunctionType) and target.__module__.startswith(
                _GATE_PREFIX
            ):
                found[f"{target.__module__}.{target.__qualname__}"] = target
    return found


def _names(fn: types.FunctionType) -> set[str]:
    return {
        str(i.argval) for code in _code_objects(fn.__code__) for i in dis.get_instructions(code)
    }


def _qualified(fn: types.FunctionType) -> str:
    return f"{fn.__module__}.{fn.__qualname__}"


def deciding_functions(fn: types.FunctionType) -> frozenset[str]:
    """Return *fn* and the gzkit functions it loads from other modules, one level."""
    external = {q for q, f in _loaded(fn).items() if f.__module__ != fn.__module__}
    return frozenset({_qualified(fn), *external})


def _refusing_members(entry: types.FunctionType) -> list[types.FunctionType]:
    """Return the functions in *entry*'s module, reachable from it there, that refuse."""
    seen = {entry.__qualname__}
    frontier, members = [entry], []
    while frontier:
        fn = frontier.pop()
        if _names(fn) & (_REFUSALS | _REFUSAL_HELPERS):
            members.append(fn)
        for local in _loaded(fn).values():
            name = local.__qualname__
            if local.__module__ == entry.__module__ and name not in seen | _REFUSAL_HELPERS:
                seen.add(name)
                frontier.append(local)
    return members


def _command_members() -> dict[str, frozenset[str]]:
    members: dict[str, frozenset[str]] = {}
    for population, module, entry_name in _COMMAND_ENTRIES:
        entry = getattr(importlib.import_module(module), entry_name)
        for fn in _refusing_members(entry):
            subject = frozenset({_qualified(fn)}) if fn is entry else deciding_functions(fn)
            members[f"{population}:{fn.__name__}"] = subject
    return members


def _precomplete_members() -> dict[str, frozenset[str]]:
    from gzkit.commands import obpi_precomplete  # noqa: PLC0415  (avoids an import cycle)

    checks = _loaded(obpi_precomplete._run_all_checks).values()
    return {
        f"precomplete-check:{fn.__name__}": deciding_functions(fn)
        for fn in checks
        if fn.__module__ == obpi_precomplete.__name__ and fn.__name__.startswith("_check_")
    }


def _runs_gz_validate(runner: types.FunctionType) -> bool:
    """Return True when a string constant of *runner* IS a ``gz validate`` command.

    The docstring is excluded: prose naming the command is not an invocation.
    """
    return any(
        isinstance(const, str)
        and const != runner.__doc__
        and _VALIDATE_COMMAND.fullmatch(const.strip())
        for nested in _code_objects(runner.__code__)
        for const in nested.co_consts
    )


def _check_step_members() -> dict[str, frozenset[str]]:
    from gzkit.commands import quality  # noqa: PLC0415  (avoids an import cycle)

    steps = [*quality._build_check_steps(), ("Test (changed)", quality._run_changed_tests)]
    return {
        f"check-step:{name}": deciding_functions(runner)
        for name, runner in steps
        if isinstance(runner, types.FunctionType) and not _runs_gz_validate(runner)
    }


def population_members() -> dict[str, frozenset[str]]:
    """Return ``{"population:member": deciding functions}`` for the four populations."""
    return {**_precomplete_members(), **_command_members(), **_check_step_members()}


def _load_accepted(project_root: Path) -> tuple[list[dict[str, object]], ValidationError | None]:
    try:
        payload = load_registry(project_root, ACCEPTED_NAME)
    except RegistryError:
        payload = None
    if not isinstance(payload, dict) or not isinstance(payload.get(ENTRIES_KEY), list):
        return [], _err(
            ACCEPTED_DISPLAY,
            f"{ACCEPTED_DISPLAY} is missing, unparseable or carries no '{ENTRIES_KEY}' list. "
            f"This inventory cannot tell a disclosed absence from a new one without it, and a "
            f"green run would assert something never measured. Repair the file. Re-run "
            f"`{_RECOVER}`.",
        )
    return [e for e in payload[ENTRIES_KEY] if isinstance(e, dict)], None


def _check_entry(
    entry: dict[str, object],
    members: Mapping[str, frozenset[str]],
    claimed: Mapping[str, frozenset[str]],
) -> tuple[str | None, list[ValidationError]]:
    """Return ``(member key or None, findings)`` for one disclosure entry."""
    population = str(entry.get("population", "")).strip()
    member = str(entry.get("member", "")).strip()
    if not population or not member:
        return None, [
            _err(
                ACCEPTED_DISPLAY,
                f"An entry in {ACCEPTED_NAME} lacks a 'population' or 'member', so it discloses "
                f"nothing that can be audited. Re-run `{_RECOVER}`.",
            )
        ]
    key = f"{population}:{member}"
    findings: list[ValidationError] = []
    if not str(entry.get("reason", "")).strip():
        findings.append(
            _err(
                key,
                f"Disclosed gate {key!r} carries no 'reason'. A disclosure without one records "
                f"that somebody noticed, not why it is tolerable. Re-run `{_RECOVER}`.",
            )
        )
    if key not in members:
        findings.append(
            _err(
                ACCEPTED_DISPLAY,
                f"Disclosed gate {key!r} is no longer a member of its population, so the entry "
                f"points at nothing and props up the shrink baseline. Remove it and lower "
                f"'baseline_count' in data/waiver_ratchet_registry.json. Re-run `{_RECOVER}`.",
            )
        )
    elif ids := enrolled_claims(members[key], claimed):
        findings.append(
            _err(
                ACCEPTED_DISPLAY,
                f"Disclosed gate {key!r} is now named by claim(s) {sorted(ids)}, so the "
                f"disclosure is stale. Surrender it: remove the entry and lower 'baseline_count' "
                f"in data/waiver_ratchet_registry.json. Re-run `{_RECOVER}`.",
            )
        )
    return key, findings


def audit_gate_population_enrollment(
    project_root: Path,
    *,
    members: Mapping[str, frozenset[str]] | None = None,
    claimed: Mapping[str, frozenset[str]] | None = None,
) -> list[ValidationError]:
    """Flag every member no claim names that is not disclosed, and every stale disclosure.

    Arms, as in ``audit_gate_enrollment``: an unnamed undisclosed member (the new hole); a
    disclosed member a claim now names; a disclosure naming no member; an entry with no
    member or reason; and an empty population or claim registry, where a green run would be
    the silence this inventory exists to break.
    """
    accepted, load_error = _load_accepted(project_root)
    if load_error is not None:
        return [load_error]
    population = population_members() if members is None else members
    named = claimed_functions() if claimed is None else claimed
    if not population or not named:
        return [
            _err(
                "gate-population" if not population else "enforcement-registry",
                "The gate populations or the enforcement registry are empty, so no member can "
                f"be compared with a claim. Re-run `{_RECOVER}`.",
            )
        ]
    errors: list[ValidationError] = []
    disclosed: set[str] = set()
    for entry in accepted:
        key, findings = _check_entry(entry, population, named)
        errors.extend(findings)
        if key is not None:
            disclosed.add(key)
    for key, functions in sorted(population.items()):
        if key in disclosed or enrolled_claims(functions, named):
            continue
        errors.append(
            _err(
                key,
                f"Gate {key!r} is named by no enforcement claim and is not disclosed. Its "
                f"deciding function(s): {', '.join(sorted(functions))}. Register an @enforces "
                f"claim whose entrypoint or gate_targets name one, with a control that fails "
                f"when its deciding guard is removed. NEVER add an entry to {ACCEPTED_NAME} to "
                f"silence a new gate (ADR-0.0.73 Boundary Invariant #8). Re-run `{_RECOVER}`.",
            )
        )
    return errors
