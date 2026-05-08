# Plan: OBPI-0.0.29-07 — Two-path Intrinsic-Complexity Attestation

## Context

ADR-0.0.29 OBPI-07 closes the 2am Scenario-3 gap: a function with genuinely irreducible cyclomatic complexity (e.g. a query optimizer at CC=24) needs a formal attestation path that the advisor honors, rather than repeatedly flagging it as a refactor candidate. Two paths are provided:
- **Decorator path**: `@intrinsic_complexity(reason=..., attestor=...)` annotated in code; advisor honors at diagnosis time by skipping the refactor recommendation and presenting the attestation instead.
- **Commit-time path**: `gz complexity-advise --attest-intrinsic --reason=... --attestor=... <path>:<qualname>` records a ledger event with Gate 5 TTY+ATTEST confirmation.

Neither path is a silent escape hatch — both require human attestation.

## Files Created

- `src/gzkit/complexity/advisor/intrinsic.py` — `@intrinsic_complexity` decorator + module-level registry
- `src/gzkit/governance/trust_audits/intrinsic_attestation.py` — event-shape validator for `validate --documents`
- `tests/complexity/advisor/test_intrinsic.py` — decorator/registry unit tests
- `tests/commands/test_complexity_advise_attest_intrinsic.py` — CLI `--attest-intrinsic` tests
- `tests/governance/test_intrinsic_attestation_event.py` — ledger event shape + schema tests
- `features/intrinsic_complexity_attestation.feature` — BDD end-to-end (both paths)

## Files Modified

- `src/gzkit/commands/complexity_advise.py` — add `--attest-intrinsic`, `--reason`, `--attestor` flags + registry enrichment
- `src/gzkit/ledger_events.py` — add `intrinsic_complexity_attestation_event()` factory
- `src/gzkit/schemas/ledger.json` — register `intrinsic-complexity-attestation` event schema
- `src/gzkit/governance/trust_audits/__init__.py` — import/export `validate_intrinsic_attestation`
- `src/gzkit/commands/validate_cmd.py` — wire `"intrinsic_attestation"` key in `audit_fns`
- `docs/user/manpages/gz-complexity-advise.md` — add `--attest-intrinsic` flag docs + example
- `docs/user/runbook.md` — add "Complexity doctrine surfaces" entry describing two paths

## Path Notes (from audit)

- Brief lists `src/gzkit/governance/ledger_events.py` — actual registry is `src/gzkit/ledger_events.py` (uses "(or schema home)" accommodation).
- Brief lists `src/gzkit/governance/trust_audits.py` — `trust_audits` is a directory package; new sub-module `intrinsic_attestation.py` is the correct target.

## Implementation Steps (TDD — Red-Green-Refactor)

### Task 1: `intrinsic.py` — Decorator + Registry

**Write failing tests first (`tests/complexity/advisor/test_intrinsic.py`):*
- `@covers("REQ-0.0.29-07-01")` — registry lookup after decoration returns `(reason, attestor, date)`
- `@covers("REQ-0.0.29-07-02")` — decorated function's behavior is identical before/after decoration (no-op)

**Implement `src/gzkit/complexity/advisor/intrinsic.py`:**
```python
_REGISTRY: dict[tuple[str, str], tuple[str, str, str]] = {}  # (file_path, qualname) -> (reason, attestor, date)

def intrinsic_complexity(*, reason: str, attestor: str):
    decoration_date = date.today().isoformat()
    def decorator(fn):
        file_path = inspect.getfile(fn)
        _REGISTRY[(file_path, fn.__qualname__)] = (reason, attestor, decoration_date)
        return fn  # no-op: fn returned unchanged
    return decorator

def get_attestation(file_path: str, qualname: str) -> tuple[str, str, str] | None:
    return _REGISTRY.get((file_path, qualname))
```

### Task 2: Registry enrichment in CLI (`complexity_advise.py`)

**Write failing tests (add to existing test file):*
- `@covers("REQ-0.0.29-07-02")` — when `(file_path, qualname)` is in registry and CC crosses warn band, diagnosis has `intrinsic_attestation` populated and `recommended_move` is suppressed in presenter output

