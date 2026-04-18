---
id: OBPI-0.0.8-05-cli-surface
parent: ADR-0.0.8-feature-toggle-system
item: 5
lane: Heavy
status: in_progress
---

# OBPI-0.0.8-05: CLI Surface

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.8-feature-toggle-system/ADR-0.0.8-feature-toggle-system.md`
- **Checklist Item:** #8 — "`gz flags` / `gz flags --stale` / `gz flag explain` CLI"

**Status:** Completed
**Date Completed:** 2026-03-30

## Objective

Implement the operator-facing CLI commands for flag inspection:
`gz flags` (list all flags with values and sources), `gz flags --stale`
(filter to stale flags only), and `gz flag explain <key>` (detailed single-flag
view with metadata, resolution source, and staleness status).

## Lane

**Heavy** — New CLI command group. Operator-facing contract per CLI Doctrine.

## Dependencies

- **Upstream:** OBPI-01 (models), OBPI-02 (FlagService for resolved values), OBPI-04 (diagnostics for stale detection and explain logic).
- **Downstream:** OBPI-08 (operator docs document these commands).
- **Parallel:** OBPI-06 (closeout migration — no dependency in either direction).

## Allowed Paths

- `src/gzkit/commands/flags.py` — Command implementations
- `src/gzkit/cli.py` — CLI registration for flags command group
- `tests/test_flag_commands.py` — CLI smoke tests

## Denied Paths

- `src/gzkit/flags/` — Read-only consumer of flag subpackage
- `src/gzkit/commands/check.py` — gz check integration belongs to OBPI-04
- `.gzkit/ledger.jsonl` — Never edit manually

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz flags` MUST display a table of all flags: key, category, default, current value, source, owner, days until review/removal.
1. REQUIREMENT: `gz flags --stale` MUST filter to flags past their review_by or remove_by dates.
1. REQUIREMENT: `gz flag explain <key>` MUST display full flag metadata, current resolved value with source attribution, staleness status, and linked ADR/issue.
1. REQUIREMENT: `gz flag explain <key>` for an unknown key MUST exit with code 1 and a clear error message.
1. REQUIREMENT: All commands MUST support `--json` for machine-readable output per CLI Doctrine.
1. REQUIREMENT: All commands MUST support `-h`/`--help` with examples per CLI Doctrine.
1. REQUIREMENT: Exit codes MUST follow the standard 4-code map: 0=success, 1=user error, 2=system error.
1. NEVER: Modify flag values from CLI commands — these are read-only inspection commands.
1. ALWAYS: Human-readable output uses Rich tables; `--json` outputs valid JSON to stdout.

> STOP-on-BLOCKERS: OBPI-01, OBPI-02, and OBPI-04 must be complete.

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item #8 referenced

### Gate 2: TDD

- [x] Smoke tests for `gz flags` (exits 0, produces table output)
- [x] Smoke tests for `gz flags --stale` (exits 0)
- [x] Smoke tests for `gz flag explain <known_key>` (exits 0, outputs metadata)
- [x] Smoke tests for `gz flag explain <unknown_key>` (exits 1)
- [x] Smoke tests for `gz flags --json` (valid JSON output)
- [x] Tests pass: `uv run gz test`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [x] Help text includes examples for all commands
- [x] Manpage content prepared (delivered in OBPI-08)

### Gate 5: Human (Heavy)

- [x] Human attestation recorded

## Acceptance Criteria

- [x] REQ-0.0.8-05-01: Given `gz flags`, when run, then exits 0 and displays a table with all registered flags.
- [x] REQ-0.0.8-05-02: Given `gz flags --stale` with no stale flags, when run, then exits 0 and displays "No stale flags."
- [x] REQ-0.0.8-05-03: Given `gz flag explain ops.product_proof`, when run, then exits 0 and displays full metadata including current value and source.
- [x] REQ-0.0.8-05-04: Given `gz flag explain nonexistent.key`, when run, then exits 1 with error message.
- [x] REQ-0.0.8-05-05: Given `gz flags --json`, when run, then outputs valid JSON array to stdout.

## Verification Commands

```bash
# CLI smoke tests
PYTHONUTF8=1 uv run gz flags
PYTHONUTF8=1 uv run gz flags --stale
PYTHONUTF8=1 uv run gz flag explain ops.product_proof
PYTHONUTF8=1 uv run gz flags --json | python -m json.tool

# Error case
PYTHONUTF8=1 uv run gz flag explain nonexistent.key; echo "Exit: $?"
# Expected: exit code 1

# Unit tests
uv run -m unittest tests.test_flag_commands -v

# Full suite regression
uv run gz test

# Code quality
uv run gz lint
uv run gz typecheck
```

## Closing Argument

OBPI-0.0.8-05 delivers the operator-facing CLI surface for the feature flag system. Before this work, operators had no way to inspect flag state from the command line — flags existed only in `data/flags.json` and could be queried only programmatically. Now `gz flags` provides a Rich table of all registered flags with resolved values, precedence sources, and deadline countdowns; `gz flags --stale` filters to overdue flags; and `gz flag explain <key>` gives full single-flag metadata including linked ADR/issue and staleness status. All commands support `--json` for machine-readable output per CLI Doctrine. The implementation is read-only — it never modifies flag values, only inspects them.

### Implementation Summary

- Files created: `src/gzkit/commands/flags.py`, `tests/test_flag_commands.py`
- Files modified: `src/gzkit/cli/parser_maintenance.py`, `src/gzkit/commands/common.py`, `config/doc-coverage.json`
- Tests: 11 passing (covering all 5 REQs)
- Lint: clean
- Typecheck: clean
- Full suite: 2157 tests pass

### Key Proof

```
$ gz flag explain ops.product_proof

ops.product_proof
  Category:      ops
  Description:   When enabled, the product proof check blocks closeout...
  Owner:         governance
  Default:       True
  Current value: True
  Source:        registry
  Review by:     2026-06-29 (91d)
  Linked ADR:    ADR-0.23.0
  Linked issue:  GHI-49
```

## Human Attestation

- **Attestor:** jeff
- **Date:** 2026-03-30
- **Attestation:** attest completed

---

**Brief Status:** Completed
