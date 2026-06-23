# Plan: Retire the Two Hand-Set Staging Flags (OBPI-0.0.74-09)

## OBPI
OBPI-0.0.74-09-mx-retire-staging-flags

## Context

ADR-0.0.74 Decision item 9 (verbatim): "Retire the two hand-set staging flags.
Delete _FRESHNESS_FAIL_CLOSED and _FLOOR_FAIL_CLOSED; both gates resolve their
severity through the leveled checkpoint (an effective `GZ_<LEVEL>`, not a
hand-set bool) — the honest generalization of the two hacks."

Current state:
- `rendition_freshness.py` has `_FRESHNESS_FAIL_CLOSED = False` (default warn mode)
- `rendition_floor_coherence.py` has `_FLOOR_FAIL_CLOSED = False` (default warn mode)
- Both gates use: `closed = _*_FAIL_CLOSED if fail_closed is None else fail_closed`

Target state after OBPI-09:
- Both flags deleted
- Default severity resolved by `checkpoint.is_advisory("<guard-name>", root)`:
  - Outside MX hangar (no marker): not advisory → fail-closed (full strength)
  - Inside MX hangar (marker present): advisory → warn mode (passes through)
- `fail_closed: bool | None = None` signature kept for explicit callers (NCs pass `fail_closed=True`)

## Files

### Modified:
- `src/gzkit/governance/trust_audits/rendition_freshness.py` — delete flag, add checkpoint wiring
- `src/gzkit/governance/trust_audits/rendition_floor_coherence.py` — delete flag, add checkpoint wiring
- `tests/governance/test_rendition_freshness.py` — add REQ-09-01/02 tests; remove old staging tests
- `tests/governance/test_rendition_floor_coherence.py` — add REQ-09-01/02 tests; remove old staging tests

