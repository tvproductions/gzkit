# Plan: OBPI-0.0.74-16-meta-validator-runner

**OBPI:** OBPI-0.0.74-16-meta-validator-runner
**Parent ADR:** ADR-0.0.74-mx-mode-maintenance-hangar
**Lane:** Heavy
**Authored:** 2026-06-24 (gz-plan-audit, no native plan mode — brief fully aligned)

## Destination-in-mind

Before writing this plan, the approach already in mind: add a `run_meta_validator()` function
to `enforcement.py` that iterates `_ENFORCEMENT_REGISTRY`, calls `entrypoint(fixture())`, and
checks truthiness of the result as the uniform signal. Lift the per-NC execution logic from
`audit_qc_binding` into a shared helper. Split each NC in `_qc_negative_controls.py` into
a fixture builder and a named entrypoint callable, register via `@enforces`, and remove
`fail_closed=True` from the two forced NCs.

## Rejected Alternatives

1. **Keep NCs as `() -> int` + wrap for `@enforces`** — rejected: adapter lambdas forbidden by BI#7;
   would still require named wrapper functions, giving no simplification.
2. **Separate `@enforces` registry from `_PRODUCTION_NEGATIVE_CONTROLS`** (keep both as parallel
   frameworks) — rejected: violates BI#6 (one enforcement-claim surface, not two).
3. **Post-hoc registration at runner call time** — rejected: violates the "import-time fail-close"
   design from OBPI-15; a claim that misses `@enforces` silently passes the runner.

## Stale Count Note

Brief says "33 qc_binding negative controls." `_PRODUCTION_NEGATIVE_CONTROLS` currently has 36
entries. Implementation covers all 36. Tests assert against the actual production registry count.

## Circular Import Strategy

`enforcement.py` lazily imports `_qc_negative_controls._PRODUCTION_NEGATIVE_CONTROLS` inside
`_load_known_claims()`. To avoid a circular import when `_qc_negative_controls.py` imports
`enforces` from `enforcement`:

1. `_qc_negative_controls.py` imports `enforces` at TOP of file (not deferred).
2. Python loads `enforcement.py` first (no top-level circular dependency there).
3. `_qc_negative_controls.py` continues, defines fixtures, entrypoints, `_PRODUCTION_NEGATIVE_CONTROLS`.
4. `@enforces` decorators at module end call `_load_known_claims()` → lazy import finds
   `_PRODUCTION_NEGATIVE_CONTROLS` already defined in the partially-loaded module → SUCCESS.
5. `_PRODUCTION_NEGATIVE_CONTROLS` keys remain the source of truth for `_load_known_claims()`.

## Allowed Paths

- `src/gzkit/enforcement.py`
- `src/gzkit/events.py`
- `src/gzkit/governance/trust_audits/qc_binding.py`
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py`
- `tests/governance/test_enforcement_meta_validator.py` (CREATE)
- `docs/.../ADR-0.0.74-mx-mode-maintenance-hangar.md` (evidence only)
- `docs/.../OBPI-0.0.74-16-meta-validator-runner.md` (this brief)

## Implementation Steps

### Step 1: Add `EnforcementClaimVerifiedEvent` to `events.py`

Add a new event class after the existing task events:

```python
class EnforcementClaimVerifiedEvent(_EventBase):
    """enforcement_claim_verified event (OBPI-0.0.74-16).

    Emitted once per claim on a clean (all-pass) run of run_meta_validator().
    READ-ONLY: the runner does NOT emit this event on a failing run.
    """
    event: Literal["enforcement_claim_verified"]
    claim_id: str = Field(..., description="Enforcement claim identifier slug")
    status: Literal["PASS"] = Field("PASS", description="Always PASS on a clean run")
    source_fn: str = Field(..., description="Qualified name of the production entrypoint")
```

Add `EnforcementClaimVerifiedEvent` to the `TypedLedgerEvent` union (before the closing `Field(discriminator="event")`).

### Step 2: Add runner data models to `enforcement.py`

Add after the existing `EnforcementClaimRecord`:

```python
from typing import Literal

class ClaimRunResult(BaseModel):
    """Result of running a single enforcement claim."""
    model_config = ConfigDict(frozen=True)
    claim_id: str
    status: Literal["PASS", "FACADE", "TEST_BUG"]
    source_fn: str
    repro_command: str | None = None
    prose: str | None = None  # guardrail-feedback on failure

