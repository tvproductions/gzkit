# CHORE: decommission-tautological-tests — Decommission Tautological Tests

**Version:** 1.0.0
**Lane:** Heavy
**Slug:** `decommission-tautological-tests`

---

## Overview

Re-runnable chore that scans `tests/**` via AST for filesystem-shaped operations
co-occurring with assertions, proposes per-file dispositions (convert /
replace-with-ledger / fold-to-validator / keep-as-fixture), is operator-paced
per file or batch, and emits `chore_decommission_processed` ledger events per
processed item. Companion `gz validate --tautological-test-audit` drift gate
fail-closes on growth above baseline + waivers (ADR-0.0.59-04).

## Policy and Guardrails

- **Lane:** Heavy — new validator scope, new state files, new ledger event type
- **Timeout:** 900s
- **Baseline:** `data/tautological_test_baseline.json` (initial empty, add ops after first sweep)
- **Waivers:** `data/tautological_test_waivers.json` (rationale-key indirection)
- The waivers file is unconditionally excluded from the scan (self-exemption)
- First sweep wave (top-5 offenders) lands in OBPI-0.0.59-05

## Workflow

### 1. Scan the test tree

```bash
uv run python -c "
from pathlib import Path
from gzkit.tautological_tests import scan_test_tree, propose_disposition
ops = scan_test_tree(Path('tests'))
print(f'{len(ops)} tautological operations found')
for op in ops[:10]:
    print(f'  {op.file_path}:{op.line_number} — {op.operation_kind} in {op.function_name}')
    print(f'    disposition: {propose_disposition(op).value}')
"
```

### 2. Review and process files

For each file in the scan results, apply the proposed disposition:

- **convert** — rewrite the operation as a behavior test (inject the file state, assert on extracted value)
- **replace-with-ledger** — use `gz adr emit-receipt` or ledger queries instead of reading files
- **fold-to-validator** — delegate the structural check to `gz validate --<scope>` and assert exit code
- **keep-as-fixture** — no change needed (legitimate fixture pattern in setUp/tearDown)

### 3. Validate drift gate

```bash
uv run gz validate --tautological-test-audit
```

Should exit 0 on clean state. Exit 3 means current count exceeds baseline + waivers.

### 4. Update baseline after sweep

After each sweep wave, regenerate the baseline:

```bash
uv run python -c "
import json
from pathlib import Path
from datetime import datetime, timezone
from gzkit.tautological_tests import scan_test_tree
ops = scan_test_tree(Path('tests'))
baseline = {
    'operations': [op.model_dump(exclude={'context_hint'}) for op in ops],
    'generated_at': datetime.now(timezone.utc).isoformat(),
}
Path('data/tautological_test_baseline.json').write_text(json.dumps(baseline, indent=2) + '\n')
print(f'Baseline updated: {len(ops)} operations')
"
```

> **Why `exclude={'context_hint'}`:** `context_hint` carries source-file docstring fragments
> for human review during the scan. Persisting them in `data/tautological_test_baseline.json`
> caused sibling trust-audit tests (`tests/governance/test_attestation_fold.py` and
> `tests/governance/test_defect_fix_routing_fold.py`) to fail-close when test docstrings
> legitimately quoted retired rule paths — the baseline file would carry those quoted paths
> as a derived artifact and trip the "no inbound references to legacy paths" structural
> fence. Drift-gate logic compares `(file_path, line_number, operation_kind, function_name)`
> tuples; `context_hint` is informational only and not part of the drift comparison key.
> (Defect surfaced in OBPI-0.0.59-05; direct-fix landed post-completion.)

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run gz validate --tautological-test-audit` | 0 |
| exitCodeEquals | `uv run gz validate --chores-layout` | 0 |
| exitCodeEquals | `uv run -m unittest tests/governance/test_tautological_tests.py -q` | 0 |

## Evidence Commands

```bash
uv run gz validate --tautological-test-audit
uv run gz validate --chores-layout
```
