# OBPI-0.0.36-02-runtime-gate-collapse Implementation Plan

## Context

- **OBPI:** OBPI-0.0.36-02-runtime-gate-collapse
- **Parent ADR:** ADR-0.0.36-universal-obpi-attestation
- **Lane:** Heavy
- **Objective:** Collapse `_requires_human_obpi_attestation` in `src/gzkit/commands/adr_audit.py` to `return True`; audit `_is_foundation_adr` for remaining call-sites; flip lane-conditional assertions in existing predicate tests; create universality test module.

## ADR Decision Item #2 (verbatim)

> `src/gzkit/commands/adr_audit.py::_requires_human_obpi_attestation` collapses to `return True`. Signature is preserved (callers do not change). The `_is_foundation_adr` helper becomes orphaned by this collapse and is grepped + removed (or retained with a deprecation marker if other call-sites exist) under OBPI-0.0.36-02.

## Files

### Modified
- `src/gzkit/commands/adr_audit.py` — gate collapse; `_is_foundation_adr` docstring
- `tests/test_adr_audit_predicates.py` — flip two lane-conditional `assertFalse` → `assertTrue`
- `docs/design/adr/foundation/ADR-0.0.36-universal-obpi-attestation/obpis/OBPI-0.0.36-02-runtime-gate-collapse.md` — correct Allowed Paths (replace non-existent `tests/commands/test_adr_audit.py` with `tests/test_adr_audit_predicates.py`)

### Created
- `tests/governance/test_attestation_universality.py` — new universality test module

## Steps

### Task 1: Fix brief Allowed Paths path drift

Update the brief's Allowed Paths section: replace `tests/commands/test_adr_audit.py` (non-existent) with `tests/test_adr_audit_predicates.py` (the actual existing predicate test file).

Rationale: the plan-audit CLI flagged this path as non-existent. The real existing test file for `_requires_human_obpi_attestation` is `tests/test_adr_audit_predicates.py`. Two tests there contain lane-conditional `assertFalse` calls that must be flipped.

### Task 2: RED — Write failing universality tests

Create `tests/governance/test_attestation_universality.py` with a `@covers("OBPI-0.0.36-02")` test class asserting `_requires_human_obpi_attestation` returns `True` for all combinations:
- `foundation × lite` (ADR-0.0.99-foundation, lite)
- `foundation × heavy` (ADR-0.0.99-foundation, heavy)
- `feature × lite` (ADR-0.1.0-feature, lite) — **this is the collapse target; currently returns False**
- `feature × heavy` (ADR-0.1.0-feature, heavy)
- `parent_adr=None` edge case — **currently returns False**

Run `uv run -m unittest tests.governance.test_attestation_universality -v` and confirm `feature × lite` and `parent_adr=None` tests FAIL (RED).

### Task 3: GREEN — Collapse the gate

Edit `src/gzkit/commands/adr_audit.py`:
1. Replace `_requires_human_obpi_attestation` body with `return True`
2. Update the docstring to reflect universal attestation, citing ADR-0.0.36 and OBPI-0.0.36-02
3. Add docstring to `_is_foundation_adr` noting it is no longer load-bearing for attestation routing — taxonomy classification at line 264 (`adr_kind = "foundation" if _is_foundation_adr(adr_id) else "feature"`) and `test_closeout_ceremony_cmd.py` are non-attestation callers — citing OBPI-0.0.36-02 and ADR-0.0.36

Preserve the full function signature: `(parent_adr: str | None, parent_lane: str, brief_frontmatter: Mapping[str, Any] | None = None) -> bool`

Do NOT touch `_enforce_human_attestation_authenticity` (already dead code per lines 410-422 comment; OBPI scope boundary).

### Task 4: Flip lane-conditional assertions in existing tests

In `tests/test_adr_audit_predicates.py`:
1. `test_lite_feature_no_sensitivity_remains_self_closeable` (line 80) — flip `assertFalse` → `assertTrue`. Update test name and docstring to reflect new universality semantics (feature × lite now requires attestation per ADR-0.0.36).
2. `test_frontmatter_argument_is_optional_for_call_site_compat` (line 117) — flip `assertFalse(_requires_human_obpi_attestation("ADR-0.1.0-some-feature", "lite"))` → `assertTrue(...)`. The test name stays relevant but the assertion-level comment must be updated: the two-argument call shape still works, but now returns True for feature×lite.
3. Add `@covers("REQ-0.0.36-02-04")` to both updated test methods (these tests assert the REQ-04 requirement: existing lane-conditional tests updated to assert universal behavior).

Run `uv run -m unittest tests.test_adr_audit_predicates -v` and confirm all pass (GREEN).

### Task 5: Verify universality tests pass (GREEN for REQ-05)

Run `uv run -m unittest tests.governance.test_attestation_universality -v` and confirm all 5 tests pass.

### Task 6: Run quality gates and generate ARB receipts

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --documents
uv run gz covers OBPI-0.0.36-02-runtime-gate-collapse --json
```

Confirm all pass and receipt IDs are recorded for Stage 4 evidence.

### Task 7: BDD scenario

Check `features/universal_obpi_attestation.feature` (exists from OBPI-0.0.36-01). Add new scenarios tagged `@REQ-0.0.36-02-01` asserting `_requires_human_obpi_attestation` returns True for `feature × lite` input (the previously-self-closeable case). Run `uv run gz arb step --name behave -- uv run -m behave --tags=@REQ-0.0.36-02-01 features/`.

### Task 8: Present OBPI Acceptance Ceremony

## Verification

```bash
uv run -m unittest tests.governance.test_attestation_universality -v
uv run -m unittest tests.test_adr_audit_predicates -v
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
```

## Notes

- **`_is_foundation_adr` retained with docstring** — has call-sites in `adr_audit.py` line 264 (taxonomy: `adr_kind = "foundation" if ... else "feature"`) and `tests/test_closeout_ceremony_cmd.py` lines 142-148. These are classification purposes unrelated to attestation routing. Per REQ-03: retain and add docstring.
- **`parent_adr=None` edge case** — ADR Decision item #2 says "collapses to `return True`". REQ-01 requires True for all inputs including None. The collapsed body is simply `return True`; the None-guard is removed.
- **Scope collision (advisory)** — 30 sibling ADRs listed as historically touching `adr_audit.py`. All are completed ADRs. No active lock conflicts.
