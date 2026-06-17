# Plan: OBPI-0.0.73-01-qc-step-registry-and-classifier

**OBPI:** OBPI-0.0.73-01-qc-step-registry-and-classifier
**ADR:** ADR-0.0.73-verification-layer-binding-audit
**Checklist item:** #1 — Registry + classifier model — `QCStep` Pydantic frozen model
`{id, name, kind, subject, binding, wired_into[], theater_flags[], enforcement_locus}`;
registry DERIVED from what `gz check` actually runs (never hand-maintained); unit tests.

## Context

`gz check` runs 32 steps via `_build_check_steps()` in `src/gzkit/commands/quality.py`.
The registry must enumerate exactly those steps — no more, no less — classified as
`bound` / `advisory` / `unenforced`. The registry membership is DERIVED at import time
from `_build_check_steps()`, not authored by hand.

**Destination-in-mind (Step 6a disclosure):** Before writing this plan, I explored
`quality.py` and know the approach: `build_qc_registry()` calls `_build_check_steps()`,
maps each `(name, runner)` tuple to a `QCStep` using a classification lookup dict keyed
by step name, and returns the list. The model is a frozen Pydantic `BaseModel` with
`extra="forbid"`.

**Rejected alternatives:**
- Hard-coding a parallel list of step names in `qc_binding.py` — rejected because that
  IS the hand-maintained list the ADR prohibits; the registry must derive membership
  from the actual check runner.
- Deriving classification via reflection/introspection of runner source — rejected as
  fragile; honest explicit classification is the right shape for OBPI-01 (OBPI-02
  validates classifications via negative controls, OBPI-01 just establishes the model).

## Files

- **CREATE** `src/gzkit/qc_binding.py` — QCStep model + build_qc_registry()
- **CREATE** `tests/governance/test_qc_binding.py` — unit tests for model + registry
- **EVIDENCE** `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/obpis/OBPI-0.0.73-01-qc-step-registry-and-classifier.md`

## Steps

### Step 1: Write failing tests (Red phase)

Author `tests/governance/test_qc_binding.py` with three behavior tests covering the
brief's three BEHAVIOR REQs:

**REQ-0.0.73-01-01** (`@covers REQ-0.0.73-01-01`):
- `test_qcstep_is_frozen` — attempt to mutate a field via `qcstep.name = "x"` →
  assert `ValidationError` or `FrozenInstanceError` raised
- `test_qcstep_extra_forbidden` — attempt `QCStep(**valid_fields, extra_field="x")` →
  assert `ValidationError` raised
- `test_qcstep_has_all_seven_fields` — construct a valid `QCStep` and assert all seven
  field names are present on the instance

**REQ-0.0.73-01-02** (`@covers REQ-0.0.73-01-02`):
- `test_registry_matches_gz_check_steps` — call `build_qc_registry()` and
  `_build_check_steps()`, assert the registry IDs (derived from step names) are in
  1:1 correspondence with the check step names — no extra, no missing

**REQ-0.0.73-01-03** (`@covers REQ-0.0.73-01-03`):
- `test_every_step_has_valid_binding` — for each step in `build_qc_registry()`, assert
  `step.binding in {"bound", "advisory", "unenforced"}`

Run `uv run -m unittest tests.governance.test_qc_binding -v` — all three tests FAIL
(Red phase confirmed; the module doesn't exist yet).

### Step 2: Implement src/gzkit/qc_binding.py (Green phase)

Create `src/gzkit/qc_binding.py` with:

1. **`QCStepBinding` enum** (str enum): `bound`, `advisory`, `unenforced`

2. **`QCStep` Pydantic model** (`frozen=True, extra="forbid"`) with fields:
   - `id: str` — machine-stable identifier (e.g. `"lint"`)
   - `name: str` — human-readable name matching `_build_check_steps()` label
   - `kind: str` — check category: `lint`, `format`, `test`, `typecheck`, `bdd`,
     `governance`, `audit`
   - `subject: str` — surface being checked: `"src/"`, `"tests/"`, `"docs/"`,
     `"governance/"`, `"all"`
   - `binding: str` — exactly one of `bound` / `advisory` / `unenforced`
   - `wired_into: list[str]` — commands this step runs in (default: `["gz check"]`)
   - `theater_flags: list[str]` — theater signatures detected (empty for OBPI-01;
     OBPI-02 populates via negative controls)
   - `enforcement_locus: str` — where enforcement fires:
     `"subprocess"`, `"python_function"`, `"advisory"`

3. **`_STEP_CLASSIFICATION` dict** mapping each `_build_check_steps()` step name to a
   `QCStepBinding` classification and metadata tuple `(kind, subject, enforcement_locus)`.
   Contains one entry per step in `_build_check_steps()`.

4. **`build_qc_registry() -> list[QCStep]`** function:
   - Calls `_build_check_steps()` from `gzkit.commands.quality`
   - For each `(name, _)` pair, looks up classification from `_STEP_CLASSIFICATION`
   - Builds and returns a `list[QCStep]`
   - Raises `KeyError` with informative message if a step name is missing from the
     classification dict (this is the sentinel that fires when `_build_check_steps()`
     adds a new step — forces the author to classify it, keeping derivation honest)

### Step 3: Run tests to verify (Green)

```
uv run -m unittest tests.governance.test_qc_binding -v
```

All three test classes pass.

### Step 4: Lint and typecheck

```
uv run ruff check . --fix
uv run ruff format .
uv run gz typecheck
```

### Step 5: Run full test suite

```
uv run gz test
```

All tests pass.

### Step 6: Verify OBPI-specific checks

```
uv run gz validate --documents
```

```
test -f src/gzkit/qc_binding.py
test -f tests/governance/test_qc_binding.py
```

```
uv run python -c "from gzkit.qc_binding import build_qc_registry; [print(s.id, s.binding) for s in build_qc_registry()]"
```

### Step 7: Present OBPI Acceptance Ceremony

(Human attestation gate — pipeline Stage 4)

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
```

## Notes

- The `theater_flags` field is empty for all steps in OBPI-01 — OBPI-02 will populate
  it via negative-control runs (`gz validate --qc-binding`). OBPI-01 establishes the
  model and registry membership; OBPI-02 validates classification honesty.
- The `_STEP_CLASSIFICATION` dict is NOT a hand-maintained registry of QC steps — it is
  classification METADATA for steps whose membership is derived from `_build_check_steps()`.
  When a new step is added to `gz check`, the `KeyError` sentinel fires at registry
  build time, forcing explicit classification.
- `kind` values: `lint`, `format`, `test`, `typecheck`, `bdd`, `audit`
- Binding classifications for current 32 steps: all non-advisory steps are `bound`
  (they exit non-zero on failure in `gz check`); the Behave step is classified `bound`
  but may be empty-run advisory in some environments (OBPI-02 will test this).