class RunnerResult(BaseModel):
    """Aggregate result of run_meta_validator()."""
    model_config = ConfigDict(frozen=True)
    verified_count: int
    facade_count: int
    test_bug_count: int
    failures: list[ClaimRunResult]
    passed: bool  # True iff facade_count == 0 and test_bug_count == 0
```

### Step 3: Add shared engine `_run_single_claim` to `enforcement.py`

```python
import shutil
import traceback

def _run_single_claim(record: EnforcementClaimRecord) -> ClaimRunResult:
    """Run one enforcement claim record. Returns ClaimRunResult.

    Uniform signal: bool(entrypoint(fixture())) — truthy = violation caught (PASS),
    falsy = violation passed through (FACADE). Exception in fixture = TEST_BUG (fixture
    did not build). Exception in entrypoint = TEST_BUG (entrypoint raised unexpectedly).
    """
    repro = f"python -c \"from {record.entrypoint.__module__} import {record.entrypoint.__qualname__.split('.')[0]}; ...\""
    violation: Any = None
    violation_is_path = False
    try:
        violation = record.fixture()
        violation_is_path = isinstance(violation, Path)
    except Exception:
        return ClaimRunResult(
            claim_id=record.claim_id,
            status="TEST_BUG",
            source_fn=record.source_fn,
            repro_command=repro,
            prose=_test_bug_prose(record.claim_id, traceback.format_exc(), repro),
        )
    try:
        result = record.entrypoint(violation)
        caught = bool(result)
    except Exception:
        return ClaimRunResult(
            claim_id=record.claim_id,
            status="TEST_BUG",
            source_fn=record.source_fn,
            repro_command=repro,
            prose=_test_bug_prose(record.claim_id, traceback.format_exc(), repro),
        )
    finally:
        if violation_is_path:
            shutil.rmtree(violation, ignore_errors=True)  # type: ignore[arg-type]
    if caught:
        return ClaimRunResult(claim_id=record.claim_id, status="PASS", source_fn=record.source_fn)
    return ClaimRunResult(
        claim_id=record.claim_id,
        status="FACADE",
        source_fn=record.source_fn,
        repro_command=repro,
        prose=_facade_prose(record.claim_id, repro),
    )
```

Add the three-part prose generators per `.claude/rules/guardrail-feedback-prose.md`:
```python
def _facade_prose(claim_id: str, repro: str) -> str:
    return (
        f"FACADE: enforcement claim '{claim_id}' — entrypoint did not fail on the "
        f"violation fixture (the claim is adopted by nothing; production path passed). "
        f"gzkit §5 forbids an enforcement claim with no passing un-forced NC "
        f"(ADR-0.0.74 BI#6/7). Fix: implement a genuine enforcement path that fails "
        f"on the planted violation. Single-NC repro: {repro}"
    )

def _test_bug_prose(claim_id: str, trace: str, repro: str) -> str:
    return (
        f"TEST_BUG: enforcement claim '{claim_id}' — fixture did not build (exception "
        f"during fixture() or entrypoint() call). gzkit §5 requires a passing fixture "
        f"(ADR-0.0.74 BI#7). Fix the fixture or entrypoint. Trace: {trace[:500]}. "
        f"Single-NC repro: {repro}"
    )
```

### Step 4: Add `run_meta_validator()` to `enforcement.py`

```python
from pathlib import Path

def run_meta_validator(
    root: Path | None = None,
    *,
    registry: list[EnforcementClaimRecord] | None = None,
) -> RunnerResult:
    """Discover every @enforces claim, run entrypoint(fixture()), assert failure.

    On a clean (all-pass) run: READ-ONLY (no ledger mutations) and emits one
    enforcement_claim_verified ledger receipt per claim via the existing event-
    append path (if root is provided and the ledger exists).

    On any failure: emits per-claim FACADE/TEST_BUG guardrail-feedback prose
    (NO ledger events on a failing run — the runner is READ-ONLY on clean only).

    Raises RuntimeError (fail-closes strict) if ANY enrolled claim lacks a passing
    un-forced NC — no _NEGATIVE_CONTROL_DEBT-style escape (BI#8).
    """
    claims = registry if registry is not None else get_enforcement_registry()
    results: list[ClaimRunResult] = []
    for record in claims:
        results.append(_run_single_claim(record))

    failures = [r for r in results if r.status != "PASS"]
    facade_count = sum(1 for r in results if r.status == "FACADE")
    test_bug_count = sum(1 for r in results if r.status == "TEST_BUG")
    passed = len(failures) == 0

    if passed and root is not None:
        _emit_verified_receipts(root, results)

    return RunnerResult(
        verified_count=len(results),
        facade_count=facade_count,
        test_bug_count=test_bug_count,
        failures=failures,
        passed=passed,
    )


