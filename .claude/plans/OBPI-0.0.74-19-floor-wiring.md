# Plan: OBPI-0.0.74-19 — Floor Wiring

## Context

OBPI: OBPI-0.0.74-19-floor-wiring
ADR: ADR-0.0.74-mx-mode-maintenance-hangar
Lane: Heavy | Sensitivity: security
Prerequisites confirmed: OBPI-17 (lock released 2026-06-25T01:23) and OBPI-18 (lock released 2026-06-25T08:39) are complete.

## Destination-in-mind Disclosure (§ Step 6a)

Before planning I had already formed the approach: wire `run_meta_validator()` as a `run_enforcement_floor_audit(project_root)` wrapper in `quality.py` (READ-ONLY via `root=None`), register it in `commands/quality.py` exactly as `("Enforcement floor", run_enforcement_floor_audit)` mirrors `("QC binding", run_qc_binding_audit)`, add a `_run_enforcement_floor()` function in `guards.py` and call it from `main()`, and add the "enforcement-floor" entry to `_QC_NEGATIVE_CONTROL_TABLE` with a synthetic-registry fixture in `_qc_nc_entrypoints.py`.

**Rejected alternatives:**
1. Wire via subprocess (`uv run gz validate --enforcement-floor`) instead of direct-import — rejected because it would require a new CLI scope not in the brief's allowed paths and would add process overhead; the `qc_binding.py` direct-import model is the right precedent.
2. Emit ledger receipts in the gz check step (pass `root=project_root` to `run_meta_validator`) — rejected because the brief explicitly says "READ-ONLY on a clean run," and the ADR item says no ledger mutation when green.
3. Add the "enforcement-floor" NC as a self-registration in a new file (like `qc_binding.py`) — rejected because the existing `_QC_NEGATIVE_CONTROL_TABLE` in `_qc_negative_controls.py` is the right home; a new file would require a new import chain and approach the `qc_binding.py` complexity without justification.

## Files

### Modified
- `src/gzkit/quality.py` — add `run_enforcement_floor_audit(project_root: Path) -> QualityResult`
- `src/gzkit/commands/quality.py` — register `("Enforcement floor", run_enforcement_floor_audit)` in check assembly
- `src/gzkit/hooks/guards.py` — add `_run_enforcement_floor(root)` helper + call in `main()`
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py` — add `_build_enforcement_floor()` fixture + "enforcement-floor" to `_QC_NEGATIVE_CONTROL_TABLE`
- `src/gzkit/governance/trust_audits/_qc_nc_entrypoints.py` — add `_ep_enforcement_floor()` entrypoint

### Created
- `tests/governance/test_enforcement_floor_wiring.py` — unit tests covering REQ-19-01, REQ-19-02, REQ-19-03

## Steps

### Step 1: RED tests (TDD)

Write `tests/governance/test_enforcement_floor_wiring.py` with failing tests:

**TestGzCheckStepWiring** (REQ-0.0.74-19-01):
- `test_enforcement_floor_step_in_check_steps`: assert "Enforcement floor" in `_build_check_steps()` step names
- `test_enforcement_floor_step_read_only_on_clean`: call `run_enforcement_floor_audit(Path.cwd())` with all-PASS registry (via `run_meta_validator(root=None)` semantics), assert `result.success == True` and no ledger event is emitted
- Both fail RED because `run_enforcement_floor_audit` doesn't exist yet

**TestPrePushGuardWiring** (REQ-0.0.74-19-02):
- `test_main_calls_enforcement_floor`: mock `run_enforcement_floor_audit` returning failure, call `main()`, assert non-zero return; mock returning success, assert zero (chained with other guards)
- Fails RED because `_run_enforcement_floor` doesn't exist in guards.py

**TestEnforcementFloorOwnQcNc** (REQ-0.0.74-19-03):
- `test_enforcement_floor_in_known_claims`: assert "enforcement-floor" in `_KNOWN_QC_CLAIM_IDS`
- `test_enforcement_floor_nc_in_table`: assert "enforcement-floor" in `{claim_id for claim_id, _, _ in _QC_NEGATIVE_CONTROL_TABLE}`
- Fails RED because "enforcement-floor" is not in the table yet

### Step 2: GREEN — add run_enforcement_floor_audit to quality.py

After the `run_qc_binding_audit` function (line ~790), add:

```python
def run_enforcement_floor_audit(project_root: Path) -> QualityResult:
    """Run the enforcement-claim meta-validator as a gz check step (ADR-0.0.74/OBPI-19).

    READ-ONLY on a clean run — no ledger mutation when all claims PASS (root=None).
    Fails closed when any enrolled claim lacks a passing un-forced NC.
    Recovery: run uv run -m gzkit.enforcement directly to see per-claim details.
    """
    from gzkit.enforcement import run_meta_validator  # noqa: PLC0415

    result = run_meta_validator(root=None)
    failures = [r for r in result.claim_results if r.outcome != "PASS"]
    if failures:
        output = "\n".join(r.message for r in failures)
        return QualityResult(
            success=False,
            command="enforcement-floor-audit",
            stdout=output,
            stderr="",
            returncode=3,
        )
    return QualityResult(
        success=True,
        command="enforcement-floor-audit",
        stdout=f"Enforcement floor: {result.verified_count} claims verified.",
        stderr="",
        returncode=0,
    )
