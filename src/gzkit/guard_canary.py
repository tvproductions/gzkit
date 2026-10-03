"""Reviewed guard mutation canaries (GHI #1154 item 5, GHI #1155).

A registered enforcement claim proves a gate by planting an input the gate must refuse. That
proof can be erased without anyone deciding to: the guard changes, the test that kills a
mutant of it is renamed, weakened or deleted, and the claim still reads green. A canary binds
one reviewed mutant to one registered claim, so any of those changes is a finding.

Operator ruling (GHI #1154, defaults taken 2026-10-01, "approve all three"): a canary is
bound by a hash of the guard source, the claim (the REQ it witnesses) and the designated
failing test id. This module checks two things, kept apart because they fail differently.

* **Binding (static, cheap).** The recorded hash still equals the hash of the guard's current
  source, the claim id and the test id; the claim is registered; the test id resolves to a
  test definition; the mutation's target occurs exactly once in the guard's file and is inside
  the guard. A stale hash means the guard moved since a human last saw it, so the canary must
  be re-reviewed, never silently re-hashed.
* **Kill (live, on an isolated copy).** The mutant is applied to a copy of the tree and the
  designated test must fail. The copy is the point: a sweep rewrites the source file it
  mutates, and running one against the working tree while other tests import it would corrupt
  them. The verdict is ``gzkit.mutation_witness``'s four-way one; only ``killed`` passes.

A claim with no canary is a finding unless it is on the shrink-only roster
(``guard_canary_grandfather.json``), the same disclosure posture as GHI #1155's enrollment.
"""

from __future__ import annotations

import ast
import contextlib
import hashlib
import importlib
import importlib.util
import inspect
import json
import shutil
import sys
import tempfile
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.core import exceptions as gz_errors
from gzkit.core.validation_rules import ValidationError
from gzkit.ledger import Ledger
from gzkit.ledger_events import guard_canary_reviewed_event
from gzkit.mutation_witness import Mutation, MutationOutcome, run_mutation_sweep
from gzkit.registries import load_registry, registry_path

_LEDGER = Path(".gzkit") / "ledger.jsonl"
_REVIEW_EVENT = "guard_canary_reviewed"
_CANARY_REGISTRY = "guard_canaries.json"
_GRANDFATHER_REGISTRY = "guard_canary_grandfather.json"
_RECOVER = "re-review the canary, then rebind it (see the registry's _doc)"
_COPIED = ("src", "tests")
_BOOTSTRAP = "import sys; sys.path[:0] = ['src', '.']; import unittest; unittest.main(module=None)"
_REQUIRED = ("claim_id", "guard", "failing_test", "binding_sha256", "authority")


class CanaryMutation(BaseModel):
    """The reviewed mutant: one exact text substitution in the guard's file."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    find: str = Field(..., min_length=1)
    replace: str
    label: str = Field(..., min_length=1)


class Canary(BaseModel):
    """One reviewed mutant bound to one registered claim."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    claim_id: str = Field(..., min_length=1)
    guard: str = Field(..., description="module:qualname of the function the claim gates")
    failing_test: str = Field(..., description="Dotted unittest id that must fail on the mutant")
    mutation: CanaryMutation
    binding_sha256: str = Field(..., min_length=64, max_length=64)
    authority: str = Field(..., min_length=1, description="Ruling or GHI the canary rests on")
    proposed_by: str = Field(default="")
    reviewed_by: str | None = Field(default=None)


