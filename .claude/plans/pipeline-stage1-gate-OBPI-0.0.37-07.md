# Plan: OBPI-0.0.37-07 Pipeline Stage 1 Fail-Close Gate

**OBPI**: OBPI-0.0.37-07-pipeline-stage1-gate
**Parent ADR**: ADR-0.0.37-constitutional-invariant-composition
**Lane**: Heavy
**Brief**: `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-07-pipeline-stage1-gate.md`

## Context

Extend `gz obpi pipeline` Stage 1 to refuse Stage 2 entry unless the active OBPI
has a fresh `brief_reconciled` ledger receipt. "Fresh" means the receipt timestamp
is newer than the most recent mtime of any file in the brief's Allowed Paths domain.

Prerequisite met: OBPI-06 is ATTESTED COMPLETED — `brief_reconciled` event type is
registered in `gzkit/events.py`, `gzkit/ledger_events.py`, and emitted by
`gz brief reconcile`.

### Discovery Findings

**Finding 1 (allowlist gap): `obpi_cmd.py` is a required coupled surface.**
The brief lists `pipeline_runtime.py` as the main modification target. However,
Stage 1 actually executes in `obpi_pipeline_cmd` in `obpi_cmd.py`. Without modifying
`obpi_cmd.py` to import and call the new gate function, the function is dead code.
Per AGENTS.md § Craftsmanship Maxim 1a (coupled-surface coherence), `obpi_cmd.py`
must be modified in the same patch. This is not scope creep — it's the minimal
wiring that makes the gate actually fire.
Resolution: plan includes the `obpi_cmd.py` wiring. This is a brief allowlist defect;
the next `gz brief reconcile` run should add `obpi_cmd.py`.

**Finding 2 (false positives): CREATE paths flagged as missing.**
`reconcile_freshness.py` and `test_reconcile_freshness.py` don't exist yet — expected
for CREATE paths. The `gz plan audit` CLI reports them as gaps, which is a
pre-existence false positive. No action needed.

**Finding 3 (advisory): 67 sibling-ADR scope collisions.**
All advisory. `docs/user/runbook.md` and `src/gzkit/pipeline_runtime.py` appear in
many ADR allowlists — this is normal for shared surfaces. No blocking action.

### Destination-in-mind disclosure (plan Step 6a)
Before this plan, I had already decided: add a `check_reconcile_receipt_gate`
function to `pipeline_runtime.py` that reads the ledger JSONL directly (following
the `audit_reconcile_freshness` pattern from `governance/trust_audits/reconcile.py`)
and calls a pure `is_receipt_fresh` helper in a new `reconcile_freshness.py` module.

### Rejected alternatives
1. **Extend `validate_brief_for_pipeline`** — rejected: that function is dead in
   production (not called from `obpi_cmd.py`), so extending it would not fire the gate.
2. **Use `Ledger.query()` class** — rejected: `pipeline_runtime.py` has no `Ledger`
   import; reading JSONL directly avoids a new import and follows the existing
   `audit_reconcile_freshness` precedent.
3. **Add gate to `pipeline_concurrency_blockers`** — rejected: that function is
   conceptually about multi-agent concurrency, not reconcile-receipt freshness.
4. **Gate as argparse hook** — rejected: not in brief scope; would add new CLI surface.

## Files

**CREATE:**
- `src/gzkit/governance/reconcile_freshness.py` **CREATE** — pure `is_receipt_fresh` helper
- `tests/governance/test_reconcile_freshness.py` **CREATE** — unit tests for `is_receipt_fresh`

**MODIFY:**
- `src/gzkit/pipeline_runtime.py` — add `check_reconcile_receipt_gate` + `__all__` entry
- `tests/test_pipeline_runtime.py` — add Stage 1 gate tests (4 cases)
- `features/brief_reconcile.feature` — add `@REQ-0.0.37-07-*` BDD scenarios
- `docs/user/runbook.md` — add Stage 1 block recovery entry
- OBPI brief (this file) — always modified as part of brief

**COUPLED SURFACE (not in brief allowlist but required):**
- `src/gzkit/commands/obpi_cmd.py` — import + call `check_reconcile_receipt_gate`

## Steps

### Step 1: Create `src/gzkit/governance/reconcile_freshness.py`

Pure helper with no gzkit imports:

```python
"""Reconcile-receipt freshness helper (OBPI-0.0.37-07).

Pure function: no ledger reads, no side effects.
"""
from __future__ import annotations
from datetime import UTC, datetime
from pathlib import Path


def is_receipt_fresh(
    receipt_ts: datetime,
    allowed_paths: list[str],
    project_root: Path,
) -> bool:
    """Return True when receipt_ts > max(mtime(p)) for all allowed_paths.

    Missing path returns False (forces re-reconcile).
    Expands glob patterns via Path.glob().
    """
    mtimes: list[float] = []
    for pattern in allowed_paths:
        direct = project_root / pattern
        if direct.exists():
            mtimes.append(direct.stat().st_mtime)
        else:
            matches = list(project_root.glob(pattern))
            if not matches:
                return False  # missing path → stale
            for match in matches:
                mtimes.append(match.stat().st_mtime)
    if not mtimes:
        return False
    max_mtime = datetime.fromtimestamp(max(mtimes), tz=UTC)
    return receipt_ts > max_mtime
```

