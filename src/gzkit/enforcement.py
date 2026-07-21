"""@enforces decorator, EnforcementClaimRecord, and import-time registry.

Provides the ``@enforces(claim, fixture, entrypoint)`` decorator (OBPI-0.0.74-15)
and the claim-type-agnostic registry the runner (OBPI-16) discovers.

Mirrors the ``@covers`` / ``@advances`` decoration-time fail-close precedent:
a malformed or unknown claim id raises ``ValueError`` at import — typos cannot
ship to runtime.

The ``entrypoint`` MUST be a direct, resolvable reference to a production
callable — never a ``functools.partial`` or ``lambda`` pre-binding a forcing
kwarg (§ Boundary Invariants #7; the runner in OBPI-16 invokes it).
"""

from __future__ import annotations

import re
import shutil
import types
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field

_EF = TypeVar("_EF")

# Claim id must be a lowercase slug: starts with a letter, contains only
# lowercase letters, digits, and hyphens.
_CLAIM_ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")

_ENFORCEMENT_REGISTRY: list[EnforcementClaimRecord] = []
_KNOWN_CLAIMS: frozenset[str] | None = None


class EnforcementClaimRecord(BaseModel):
    """A registered ``@enforces`` decoration linking a claim to its NC and entrypoint.

    Captured at decoration time. The runner (OBPI-16) discovers every record in
    ``_ENFORCEMENT_REGISTRY`` and invokes ``entrypoint(fixture())`` to verify the
    claim is genuinely enforced.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)

    claim_id: str = Field(..., description="Enforcement claim identifier slug")
    fixture: Callable[[], Any] = Field(
        ..., description="Violation-builder callable; runner calls fixture()"
    )
    entrypoint: Callable[..., Any] = Field(
        ..., description="Production callable; runner calls entrypoint(fixture())"
    )
    source_fn: str = Field(
        ..., description="Qualified name of the entrypoint for discovery/logging"
    )
    source_file: str | None = Field(None, description="Source file path of the entrypoint")
    source_line: int | None = Field(
        None, description="First source line of the entrypoint (1-indexed)"
    )
    expect: str | None = Field(
        None,
        description=(
            "Substring the caught finding MUST contain. When set, the runner requires "
            "the entrypoint to fail for THIS reason, not merely to fail (GHI #699)."
        ),
    )


def _qualified_fn_name(fn: object) -> str:
    """Return the fully qualified name of a callable."""
    module = getattr(fn, "__module__", None) or "<unknown>"
    qualname = getattr(fn, "__qualname__", None) or getattr(fn, "__name__", "<unknown>")
    return f"{module}.{qualname}"


def _load_known_claims() -> frozenset[str]:
    """Load and cache the set of known enforcement claim ids.

    Production source: ``_KNOWN_QC_CLAIM_IDS`` from the qc_binding negative-control
    module (every qc NC + ``qc-binding``). Tests inject via ``set_known_claims()``.
    Mirrors the lazy-load pattern of ``_load_known_reqs()`` in traceability and
    ``_load_known_task_reqs()`` in tasks. The lazy import tolerates the re-entrant
    case where ``_qc_negative_controls`` is mid-import and calling ``enforces`` in its
    own registration loop — ``_KNOWN_QC_CLAIM_IDS`` is defined before that loop runs.
    """
    global _KNOWN_CLAIMS
    if _KNOWN_CLAIMS is not None:
        return _KNOWN_CLAIMS

    from gzkit.governance.trust_audits._qc_negative_controls import (  # noqa: PLC0415
        _KNOWN_QC_CLAIM_IDS,
    )

    _KNOWN_CLAIMS = _KNOWN_QC_CLAIM_IDS
    return _KNOWN_CLAIMS


def set_known_claims(claims: frozenset[str]) -> None:
    """Inject known claim identifiers for testing."""
    global _KNOWN_CLAIMS
    _KNOWN_CLAIMS = claims


def enforces(
    claim: str,
    fixture: Callable[[], Any],
    entrypoint: Callable[..., Any],
    expect: str | None = None,
) -> Callable[[_EF], _EF]:
    """Declare that a production callable enforces an enforcement claim.

    Validates the claim identifier format and known-claims membership at
    decoration time, then registers an :class:`EnforcementClaimRecord` into
    the module-level registry. Returns the decorated callable unchanged —
    registration is metadata-only.

    Raises:
        ValueError: If ``claim`` has an invalid format or is not in the
            registered known-claims set.

    """
    if not _CLAIM_ID_RE.match(claim):
        msg = (
            f"Malformed enforcement claim id: {claim!r} — "
            f"must match {_CLAIM_ID_RE.pattern!r} (lowercase slug)"
        )
        raise ValueError(msg)

    known = _load_known_claims()
    if claim not in known:
        msg = f"Unknown enforcement claim id: {claim!r} — not in the registered known-claims set"
        raise ValueError(msg)

    source_file: str | None = None
    source_line: int | None = None
    code = getattr(entrypoint, "__code__", None)
    if isinstance(code, types.CodeType):
        source_file = code.co_filename
        source_line = code.co_firstlineno

    source_fn = _qualified_fn_name(entrypoint)

    def decorator(fn: _EF) -> _EF:
        record = EnforcementClaimRecord(
            claim_id=claim,
            fixture=fixture,
            entrypoint=entrypoint,
            source_fn=source_fn,
            source_file=source_file,
            source_line=source_line,
            expect=expect,
        )
        _ENFORCEMENT_REGISTRY.append(record)
        return fn

    return decorator


def registered_claims() -> list[str]:
    """Return the list of registered enforcement claim ids."""
    return [r.claim_id for r in _ENFORCEMENT_REGISTRY]


def get_enforcement_registry() -> list[EnforcementClaimRecord]:
    """Return a copy of the global enforcement registry."""
    return list(_ENFORCEMENT_REGISTRY)


def reset_enforcement_registry() -> None:
    """Clear the global enforcement registry and known-claims cache. For testing only.

    Resets ``_KNOWN_CLAIMS`` to None so the next ``_load_known_claims()`` reloads the
    production set — a test that injected ``set_known_claims`` does not leak into later
    tests, and ``_ensure_production_claims_registered`` can re-register cleanly.
    """
    global _KNOWN_CLAIMS
    _ENFORCEMENT_REGISTRY.clear()
    _KNOWN_CLAIMS = None


# ---------------------------------------------------------------------------
# Meta-validator runner (OBPI-0.0.74-16)
# ---------------------------------------------------------------------------


class ClaimRunResult(BaseModel):
    """Result of running a single enforcement claim's NC fixture + entrypoint."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    claim_id: str = Field(..., description="Enforcement claim identifier slug")
    outcome: Literal["PASS", "FACADE", "TEST_BUG"] = Field(
        ...,
        description="PASS = caught; FACADE = did not catch; TEST_BUG = exception",
    )
    message: str = Field(..., description="Human-readable outcome description with repro guidance")
    source_fn: str = Field(default="", description="Qualified name of the production entrypoint")