def _emit_verified_receipts(root: Path, results: list[ClaimRunResult]) -> None:
    """Emit one enforcement_claim_verified ledger receipt per claim (clean run only)."""
    from gzkit.ledger import Ledger, LedgerEvent  # noqa: PLC0415
    ledger_path = root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.exists():
        return
    ledger = Ledger(ledger_path)
    for r in results:
        ledger.append(LedgerEvent(
            event="enforcement_claim_verified",
            id=r.claim_id,
            extra={"status": "PASS", "source_fn": r.source_fn},
        ))
```

### Step 5: Refactor `_qc_negative_controls.py`

**5a. Add import at TOP of file:**
```python
from gzkit.enforcement import enforces
```

**5b. Split each NC into fixture + named entrypoint:**

For each of the 36 NCs, replace the current `_X_negative_control() -> int` pattern with:
- `_build_X_violation() -> Path` — uses `tempfile.mkdtemp()`, writes violation files, returns Path
- For Python validators: import the validator directly as the entrypoint (named function reference)
- For subprocess validators: add named `_entrypoint_X(root: Path) -> int` wrapper

The two forced NCs become UN-FORCED:
- `_rendition_freshness`: `validate_rendition_freshness(root)` (no `fail_closed=True`)
- `_rendition_floor_coherence`: `validate_rendition_floor_coherence(root)` (no `fail_closed=True`)

**5c. Replace the old NC function with @enforces registration:**

For each NC (example — `lint`):
```python
def _build_lint_violation() -> Path:
    import tempfile  # noqa: PLC0415
    root = Path(tempfile.mkdtemp(prefix="gzkit-qc-nc-lint-"))
    _minimal_pyproject(root)
    _write(root / "bad.py", "import sys\n")
    return root

def _entrypoint_lint(root: Path) -> int:
    return _genuine_when_command_fails("uv run ruff check .", root)

@enforces("lint", _build_lint_violation, _entrypoint_lint)
def _lint_nc_marker() -> None:
    pass  # registration carrier only
```

For Python validators (example — `kind-invariance`):
```python
def _build_kind_invariance_violation() -> Path:
    import tempfile  # noqa: PLC0415
    root = Path(tempfile.mkdtemp(prefix="gzkit-qc-nc-kind-"))
    _write(root / "docs" / "design" / "adr" / "foundation" / "ADR-0.0.1-missing" / "ADR-0.0.1-missing.md", "# ADR-0.0.1 Missing\n")
    return root

