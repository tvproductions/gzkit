"""Gate-enrollment inventory and disclosure (GHI #1155).

``run_meta_validator`` verifies the claims that are PRESENT. It is structurally unable
to notice a gate that has NO claim, so a gate whose verdict decides completion,
attestation or a push can be green and unfalsified with nothing reporting the absence.
Nine of the twelve gates GHI #1154 lists had no registered claim on the function that
was hollow, measured at each fix commit's parent.

**Population.** The code already declares every ``gz validate`` scope in
``VALIDATOR_REGISTRY``; this audit reads that, never a second list (hexagonal rule 8).
Each scope's *deciding functions* are the gzkit callables its runner delegates to,
read from the runner's bytecode: attributes of the ``_ta()`` audit package and
module-level functions, one level through a local helper. A claim *names* a gate when
that function is its ``source_fn`` or one of its ``gate_targets``. Both are producer
facts, so this compares two read values and grades no prose.

**What this module is, and is not.** INVENTORY AND DISCLOSURE for the validate-scope
population, on the ``exemption_controls`` and ``gate_callers`` posture: a scope with no
claim is either named in the shrink-only accepted-list or a finding. It does not write
controls. Other gate populations (``gz check`` steps that run a tool, ``gz obpi
precomplete`` checks, ``gz obpi complete`` refusals, ``gz closeout`` steps) are not yet
enumerated here; the issue names them as the starting set, not a claim of completeness.
"""

from __future__ import annotations

import dis
import types
from collections.abc import Callable, Iterable, Mapping
from pathlib import Path

from gzkit.core.validation_rules import ValidationError
from gzkit.enforcement import EnforcementClaimRecord
from gzkit.registries import RegistryError, load_registry

ACCEPTED_NAME = "gate_enrollment_grandfather.json"
_ACCEPTED_DISPLAY = f"data/{ACCEPTED_NAME}"
_ENTRIES_KEY = "accepted_scopes"
_RECOVER = "uv run gz validate --gate-enrollment"
_GATE_PREFIX = "gzkit."


def _err(artifact: str, message: str) -> ValidationError:
    """Build one finding in this audit's namespace."""
    return ValidationError(type="gate-enrollment", artifact=artifact, message=message)


def delegated_functions(
    run: Callable[..., object],
    audit_package: types.ModuleType,
    local_module: str,
) -> frozenset[str]:
    """Return ``module.name`` of the gzkit callables a scope runner delegates to.

    Reads the runner's bytecode: an attribute of ``audit_package`` that is a gzkit
    function, or a module-level gzkit function. A function defined in ``local_module``
    is a helper, so it is followed ONE level and its own delegations are read instead.
    The depth bound keeps a helper's utilities from reading as the gate.
    """

    def read(code: types.CodeType, glb: dict[str, object], *, follow: bool) -> set[str]:
        found: set[str] = set()
        for ins in dis.get_instructions(code):
            fn: object = None
            if ins.opname == "LOAD_ATTR":
                fn = getattr(audit_package, str(ins.argval), None)
            elif ins.opname == "LOAD_GLOBAL":
                fn = glb.get(str(ins.argval))
            if not isinstance(fn, types.FunctionType) or not fn.__module__.startswith(_GATE_PREFIX):
                continue
            if fn.__module__ == local_module and follow:
                found |= read(fn.__code__, fn.__globals__, follow=False)
            elif fn.__module__ != local_module:
                found.add(f"{fn.__module__}.{fn.__qualname__}")
        return found

    code = getattr(run, "__code__", None)
    if not isinstance(code, types.CodeType):
        return frozenset()
    return frozenset(read(code, getattr(run, "__globals__", {}), follow=True))


def scope_population() -> dict[str, frozenset[str]]:
    """Return ``{scope stem: deciding functions}`` from ``VALIDATOR_REGISTRY``."""
    from gzkit.commands import validate_cmd  # noqa: PLC0415  (avoids an import cycle)

    audit_package = validate_cmd._ta()
    return {
        entry.stem: delegated_functions(entry.run, audit_package, validate_cmd.__name__)
        for entry in validate_cmd.VALIDATOR_REGISTRY
    }


def claimed_functions(
    records: Iterable[EnforcementClaimRecord] | None = None,
) -> dict[str, frozenset[str]]:
    """Return ``{function: claim ids naming it}``, over ``records`` or every production claim.

    A control passes the registry the floor run already populated, so one floor run
    does not rediscover its claims once per member it plants.
    """
    from gzkit.enforcement import production_enforcement_registry  # noqa: PLC0415

    named: dict[str, set[str]] = {}
    for record in production_enforcement_registry() if records is None else records:
        for target in (record.source_fn, *(t.replace(":", ".") for t in record.gate_targets)):
            named.setdefault(target, set()).add(record.claim_id)
    return {fn: frozenset(ids) for fn, ids in named.items()}


def enrolled_claims(
    functions: Iterable[str], claimed: Mapping[str, frozenset[str]]
) -> frozenset[str]:
    """Return the claim ids that name any of ``functions``."""
    return frozenset(c for fn in functions for c in claimed.get(fn, ()))


