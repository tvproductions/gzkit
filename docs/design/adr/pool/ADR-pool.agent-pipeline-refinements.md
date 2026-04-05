# ADR-pool.agent-pipeline-refinements

- **Status:** Pool
- **Lane:** Lite
- **Date:** 2026-04-05
- **Origin:** GHI #35 triage (pre-1.0 residual gaps from SPEC-agent-capability-uplift)

## Intent

Bundle three small, pre-1.0 agent pipeline improvements that emerged from the SPEC-agent-capability-uplift triage. Each addresses a gap where the pipeline accepts informal or single-pass work that should be structured and validated.

## Target Scope

### 1. Decision Locking with Formal D-IDs (CAP-02)

Add a `## Decisions` section to the ADR authoring template with formally identified decisions (D-01, D-02, ...) and status tracking (locked / discretion / deferred). Update gz-adr-create skill to scaffold the section. Complements ADR-pool.spec-delta-markers.

### 2. Plan-Audit Adversarial Iteration (CAP-05)

Upgrade gz-plan-audit from single-pass to a bounded 3-iteration loop with dimension-specific fixes and blocker/warning classification. The skill already exists — this is a behavioral upgrade, not a new surface.

### 3. Spec Quality Validation (CAP-04)

Add `gz validate --requirements` flag to validate requirement format (REQ-ID presence, GIVEN/WHEN/THEN structure), completeness (all checklist items covered), and cross-artifact consistency (requirements referenced in briefs exist in parent ADR).

## Non-Goals

- No new CLI commands — all three are additions to existing commands/skills
- No schema changes to the ledger
- No changes to gate sequencing

## Dependencies

- **None blocking** — all three build on stable, validated foundations (ADR-0.12.0, ADR-0.21.0)

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. At least one of the three gaps becomes a recurring pain point in daily workflow.

## See Also

- [SPEC-agent-capability-uplift](../../briefs/SPEC-agent-capability-uplift.md) — CAP-02, CAP-04, CAP-05. These are the three pre-1.0 residual gaps from the 22-capability triage.
- [GHI #35](https://github.com/tvproductions/gzkit/issues/35) — Tracking issue with checklist for these three items.