### Step 2: Add `check_reconcile_receipt_gate` to `pipeline_runtime.py`

Add at the end of `pipeline_runtime.py` (before `__all__`), plus add exports.

New private helper `_extract_brief_allowlist(brief_path)` — extracts allowed paths
from a brief using `parse_brief` for BriefStructure, or inline regex for legacy briefs.

New public function `check_reconcile_receipt_gate(obpi_id, brief_path, project_root)`:
- Reads `.gzkit/ledger.jsonl` line by line (no Ledger class needed)
- Finds latest `brief_reconciled` event whose `brief_id == obpi_id`
- If none: returns blocker "Stage 2 entry blocked: no `brief_reconciled` receipt..."
- Calls `is_receipt_fresh(receipt_ts, allowed_paths, project_root)`
- If stale: returns blocker naming the drifted path
- If fresh but `has_drift=True`: returns blocker naming drifted dimensions
- If pass: returns `[]`

For the "drifted path" name in the stale case, a private `_find_drifted_path` scans
the allowed paths and returns the first one newer than receipt_ts (or "(missing)").

Add `"check_reconcile_receipt_gate"` to `__all__`.

### Step 3: Wire gate into `src/gzkit/commands/obpi_cmd.py` (coupled surface)

In `obpi_pipeline_cmd`, after the concurrency/receipt check at line ~431,
before `write_pipeline_markers`:

```python
from gzkit.pipeline_runtime import (  # add to existing import
    check_reconcile_receipt_gate,
    ...
)

# In obpi_pipeline_cmd, after "if blockers: raise SystemExit(1)":
reconcile_blockers = check_reconcile_receipt_gate(obpi_id, obpi_file, project_root)
if reconcile_blockers:
    _print_pipeline_blockers(obpi_id, reconcile_blockers)
    raise SystemExit(3)
```

Exit code 3 (Policy Breach per AGENTS.md § CLI Contract).

### Step 4: Write unit tests

**`tests/governance/test_reconcile_freshness.py`** (CREATE):
- `test_receipt_fresh_when_ts_newer` — receipt_ts > max mtime → True
- `test_receipt_stale_when_ts_older` — receipt_ts < max mtime → False
- `test_missing_path_returns_false` — path doesn't exist → False
- `test_empty_allowed_paths_returns_false` — no paths → False

Each test: create a TempDirectory, write a file, set mtime via `os.utime`,
assert the return value.

**`tests/test_pipeline_runtime.py`** additions:
- `test_gate_blocks_when_no_receipt` — empty ledger → blocker
- `test_gate_blocks_when_receipt_stale` — receipt older than file mtime → blocker
- `test_gate_blocks_when_receipt_fresh_but_drifted` — fresh + has_drift=True → blocker
- `test_gate_passes_when_receipt_fresh_and_clean` — fresh + has_drift=False → []

Each test: create a TempDirectory with a ledger JSONL, write a brief file,
call `check_reconcile_receipt_gate`, assert the result.

### Step 5: Add BDD scenarios to `features/brief_reconcile.feature`

Add 4 scenarios tagged `@REQ-0.0.37-07-02`, `@REQ-0.0.37-07-03`,
`@REQ-0.0.37-07-04`, `@REQ-0.0.37-07-05`:
- "Stage 1 blocks when no brief_reconciled receipt exists"
- "Stage 1 blocks when brief_reconciled receipt is stale"
- "Stage 1 blocks when receipt has_drift=True"
- "Stage 1 passes when receipt is fresh and drift-free"

BDD steps will exercise `check_reconcile_receipt_gate` directly.

### Step 6: Add runbook entry to `docs/user/runbook.md`

Under the pipeline section, add a "When Stage 1 blocks" entry:
> **When Stage 1 blocks: no or stale brief_reconciled receipt**
> Run `gz brief reconcile OBPI-ID` to refresh the receipt, then retry the pipeline.

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_reconcile_freshness tests.test_pipeline_runtime -v
uv run mkdocs build --strict
uv run -m behave features/brief_reconcile.feature --tags=REQ-0.0.37-07
```

## Notes

- REQ-07-06 requires additive check (existing Stage 1 behaviors preserved).
  The gate fires AFTER concurrency blocker and plan-receipt checks.
- Exit code 3 (Policy Breach) not exit code 1 (User/Config Error) per REQ-02/03/04.
- The `obpi_cmd.py` coupling is the smallest possible: one import addition,
  three lines of code, zero changes to existing logic.
- `reconcile_freshness.py` has no gzkit imports — intentionally pure to enable
  test isolation without gzkit initialization.