**Implement enrichment in `_analyze_file`:**
After `engine.diagnose()` returns a non-None diagnosis, check registry:
```python
from gzkit.complexity.advisor.intrinsic import get_attestation
# qualname from radon: block.classname + "." + block.name if block.classname else block.name
qualname = f"{block.classname}.{block.name}" if getattr(block, "classname", None) else block.name
attestation = get_attestation(str(source_file), qualname)
if attestation is not None:
    reason, attestor, attested_at = attestation
    attestation_id = f"{source_file}::{qualname}"
    diagnosis = diagnosis.model_copy(update={
        "intrinsic_attestation": IntrinsicAttestationRef(attestation_id=attestation_id)
    })
```

**Attestation rendering stays in `complexity_advise.py` (presentation.py is NOT in OBPI-07 allowed paths).** After `_analyze_file` enriches a diagnosis, collect attested diagnoses separately. Attested functions are removed from the `diagnoses` list passed to the presenter (so they never appear as refactor recommendations) and rendered inline in `complexity_advise_cmd` with the canonical phrase "intrinsic complexity attested by `<attestor>` on `<date>`: `<reason>`", looked up via `get_attestation(file_path, decoded_qualname)` using the decoded `attestation_id`.

### Task 3: `--attest-intrinsic` commit-time path

**Write failing tests (`tests/commands/test_complexity_advise_attest_intrinsic.py`):**
- `@covers("REQ-0.0.29-07-03")` — function NOT crossing a band → exit 1, no event
- `@covers("REQ-0.0.29-07-04")` — function crossing warn band + TTY + ATTEST → one ledger event with canonical payload
- `@covers("REQ-0.0.29-07-05")` — headless invocation → exit 1, no event
- `@covers("REQ-0.0.29-07-07")` — failed invocation (invalid path) → no partial state

**Implement in `complexity_advise_cmd`:**
```python
# New flags: attest_intrinsic: bool, reason: str | None, attestor: str | None
# New argument form: path may be "file.py:ClassName.method_name"

if attest_intrinsic:
    return _run_attest_intrinsic(path=path, reason=reason, attestor=attestor, rule_path=rule_path)
```

`_run_attest_intrinsic`:
1. Parse `<path>:<qualname>` argument
2. Run radon + table.band_for() on that specific function — if no crossing → print error, return 1
3. Call `_enforce_attest_intrinsic_authenticity()` (replicates `_enforce_human_attestation_authenticity` pattern from `adr_audit.py`):
   - TTY path: show confirmation, require `ATTEST` input
   - Headless: raise error, no event emitted
4. Build `intrinsic_complexity_attestation_event(...)` and append to ledger
5. Print receipt ID

### Task 4: Ledger event factory + schema

**Write failing tests (`tests/governance/test_intrinsic_attestation_event.py`):**
- `@covers("REQ-0.0.29-07-06")` — event in ledger → `gz validate --documents` exit 0
- `@covers("REQ-0.0.29-07-06")` — malformed event in ledger → `gz validate --documents` exit non-zero
- `@covers("REQ-0.0.29-07-11")` — tests use `tempfile`-backed ledger, never touch live ledger

**Add to `src/gzkit/ledger_events.py`:**
```python
def intrinsic_complexity_attestation_event(
    *, file_path: str, qualname: str, reason: str, attestor: str,
    attestation_date: str, crossing_metric: str, crossing_band: str, crossing_value: float,
) -> LedgerEvent:
    return LedgerEvent(
        event="intrinsic-complexity-attestation",
        id=f"{file_path}::{qualname}",
        extra={"file_path": file_path, "qualname": qualname, "reason": reason,
               "attestor": attestor, "attestation_date": attestation_date,
               "crossing_metric": crossing_metric, "crossing_band": crossing_band,
               "crossing_value": crossing_value},
    )
```

**Extend `src/gzkit/schemas/ledger.json`** with `"intrinsic-complexity-attestation"` entry under `"events"` — required fields: `file_path, qualname, reason, attestor, attestation_date, crossing_metric, crossing_band, crossing_value`.

### Task 5: trust_audits extension

