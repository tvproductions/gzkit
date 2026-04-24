# Plan: OBPI-0.25.0-02 Progress Pattern — Confirm Decision

## Context

OBPI-0.25.0-02 requires evaluating airlineops `core/progress.py` (383 lines) against gzkit's Rich progress usage to determine: Absorb, Confirm, or Exclude.

After thorough comparison, the decision is **Confirm** — gzkit's existing progress infrastructure is more integrated, more Pythonic, and already surpasses what airlineops offers.

## Comparison Summary

### gzkit (already has)

- `src/gzkit/cli/progress.py` (135 lines): `progress_spinner`, `progress_phase`, `progress_bar` — context-manager-based, mode-aware (quiet/json suppression), stderr-targeted
- `src/gzkit/cli/formatters.py` `ProgressContext` class: step-counted progress with TTY-aware Rich rendering, non-TTY fallback (`[step/total]` to stderr), quiet/json suppression
- Integrated with `OutputFormatter` for consistent CLI output mode handling

### airlineops (evaluated)

| Pattern | Assessment |
|---------|-----------|
| `build_progress_columns()` | Hardcoded column list; gzkit inlines equivalent columns per context |
| `ProgressManager` dataclass | Imperative start/stop facade; less Pythonic than gzkit's context managers |
| `progress_scope()` | Context manager with Windows Unicode safety; gzkit handles UTF-8 at runtime entrypoint |
| `make_batch_progress_callback()` | Callback pattern; less clean than context manager approach |
| `make_download_progress()` | Domain-specific (download operations); gzkit has no download use case |
| `sqlite_heartbeat()` | No-op placeholder with no implementation |
| `create_warehouse_progress()` | Warehouse-domain-specific; fails subtraction test |

### Why gzkit wins

1. **Mode integration**: gzkit progress respects quiet/json/human output modes via OutputFormatter — airlineops has no equivalent
2. **Context managers**: gzkit uses `with` blocks throughout — airlineops relies on imperative start/stop
3. **TTY fallback**: gzkit's `ProgressContext` has non-TTY fallback printing `[step/total]` — airlineops lacks this
4. **Stderr discipline**: gzkit routes all progress to stderr — airlineops mixed
5. **No domain leakage**: airlineops's warehouse, download, and SQLite helpers are domain-specific

## Implementation Steps

### Step 1: Update the OBPI brief with comparison and Confirm decision

File: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-02-progress-pattern.md`

- Add a `## Comparison` section with the analysis above
- Record `## Decision: Confirm` with rationale citing concrete capability differences
- Record Gate 4 BDD as `N/A` — no operator-visible behavior change (Confirm decision, no code changes)
- Author the Closing Argument section from delivered evidence
- Check all completion checklist items

### Step 2: Run verification

```bash
uv run gz test
uv run gz lint
uv run gz typecheck
```

No code changes expected — this is a Confirm decision. Tests must remain green.

## Files Modified

- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-02-progress-pattern.md` — brief completion with comparison and decision

## Verification

```bash
# Brief records the decision
rg -n 'Confirm' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-02-progress-pattern.md

# Tests remain green
uv run gz test

# Lint clean
uv run gz lint
```
