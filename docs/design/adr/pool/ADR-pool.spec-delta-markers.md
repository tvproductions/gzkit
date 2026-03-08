# ADR-pool.spec-delta-markers: Spec Delta Markers in ADR Template

## Status

Proposed

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

## Inspired By

[OpenSpec](https://github.com/Fission-AI/OpenSpec) — spec deltas with ADDED/MODIFIED/REMOVED
markers and GIVEN/WHEN/THEN scenarios for testable specifications.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None

---

## Notes

- Low effort, high clarity improvement — template-only change
- GIVEN/WHEN/THEN is out of scope here (that's BDD, already Gate 4)
- Delta markers are most valuable for Heavy lane ADRs with external contract changes