**Create `src/gzkit/governance/trust_audits/intrinsic_attestation.py`:**
Follows `evaluation_justify_binding.py` pattern — iterates ledger JSONL, filters for `intrinsic-complexity-attestation` events, validates required fields and types. Returns `list[ValidationError]`.

**Update `src/gzkit/governance/trust_audits/__init__.py`:**
- Add import: `from gzkit.governance.trust_audits.intrinsic_attestation import validate_intrinsic_attestation`
- Add to `__all__`

**Update `src/gzkit/commands/validate_cmd.py`:**
- Add `"intrinsic_attestation": lambda: trust_audits.validate_intrinsic_attestation(project_root)` to `audit_fns` dict

### Task 6: Docs

**`docs/user/manpages/gz-complexity-advise.md`:** Add `--attest-intrinsic`, `--reason`, `--attestor` flags; add example invocation showing both paths.

**`docs/user/runbook.md`:** Add entry under "Complexity doctrine surfaces" describing:
- Decorator path: when to use (pre-known irreducible; persists in code)
- Commit-time path: when to use (in-flight discovery; persists in ledger)
- Both require human attestation; neither is a silent escape hatch

### Task 7: BDD scenarios

**`features/intrinsic_complexity_attestation.feature`:**
Tagged `@REQ-0.0.29-07-01` through `@REQ-0.0.29-07-05`. Scenarios:
1. Decorator path: decorate a function, run engine, see "intrinsic complexity attested" in output
2. Commit-time path: run `--attest-intrinsic` on a crossing function → one ledger event
3. Guard: run `--attest-intrinsic` on non-crossing function → refused
4. Guard: headless `--attest-intrinsic` → refused, no event

## Key Design Decisions

**Registry key = `(inspect.getfile(fn), fn.__qualname__)`.** The CLI reconstructs qualname from radon's `block.classname` + `block.name` and resolves `file_path` from the source file Path.

**Frozen diagnosis enrichment via `.model_copy()`.** `AdvisorDiagnosis` is `frozen=True`. Enriched copy is constructed with `diagnosis.model_copy(update={"intrinsic_attestation": IntrinsicAttestationRef(attestation_id=...)})`. `diagnosis.py` is DENIED — no edits to existing classes.

**TTY gate replicates `_enforce_human_attestation_authenticity` from `adr_audit.py`.** Same three-branch pattern (TTY → ATTEST, agent-relayed → pipeline marker, headless → fail-closed).

**Ledger event `id` = `f"{file_path}::{qualname}"`.** Composite identifier per the `adr-evaluation` precedent where `id` is the primary artifact.

**`presentation.py` is NOT in OBPI-07 allowed paths.** Attestation rendering lives in `complexity_advise.py`. Attested diagnoses are partitioned out before the presenter call and rendered separately with the canonical phrase.

## Verification

```bash
# Task-by-task verification (scoped)
uv run gz arb step --name unittest -- uv run -m unittest tests/complexity/advisor/test_intrinsic.py tests/commands/test_complexity_advise_attest_intrinsic.py tests/governance/test_intrinsic_attestation_event.py -v

# Full suite
uv run gz arb step --name unittest -- uv run -m unittest -q

# Lint + typecheck
uv run gz arb ruff
uv run gz arb typecheck

# Heavy-lane docs
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict

# BDD
uv run -m behave features/intrinsic_complexity_attestation.feature

# validate --documents coverage
uv run gz validate --documents
```

## Destination-in-Mind

Decorator + registry in `intrinsic.py`; CLI enrichment via `model_copy()`; `--attest-intrinsic` flag replicates `_enforce_human_attestation_authenticity`; ledger event factory in root `ledger_events.py`; trust-audit sub-module for event-shape validation; BDD + manpage + runbook docs.

**Rejected alternatives:**
- Modifying `IntrinsicAttestationRef` in `diagnosis.py` (DENIED path).
- Storing attestation data in `IntrinsicAttestationRef` fields instead of registry (denied by schema boundary).
- ARB receipts for intrinsic attestation (ADR Negative #12 explicitly forbids).
- Flat `trust_audits.py` file (doesn't exist; directory package requires sub-module).
