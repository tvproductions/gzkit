# decommission-tautological-tests

Re-runnable AST-based scanner for tautological test patterns in `tests/**`.
Identifies filesystem-shaped operations co-occurring with assertions, proposes
dispositions (convert / replace-with-ledger / fold-to-validator / keep-as-fixture),
and enforces a drift gate via `gz validate --tautological-test-audit` (ADR-0.0.59-04).

## Quick Start

```bash
# Check drift gate (should exit 0 on clean state)
uv run gz validate --tautological-test-audit

# Inspect what the scanner finds
uv run python -c "
from pathlib import Path
from gzkit.tautological_tests import scan_test_tree, propose_disposition
ops = scan_test_tree(Path('tests'))
print(f'{len(ops)} tautological operations found')
for op in ops[:5]:
    print(f'  {op.file_path}:{op.line_number} — {propose_disposition(op).value}')
"
```

## Lane

**heavy** — new validator scope, ledger event type, state files

## State Files

- `data/tautological_test_baseline.json` — baselined operation count
- `data/tautological_test_waivers.json` — per-file waivers with rationale keys