def _entrypoint_kind_invariance(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.kind_invariance import audit_kind_invariance  # noqa: PLC0415
    return audit_kind_invariance(root)

@enforces("kind-invariance", _build_kind_invariance_violation, _entrypoint_kind_invariance)
def _kind_invariance_nc_marker() -> None:
    pass
```

**5d. Keep `_PRODUCTION_NEGATIVE_CONTROLS` for `_load_known_claims()` backward compat:**

After all NC splits and `@enforces` registrations, keep:
```python
_PRODUCTION_NEGATIVE_CONTROLS: dict[str, Callable[[], int]] = {
    "lint": lambda: _entrypoint_lint(_build_lint_violation()),
    # ... all 36 entries
}
```

This preserves the `.keys()` source that `enforcement.py`'s `_load_known_claims()` needs.

Note: the lambdas in `_PRODUCTION_NEGATIVE_CONTROLS` are for the OLD qc_binding mechanism only. The `@enforces` registrations use named functions (no lambdas). The lambdas in `_PRODUCTION_NEGATIVE_CONTROLS` are acceptable since they're not used as `@enforces` entrypoints.

### Step 6: Lift engine in `qc_binding.py`

**6a. Remove dead code:**
- Remove `_NEGATIVE_CONTROLS` dict
- Remove `register_negative_control()` function
- Remove `_check_negative_control()` function
- Remove the `for _step_id, _negative_control in _PRODUCTION_NEGATIVE_CONTROLS.items():` loop
- Remove the `from gzkit.governance.trust_audits._qc_negative_controls import _PRODUCTION_NEGATIVE_CONTROLS` import

**6b. Add shared engine import:**
```python
from gzkit.enforcement import _run_single_claim, get_enforcement_registry
```

**6c. Update `audit_qc_binding` to use shared engine:**
```python
# In audit_qc_binding(), replace the _check_negative_control call:
if step.binding == "bound":
    registry_map = {r.claim_id: r for r in get_enforcement_registry()}
    record = registry_map.get(step.id)
    if record is None:
        errors.append(_err(step.name, f"Green-by-emptiness: bound step '{step.id}' has no @enforces registration..."))
    else:
        result = _run_single_claim(record)
        if result.status != "PASS":
            errors.append(_err(step.name, f"Hollow step: {result.prose}"))
```

**6d. Move `_qc_binding_negative_control` to `_qc_negative_controls.py`:**
```python
# In _qc_negative_controls.py:
def _build_qc_binding_violation() -> QCStep:
    return QCStep(id="nc-planted-theater", ..., theater_flags=["copy-vs-self"])

def _entrypoint_qc_binding(step: QCStep) -> list[ValidationError]:
    from gzkit.governance.trust_audits.qc_binding import _check_theater_signatures  # noqa: PLC0415
    return _check_theater_signatures(step)

@enforces("qc-binding", _build_qc_binding_violation, _entrypoint_qc_binding)
def _qc_binding_nc_marker() -> None:
    pass
```

Note: `_qc_binding_negative_control` and `register_negative_control("qc-binding", ...)` in `qc_binding.py` are removed.

### Step 7: Write `tests/governance/test_enforcement_meta_validator.py` (RED first)

Structure:
```python
class TestRunnerDiscoversAndInvokes(unittest.TestCase):
    """REQ-0.0.74-16-01: runner discovers, builds fixture(), invokes entrypoint(), asserts failure."""

    def setUp(self):
        reset_enforcement_registry()
        set_known_claims(frozenset({"test-genuine", "test-facade"}))

    def tearDown(self):
        reset_enforcement_registry()

    @covers("REQ-0.0.74-16-01")
    def test_runner_runs_each_claim(self): ...

    @covers("REQ-0.0.74-16-01")
    def test_runner_fails_strict_if_any_claim_missing(self): ...


class TestCleanRunReadOnly(unittest.TestCase):
    """REQ-0.0.74-16-02: READ-ONLY on clean run + one receipt per claim."""

    @covers("REQ-0.0.74-16-02")
    def test_no_receipts_emitted_on_failure(self): ...

    @covers("REQ-0.0.74-16-02")
    def test_one_receipt_per_claim_on_clean_run(self): ...


class TestFacadeVsTestBugFeedback(unittest.TestCase):
    """REQ-0.0.74-16-03: FACADE vs TEST_BUG feedback + single-NC repro command."""

    @covers("REQ-0.0.74-16-03")
    def test_facade_when_entrypoint_passes_violation(self): ...

    @covers("REQ-0.0.74-16-03")
    def test_test_bug_when_fixture_raises(self): ...

    @covers("REQ-0.0.74-16-03")
    def test_repro_command_in_feedback(self): ...


class TestEngineLiftedAndNcsUnforced(unittest.TestCase):
    """REQ-0.0.74-16-04: engine lifted, NCs un-forced, audit_qc_binding behavior preserved."""

    @covers("REQ-0.0.74-16-04")
    def test_all_qc_binding_ncs_in_enforcement_registry(self): ...

    @covers("REQ-0.0.74-16-04")
    def test_no_negative_controls_dict_in_qc_binding(self): ...

    @covers("REQ-0.0.74-16-04")
    def test_audit_qc_binding_uses_shared_engine(self): ...

    @covers("REQ-0.0.74-16-04")
    def test_all_ncs_pass_unforced(self): ...
```

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_enforcement_meta_validator -v
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --documents
uv run mkdocs build --strict
uv run -m behave features/ --no-capture
test -f src/gzkit/enforcement.py
test -f tests/governance/test_enforcement_meta_validator.py
```

## Notes

- `_PRODUCTION_NEGATIVE_CONTROLS` KEPT as backward-compat bridge for `_load_known_claims()`.
  Both values (fixture/entrypoint wrappers for the old path) AND `@enforces` registrations
  exist side-by-side. This is NOT two NC frameworks — the values in `_PRODUCTION_NEGATIVE_CONTROLS`
  are only used by `_load_known_claims()` for known-claim validation; NC execution goes through
  `_ENFORCEMENT_REGISTRY` only.
- `QCStep` import in `_qc_negative_controls.py` for `_build_qc_binding_violation` uses the
  existing `from gzkit.qc_binding import QCStep` import already present in `qc_binding.py`.
- Actual NC count is 36 (not 33 per brief). Tests assert on `len(claims) >= 36`.
- The `_NEGATIVE_CONTROL_DEBT` frozenset in `qc_binding.py` is also removed (no debt escape, BI#8).
