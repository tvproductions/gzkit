---
id: ADR-pool.spec-delta-markers
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: openspec
---

# ADR-pool.spec-delta-markers: Spec Delta Markers in ADR Template

## Status

Pool

## Date

2026-03-08

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Add structured ADDED/MODIFIED/REMOVED markers to the ADR template's Feature Checklist
or a new `## Changes` section. Currently the checklist is binary (done/not done) and
doesn't capture what changed about the system in a reviewable format. Delta markers
make ADR reviews clearer and align with spec-driven development conventions.

---

## Target Scope

- Add `## Changes` section to the ADR template with structured markers:
  - `ADDED: <description>` — new capability introduced
  - `MODIFIED: <description>` — existing behavior changed
  - `REMOVED: <description>` — capability or contract removed
- Update `gz plan` to include the section in generated ADRs
- Optional: `gz diff <adr-id>` to summarize changes in terminal output

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No GIVEN/WHEN/THEN scenario embedding (that's BDD, already Gate 4).
- No automated delta detection from code diffs.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Delta marker format is accepted.
3. Template change scope (ADR only vs. ADR + OBPI) is decided.

---

## Inspired By

[OpenSpec](https://github.com/Fission-AI/OpenSpec) — spec deltas with ADDED/MODIFIED/REMOVED
markers and GIVEN/WHEN/THEN scenarios for testable specifications.

---

## Notes

- Low effort, high clarity improvement — template-only change.
- Delta markers are most valuable for Heavy lane ADRs with external contract changes.
- Consider: should delta markers be required or optional in the template?
