# Plan: OBPI-0.0.41-04 Lock-Handoff Coupling Validator

## OBPI
OBPI-0.0.41-04-lock-handoff-coupling-validator

## Parent ADR
ADR-0.0.41-token-block-lock-discipline

## ADR Intent Quoted (Decision Item 5)
> "A new validator scope `gz validate --lock-handoff-coupling` replays
> the ledger and fail-closes on any `obpi_lock_released` event missing a
> `handoff_path` payload field, or referencing a path that does not exist
> or whose frontmatter timestamp predates the matching claim."

## Parent ADR Boundary Invariant (REQ-04-08 STRUCTURAL-FENCE anchor — already present)
Section `## Boundary Invariants` item 1 in the ADR reads verbatim:
> "Every `obpi_lock_released` event in `.gzkit/ledger.jsonl` emitted on or
> after the OBPI-02 closeout cutover carries a valid `handoff_path` payload;
> the referenced handoff exists on disk, postdates its matching
> `obpi_lock_claimed` event, and satisfies the Sub-Invariant 2
> minimum-information rule."
No ADR edit needed for REQ-04-08.

## Files

### New files
- `src/gzkit/governance/trust_audits/lock_handoff_coupling.py`
- `tests/governance/test_lock_handoff_coupling_validator.py`

### Modified files
- `src/gzkit/governance/trust_audits/__init__.py`
- `src/gzkit/quality.py`
- `src/gzkit/commands/quality.py`
- `src/gzkit/cli/parser_maintenance.py`
- `src/gzkit/commands/validate_cmd.py`
- `docs/user/manpages/validate.md`
- `docs/user/manpages/check.md`
- `tests/governance/test_token_block_discipline.py`

## Prerequisite: OBPI-03 cutover confirmed
`obpi_receipt_emitted` for OBPI-0.0.41-03 is in the ledger at
`2026-06-11T23:15:18.983669+00:00`. The post-OBPI-02 cutover (OBPI-02
completion: `2026-06-07T11:07:35.082516+00:00`) is in the ledger. Validator
derives both via ledger replay, never hardcodes.

## Implementation Steps

### Step 1: Write tests RED (TDD — before any source changes)

Author `tests/governance/test_lock_handoff_coupling_validator.py` with all
six behavioral test methods (they will fail ImportError until Step 2):

```
TestLockHandoffCouplingValidator
  test_clean_ledger_passes            — REQ-0.0.41-04-01
  test_missing_handoff_path_fails     — REQ-0.0.41-04-02
  test_nonexistent_handoff_path_fails — REQ-0.0.41-04-03
  test_predated_handoff_fails         — REQ-0.0.41-04-04
  test_missing_minimum_info_field_fails — REQ-0.0.41-04-05 (4 sub-cases)
  test_pre_cutover_events_grandfathered — REQ-0.0.41-04-06
```

Each test uses a `TempDir` project root, writes synthetic ledger lines and
handoff fixture files, then calls `validate_lock_handoff_coupling(project_root)`
and asserts `ValidationError` presence/absence.

Confirm RED by running: `uv run -m unittest tests/governance/test_lock_handoff_coupling_validator -v`
Expected: ImportError or AttributeError (module does not exist yet).

Also add to `tests/governance/test_token_block_discipline.py`:

```
test_lock_handoff_coupling_in_default_check_pipeline  — REQ-0.0.41-04-07
```

Asserts `("Lock-handoff coupling", run_lock_handoff_coupling_audit)` appears
in the list returned by `_build_check_steps()`.

### Step 2: Implement the validator (GREEN phase)

Create `src/gzkit/governance/trust_audits/lock_handoff_coupling.py`.

**Key design points:**

1. **Cutover detection** — scan ledger for `obpi_receipt_emitted` event with
   `id` matching `OBPI-0.0.41-02-*`; its `ts` is the cutover. If absent, all
   events are grandfathered (validator returns no errors).

2. **Validator function signature:**
   ```python
   def validate_lock_handoff_coupling(
       project_root: Path,
   ) -> list[ValidationError]:
   ```
   Uses `gzkit.ledger.Ledger(project_root / ".gzkit" / "ledger.jsonl").read_all()`
   — canonical replay API only, no direct JSON parsing of `ledger.jsonl`.

3. **Event pairing** — build index of `obpi_lock_claimed` events keyed by
   `(event.id, event.extra["agent"])`. For each `obpi_lock_released` event:
   - `ts >= cutover_ts` → enforce; `ts < cutover_ts` → skip.
   - Find the latest claim before this release for the same `(obpi_id, agent)`.
   - Check `handoff_path` in `event.extra` → error REQ-04-02 if absent.
   - Resolve `project_root / handoff_path` → error REQ-04-03 if not on disk.
   - Parse handoff frontmatter `timestamp` vs claim `ts` → error REQ-04-04
     if `frontmatter.timestamp < claim.ts`.
   - Check four min-info fields in frontmatter/body → error REQ-04-05 per
     missing field: `last_lock_event_timestamp`, `last_commit_sha`, `branch`,
     and `## Decisions Made` section in body.
   - Every error surfaces event `ts`, `obpi_id`, and `agent` (REQ-04-02/05).

