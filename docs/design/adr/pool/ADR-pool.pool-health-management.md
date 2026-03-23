---
id: ADR-pool.pool-health-management
status: Pool
lane: lite
parent: ADR-0.6.0-pool-promotion-protocol
---

# ADR-pool.pool-health-management: Pool Health Management Strategy

## Status

Pool

## Date

2026-03-23

## Parent ADR

[ADR-0.6.0-pool-promotion-protocol](../pre-release/ADR-0.6.0-pool-promotion-protocol/ADR-0.6.0-pool-promotion-protocol.md)

---

## Intent

Define a periodic pool triage process that detects overlap, identifies natural ADR clusters, retires stale items, and produces promotion recommendations — so the pool remains a useful intake queue rather than an unmanaged backlog.

**Motivation:** As of 2026-03-23, the pool contains 54 entries (15 promoted/superseded, 39 active). The SPEC-agent-capability-uplift exercise revealed that 5 pool ADRs were directly subsumed by new work and 8 overlapped with it. Without a triage process, the pool grows unbounded and overlapping items create confusion about what is already scoped vs still incubating.

---

## Target Scope

### 1. Overlap Detection

- Periodic scan (quarterly or before major planning cycles) that identifies pool ADRs addressing the same design space.
- Output: overlap clusters with shared surface areas identified.
- Tooling: `gz pool triage --overlap` produces a cluster report.

### 2. Cluster Identification

- Group overlapping pool ADRs into natural ADR candidates.
- Each cluster gets a recommended ADR boundary (which pool items it subsumes, what scope it covers).
- Example: `graduated-oversight-model` + `controlled-agency-recovery` → "Agent Autonomy" ADR candidate.

### 3. Staleness Criteria

- Pool ADR age thresholds:
  - **Fresh** (<3 months): Active incubation. No action needed.
  - **Aging** (3-6 months): Review for promotion readiness or archival.
  - **Stale** (>6 months, no promotion signal): Candidate for archival with rationale.
- Staleness is measured from creation date or last substantive update (whichever is later).
- Archived items move to `docs/design/adr/pool/archive/` with `status: Archived` and rationale.

### 4. Supersession Protocol

- When a spec, ADR, or new pool ADR subsumes an older pool item:
  - Older item marked `status: Superseded` with `superseded_by:` reference.
  - Supersession recorded as a ledger event.
  - Older item retained in pool directory for historical context (not deleted).
- When multiple pool ADRs merge into a single ADR candidate:
  - All source pool ADRs marked superseded with reference to the promoted ADR.
  - The promoted ADR's lineage section lists all source pool items.

### 5. Promotion Triggers

A pool ADR (or cluster) is ready for promotion when:
- External demand signal exists (user request, spec reference, or blocking dependency).
- Overlap with 2+ other pool items suggests consolidation is needed.
- The design space is well-enough understood to scope OBPIs (not just intent).
- A parent ADR or PRD exists to anchor the promotion.

### 6. Triage Cadence

- **Before major planning:** Run overlap detection + cluster identification (as done in SPEC-agent-capability-uplift).
- **Quarterly:** Review staleness, archive items with no promotion signal.
- **On pool ADR creation:** Check for overlap with existing pool items before accepting.

---

## Non-Goals

- Changing the promotion mechanics (ADR-0.6.0 covers that).
- Auto-promoting pool ADRs (promotion requires human judgment).
- Limiting pool size artificially (the pool is an intake queue, not a backlog with WIP limits).

---

## Evidence of Need

The SPEC-agent-capability-uplift (2026-03-23) analyzed 15 pool ADRs for overlap with 22 proposed capabilities. Findings:
- 5 pool ADRs were directly subsumed by new work (should have been caught earlier).
- 8 pool ADRs complemented new work (useful, but the relationship wasn't documented until the spec exercise).
- Several pool ADRs addressed the same design space from different angles without cross-referencing each other.

Without this triage process, these overlaps would have continued accumulating silently.

---

## Dependencies

- ADR-0.6.0-pool-promotion-protocol (promotion mechanics)
- `gz adr promote` CLI surface (existing)
