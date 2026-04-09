# Plan: OBPI-0.25.0-03 Signature Pattern Evaluation

## Context

OBPI-0.25.0-03 evaluates `airlineops/src/airlineops/core/signature.py` (365 lines) for absorption into gzkit. The module provides dataset signature computation and cryptographic fingerprinting for airline-specific dataset families. gzkit has no equivalent module and no hashlib usage in `src/gzkit/`.

## Decision: Exclude

The module is **airline-domain-specific**. Every significant construct is tied to airline dataset semantics:

- `DatasetFamily` = `Literal["bts_db1b", "bts_db28dm", "bts_asqp", "bts_db10", "bts_db20", "faa", "exog"]`
- 6 character extractors for airline dataset families (DB1B ticket counts, DB28 passenger totals, ASQP flight counts, FAA AIRAC cycles, exogenous datasets)
- `_detect_dataset_family()` — prefix-based airline dataset detection
- `_load_catalog()` / `_find_dataset_root()` — airline `data/datasets/` directory structure
- `SignaturePayload` fields: `dataset_id`, `dataset_family`, `row_count`, `period_count`, `period_range`, `character` — all airline dataset concepts

The only generic primitives are:

- `_compute_fingerprint()` — JSON `sort_keys` + SHA256 (~10 lines)
- `_timestamp_utc()` — UTC ISO format (~3 lines)

These are trivial utilities that don't warrant a standalone module. gzkit can add a `hashlib.sha256` call inline wherever needed in the future.

## Implementation Steps

### Step 1: Update OBPI brief with comparison and Exclude decision

**File:** `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-03-signature-pattern.md`

Add to the brief (following the existing pattern from OBPI-0.25.0-01 and OBPI-0.25.0-02):

1. Add **DECISION** section: Exclude with rationale
2. Add **COMPARISON ANALYSIS** table: dimension-by-dimension breakdown
3. Add **Gate 4 BDD: N/A** rationale (Exclude, no behavior change)
4. Check acceptance criteria (REQ-0.25.0-03-01 through 05)
5. Check quality gates (Gates 1-4, leave Gate 5 for human)
6. Add **Evidence** section: value narrative, key proof, implementation summary
7. Author **Closing Argument**

### Step 2: No code changes

Exclude decision = no new modules, no new tests, no behavior changes.

## Files Modified

- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-03-signature-pattern.md` (brief update only)

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
```

All should pass unchanged since no code is modified.