### Not touched:
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py` — NCs already pass `fail_closed=True` explicitly; no change needed

## Steps

### Step 1 — RED: Write failing checkpoint-wiring tests (REQ-0.0.74-09-01)

**`tests/governance/test_rendition_freshness.py`**: Add class `TestCheckpointWiringFreshness`.

Import `from gzkit.mx import marker as _marker` and `from gzkit.mx.marker import Marker`.

Two tests:
1. `test_without_mx_marker_gate_is_fail_closed`:
   - Seed corpus, save rendition without sidecar (drift condition)
   - No marker written
   - Call `validate_rendition_freshness(self.root)` (no `fail_closed` arg)
   - Assert: `len(errors) == 1` (gate is fail-closed outside the hangar)
   - Decorate: `@covers("REQ-0.0.74-09-01")`

2. `test_with_mx_marker_gate_is_advisory`:
   - Seed corpus, save rendition without sidecar (same drift condition)
   - Write marker: `_marker.write(Marker(session_id="test-session"), self.root)`
   - Call `validate_rendition_freshness(self.root)` (no `fail_closed` arg)
   - Assert: `errors == []` (gate is advisory inside the hangar)
   - Decorate: `@covers("REQ-0.0.74-09-01")`

Also add `@covers("REQ-0.0.74-09-02")` to one existing fail-closed test that demonstrates
the gate genuinely binds when forced hard — pick `test_missing_sidecar_is_drift`
(already passes `fail_closed=True`).

**`tests/governance/test_rendition_floor_coherence.py`**: Add class `TestCheckpointWiringFloor`.

Same two tests, adapted for floor coherence:
1. `test_without_mx_marker_gate_is_fail_closed`: invariant entry, rendition missing it, no marker → 1 error
2. `test_with_mx_marker_gate_is_advisory`: same setup, marker written → no errors
Add `@covers("REQ-0.0.74-09-01")` to both.
Add `@covers("REQ-0.0.74-09-02")` to `test_missing_invariant_entry_is_fail_closed` (already explicit `fail_closed=True`).

Run `uv run -m unittest tests.governance.test_rendition_freshness tests.governance.test_rendition_floor_coherence`
→ Expect RED on the two new `TestCheckpointWiring*` tests (flag still exists; default is warn → advisory test
passes unexpectedly, no-marker test fails to return errors).

### Step 2 — GREEN: Delete flags, add checkpoint wiring, remove obsolete staging tests

**`src/gzkit/governance/trust_audits/rendition_freshness.py`**:
- Add import: `from gzkit.mx import checkpoint as _checkpoint` (after existing imports)
- Delete the constant and its comment block:
  ```python
  # Staging flag (OBPI-0.0.41 warn→fail precedent). Increment 2 flips this to True.
  _FRESHNESS_FAIL_CLOSED = False
  ```
- Replace in `validate_rendition_freshness`:
  ```python
  closed = _FRESHNESS_FAIL_CLOSED if fail_closed is None else fail_closed
  ```
  with:
  ```python
  closed = (not _checkpoint.is_advisory("rendition-freshness", root)) if fail_closed is None else fail_closed
  ```
- Update module docstring: remove the staging-flag paragraph ("Staging (OBPI-0.0.41...)"),
  replace with one line: "Severity resolved through the shared MX checkpoint (OBPI-0.0.74-09):
  advisory inside the hangar, fail-closed outside."

**`src/gzkit/governance/trust_audits/rendition_floor_coherence.py`**:
- Add import: `from gzkit.mx import checkpoint as _checkpoint`
- Delete the constant and its comment block:
  ```python
  # Staging flag (OBPI-0.0.41 warn→fail precedent). Flips to True only when ...
  _FLOOR_FAIL_CLOSED = False
  ```
- Replace in `validate_rendition_floor_coherence`:
  ```python
  closed = _FLOOR_FAIL_CLOSED if fail_closed is None else fail_closed
  ```
  with:
  ```python
  closed = (not _checkpoint.is_advisory("rendition-floor-coherence", root)) if fail_closed is None else fail_closed
  ```
- Update module docstring: remove staging paragraph, same brief replacement.

**`tests/governance/test_rendition_freshness.py`**:
- Remove class `TestRenditionFreshnessWarnStaging` entirely (3 tests). These tested the
  old `_FRESHNESS_FAIL_CLOSED = False` default behavior. After OBPI-09, the default
  is fail-closed outside the hangar; there is no more module-flag staging.
- Add import: `from gzkit.mx import marker as _marker` and `from gzkit.mx.marker import Marker`
  (needed by new tests added in Step 1).

**`tests/governance/test_rendition_floor_coherence.py`**:
- Remove class `TestStagedWarn` entirely (1 test). Same reason.
- Add import: `from gzkit.mx import marker as _marker` and `from gzkit.mx.marker import Marker`

Run `uv run -m unittest tests.governance.test_rendition_freshness tests.governance.test_rendition_floor_coherence`
→ Expect GREEN: new checkpoint tests pass, removed staging tests gone, all existing tests pass.

### Step 3 — Lint, type check, full test suite

```bash
uv run ruff check . --fix && uv run ruff format .
uv run -m unittest -q
```

### Step 4 — Verify gate behavior

```bash
# Flags are gone from both files:
test -f src/gzkit/governance/trust_audits/rendition_freshness.py
test -f src/gzkit/governance/trust_audits/rendition_floor_coherence.py
# Gates pass outside the hangar (no false positives in the real tree):
uv run gz validate --rendition-freshness
uv run gz validate --rendition-floor-coherence
# Negative controls still bind:
uv run gz validate --qc-binding
```

## Destination-in-Mind Disclosure (Step 6a)

**Conclusion formed before writing plan:** Delete both `_*_FAIL_CLOSED` constants;
replace the `closed = <flag> if fail_closed is None else fail_closed` line in each gate
with `closed = (not _checkpoint.is_advisory("<guard-name>", root)) if fail_closed is None
else fail_closed`; remove the old staging test classes since they tested behavior the
checkpoint supersedes.

**Rejected alternatives:**

A. Make default `fail_closed=True` without checkpoint wiring. Rejected: doesn't provide
   hangar advisory demotion; the checkpoint is the point of OBPI-09.

B. Call `checkpoint.resolve()` with a `GZ_<LEVEL>` constant instead of `is_advisory()`.
   Rejected: `is_advisory()` is the right abstraction — it directly answers the bool
   question the `closed` variable needs, without introducing a level constant these
   gates don't otherwise emit.

C. Add a new `guard_level: int` parameter to the validator functions. Rejected:
   speculative complexity; a single call to `is_advisory()` is minimal and correct.

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --rendition-freshness
uv run gz validate --rendition-floor-coherence
uv run gz validate --qc-binding
test -f src/gzkit/governance/trust_audits/rendition_freshness.py
test -f src/gzkit/governance/trust_audits/rendition_floor_coherence.py
test -f src/gzkit/mx/checkpoint.py
```

## Notes

- REQ-0.0.74-09-03 is a STRUCTURAL-FENCE — proven at ADR closeout via parent ADR
  § Boundary Invariants #2; no code labor here.
- `req_atomic:` exemption declared in brief frontmatter for all three REQs; seq=01 per REQ.
- Negative controls in `_qc_negative_controls.py` are NOT in Allowed Paths;
  they already pass `fail_closed=True` explicitly and need no changes.