```

Note: `project_root` accepted for interface consistency (all gz check steps take `project_root`) but not passed to `run_meta_validator` (READ-ONLY contract). ARG unused-argument rule not in ruff select — no lint issue.

### Step 3: GREEN — register in commands/quality.py

Add to the import block:
```python
run_enforcement_floor_audit,
```

Add to the `_build_check_steps()` return list (after `("Dispatch attestation", run_dispatch_attestation_audit)` or near the end):
```python
("Enforcement floor", run_enforcement_floor_audit),
```

### Step 4: GREEN — wire into guards.py

Add to `guards.py` (before `main()`):
```python
def _run_enforcement_floor(root: Path) -> int:
    """Run the enforcement-floor audit as a pre-push guard. READ-ONLY on clean."""
    from gzkit.quality import run_enforcement_floor_audit  # noqa: PLC0415

    result = run_enforcement_floor_audit(root)
    if not result.success:
        _safe_print(f"[pre-push] Enforcement floor failed:\n{result.stdout}")
        return 1
    return 0
```

Add to `main()`:
```python
rc = _run_enforcement_floor(root)
if rc:
    return rc
```

### Step 5: GREEN — add enforcement-floor NC to _qc_negative_controls.py

Add two module-level helpers before `_QC_NEGATIVE_CONTROL_TABLE`:
```python
def _nc_facade_ep(_v: object) -> int:
    """FACADE entrypoint for enforcement-floor NC probe — always returns 0 (does not catch)."""
    return 0


def _nc_probe_fixture() -> None:
    """Inert fixture for the enforcement-floor NC probe."""
    return None


def _build_enforcement_floor() -> list:
    """Build a synthetic registry with one FACADE claim for the enforcement-floor NC.

    The meta-validator must detect the FACADE (facade_count > 0 = PASS for this NC).
    If run_meta_validator is gutted to not detect FACADEs, this surfaces as FACADE.
    """
    from gzkit.enforcement import EnforcementClaimRecord  # noqa: PLC0415

    return [
        EnforcementClaimRecord(
            claim_id="nc-probe",
            fixture=_nc_probe_fixture,
            entrypoint=_nc_facade_ep,
            source_fn="_qc_negative_controls._nc_facade_ep",
            source_file=None,
            source_line=None,
        )
    ]
```

Add to `_QC_NEGATIVE_CONTROL_TABLE`:
```python
("enforcement-floor", _build_enforcement_floor, _ep._ep_enforcement_floor),
```

### Step 6: GREEN — add _ep_enforcement_floor to _qc_nc_entrypoints.py

```python
def _ep_enforcement_floor(records: list) -> int:
    """NC entrypoint for enforcement-floor: meta-validator must detect FACADE claims.

    Returns facade_count (non-zero = caught the FACADE = PASS for this NC).
    If run_meta_validator is gutted to skip FACADE detection, this returns 0 = FACADE.
    """
    from gzkit.enforcement import run_meta_validator  # noqa: PLC0415

    result = run_meta_validator(registry=records, root=None)
    return result.facade_count + result.test_bug_count
```

### Step 7: Run lint and type-check, fix any issues

```bash
uv run ruff check . --fix && uv run ruff format .
uv run ty check .
```

### Step 8: Verify all tests pass

```bash
uv run -m unittest tests.governance.test_enforcement_floor_wiring -v
uv run -m unittest -q
```

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
```

REQ coverage:
- REQ-0.0.74-19-01 [behavior]: `TestGzCheckStepWiring` in test_enforcement_floor_wiring.py
- REQ-0.0.74-19-02 [behavior]: `TestPrePushGuardWiring` in test_enforcement_floor_wiring.py
- REQ-0.0.74-19-03 [behavior]: `TestEnforcementFloorOwnQcNc` in test_enforcement_floor_wiring.py
- REQ-0.0.74-19-04 [structural-fence]: parent ADR § Boundary Invariants #8 (no impl artifact needed)

## Notes

- The `nc-probe` claim_id in `_build_enforcement_floor` is NOT registered via `@enforces()` (no `_KNOWN_CLAIMS` validation), so it can use any valid slug. It exists only as a synthetic violation fixture for the NC.
- `_ep_enforcement_floor` takes a `list` (the raw list returned by `_build_enforcement_floor`), not a Path — same pattern as `qc_binding`'s `_build_qc_binding_violation()` returning a `QCStep`.
- `run_enforcement_floor_audit` always passes `root=None` to enforce READ-ONLY behavior; the `project_root` parameter is accepted for API consistency only.
