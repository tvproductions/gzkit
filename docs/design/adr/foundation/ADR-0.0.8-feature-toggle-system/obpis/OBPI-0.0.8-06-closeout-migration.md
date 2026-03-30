---
id: OBPI-0.0.8-06-closeout-migration
parent: ADR-0.0.8-feature-toggle-system
item: 6
lane: Lite
status: Completed
---

# OBPI-0.0.8-06: Closeout Migration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.8-feature-toggle-system/ADR-0.0.8-feature-toggle-system.md`
- **Checklist Item:** #9 — "Closeout migration to FeatureDecisions"

**Status:** Completed

## Objective

Migrate the closeout product proof check from the `config.gates` prototype
to `FeatureDecisions.product_proof_enforced()`. This is the GHI #49 use case
that motivated the entire ADR. After this OBPI, closeout enforcement level
is controlled by the flag system, not the ad-hoc gates dict.

## Lane

**Lite** — Internal behavior routing. The closeout command's external contract
(arguments, output format, exit codes) does not change. Only the internal
source of the enforcement decision changes.

## Dependencies

- **Upstream:** OBPI-03 (FeatureDecisions with `product_proof_enforced()` method).
- **Downstream:** OBPI-07 (config.gates removal — depends on this migration completing first).
- **Parallel:** OBPI-05 (CLI surface — no dependency in either direction).

## Allowed Paths

- `src/gzkit/commands/closeout.py` — Replace config.gates lookup with decisions call
- `tests/test_closeout_migration.py` — Migration-specific tests

## Denied Paths

- `src/gzkit/flags/` — Read-only consumer; do not modify flag infrastructure
- `src/gzkit/core/config.py` — Do not remove config.gates yet (OBPI-07)
- `.gzkit/ledger.jsonl` — Never edit manually

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Closeout product proof enforcement MUST be read from `decisions.product_proof_enforced()`, not `config.gate("product_proof")`.
1. REQUIREMENT: Behavioral parity: with `ops.product_proof=true`, closeout MUST block on missing product proof (same as current `enforce` level). With `ops.product_proof=false`, closeout MUST warn but not block (same as current `advisory` level).
1. REQUIREMENT: During transition, if both `config.gates` and flag service are available, the flag service value takes precedence.
1. REQUIREMENT: No change to closeout command arguments, output format, or exit codes.
1. NEVER: Remove config.gates in this OBPI — that is OBPI-07.
1. ALWAYS: Test both flag ON and flag OFF paths to confirm behavioral parity.

> STOP-on-BLOCKERS: OBPI-03 must be complete (FeatureDecisions with product_proof_enforced available).

## Quality Gates (Lite)

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item #9 referenced

### Gate 2: TDD

- [x] Unit tests validate closeout blocks when product_proof_enforced=True and proof missing
- [x] Unit tests validate closeout warns when product_proof_enforced=False and proof missing
- [x] Unit tests validate closeout passes when proof present (regardless of flag state)
- [x] Tests pass: `uv run gz test`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

## Acceptance Criteria

- [x] REQ-0.0.8-06-01: Given `ops.product_proof=true` and an OBPI without product proof, when `gz closeout` runs, then closeout is blocked with error message.
- [x] REQ-0.0.8-06-02: Given `ops.product_proof=false` and an OBPI without product proof, when `gz closeout` runs, then a warning is emitted but closeout proceeds.
- [x] REQ-0.0.8-06-03: Given any flag state and an OBPI with product proof present, when `gz closeout` runs, then closeout succeeds normally.
- [x] REQ-0.0.8-06-04: Given a grep for `config.gate.*product_proof` in `commands/closeout.py`, when run, then primary path uses decisions.product_proof_enforced() (config.gate only in transition fallback).

## Verification Commands

```bash
# Migration-specific tests
uv run -m unittest tests.test_closeout_migration -v

# Verify config.gates reference removed from closeout
grep -n "config.gate" src/gzkit/commands/closeout.py
# Expected: only in REQ-03 transition fallback

# Verify decisions reference present
grep -n "product_proof_enforced" src/gzkit/commands/closeout.py
# Expected: at least one match

# Full suite regression
uv run gz test

# Code quality
uv run gz lint
uv run gz typecheck
```

## Evidence

### Implementation Summary

- Files created: `tests/test_closeout_migration.py` (5 tests covering all 4 REQs)
- Files modified: `src/gzkit/commands/closeout.py` (import get_decisions/FlagError, replace config.gate with decisions.product_proof_enforced, add REQ-03 transition fallback)
- Validation commands run: `uv run gz lint`, `uv run gz typecheck`, `uv run gz test` (2162 pass)
- Date completed: 2026-03-30

### Key Proof

```bash
$ grep -n "product_proof_enforced" src/gzkit/commands/closeout.py
564:        enforce_proof = decisions.product_proof_enforced()

$ uv run -m unittest tests.test_closeout_migration -v
test_blocks_when_enforced_and_missing ... ok
test_warns_when_not_enforced_and_missing ... ok
test_succeeds_with_proof_flag_true ... ok
test_succeeds_with_proof_flag_false ... ok
test_primary_path_uses_decisions_not_config_gate ... ok
Ran 5 tests in 0.339s — OK
```

## Human Attestation

- Attestor: jeff
- Attestation: attest completed
- Date: 2026-03-30

---

**Brief Status:** Completed
**Date Completed:** 2026-03-30
