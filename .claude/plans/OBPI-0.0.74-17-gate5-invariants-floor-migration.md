# Plan: OBPI-0.0.74-17 — Gate5 Invariants Floor Migration

**OBPI:** OBPI-0.0.74-17-gate5-invariants-floor-migration
**Parent ADR:** ADR-0.0.74-mx-mode-maintenance-hangar (item 17)
**Lane:** Heavy

## Context

OBPI-0.0.74-17 migrates the `GATE5_INVARIANTS` never-relax floor onto the
`@enforces` surface. Four floor members lack `@enforces` entries:
`secrets`, `operator-pii`, `ledger`, `gate5-attestation`.
(`grader-gaming` is OBPI-13.)

Prerequisites confirmed present:
- `src/gzkit/enforcement.py` — `@enforces` decorator + registry + runner (OBPI-15/16)
- `src/gzkit/mx/invariants.py` — `GATE5_INVARIANTS` frozenset (OBPI-03)

## Design Decisions

### D1 — Honest negative: secrets and operator-pii are named-not-enforced

Per ADR §Consequences/Negative #7 and ADR item 17:
- `validate_no_secrets` (handoff_validation.py) is HANDOFF-SCOPED — not a gate5 production path
- `_EMAIL_RE` (correction_mining.py) is INSIGHTS-SCOPED — not a gate5 production path
- Binding either as a gate5 `@enforces` entrypoint would be a narrower proxy — FORBIDDEN

Resolution: declare `_GATE5_NAMED_NOT_ENFORCED = frozenset({"secrets", "operator-pii"})`
in `invariants.py`. No `@enforces` entries for these two members. REQ-17-01 and
REQ-17-02 are satisfied by this honest-negative surfacing.

### D2 — Claim IDs use hyphen namespace (colon disallowed by _CLAIM_ID_RE)

The `@enforces` validator enforces `^[a-z][a-z0-9-]*$`. Colons are not allowed.
- Ledger claim ID: `"gate5-ledger"`
- Gate5-attestation absence claim ID: `"gate5-attestation-absence"`

The Demo in the brief uses `c.startswith('gate5:')` — this was aspirational notation.
Actual filtering should use `c.startswith('gate5-')`.

### D3 — Known-claims extension via _ensure_gate5_claims_registered()

`enforcement._load_known_claims()` only knows `_KNOWN_QC_CLAIM_IDS`. Gate5 claim IDs
are not there. Within the Allowed Paths constraint (`enforcement.py` is denied),
`invariants.py` will call `set_known_claims(_KNOWN_QC_CLAIM_IDS | _GATE5_CLAIM_IDS)`
inside `_ensure_gate5_claims_registered()` before registering. This extends the
known-claims cache before the `@enforces` call validates the claim ID.

The `_KNOWN_QC_CLAIM_IDS` import in `_ensure_gate5_claims_registered` uses a lazy
import with `# noqa: PLC0415` (cycle avoidance pattern, established in enforcement.py).

### D4 — gate5-attestation entrypoint: combined _requires_human + empty check

`_requires_human_obpi_attestation` (adr_audit.py) always returns True — the full
rejection path is inside obpi_complete.py's `if requires_human and not attestation_text.strip()`.
The entrypoint for gate5-attestation-absence combines both conditions without calling
`_fail()` (which would sys.exit):

```python
def _ep_gate5_attestation_absence(scenario: dict) -> bool:
    from gzkit.commands.adr_audit import _requires_human_obpi_attestation  # noqa: PLC0415
    requires = _requires_human_obpi_attestation(parent_adr=None, parent_lane=scenario["parent_lane"])
    return requires and not scenario["attestation_text"].strip()
```

This IS genuine: if `_requires_human_obpi_attestation` ever returned False, the NC
would fail (FACADE). The absence case (empty attestation text) returns True = caught.

### D5 — ledger entrypoint wraps validate_ledger with the .gzkit/ledger.jsonl path

`validate_ledger(path)` takes the ledger FILE path. The fixture returns the root dir
(for `shutil.rmtree` cleanup by `_run_single_claim`). The entrypoint wrapper:

```python
def _ep_gate5_ledger(root: Path) -> list:
    from gzkit.validate_pkg.ledger_check import validate_ledger  # noqa: PLC0415
    return validate_ledger(root / ".gzkit" / "ledger.jsonl")
```

Returns a list of `ValidationError` — truthy (non-empty) when the violation is caught.

## Files

| File | Action | Purpose |
|------|--------|---------|
| `src/gzkit/mx/invariants.py` | Modify | Add gate5 @enforces registrations + named-not-enforced |
| `tests/mx/test_gate5_invariants_live_nc.py` | Create | Live un-forced NCs for REQ-17-01 through REQ-17-04 |

## Steps

### Step 1: Extend src/gzkit/mx/invariants.py

Add after `GATE5_INVARIANTS` constant:

a. Import `enforces`, `get_enforcement_registry`, `set_known_claims` from
   `gzkit.enforcement` (top-level)

b. Define constants:
   ```python
   _GATE5_NAMED_NOT_ENFORCED: frozenset[str] = frozenset({"secrets", "operator-pii"})
   _GATE5_CLAIM_IDS: frozenset[str] = frozenset({"gate5-ledger", "gate5-attestation-absence"})
   ```

c. Define fixture for gate5-ledger:
   ```python
   def _build_gate5_ledger() -> Path:
       # mkdtemp, mkdir .gzkit, write malformed ledger.jsonl
       # missing required 'schema', 'id', 'ts' fields
   ```

