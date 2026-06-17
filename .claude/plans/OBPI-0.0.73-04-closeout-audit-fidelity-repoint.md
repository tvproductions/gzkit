# Plan: OBPI-0.0.73-04-closeout-audit-fidelity-repoint

## OBPI
OBPI-0.0.73-04-closeout-audit-fidelity-repoint

## Parent ADR
ADR-0.0.73-verification-layer-binding-audit

## ADR Decision Item (verbatim)
> Closeout + audit both invoke the fidelity gate (`src/gzkit/commands/closeout_ceremony.py`, `src/gzkit/commands/audit_cmd.py`). BOTH the closeout ceremony and the audit ceremony invoke `gz adr fidelity`, replacing the prose 'Demonstrate Value' step with a bound, runnable gate. One gate, two consumers — not duplicated prose.

## REQs to satisfy
- REQ-0.0.73-04-01 [BEHAVIOR]: closeout ceremony invokes fidelity gate, fails if any assertion fails
- REQ-0.0.73-04-02 [BEHAVIOR]: audit ceremony invokes same standalone fidelity gate
- REQ-0.0.73-04-03 [BEHAVIOR]: absence of Fidelity Assertions block is flagged (not silently accepted)
- REQ-0.0.73-04-04 [SUPPORT]: runbooks updated; `gz validate --documents` exits 0
- REQ-0.0.73-04-05 [SUPPORT]: skills repointed + synced; `gz validate --surfaces` exits 0

## Pre-execution disclosures (§ Step 6a)

**Destination-in-mind before planning:** Call `run_fidelity_gate` inside `_gate_closeout_proof`
(closeout ceremony) and inside `audit_cmd` (audit), with `parse_fidelity_assertions` raising
`ValueError` on absence being converted to `PolicyBreachError` / audit failure respectively.
Test-first (RED) before each implementation step.

**Rejected alternatives:**
- Adding a NEW CeremonyStep between EXECUTE and ATTESTATION — rejected: requires state machine
  surgery, breaks CeremonyStep enum integer values used in persistence, major scope expansion.
- Running fidelity gate at ceremony initialization — rejected: ADR fidelity assertions reference
  surfaces that may not exist until implementation is verified; EXECUTE→ATTESTATION edge is the
  correct semantic moment (after all walkthrough commands have run).
- Adding fidelity gate only to the SKILL, not the code — rejected: the ADR explicitly targets
  `closeout_ceremony.py` and `audit_cmd.py` as the surfaces; prose-only change is theater.

## Implementation Steps

### Step 1: Create test file (RED phase)

Create `tests/governance/test_closeout_audit_fidelity.py` with tests derived from REQs (NOT
from implementation). Each test covers one REQ and will be RED before implementation.

Tests to write:
1. `TestCloseoutFidelityGate.test_gate_invoked_and_fails_on_assertion_failure`
   — @covers REQ-0.0.73-04-01: mock `_gate_closeout_proof` to call the fidelity check;
   provide an ADR with a failing assertion; verify `PolicyBreachError` is raised.
2. `TestAuditFidelityGate.test_audit_invokes_fidelity_gate`
   — @covers REQ-0.0.73-04-02: mock `run_fidelity_gate` with a failing assertion in audit_cmd;
   verify audit exits non-zero / raises.
3. `TestFidelityAbsenceHandling.test_closeout_flags_missing_block`
   — @covers REQ-0.0.73-04-03: ADR without `## Fidelity Assertions`; verify closeout raises
   `PolicyBreachError` with absence message.
4. `TestFidelityAbsenceHandling.test_audit_flags_missing_block`
   — @covers REQ-0.0.73-04-03: same absence pattern for audit_cmd.

### Step 2: Add fidelity gate to closeout_ceremony.py

Add a private helper `_run_fidelity_gate_check(project_root, state, adr_file)` that:
- Calls `parse_fidelity_assertions(adr_file)` — raises `PolicyBreachError` on `ValueError`
  (absence) with message: "ADR has no ## Fidelity Assertions block — the prose 'Demonstrate
  Value' step is gone; a runnable block is required (ADR-0.0.73, OBPI-0.0.73-04)."
- Calls `run_fidelity_gate(assertions, adr_id=state.adr_id)`
- For any failed assertions: raises `PolicyBreachError` with failed claim names.

