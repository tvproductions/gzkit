---
id: ADR-pool.student-mode
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: bmad
---

# ADR-pool.student-mode: Student Mode Configuration

## Status

Pool

## Date

2026-03-08

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Add a `mode: student` configuration option that reduces ADR ceremony to the essentials:
Title, Context, Decision, Status. No Feature Checklist, no OBPI decomposition, no lane
classification. Students graduate to `mode: lite` when ready. This lowers the barrier to
entry without removing the governance backbone.

---

## Target Scope

- New config value: `mode: student` in `.gzkit.yaml`
- Student-mode ADR template: Title, Context, Decision, Alternatives, Status
- Student-mode task template: Objective, Requirements, Acceptance Criteria, Verification
- `gz init --mode student` bootstraps with student defaults
- `gz plan` and `gz specify` use simplified templates when mode is student
- Gates in student mode: Gate 1 (ADR exists) + Gate 2 (tests pass) only
- Student mode skips: OBPI naming, lane classification, attestation ceremony

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No changes to existing Lite/Heavy lane mechanics.
- No auto-graduation from student to lite mode.

---

## Dependencies

- **Blocks on**: ADR-pool.release-hardening (student mode is part of release readiness)
- **Blocked by**: None

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Student-mode template variants are accepted.
3. Gate reduction scope (which gates to skip) is decided.

---

## Inspired By

[BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD) — scale-adaptive ceremony
that adjusts process weight to project size. A bug fix gets a lightweight story; a
rewrite gets full PRD + architecture + stories.

---

## Notes

- This is the single highest-impact improvement for classroom adoption.
- Student → Lite → Heavy is the graduation path.
- Must not break existing Lite/Heavy workflows — student mode is additive.
- Consider: should `gz init` prompt for mode interactively?
- The student guides in docs/examples/ were designed with this mode in mind.