class RunnerResult(BaseModel):
    """Aggregate result from run_meta_validator()."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    verified_count: int = Field(
        ..., description="Number of claims that PASSED (entrypoint caught violation)"
    )
    facade_count: int = Field(
        ..., description="Number of FACADE outcomes (entrypoint did not catch)"
    )
    test_bug_count: int = Field(
        ..., description="Number of TEST_BUG outcomes (exception during run)"
    )
    claim_results: list[ClaimRunResult] = Field(
        ..., description="Per-claim results in discovery order"
    )


def _render_findings(result: Any) -> str:
    """Flatten an entrypoint result to searchable text for ``expect`` matching.

    Entrypoints return either a ``list[ValidationError]`` or an exit-style ``int``.
    Only the list form carries a reason, so an ``int``-returning entrypoint cannot
    satisfy an ``expect`` — which is deliberate: a bare exit code is exactly the
    signal that cannot distinguish catching the violation from crashing.
    """
    if isinstance(result, list):
        return " | ".join(
            f"{getattr(item, 'type', '')}:{getattr(item, 'message', item)}" for item in result
        )
    return ""


def _run_single_claim(record: EnforcementClaimRecord) -> ClaimRunResult:
    """Run one enforcement claim's NC: fixture() → path, entrypoint(path) → result.

    Uniform signal: ``bool(result)`` — truthy = entrypoint caught the violation (PASS);
    falsy = entrypoint did not catch (FACADE). Either side raising = TEST_BUG.
    Cleans up the fixture path with ``shutil.rmtree`` after the run.
    """
    fixture_path: Path | None = None
    try:
        fixture_result = record.fixture()
        if isinstance(fixture_result, Path):
            fixture_path = fixture_result
    except Exception as exc:
        return ClaimRunResult(
            claim_id=record.claim_id,
            outcome="TEST_BUG",
            source_fn=record.source_fn,
            message=(
                f"TEST_BUG: fixture() raised for claim {record.claim_id!r}: {exc!r}. "
                f"The fixture must build the violation without error. "
                f"Repro: call {record.source_fn!r}() directly and observe the exception."
            ),
        )

    try:
        ep_result = record.entrypoint(fixture_result)
        caught = bool(ep_result)
    except Exception as exc:
        return ClaimRunResult(
            claim_id=record.claim_id,
            outcome="TEST_BUG",
            source_fn=record.source_fn,
            message=(
                f"TEST_BUG: entrypoint() raised for claim {record.claim_id!r}: {exc!r}. "
                f"The entrypoint must run without exception on the fixture. "
                f"Repro: call {record.source_fn!r}(fixture()) directly and observe the exception."
            ),
        )
    finally:
        if fixture_path is not None:
            shutil.rmtree(fixture_path, ignore_errors=True)

    if caught and record.expect is not None:
        rendered = _render_findings(ep_result)
        if record.expect not in rendered:
            return ClaimRunResult(
                claim_id=record.claim_id,
                outcome="FACADE",
                source_fn=record.source_fn,
                message=(
                    f"FACADE: claim {record.claim_id!r} entrypoint failed, but NOT for the "
                    f"reason the claim names. Expected a finding containing "
                    f"{record.expect!r}; got: {rendered[:400]!r}. "
                    f"A control that accepts any failure cannot tell 'caught the violation' "
                    f"from 'bailed on configuration' or 'crashed' — the §5 clause (c) defect "
                    f"(GHI #699). Either the fixture stopped planting the violation, or the "
                    f"enforcement now fails earlier for an unrelated reason. "
                    f"Repro: call {record.source_fn!r}(fixture()) and read the finding."
                ),
            )

    if caught:
        return ClaimRunResult(
            claim_id=record.claim_id,
            outcome="PASS",
            source_fn=record.source_fn,
            message=f"PASS: claim {record.claim_id!r} entrypoint caught the violation.",
        )
    return ClaimRunResult(
        claim_id=record.claim_id,
        outcome="FACADE",
        source_fn=record.source_fn,
        message=(
            f"FACADE: claim {record.claim_id!r} entrypoint did NOT catch the violation "
            f"(returned falsy on a violation fixture). "
            f"The enforcement claim adopted by nothing — the check is theater. "
            f"Repro: call {record.source_fn!r}(fixture()) and observe that it returns falsy."
        ),
    )


def _emit_verified_receipts(results: list[ClaimRunResult], root: Path | None) -> None:
    """Emit one enforcement_claim_verified ledger receipt per PASS result.

    READ-ONLY on a clean run contract: only emits when ``root`` is provided
    and results contain PASS outcomes. No ledger mutation on failures or when
    ``root`` is None (test-isolation path).
    """
    if root is None:
        return
    passing = [r for r in results if r.outcome == "PASS"]
    if not passing:
        return

    from gzkit.ledger import Ledger, LedgerEvent  # noqa: PLC0415

    ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
    for r in passing:
        ledger.append(
            LedgerEvent(
                event="enforcement_claim_verified",
                id=r.claim_id,
                extra={
                    "claim_id": r.claim_id,
                    "outcome": r.outcome,
                    "source_fn": r.source_fn,
                },
            )
        )


def _ensure_production_claims_registered() -> None:
    """(Re)register the production enforcement claims, robust against registry resets.

    ``@enforces`` registers at import time, but ``reset_enforcement_registry()`` (a test
    helper) wipes the global registry permanently — re-importing a cached module does not
    re-run its module-level registration. So this calls the claim sources' idempotent
    re-registration entrypoint rather than relying on import side effects alone.

    This is the SINGLE production-discovery seam: every claim source that must be live in
    ``gz check``'s enforcement-floor audit (``run_enforcement_floor_audit`` ->
    ``run_meta_validator(root=None)``) is registered here. A source that authors an
    ``@enforces`` registration but is not reachable from this function is an ORPHAN — its
    claim is never discovered and its floor membership is a facade (the §5 failure class).

    Claim sources wired here:
      * ``qc_binding`` — every qc NC + ``qc-binding`` (OBPI-0.0.74-16).
      * ``mx.invariants`` — the bound ``gate5_invariants`` floor members ``gate5-ledger`` and
        ``gate5-attestation-absence`` (OBPI-0.0.74-17). ``secrets`` / ``operator-pii`` are the
        honest-negative named-not-enforced members and are deliberately NOT registered.
      * ``mx.proxy_reality`` — ``grader-gaming``, the floor member's live proxy-reality NC
        (OBPI-0.0.74-13).
      * ``handoff_resume_gate`` — ``handoff-resume-unauthorized-write`` and
        ``-bash``, one per clause of the § RESUME Operator Authorization Gate
        ("no file mutation / gz ceremony / migration"). Split deliberately: a gate
        hooking only Write|Edit leaves the bash claim undischargeable, so a
        partial mechanism fails ``gz check`` instead of shipping with a caveat
        (GHI #574).

    The gate5 + grader-gaming sources were authored Completed but left un-wired here (the
    docstring formerly named them "future work" that never landed); GHI tracks the
    OBPI-17/19 incomplete-implementation miss. Lazy imports avoid an import cycle with the
    ``mx`` package, which imports this module.
    """
    from gzkit.airlock.enter import _ensure_airlock_claims_registered  # noqa: PLC0415
    from gzkit.governance.trust_audits import qc_binding  # noqa: PLC0415
    from gzkit.handoff_resume_gate import _ensure_resume_gate_claims_registered  # noqa: PLC0415
    from gzkit.mx.invariants import _ensure_gate5_claims_registered  # noqa: PLC0415
    from gzkit.mx.proxy_reality import _ensure_grader_gaming_registered  # noqa: PLC0415

    qc_binding._ensure_qc_claims_registered()
    _ensure_gate5_claims_registered()
    _ensure_grader_gaming_registered()
    _ensure_airlock_claims_registered()
    _ensure_resume_gate_claims_registered()


def run_meta_validator(
    registry: list[EnforcementClaimRecord] | None = None,
    root: Path | None = None,
) -> RunnerResult:
    """Discover every @enforces claim, run entrypoint(fixture()), and report results.

    On a clean (all-PASS) run: READ-ONLY when ``root`` is None; emits one
    ``enforcement_claim_verified`` receipt per claim when ``root`` is provided.

    On failure: per-claim guardrail-feedback prose distinguishes FACADE (entrypoint
    did not catch the violation) from TEST_BUG (fixture or entrypoint raised), and
    names the single-NC repro command. Never a bare failing count.

    ``registry`` defaults to the full discovered ``get_enforcement_registry()`` when
    None — production claim sources are imported first so discovery is complete.
    """
    if registry is None:
        _ensure_production_claims_registered()
    records = registry if registry is not None else get_enforcement_registry()
    claim_results: list[ClaimRunResult] = [_run_single_claim(r) for r in records]

    verified = sum(1 for r in claim_results if r.outcome == "PASS")
    facades = sum(1 for r in claim_results if r.outcome == "FACADE")
    bugs = sum(1 for r in claim_results if r.outcome == "TEST_BUG")

    _emit_verified_receipts(claim_results, root)

    return RunnerResult(
        verified_count=verified,
        facade_count=facades,
        test_bug_count=bugs,
        claim_results=claim_results,
    )
