# ADR-pool.adr-amendment-tracking: ADR Amendment Tracking

## Status

Proposed

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

- New CLI command: `gz amend <adr-id> --reason "..." `
- New ledger event type: `decision_amended` with fields: id, reason, diff_summary, ts
- ADR stays at its current gate — amendment doesn't reset progress
- Optional: append an `## Amendments` section to the ADR file with timestamped entries

---

## Inspired By

[OpenSpec](https://github.com/Fission-AI/OpenSpec) — fluid artifact updates philosophy:
"update any artifact at any time" without restarting the workflow.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None

---

## Notes

- OpenSpec allows free iteration; gzkit's gates resist it. This is the compromise.
- Amendments should be rare — if they're frequent, the ADR was premature
- Consider: should amendments require re-verification of passed gates?