class CanaryRun(BaseModel):
    """The observed result of one canary's live run."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    claim_id: str
    outcome: MutationOutcome
    reason: str = ""


def binding_hash(guard_source: str, claim_id: str, failing_test: str) -> str:
    """Return the hash that binds a canary to the guard, the claim and the designated test."""
    payload = "\n".join((guard_source, claim_id, failing_test))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _lookup(guard: str) -> object | None:
    """Return the object named ``module:qualname``, or ``None`` when it does not resolve."""
    module_name, _, qualname = guard.partition(":")
    target: object | None = None
    with contextlib.suppress(ImportError, AttributeError):
        target = importlib.import_module(module_name)
        for part in qualname.split("."):
            target = getattr(target, part)
    return target


def resolve_guard(guard: str) -> tuple[str, Path] | None:
    """Return (source text, file) of the function named ``module:qualname``, or ``None``."""
    target = _lookup(guard)
    if not inspect.isfunction(target):
        return None
    return inspect.getsource(target), Path(inspect.getsourcefile(target) or "")


def _defines(tree: ast.AST, names: list[str]) -> bool:
    """Return True when *tree* defines the nested class/function path *names*."""
    scope: ast.AST = tree
    for name in names:
        found = next(
            (
                node
                for node in getattr(scope, "body", [])
                if isinstance(node, ast.ClassDef | ast.FunctionDef) and node.name == name
            ),
            None,
        )
        if found is None:
            return False
        scope = found
    return True


def _module_file(name: str) -> str | None:
    """Return the ``.py`` file module *name* lives in, or ``None`` when it is not a module."""
    try:
        spec = importlib.util.find_spec(name)
    except (ImportError, ValueError):  # a prefix that is a class or function is not a module
        spec = None
    origin = None if spec is None else spec.origin
    return origin if origin and origin.endswith(".py") else None


def _test_module_source(parts: list[str]) -> tuple[ast.AST, list[str]] | None:
    """Return the parsed module a dotted test id lives in and the path left inside it."""
    candidates = (
        (_module_file(".".join(parts[:split])), split) for split in range(len(parts) - 1, 0, -1)
    )
    found = next(((origin, split) for origin, split in candidates if origin), None)
    if found is None:
        return None
    origin, split = found
    return ast.parse(Path(origin).read_text(encoding="utf-8")), parts[split:]


def resolves_test_id(test_id: str) -> bool:
    """Return True when a dotted unittest id names a test definition, without importing it."""
    found = _test_module_source(test_id.split("."))
    return found is not None and _defines(*found)


def load_canaries(project_root: Path) -> list[Canary]:
    """Return the committed canaries, validated into models."""
    payload = load_registry(project_root, _CANARY_REGISTRY)
    return [Canary.model_validate(c) for c in payload.get("canaries", [])]


def _err(artifact: str, message: str) -> ValidationError:
    return ValidationError(type="guard-canary", artifact=artifact, message=message)


def _check_one(canary: Canary, registered: set[str]) -> list[ValidationError]:
    """Return the binding findings for one canary."""
    name = canary.claim_id
    if name not in registered:
        return [
            _err(
                name,
                f"Canary {name} names a claim that is not registered, so it guards nothing. "
                f"Remove it or register the claim. Then {_RECOVER}.",
            )
        ]
    resolved = resolve_guard(canary.guard)
    if resolved is None:
        return [_err(name, f"Canary {name} guard {canary.guard!r} does not resolve. {_RECOVER}.")]
    source, source_file = resolved
    errors: list[ValidationError] = []
    if binding_hash(source, name, canary.failing_test) != canary.binding_sha256:
        errors.append(
            _err(
                name,
                f"Canary {name} binding is stale: the guard source, the claim or the designated "
                f"test {canary.failing_test} changed since a human reviewed it, so the mutant "
                f"may no longer test what it was reviewed against. {_RECOVER}.",
            )
        )
    if not resolves_test_id(canary.failing_test):
        errors.append(
            _err(
                name,
                f"Canary {name} designated test {canary.failing_test} no longer resolves to a "
                f"test definition: deleting the test that kills the mutant is the silent "
                f"erasure this canary exists to refuse. Restore it or {_RECOVER}.",
            )
        )
    find = canary.mutation.find
    if find == canary.mutation.replace or source.count(find) != 1:
        errors.append(
            _err(
                name,
                f"Canary {name} mutation is not a single change inside the guard: its target "
                f"occurs {source.count(find)} time(s) in the guard and the edit "
                f"{'is' if find == canary.mutation.replace else 'is not'} a no-op. "
                f"{_RECOVER}.",
            )
        )
    elif source_file.read_text(encoding="utf-8").count(find) != 1:
        errors.append(
            _err(
                name,
                f"Canary {name} mutation target is not unique in {source_file.name}, so the "
                f"sweep could mutate a different line than the one reviewed. {_RECOVER}.",
            )
        )
    return errors


def check_canaries(project_root: Path, registered: set[str]) -> list[ValidationError]:
    """Return every binding finding, and every claim that has neither canary nor disclosure."""
    canaries = load_canaries(project_root)
    errors = [e for canary in canaries for e in _check_one(canary, registered)]
    covered = {c.claim_id for c in canaries}
    disclosed = set(load_registry(project_root, _GRANDFATHER_REGISTRY).get("claims", []))
    errors.extend(
        _err(
            claim,
            f"Claim {claim} has no guard mutation canary and is not on the shrink-only roster "
            f"{_GRANDFATHER_REGISTRY}. A control no reviewed mutant is bound to can be erased "
            f"without notice (GHI #1154). Bind a canary for it.",
        )
        for claim in sorted(registered - covered - disclosed)
    )
    errors.extend(
        _err(
            claim,
            f"The canary roster {_GRANDFATHER_REGISTRY} names {claim}, which "
            f"{'now has a canary' if claim in covered else 'is no longer registered'}. A stale "
            f"entry props up the shrink baseline. Remove it.",
        )
        for claim in sorted((disclosed & covered) | (disclosed - registered))
    )
    return errors


def _ledger_file(project_root: Path, ledger_path: Path | None) -> Path:
    return ledger_path if ledger_path is not None else project_root / _LEDGER


def review_witnesses(project_root: Path, ledger_path: Path | None = None) -> set[tuple[str, str]]:
    """Return every (claim id, binding) a ``guard_canary_reviewed`` event records.

    A missing ledger or an unparseable row contributes nothing: a review the ledger cannot
    show is not a review.
    """
    path = _ledger_file(project_root, ledger_path)
    if not path.is_file():
        return set()
    witnesses: set[tuple[str, str]] = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        with contextlib.suppress(ValueError):
            row = json.loads(line)
            if isinstance(row, dict) and row.get("event") == _REVIEW_EVENT:
                witnesses.add((str(row.get("id")), str(row.get("binding_sha256"))))
    return witnesses


def unreviewed(project_root: Path, ledger_path: Path | None = None) -> list[str]:
    """Return the claims whose canary has no recorded operator review at its current binding.

    The witness is a ``guard_canary_reviewed`` event, never the ``reviewed_by`` field: the
    field is writable by anyone, so it cannot tell an operator's review from an agent's
    (GHI #1161). A review of an earlier binding does not count, so a rebound canary must be
    reviewed again. Session orientation calls this function rather than re-deriving it.
    """
    witnesses = review_witnesses(project_root, ledger_path)
    return [
        c.claim_id
        for c in load_canaries(project_root)
        if (c.claim_id, c.binding_sha256) not in witnesses
    ]


def _stale(canary: Canary) -> bool:
    resolved = resolve_guard(canary.guard)
    if resolved is None:
        return True
    return binding_hash(resolved[0], canary.claim_id, canary.failing_test) != canary.binding_sha256


def record_review(
    project_root: Path,
    claim_ids: list[str],
    *,
    attestor: str,
    operator_text: str,
    ruling_source: str | None = None,
    ledger_path: Path | None = None,
) -> list[str]:
    """Record the operator's review of each named canary; return the claims recorded.

    Every input is checked before anything is written, so a refusal leaves the ledger and
    the registry untouched. Empty words, an empty attestor or an unknown claim is a usage
    error. A stale binding is a policy breach: the operator would be accepting a mutant
    against a guard that has changed since the canary was bound.
    """
    words, who = operator_text.strip(), attestor.strip()
    if not words or not who:
        raise gz_errors.ValidationError(
            "A review needs the operator's verbatim words and the attestor: a review that "
            "names neither cannot be told from one an agent wrote (GHI #1161)."
        )
    wanted = list(dict.fromkeys(claim_ids))
    by_id = {c.claim_id: c for c in load_canaries(project_root)}
    unknown = [claim for claim in wanted if claim not in by_id]
    if not wanted or unknown:
        raise gz_errors.ValidationError(
            f"No canary is bound to {', '.join(unknown) or 'any claim given'}. "
            f"Name claims from {_CANARY_REGISTRY}."
        )
    stale = [claim for claim in wanted if _stale(by_id[claim])]
    if stale:
        raise gz_errors.PolicyBreachError(
            f"Canary binding is stale for {', '.join(stale)}: the guard, claim or designated "
            f"test changed since the mutant was bound, so a review now would accept a mutant "
            f"nobody re-read. {_RECOVER}."
        )
    ledger = Ledger(_ledger_file(project_root, ledger_path))
    for claim in wanted:
        ledger.append(
            guard_canary_reviewed_event(
                claim_id=claim,
                binding_sha256=by_id[claim].binding_sha256,
                attestor=who,
                operator_text=operator_text,
                ruling_source=ruling_source,
            )
        )
    _project_reviewer(project_root, set(wanted), who)
    return wanted


def _project_reviewer(project_root: Path, claims: set[str], attestor: str) -> None:
    """Write ``reviewed_by`` as a readable projection of the recorded review."""
    path = registry_path(project_root, _CANARY_REGISTRY)
    payload = load_registry(project_root, _CANARY_REGISTRY)
    for record in payload.get("canaries", []):
        if isinstance(record, dict) and record.get("claim_id") in claims:
            record["reviewed_by"] = attestor
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _copy_tree(project_root: Path, destination: Path) -> None:
    """Copy what a test run needs into *destination*, leaving bytecode behind."""
    config_dir = registry_path(project_root, _CANARY_REGISTRY).parent
    for source in (*(project_root / name for name in _COPIED), config_dir):
        shutil.copytree(
            source,
            destination / source.relative_to(project_root),
            ignore=shutil.ignore_patterns("__pycache__"),
        )


def run_canaries(project_root: Path, claim_ids: set[str] | None = None) -> list[CanaryRun]:
    """Apply each canary's mutant to an isolated copy and report whether its test kills it.

    One copy serves every canary: the sweep restores the file it mutates after each mutant.
    """
    runs: list[CanaryRun] = []
    with tempfile.TemporaryDirectory() as tmp:
        copy_root = Path(tmp)
        _copy_tree(project_root, copy_root)
        for canary in load_canaries(project_root):
            if claim_ids is not None and canary.claim_id not in claim_ids:
                continue
            resolved = resolve_guard(canary.guard)
            if resolved is None:
                runs.append(CanaryRun(claim_id=canary.claim_id, outcome="invalid", reason="guard"))
                continue
            relative = resolved[1].resolve().relative_to(project_root.resolve())
            sweep = run_mutation_sweep(
                copy_root,
                copy_root / relative,
                [
                    Mutation(
                        find=canary.mutation.find,
                        replace=canary.mutation.replace,
                        label=canary.mutation.label,
                        expected_tests=[canary.failing_test],
                    )
                ],
                [sys.executable, "-c", _BOOTSTRAP, "-v", canary.failing_test],
            )
            witness = sweep.witnesses[0]
            runs.append(
                CanaryRun(claim_id=canary.claim_id, outcome=witness.outcome, reason=witness.reason)
            )
    return runs
