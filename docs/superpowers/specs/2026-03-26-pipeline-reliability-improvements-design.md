# Pipeline Reliability Improvements

**Date:** 2026-03-26
**Status:** Draft
**Scope:** Three targeted improvements to reduce agent friction and pipeline deadlocks

## Context

Analysis of 258 Claude Code sessions (2,883 messages, 2026-02-23 to 2026-03-25) identified
three high-impact improvement areas:

1. Agent repeatedly splits import additions from their usages, causing the post-edit ruff
   hook to strip imports before they're referenced.
2. Stale pipeline artifacts (markers, receipts, locks) create deadlocks that block
   implementation sessions.
3. Pipeline Stage 3 verification only runs brief-specific commands — if a brief omits
   baseline checks (lint, typecheck, test), they don't run.

## Improvement 1: Atomic Import Rule (AGENTS.md)

**Change:** Add behavioral rule to `agents.local.md`.

**Rule text:**

> When adding imports in an Edit call, always include the code that uses them in the same
> edit. The post-edit ruff hook removes unused imports immediately — splitting import
> addition and usage across separate edits causes the import to be deleted before it's
> referenced.

**Rationale:** The post-edit-ruff hook (`post-edit-ruff.py`) already runs
`ruff check --fix` after every Python edit. It correctly removes unused imports. The
friction occurs when the agent adds an import in one edit and its call site in a subsequent
edit — ruff strips the import between edits. This is an agent behavior problem, not a hook
problem.

**Files changed:** `agents.local.md` only (propagates to AGENTS.md via control-surface
sync).

**No code changes. No hook changes.**

## Improvement 2: `gz preflight` CLI Command

**Change:** New CLI command to detect and clean stale pipeline artifacts.

### Command Signature

```
gz preflight [--apply] [--json]
```

### Artifact Scan

| Artifact | Location | Stale Condition |
|---|---|---|
| Pipeline markers | `.claude/plans/.pipeline-active-*.json` | `updated_at` > 4 hours old, or unreadable |
| Plan-audit receipts | `.claude/plans/.plan-audit-receipt-*.json` | No matching plan file, or timestamp < plan mtime |
| OBPI locks | `.gzkit/locks/obpi/*.lock.json` | `claimed_at` + `ttl_minutes` exceeded |

### Behavior

- **Default (dry-run):** Reports findings as a human-readable table. Exit 1 if issues found,
  exit 0 if clean.
- **`--apply`:** Removes stale markers, orphan receipts, and expired locks. Prints what was
  removed. Exit 0 on success.
- **`--json`:** Structured output to stdout.

### Example Output

```
Preflight scan:
  Stale markers:   1  (.pipeline-active-OBPI-0.1.17-08.json, 6.2h old)
  Orphan receipts: 1  (.plan-audit-receipt-OBPI-0.1.16-38.json, no plan file)
  Expired locks:   0

Run with --apply to clean up.
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Clean (no issues) or cleaned (`--apply`) |
| 1 | Issues found (dry-run only) |
| 2 | System/IO error |

### Implementation

**New file:** `src/gzkit/commands/preflight.py`

**Registration:** Added to CLI group in `src/gzkit/commands/__init__.py`.

**Reuses existing runtime helpers:**
- `find_stale_pipeline_markers()` / `clear_stale_pipeline_markers()` from
  `pipeline_runtime.py`
- `load_pipeline_json()` for receipt and lock file parsing

**New logic:**
- Orphan receipt detection: receipt file's `obpi_id` field has no corresponding
  `.pipeline-active-{obpi_id}.json` marker AND no plan file in `.claude/plans/` references
  that OBPI ID. Also flagged: receipt mtime < plan file mtime (timestamp inversion).
- Lock expiry: parse `claimed_at` (ISO 8601) + `ttl_minutes` (default 120), flag if
  sum < now.

### Scope Boundary

Does NOT touch OBPI audit ledger entries or brief status. Those are governance artifacts
that require the full audit/attest pipeline.

## Improvement 3: Pipeline Stage 3 Baseline Checks

**Change:** Prepend mandatory baseline verification commands in
`_pipeline_verification_commands()`.

### Baseline Commands

```python
BASELINE_VERIFICATION = [
    "uv run gz lint",
    "uv run gz typecheck",
    "uv run gz test",
]
```

### Modified Function

**File:** `src/gzkit/commands/obpi_cmd.py`, function `_pipeline_verification_commands()`
(line 139).

Before: commands are sourced exclusively from the OBPI brief's `## Verification` section.

After: baseline commands are prepended before brief-specific commands. The existing
deduplication logic (lines 153-159) prevents double-runs when a brief includes any baseline
command.

Heavy-lane extras (`mkdocs build --strict`, `behave features/`) remain appended after
brief-specific commands, unchanged.

### Effect

Every OBPI pipeline run — regardless of brief content — executes lint, typecheck, and test.
CLI verification can never be skipped.

### Test Coverage

Unit test for `_pipeline_verification_commands()` asserting:
- Baseline commands appear first when brief is empty
- Baseline commands appear first when brief has custom commands
- Baseline commands are not duplicated when brief includes them
- Heavy-lane extras still append after brief-specific commands

## Implementation Order

1. **Atomic import rule** — `agents.local.md` change (no code, immediate effect)
2. **Baseline checks** — Small code change in `obpi_cmd.py` + unit test
3. **`gz preflight`** — New command module + registration + tests

## Lane Assessment

- Improvement 1: No code — not lane-gated
- Improvement 2: New CLI subcommand — **Heavy lane** per CLI doctrine
- Improvement 3: Existing function modification — **Lite lane** (additive behavior, no
  contract change)
