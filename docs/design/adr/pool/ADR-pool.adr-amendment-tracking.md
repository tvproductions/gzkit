---
id: ADR-pool.adr-amendment-tracking
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: openspec
---

# ADR-pool.adr-amendment-tracking: ADR Amendment Tracking

## Status

Pool

## Date

2026-03-08

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Add `gz amend <adr-id>` to record mid-flight design changes. Currently, if an ADR's
decision changes during implementation, the file is edited but there's no audit trail
of what changed or why. This command records a `decision_amended` ledger event with
a diff summary, preserving gate integrity while acknowledging that designs evolve.

---

## Target Scope

- New CLI command: `gz amend <adr-id> --reason "..."`
- New ledger event type: `decision_amended` with fields: id, reason, diff_summary, ts
- ADR stays at its current gate — amendment doesn't reset progress
- Optional: append an `## Amendments` section to the ADR file with timestamped entries

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No automatic gate rollback on amendment.
- No changes to existing ADR lifecycle states.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Amendment event schema is accepted.
3. Gate-reset policy (no reset vs. selective reset) is decided.

---

## Inspired By

[OpenSpec](https://github.com/Fission-AI/OpenSpec) — fluid artifact updates philosophy:
"update any artifact at any time" without restarting the workflow.

---

## Notes

- OpenSpec allows free iteration; gzkit's gates resist it. This is the compromise.
- Amendments should be rare — if they're frequent, the ADR was premature.
- Consider: should amendments require re-verification of passed gates?