def _load_accepted(project_root: Path) -> tuple[list[dict[str, object]], ValidationError | None]:
    """Read the shrink-only accepted-list, or return the finding that it is unreadable."""
    try:
        payload = load_registry(project_root, ACCEPTED_NAME)
    except RegistryError:
        return [], _err(
            _ACCEPTED_DISPLAY,
            f"{_ACCEPTED_DISPLAY} is missing or unparseable. This inventory cannot tell a "
            f"disclosed absence from a new one without it, and a green run would assert "
            f"something never measured. Repair the file. Re-run `{_RECOVER}`.",
        )
    if not isinstance(payload, dict) or not isinstance(payload.get(_ENTRIES_KEY), list):
        return [], _err(
            _ACCEPTED_DISPLAY,
            f"{_ACCEPTED_DISPLAY} carries no '{_ENTRIES_KEY}' list. Re-run `{_RECOVER}`.",
        )
    return [e for e in payload[_ENTRIES_KEY] if isinstance(e, dict)], None


def _check_accepted_entry(
    entry: dict[str, object],
    population: Mapping[str, frozenset[str]],
    claimed: Mapping[str, frozenset[str]],
) -> tuple[str | None, list[ValidationError]]:
    """Return ``(scope id or None, findings)`` for one accepted-list entry."""
    scope = str(entry.get("scope", "")).strip()
    if not scope:
        return None, [
            _err(
                _ACCEPTED_DISPLAY,
                f"An entry in {ACCEPTED_NAME} has no 'scope' stem, so it accepts nothing and "
                f"cannot be audited. Re-run `{_RECOVER}`.",
            )
        ]
    findings: list[ValidationError] = []
    if not str(entry.get("reason", "")).strip():
        findings.append(
            _err(
                scope,
                f"Accepted scope {scope!r} carries no 'reason'. An acceptance without one records "
                f"that somebody noticed, not why it is tolerable. Re-run `{_RECOVER}`.",
            )
        )
    if scope not in population:
        findings.append(
            _err(
                _ACCEPTED_DISPLAY,
                f"Accepted scope {scope!r} is not a registered validate scope any more, so the "
                f"acceptance points at nothing and props up the shrink baseline. Remove the entry "
                f"and decrement 'baseline_count' in data/waiver_ratchet_registry.json. "
                f"Re-run `{_RECOVER}`.",
            )
        )
    elif ids := enrolled_claims(population[scope], claimed):
        findings.append(
            _err(
                _ACCEPTED_DISPLAY,
                f"Accepted scope {scope!r} is now named by claim(s) {sorted(ids)}, so the "
                f"acceptance is stale. Surrender it: remove the entry and decrement "
                f"'baseline_count' in data/waiver_ratchet_registry.json; that is what keeps this "
                f"list shrink-only. Re-run `{_RECOVER}`.",
            )
        )
    return scope, findings


def audit_gate_enrollment(
    project_root: Path,
    *,
    population: Mapping[str, frozenset[str]] | None = None,
    claimed: Mapping[str, frozenset[str]] | None = None,
) -> list[ValidationError]:
    """Flag every validate scope no claim names that is not accepted, and every stale entry.

    Returns one :class:`ValidationError` per finding (non-empty means exit 3). Arms:

    1. a scope no claim names and absent from the accepted-list: the new hole;
    2. an accepted scope a claim now names: the stale acceptance;
    3. an accepted scope that no longer exists: a dead pointer;
    4. an accepted entry with no scope or no reason;
    5. an empty population or an empty claim registry: with nothing to compare, a green
       run would be the silence this inventory exists to break.
    """
    accepted, load_error = _load_accepted(project_root)
    if load_error is not None:
        return [load_error]
    scopes = scope_population() if population is None else population
    named = claimed_functions() if claimed is None else claimed
    if not scopes or not named:
        return [
            _err(
                "validate-registry" if not scopes else "enforcement-registry",
                "The scope population or the enforcement registry is empty, so no scope can be "
                "compared with a claim and a green run would assert something never measured. "
                f"Re-run `{_RECOVER}`.",
            )
        ]

    errors: list[ValidationError] = []
    accepted_ids: set[str] = set()
    for entry in accepted:
        scope, findings = _check_accepted_entry(entry, scopes, named)
        errors.extend(findings)
        if scope is not None:
            accepted_ids.add(scope)

    for scope, functions in sorted(scopes.items()):
        if scope in accepted_ids or enrolled_claims(functions, named):
            continue
        deciding = ", ".join(sorted(functions)) or "none resolved from its runner"
        errors.append(
            _err(
                scope,
                f"Validate scope {scope!r} is named by no enforcement claim and is not on the "
                f"disclosed list. Its deciding function(s): {deciding}. Register an @enforces "
                f"claim whose entrypoint or gate_targets name it, with a control that fails when "
                f"its deciding guard is removed. NEVER add an entry to {ACCEPTED_NAME} to "
                f"silence a newly authored scope; that is the laundering ADR-0.0.73 Boundary "
                f"Invariant #8 forbids. Re-run `{_RECOVER}`.",
            )
        )
    return errors
