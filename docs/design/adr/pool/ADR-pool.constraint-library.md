---
id: ADR-pool.constraint-library
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
---

# ADR-pool.constraint-library: Rejection-Derived Constraint Library

## Status

Pool

## Date

2026-03-10

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Capture human rejection events as durable, queryable constraints instead of
letting them evaporate in chats, edits, or one-off review comments. gzkit
should treat "this output is wrong, and here is why" as a first-class knowledge
creation event that can be stored, scoped, reused, and eventually enforced.

---

## Target Scope

- Define the canonical object model for:
  - rejection events,
  - derived constraints,
  - provenance links back to the rejected output/context,
  - lifecycle states such as draft, approved, enforced, deprecated, and superseded.
- Separate deterministic rules from advisory heuristics so constraint reuse does
  not blur hard business logic with softer taste overlays.
- Define team/project/task scoping and inheritance rules for constraint
  application.
- Require examples or before/after pairs so constraints are teachable to both
  humans and agents.
- Keep the system ledger-first and auditable, with append-only event lineage for
  constraint creation and amendment.

## Non-Goals

- No standalone dashboard-first workflow.
- No MCP server or chat-tool integration in the initial pool definition.
- No assumption that every rejection becomes a fail-closed rule.
- No universal cross-company taste library; constraints remain local to the
  relevant team or domain.

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: ADR-pool.ai-runtime-foundations, ADR-pool.evaluation-infrastructure, ADR-pool.spec-triangle-sync

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Constraint object model and provenance contract are accepted.
2. Deterministic-rule vs. advisory-heuristic semantics are agreed upon.
3. Storage and lineage approach fits gzkit's ledger-first runtime posture.

## Notes

- Product thesis: gzkit should scale expert "no" moments into reusable
  constraints instead of treating them as disposable review chatter.
- High-value path: convert repeat rejections into durable rules, then into
  operator surfaces, checks, or training examples.
- This ADR is the semantic foundation for later CLI and MCP surfaces.