4. **Error type** — `type="lock_handoff_coupling"` (added to
   `_POLICY_BREACH_ERROR_TYPES` for exit-3 behavior).

5. **Shape** — mirrors `advisor_proof_binding.py`: `from __future__ import
   annotations`, stdlib only, all helpers private, single public function.

Confirm GREEN: `uv run -m unittest tests/governance/test_lock_handoff_coupling_validator -v`
All six methods pass.

### Step 3: Export from `trust_audits/__init__.py`

Add import:
```python
from gzkit.governance.trust_audits.lock_handoff_coupling import (
    validate_lock_handoff_coupling,
)
```
Add to `__all__`: `"validate_lock_handoff_coupling"`.

### Step 4: Add `run_lock_handoff_coupling_audit` to `quality.py`

Append after `run_task_envelope_coherence_audit`:
```python
def run_lock_handoff_coupling_audit(project_root: Path) -> QualityResult:
    """Run the lock-handoff coupling audit (ADR-0.0.41 / OBPI-04).

    Fails closed (exit 3) when any obpi_lock_released event in the ledger
    (post-OBPI-02 cutover) lacks a valid handoff_path, references a missing
    file, has a predated frontmatter timestamp, or missing min-info fields.
    Recovery: uv run gz validate --lock-handoff-coupling for diagnostics.
    """
    return run_command("uv run gz validate --lock-handoff-coupling", cwd=project_root)
```

### Step 5: Add to `_build_check_steps()` in `commands/quality.py`

Add to the import list from `gzkit.quality`:
```python
run_lock_handoff_coupling_audit,
```

Add to the returned list (before the final `return`):
```python
("Lock-handoff coupling", run_lock_handoff_coupling_audit),
```

Confirm `test_lock_handoff_coupling_in_default_check_pipeline` now passes.

### Step 6: Register `--lock-handoff-coupling` in `parser_maintenance.py`

Mirror the `--advisor-proof-binding` block (around line 590-596):
```python
p_validate.add_argument(
    "--lock-handoff-coupling",
    dest="check_lock_handoff_coupling",
    action="store_true",
    help="Validate every obpi_lock_released event carries a valid handoff_path (ADR-0.0.41).",
)
```

### Step 7: Wire `validate_cmd.py` at all five sites

Follow the exact `advisor_proof_binding` pattern:

1. **Function signature** (`validate` function, ~line 192):
   ```python
   check_lock_handoff_coupling: bool = False,
   ```

2. **`default_scopes` dict** (~line 269):
   ```python
   "lock_handoff_coupling": check_lock_handoff_coupling,
   ```

3. **Runner mapping dict** (~line 386):
   ```python
   "lock_handoff_coupling": lambda: trust_audits.validate_lock_handoff_coupling(project_root),
   ```

4. **`_POLICY_BREACH_ERROR_TYPES` frozenset** (~line 900):
   ```python
   "lock_handoff_coupling",
   ```

5. **Pass-through / outer caller** (~line 1340 region, `check_advisor_proof_binding=` chain):
   ```python
   check_lock_handoff_coupling=check_lock_handoff_coupling,
   ```

   Also add to the outer function's signature (~line 1165 region):
   ```python
   check_lock_handoff_coupling: bool = False,
   ```

   And pass-through dict (~line 1430 region):
   ```python
   "lock_handoff_coupling": check_lock_handoff_coupling,
   ```

### Step 8: Update documentation

**`docs/user/manpages/validate.md`** — add `--lock-handoff-coupling` entry after
`--advisor-proof-binding` with description, exit codes (0: clean, 3: policy breach),
and example.

**`docs/user/manpages/check.md`** — note "Lock-handoff coupling" as a new default step.

### Step 9: Add BDD scenarios

Add to `features/obpi_lock.feature` (or the existing file's relevant section):

```gherkin
Scenario: lock-handoff coupling validator passes on clean ledger
  Given I have a project root with no obpi_lock_released events
  When I run "gz validate --lock-handoff-coupling"
  Then the exit code is 0

Scenario: lock-handoff coupling validator fails on missing handoff_path
  Given a post-cutover obpi_lock_released event with no handoff_path
  When I run "gz validate --lock-handoff-coupling"
  Then the exit code is 3
  And the output names the failing event's obpi_id and agent
```

## Verification Commands

```bash
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --lock-handoff-coupling
uv run gz check --json
uv run gz cli audit
uv run gz validate --documents
```

## Notes

- `advisor_proof_binding` is the canonical reference shape throughout
- `opt_in_scopes` in `_resolve_scopes` (flag-activated in validate) + default
  in `_build_check_steps` (default in gz check) — same pattern as `closeout_proof`
- Min-info fields in frontmatter: `last_lock_event_timestamp`, `last_commit_sha`,
  `branch`; decision context detected by `## Decisions Made` section in body
- Cutover detection: first `obpi_receipt_emitted` event with `id` prefix
  `OBPI-0.0.41-02-`; if absent, all events grandfathered
