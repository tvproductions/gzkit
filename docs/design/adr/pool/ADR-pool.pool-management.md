---
id: ADR-pool.pool-management
status: Pool
lane: heavy
parent: ADR-0.6.0-pool-promotion-protocol
---

# ADR-pool.pool-management: Pool Management Strategy

## Status

Pool

## Date

2026-03-23 (created as pool-health-management)
2026-04-04 (extended with priority ranking — GHI #98)

## Parent ADR

[ADR-0.6.0-pool-promotion-protocol](../pre-release/ADR-0.6.0-pool-promotion-protocol/ADR-0.6.0-pool-promotion-protocol.md)

---

## Intent

Define a pool management process that (1) detects overlap, identifies natural ADR clusters, retires stale items, and produces promotion recommendations, and (2) maintains a priority-ranked backlog so execution intent is signaled without version commitment.

**Motivation:** Pre-booking 16 absorption-wave ADRs (0.25.0-0.40.0) created semver lock-in and stale commitment. The governance chain evaluation (2026-04-04) revealed that Category B sequencing guidance (which pool ADRs to promote first based on governance-chain impact) needs a durable home. The pool must be more than an unmanaged intake queue — it needs a ranked priority signal that feeds into execution sequencing decisions.

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

### 7. Priority Ranking

**Model:** Scored triage, operator rank. Triage runs produce a computed default order from three dimensions; the operator assigns the actual rank integer with an override and reason.

**Computed Dimensions (3):**

| Dimension | Source | Description |
|-----------|--------|-------------|
| **Governance-chain ADDRESS density** | Evaluation reports | How many systemic findings does this pool ADR address? Higher density = more governance-chain hardening per promotion. |
| **Dependency blocking count** | Pool file `Dependencies` sections | How many other pool or booked ADRs list this one as a dependency? Higher count = more downstream work unblocked by promotion. |
| **Cluster size** | Overlap detection output | How many other pool ADRs touch the same design space? Larger clusters signal consolidation urgency. |

Operator demand and absorption readiness are captured via the override mechanism, not as computed dimensions.

**Computation timing:** On-demand at triage time, not continuous. Operator invokes `gz pool rank`.

**Governing artifact:** `.gzkit/pool-priority.json` — mutable ranked list with computed scores and operator override fields. Ledger event (`pool_triage_completed`) records each triage run as an append-only snapshot.

**CLI surface:**

```
gz pool rank              # compute and display ranked table
gz pool rank --apply      # compute and write to .gzkit/pool-priority.json
gz pool override <slug> --rank N --reason "..."
gz pool show              # display current priority table with overrides
```

**Override protocol:** Operator can set any rank with a reason. Overrides persist across triage runs — a re-run of `gz pool rank --apply` recomputes scores but preserves overrides unless the operator clears them. This ensures operator judgment is durable while computed dimensions update as the project evolves.

---

## Non-Goals

- Changing the promotion mechanics (ADR-0.6.0 covers that).
- Auto-promoting pool ADRs (promotion requires human judgment).
- Limiting pool size artificially (the pool is a managed backlog, not a WIP-limited queue).
- Replacing operator judgment with a formula (computed scores inform ranking, they don't determine it).

---

## Evidence of Need

1. The SPEC-agent-capability-uplift (2026-03-23) analyzed 15 pool ADRs for overlap with 22 proposed capabilities. Findings: 5 pool ADRs were directly subsumed by new work and 8 overlapped with it. Without triage, these overlaps would have continued accumulating silently.

2. The governance chain evaluation (2026-04-04) produced Category B sequencing guidance — recommended absorption-wave priority order based on ADDRESS density. This analysis has no durable home. Each evaluation re-derives priority from scratch because no artifact captures the ranked state between evaluations.

3. Operator identified (2026-04-04) that pre-booking 16 absorption ADRs created semver lock-in: completing ADR-0.34.0 then ADR-0.28.0 makes numbering incoherent. Priority ranking at the pool level avoids version commitment until promotion time.

---

## Documentation Requirements

When promoted and implemented:
- **Manpages** in `docs/user/manpages/` for `gz pool rank`, `gz pool override`, `gz pool show`
- **Runbook entries** in `docs/user/runbook.md` for pool triage workflow and priority override workflow
- **Docstrings** on CLI command functions, Pydantic models for `pool-priority.json` schema, and triage dimension computation functions
- **Command docs** in `docs/user/commands/` following existing patterns

---

## Dependencies

- ADR-0.6.0-pool-promotion-protocol (promotion mechanics)
- `gz adr promote` CLI surface (existing)
- Governance chain evaluation framework (produces ADDRESS density input)
