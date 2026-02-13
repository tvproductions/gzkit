---
id: ADR-pool.evaluation-infrastructure
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: ADR-pool.ai-runtime-foundations
---

# ADR-pool.evaluation-infrastructure

## Status

Proposed

## Date

2026-02-11

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) -- Phase 8: Evaluation Infrastructure

---

## Intent

Create application-specific evaluation infrastructure so AI workflow quality is measured with deterministic evidence before and after model/prompt changes.

---

## Target Scope

- Define reference datasets for top-level workflows (golden paths and edge cases).
- Add offline eval harnesses as first-class quality checks.
- Define release gates based on eval deltas for AI-sensitive surfaces.
- Add regression detection for model/prompt changes before high-agency rollout.

---

## Dependencies

- **Blocks on**: ADR-pool.ai-runtime-foundations
- **Blocked by**: ADR-pool.ai-runtime-foundations

---

## Notes

- This phase treats evals as tests for non-deterministic behavior, not as optional analytics.
- Dataset curation and rubric versioning should be traceable in governance artifacts.
