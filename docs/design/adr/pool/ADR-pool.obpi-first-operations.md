---
id: ADR-pool.obpi-first-operations
status: Superseded
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: ADR-0.3.0
promoted_to: ADR-0.7.0-obpi-first-operations
---

# ADR-pool.obpi-first-operations: OBPI-First Operations
> Promoted to `ADR-0.7.0-obpi-first-operations` on 2026-02-21. This pool file is retained as historical intake context.


## Status

Proposed

## Date

2026-02-17

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) -- Governance parity and execution model correction

---

## Intent

Correct gzkit's operating model so OBPI is the primary unit of execution and completion, with ADR lifecycle used as roll-up governance state.

This aligns with learned AirlineOps practice: incremental value is delivered and evidenced per OBPI, not deferred to ADR-end gate batches.

---

## Target Scope

- Reframe operator workflow and runbook around an OBPI increment loop.
- Define ADR closeout as a separate downstream loop after OBPI batch completion.
- Require OBPI evidence quality as the completion anchor for progress reporting.
- Align docs, command references, and governance language with OBPI-first semantics.
- Capture and enforce AirlineOps-derived execution heuristics for incremental work.

---

## Non-Goals

- No removal of ADR-level attestation/audit authority.
- No change to canonical gate definitions.
- No pool OBPIs before this entry is promoted.

---

## Dependencies

- **Blocks on**: ADR-0.3.0 (canon reconciliation baseline)
- **Blocked by**: ADR-0.3.0

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human confirms OBPI-first doctrine as required project policy.
2. Current ADR-first operational wording is identified and queued for correction.
3. Acceptance criteria for OBPI-level evidence quality are approved.

---

## Notes

- Immediate correction starts in `docs/user/runbook.md` and related workflow pages.
- This pool entry is doctrine-level; concrete command/ledger changes are tracked separately.