Wire it into `_gate_closeout_proof` AFTER the existing `validate_closeout_proof` check:
```python
def _gate_closeout_proof(project_root: Path, state: CeremonyState) -> None:
    if state.current_step != CeremonyStep.EXECUTE:
        return
    # existing closeout-proof gate...
    ...
    # NEW: fidelity gate
    _run_fidelity_gate_check(project_root, state, adr_file)
```

`adr_file` must be resolved inside `_gate_closeout_proof` — use `resolve_adr_file` from
`gzkit.commands.common`. Add import of `parse_fidelity_assertions`, `run_fidelity_gate` from
`gzkit.fidelity`.

### Step 3: Add fidelity gate to audit_cmd.py

In `audit_cmd()`, after `result_rows, failures = _run_audit_verifications(...)`, add:

```python
# Run fidelity gate (one gate, two consumers — ADR-0.0.73 OBPI-04)
try:
    assertions = parse_fidelity_assertions(adr_file)
    fidelity_results = run_fidelity_gate(assertions, adr_id=adr_id)
    fidelity_failures = sum(1 for r in fidelity_results if r.result == "fail")
except ValueError:
    # No Fidelity Assertions block — flag as failure per REQ-0.0.73-04-03
    console.print("[red]Fidelity gate:[/red] ADR has no ## Fidelity Assertions block.")
    sys.exit(3)
if fidelity_failures:
    console.print(f"[red]Fidelity gate:[/red] {fidelity_failures} assertion(s) failed.")
    sys.exit(3)
```

Add imports: `from gzkit.fidelity import parse_fidelity_assertions, run_fidelity_gate`.

Place the fidelity block BEFORE the ledger writes so a fidelity failure doesn't record a
false validation receipt.

### Step 4: Update gz-adr-audit/SKILL.md

Replace Step 3 "Demonstrate Value" prose section with:

```
### 3. Fidelity Gate (replaces prose Demonstrate Value)

Run the bound fidelity gate against the ADR:

    uv run gz adr fidelity <ADR>

The gate reads the ADR's `## Fidelity Assertions` block and runs each command, comparing
observed vs expected exit. Any failure blocks audit completion. If the block is absent, the
audit fails — the prose 'Demonstrate Value' step is gone (ADR-0.0.73, OBPI-0.0.73-04).

The narrator persona is no longer dispatched for this step; the gate output IS the evidence.
```

Also update the persona dispatch table: remove narrator from Step 3, or note it is retired.

### Step 5: Update gz-adr-closeout-ceremony/SKILL.md

In the walkthrough/EXECUTE step section, add a note that the fidelity gate runs automatically
at the EXECUTE→ATTESTATION boundary:

```
> **Fidelity gate (ADR-0.0.73, OBPI-0.0.73-04):** When --next is invoked after the last
> walkthrough command, the ceremony automatically runs `gz adr fidelity <ADR>` before
> advancing to ATTESTATION. If any assertion fails, the ceremony blocks. If the ADR has
> no `## Fidelity Assertions` block, the ceremony fails closed. No prose 'Demonstrate Value'
> step — the gate IS the demonstration.
```

### Step 6: Update runbooks

`docs/user/runbook.md`: Find the closeout/audit section and add a note that the fidelity
gate runs automatically. Remove any prose instruction to "demonstrate value manually".

`docs/governance/governance_runbook.md`: Same pattern — note the fidelity gate replaces
the prose step.

### Step 7: Sync skill mirrors

After editing canonical skills under `.gzkit/skills/`, run:
```bash
uv run gz agent sync control-surfaces
```

### Step 8: Run quality gates

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --documents
uv run gz validate --surfaces
uv run gz covers OBPI-0.0.73-04-closeout-audit-fidelity-repoint --json
```

## Files

### CREATE
- `tests/governance/test_closeout_audit_fidelity.py`

### MODIFY
- `src/gzkit/commands/closeout_ceremony.py`
- `src/gzkit/commands/audit_cmd.py`
- `.gzkit/skills/gz-adr-audit/SKILL.md`
- `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md`
- `docs/user/runbook.md`
- `docs/governance/governance_runbook.md`

## Verification Commands
```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
test -f src/gzkit/commands/closeout_ceremony.py
test -f tests/governance/test_closeout_audit_fidelity.py
```
