---
id: OBPI-0.0.8-06-closeout-migration
parent: ADR-0.0.8-feature-toggle-system
item: 6
lane: Lite
status: Pending
---

# OBPI-0.0.8-06: Closeout Migration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.8-feature-toggle-system/ADR-0.0.8-feature-toggle-system.md`
- **Checklist Item:** #9 — "Closeout migration to FeatureDecisions"

**Status:** Pending

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

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item #9 referenced

### Gate 2: TDD

- [ ] Unit tests validate closeout blocks when product_proof_enforced=True and proof missing
- [ ] Unit tests validate closeout warns when product_proof_enforced=False and proof missing
- [ ] Unit tests validate closeout passes when proof present (regardless of flag state)
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

## Acceptance Criteria

- [ ] REQ-0.0.8-06-01: Given `ops.product_proof=true` and an OBPI without product proof, when `gz closeout` runs, then closeout is blocked with error message.
- [ ] REQ-0.0.8-06-02: Given `ops.product_proof=false` and an OBPI without product proof, when `gz closeout` runs, then a warning is emitted but closeout proceeds.
- [ ] REQ-0.0.8-06-03: Given any flag state and an OBPI with product proof present, when `gz closeout` runs, then closeout succeeds normally.
- [ ] REQ-0.0.8-06-04: Given a grep for `config.gate.*product_proof` in `commands/closeout.py`, when run, then no matches found (reference replaced).

## Verification Commands

```bash
# Migration-specific tests
uv run -m unittest tests.test_closeout_migration -v

# Verify config.gates reference removed from closeout
grep -n "config.gate" src/gzkit/commands/closeout.py
# Expected: no matches

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

- Files created/modified: (to be filled on completion)
- Validation commands run: (to be filled on completion)
- Date completed: (to be filled on completion)

### Key Proof

(to be filled on completion)

---

**Brief Status:** Pending
