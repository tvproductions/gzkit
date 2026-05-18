# Implementation Plan: OBPI-0.0.36-03-validate-receipt-shape-scope

**OBPI:** OBPI-0.0.36-03-validate-receipt-shape-scope  
**Parent ADR:** ADR-0.0.36-universal-obpi-attestation  
**Lane:** Heavy  
**ADR cutoff date:** 2026-04-26  

## Context

Prerequisites confirmed complete:
- OBPI-0.0.36-01 (agents.md matrix collapse): ATTESTED COMPLETED
- OBPI-0.0.36-02 (runtime gate collapse): ATTESTED COMPLETED

### Path Corrections (Brief Drift — Discovered at Audit Time)

The brief lists several paths that do not match the codebase:

| Brief path | Actual path | Reason |
|---|---|---|
| `src/gzkit/governance/trust_audits.py` | `src/gzkit/governance/trust_audits/receipt_shape.py` | `trust_audits` is a package directory, not a file |
| `src/gzkit/commands/validate.py` | `src/gzkit/commands/validate_cmd.py` | actual filename |
| `src/gzkit/cli/parser_artifacts.py` (flag reg) | `src/gzkit/cli/parser_maintenance.py` | validate flags live in parser_maintenance |
| `src/gzkit/validate_pkg/__init__.py` | not applicable | package doesn't exist; trust_audits package is the target |

The waiver file `data/historical_self_close_waivers.json` does not yet exist (OBPI-0.0.36-04 pending). REQ-5 specifies warn-only for pre-cutoff receipts when the waiver file is absent; fail-closed only when it exists and a waiver entry is missing.

## Files to Create

- `src/gzkit/governance/trust_audits/receipt_shape.py` — core audit logic
- `tests/governance/test_validate_receipt_shape.py` — REQ-derived semantic tests
- `features/validate_receipt_shape.feature` — BDD scenarios @REQ-0.0.36-03-NN

## Files to Modify

- `src/gzkit/governance/trust_audits/__init__.py` — export `audit_receipt_shape`
- `src/gzkit/cli/parser_maintenance.py` — register `--receipt-shape` flag
- `src/gzkit/commands/validate_cmd.py` — add param, explicit_scope entry, runner lambda
- `src/gzkit/quality.py` — add `run_receipt_shape_audit`; wire into `_build_check_steps`
- `tests/commands/test_validate.py` — flag-wiring test
- `docs/user/manpages/gz-validate.md` — new scope, exit codes, cutoff semantics
- `docs/user/runbook.md` — receipt-shape integrity entry
- `docs/governance/governance_runbook.md` — receipt-shape integrity entry

## Steps

### Step 1: TDD RED — Write failing tests

Write `tests/governance/test_validate_receipt_shape.py` with failing assertions for each deprecated shape. Tests must run red before any implementation.

REQ-derived test cases:
- `test_post_cutoff_optional_attestation_requirement_fails` — REQ-2
- `test_post_cutoff_completed_without_attested_prefix_fails` — REQ-3
- `test_post_cutoff_agent_attestor_fails` — REQ-4
- `test_pre_cutoff_deprecated_shape_warns_when_no_waiver_file` — REQ-5 (no file)
- `test_pre_cutoff_deprecated_shape_passes_when_waivered` — REQ-5 (waiver present)
- `test_canonical_post_cutoff_shapes_pass` — negative: `attested_completed`, `required`, human attestor

### Step 2: Implement `src/gzkit/governance/trust_audits/receipt_shape.py`

Function: `audit_receipt_shape(project_root: Path) -> list[ValidationError]`

Logic:
1. Read ADR-0.0.36 frontmatter to extract `date:` as cutoff (never hard-code)
2. Locate and read `data/historical_self_close_waivers.json` (may not exist — REQ-5)
3. Scan `.gzkit/ledger.jsonl` for `obpi_receipt_emitted` events
4. For each receipt event, parse `ts` as `event_date`
5. If `event_date >= cutoff`:
   - `evidence.attestation_requirement == "optional"` → error (REQ-2)
   - `evidence.obpi_completion` present but not starting with `"attested_"` → error (REQ-3)
   - `evidence.attestor` matches `^agent:` (case-insensitive) → error (REQ-4)
6. If `event_date < cutoff` (pre-cutoff):
   - If waiver file absent → warn only (ValidationError type="warning")
   - If waiver file present → check waiver entries; error if not waivered

### Step 3: Export from `__init__.py`

Add `from gzkit.governance.trust_audits.receipt_shape import audit_receipt_shape` to `src/gzkit/governance/trust_audits/__init__.py`.

### Step 4: Register flag in `parser_maintenance.py`

```python
p_validate.add_argument(
    "--receipt-shape",
    dest="check_receipt_shape",
    action="store_true",
    help="Refuse post-cutoff receipts with deprecated shapes: attestation_requirement:optional, obpi_completion:completed (no attested_ prefix), attestor:^agent: (ADR-0.0.36)",
)
```

### Step 5: Wire dispatch in `validate_cmd.py`

1. Add `check_receipt_shape: bool = False` to `_collect_errors` signature
2. Add `"receipt_shape": check_receipt_shape` to `explicit_scopes` dict
3. Add runner: `"receipt_shape": lambda: trust_audits.audit_receipt_shape(project_root)` to `_explicit_scope_runners`
4. Update `validate_cmd` caller (top-level `validate` function) to pass the flag through

### Step 6: Wire into `gz check` in `quality.py`

1. Add `run_receipt_shape_audit(project_root: Path) -> QualityResult` calling `uv run gz validate --receipt-shape`
2. Add `("Receipt shape", run_receipt_shape_audit)` to `_build_check_steps()` return list

### Step 7: TDD GREEN — Run tests to confirm pass

```bash
uv run -m unittest tests.governance.test_validate_receipt_shape -v
```

### Step 8: Flag-wiring test in `tests/commands/test_validate.py`

Add test asserting `--receipt-shape` flag is registered and routes to `audit_receipt_shape`.

### Step 9: Manpage update — `docs/user/manpages/gz-validate.md`

Add `--receipt-shape` entry: scope description, exit codes (0=clean, 3=policy breach), cutoff-date semantics paragraph.

### Step 10: Runbook updates

- `docs/user/runbook.md`: add receipt-shape integrity entry in validate section
- `docs/governance/governance_runbook.md`: add entry

### Step 11: BDD feature file — `features/validate_receipt_shape.feature`

Scenarios tagged `@REQ-0.0.36-03-NN` for each deprecated shape acceptance criterion.

### Step 12: Quality gate verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run -m behave features/validate_receipt_shape.feature
uv run gz validate --receipt-shape
uv run gz validate --cli-alignment
```
