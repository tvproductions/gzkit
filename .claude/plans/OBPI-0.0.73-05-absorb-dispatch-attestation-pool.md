# Plan: OBPI-0.0.73-05 — Absorb Dispatch Attestation Pool

**OBPI:** OBPI-0.0.73-05-absorb-dispatch-attestation-pool
**ADR Decision item #5 (verbatim):** "Absorb ADR-pool.obpi-pipeline-dispatch-attestation — fold the dispatch-attestation concern into this ADR's bound-checker mechanism; retire/annotate the pool ADR; ledger event; unit tests"

## Context

ADR-0.0.73 is building the verification layer binding audit. The pool ADR `ADR-pool.obpi-pipeline-dispatch-attestation` scopes the dispatch-attestation concern (pipeline subagent dispatch producing ledger events, mechanical gates against bail-to-inline). This concern is the same "checker not bound" class that ADR-0.0.73 addresses. OBPI-05 folds it into the QC registry as a bound step and retires the pool ADR.

`build_qc_registry()` derives its registry from `_build_check_steps()` in `quality.py`. Every new step must be (a) added to `_build_check_steps()` and (b) classified in `_STEP_CLASSIFICATION` in `qc_binding.py`. The "bound" classification means the step fails non-zero on violation; the negative-control fixture was established by OBPI-02 and does not need to be added here.

## Files

**Modified:**
- `docs/design/adr/pool/ADR-pool.obpi-pipeline-dispatch-attestation.md` — annotate as absorbed (status: Superseded, absorbed_into: ADR-0.0.73 frontmatter field, absorption note section)
- `src/gzkit/quality.py` — add `run_dispatch_attestation_audit` function; wire into `_build_check_steps()`
- `src/gzkit/qc_binding.py` — add "Dispatch attestation" to `_STEP_CLASSIFICATION`

**Created:**
- `tests/governance/test_dispatch_attestation_absorption.py` — unit tests covering REQ-0.0.73-05-01, REQ-0.0.73-05-02, REQ-0.0.73-05-03

## Steps

### Step 1: Annotate pool ADR as absorbed

Edit `docs/design/adr/pool/ADR-pool.obpi-pipeline-dispatch-attestation.md`:
- Change `status: Pool` → `status: Superseded` in frontmatter
- Add `absorbed_into: ADR-0.0.73` field in frontmatter
- Add `## Absorption Note` section at the end of the body explaining it was absorbed into ADR-0.0.73 OBPI-05

### Step 2: Add `run_dispatch_attestation_audit` to `quality.py`

Implement a Python function (not a shell command delegation) that:
- Reads `docs/design/adr/pool/ADR-pool.obpi-pipeline-dispatch-attestation.md`
- Checks that the file contains `absorbed_into: ADR-0.0.73` (the annotation marker)
- Returns `QualityResult(success=True)` if found
- Returns `QualityResult(success=False, returncode=3)` with a recovery message if not found

This is the bound enforcement step — if someone removes the annotation, this step fails.

### Step 3: Wire into `_build_check_steps()` in `quality.py`

- Import `run_dispatch_attestation_audit` in `_build_check_steps()`
- Add `("Dispatch attestation", run_dispatch_attestation_audit)` to the list (append after "Line endings")

### Step 4: Add classification in `qc_binding.py`

Add to `_STEP_CLASSIFICATION`:
```python
"Dispatch attestation": ("audit", "docs/", "bound", "python_function"),
```

### Step 5: Write unit tests

Create `tests/governance/test_dispatch_attestation_absorption.py`:

**REQ-0.0.73-05-01** (BEHAVIOR): Test that `build_qc_registry()` includes a step with `dispatch` in its id and `binding == "bound"`.

**REQ-0.0.73-05-02 + REQ-0.0.73-05-03** (SUPPORT): Test that `run_dispatch_attestation_audit` returns `success=True` over the project root (i.e., the annotated pool ADR is present). Also test that the pool ADR file contains `absorbed_into: ADR-0.0.73`.

**Negative control** (BEHAVIOR): Create a temp directory with a pool ADR copy that lacks the annotation; verify `run_dispatch_attestation_audit` returns `success=False` with exit code 3.

### Step 6: Run ADR status refresh

`uv run gz register-adrs` — regenerates the ADR status index to reflect the pool ADR's new Superseded status.

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_dispatch_attestation_absorption -v
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --documents
uv run gz validate --adr-status-fresh
```

Demo:
```python
from gzkit.qc_binding import build_qc_registry
print([s.id for s in build_qc_registry() if 'dispatch' in s.id])
# Expected: ['dispatch-attestation']
```

## Notes

- Pool ADR scope-collision with OBPI-0.0.37-10 and OBPI-0.0.42-04 is advisory only — those OBPIs touched the same pool ADR file but for different concerns
- `artifact_edited` ledger events for the pool ADR file are emitted naturally by git-sync when the file is committed (satisfies REQ-0.0.73-05-02 and REQ-0.0.73-05-03 ledger evidence requirement)
- "Dispatch attestation" step binding is `bound` per the ADR-0.0.73 classification contract; the negative-control fixture for `gz validate --qc-binding` is provided by the unit test negative control