d. Define entrypoint wrapper for gate5-ledger (lazy import, noqa: PLC0415):
   ```python
   def _ep_gate5_ledger(root: Path) -> list:
       from gzkit.validate_pkg.ledger_check import validate_ledger
       return validate_ledger(root / ".gzkit" / "ledger.jsonl")
   ```

e. Define fixture for gate5-attestation-absence:
   ```python
   def _build_gate5_attestation_absence() -> dict:
       return {"attestation_text": "", "parent_lane": "heavy"}
   ```

f. Define entrypoint wrapper for gate5-attestation-absence (lazy import):
   ```python
   def _ep_gate5_attestation_absence(scenario: dict) -> bool:
       from gzkit.commands.adr_audit import _requires_human_obpi_attestation
       requires = _requires_human_obpi_attestation(parent_adr=None, parent_lane=scenario["parent_lane"])
       return requires and not scenario["attestation_text"].strip()
   ```

g. Define NC table, marker, and `_ensure_gate5_claims_registered()`:
   - Imports `_KNOWN_QC_CLAIM_IDS` lazily to extend known-claims before `@enforces` call
   - Idempotent: skips already-registered claim IDs
   - Call `_ensure_gate5_claims_registered()` at module bottom

### Step 2: Create tests/mx/test_gate5_invariants_live_nc.py

Following the test convention from `tests/mx/test_gate5_invariants.py`:

```
TestGate5NamedNotEnforced
  test_secrets_named_not_enforced — REQ-0.0.74-17-01
    Asserts "secrets" in _GATE5_NAMED_NOT_ENFORCED
    Asserts no @enforces registry entry exists with claim_id="gate5-secrets" or similar
  test_operator_pii_named_not_enforced — REQ-0.0.74-17-02
    Same pattern for operator-pii

TestGate5LedgerLiveNC
  setUp: reset_enforcement_registry(), _ensure_gate5_claims_registered()
  tearDown: reset_enforcement_registry()
  test_ledger_nc_claims_registered — REQ-0.0.74-17-03
    Asserts "gate5-ledger" in registered_claims()
  test_ledger_nc_catches_broken_ledger — REQ-0.0.74-17-03
    Runs fixture → entrypoint directly, asserts result is truthy
  test_ledger_nc_passes_valid_ledger — REQ-0.0.74-17-03
    Runs with a VALID ledger, asserts result is falsy (genuine: only catches violations)

TestGate5AttestationAbsenceLiveNC
  setUp: reset_enforcement_registry(), _ensure_gate5_claims_registered()
  tearDown: reset_enforcement_registry()
  test_attestation_absence_nc_registered — REQ-0.0.74-17-04
    Asserts "gate5-attestation-absence" in registered_claims()
  test_attestation_absence_nc_catches_empty — REQ-0.0.74-17-04
    Calls _ep_gate5_attestation_absence({"attestation_text": "", "parent_lane": "heavy"})
    Asserts truthy (caught)
  test_attestation_absence_nc_does_not_flag_present — REQ-0.0.74-17-04
    Calls entrypoint with non-empty attestation, asserts falsy (genuine: only catches absence)
```

Each test class decorated with `@covers("REQ-0.0.74-17-NN")`.

### Step 3: Run ARB quality gates

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
```

### Step 4: Verify covers parity

```bash
uv run gz covers OBPI-0.0.74-17 --json
```

All REQ-17-01 through REQ-17-04 must show `covered: true`.

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
test -f src/gzkit/mx/invariants.py
test -f tests/mx/test_gate5_invariants_live_nc.py
# Demo: gate5 claims should appear
uv run python -c "from gzkit.mx.invariants import _ensure_gate5_claims_registered; from gzkit.enforcement import registered_claims; _ensure_gate5_claims_registered(); print('gate5 claims:', [c for c in registered_claims() if c.startswith('gate5-')])"
```

## Confidence Assessment (Stage 1→2 Gate)

Confidence: ~85% — close to threshold, one uncertainty remains.

**Approach already formed:** Use `_ensure_gate5_claims_registered()` in `invariants.py`
to extend known-claims via `set_known_claims()` before registration. Named-not-enforced
for secrets/operator-pii via `_GATE5_NAMED_NOT_ENFORCED` constant.

**Rejected alternatives:**
1. Binding `validate_no_secrets` (handoff-scoped) as gate5-secrets entrypoint — FORBIDDEN by honest-negative clause
2. Editing `enforcement.py` to extend `_load_known_claims` — outside Allowed Paths
3. Using subprocess for the gate5-attestation-absence NC — too heavy, fragile

**Uncertainty:** `set_known_claims()` is documented "for testing" but used here at
module level for production claim-source extension. This is a pragmatic choice
within the Allowed Paths constraint. If the operator prefers the clean architectural
path, `enforcement.py` should be added to Allowed Paths (brief amendment) to
extend `_ensure_production_claims_registered` and `_load_known_claims` properly.
Operator decision required before implementation.

## Notes

- REQ-17-05 is STRUCTURAL-FENCE: proved by BI#9 at ADR closeout, no test required
- `grader-gaming`'s entry is OBPI-13, NOT authored here
- No new dependencies added (enforcement, validate_pkg, commands.adr_audit are
  already in the dependency graph; lazy imports avoid circular import risk)
- Operator-PII prohibition: only SYNTHETIC PII shape, never real email
