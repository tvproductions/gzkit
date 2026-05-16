---
id: ADR-0.0.46-pool-management
status: Proposed
kind: foundation
semver: 0.0.46
lane: heavy
parent: ADR-0.6.0-pool-promotion-protocol
date: 2026-05-16
promoted_from: ADR-pool.pool-management
---

# ADR-0.0.46-pool-management: Pool Management Strategy

## Persona

<!-- Describe the behavioral identity for agents working on this ADR.
     Frame as values and craftsmanship standards, not expertise claims.
     See .gzkit/personas/ for reusable persona definitions. -->

{persona}

## Intent

Define a pool management process that (1) detects overlap, identifies natural ADR clusters, retires stale items, and produces promotion recommendations, and (2) maintains a priority-ranked backlog so execution intent is signaled without version commitment.

**Motivation:** Pre-booking 16 absorption-wave ADRs (0.25.0-0.40.0) created semver lock-in and stale commitment. The governance chain evaluation (2026-04-04) revealed that Category B sequencing guidance (which pool ADRs to promote first based on governance-chain impact) needs a durable home. The pool must be more than an unmanaged intake queue — it needs a ranked priority signal that feeds into execution sequencing decisions.

**Current state:** pool ADRs are durable intent records, but their readiness,
overlap, supersession, and priority are still inferred from scattered prose,
manual `rg` passes, and the interim `src/gzkit/chores/pool-triage/CHORE.md`
drift report. That makes the pool large but not reliably navigable. The
operator can ask which pool item to promote next, yet the answer depends on
agent memory and one-off synthesis rather than a governed pool state model.

**Target state:** gzkit treats the pool as managed planning infrastructure.
Pool state remains Layer-1 document truth plus Layer-2 ledger history, while
the planned ranking and triage surfaces project derived views that are
rebuildable. The outcome is a pull-model backlog: overlap clusters,
newly-unblocked items, stale entries, superseded entries, computed ranks, and
operator overrides are visible before a SemVer ADR is booked.

---

## Decision

Promote `ADR-pool.pool-management` into active implementation and execute the following tracked scope:

1. Establish pool metadata and lifecycle rules as the canonical planning
   contract for backlog ADRs.
2. Provide read-only triage and computed ranking surfaces for overlap,
   staleness, newly-unblocked work, dependency blocking count, ADDRESS density,
   and cluster size.
3. Preserve operator judgment as explicit override state with a reason, rather
   than letting computed scores silently become decision authority.
4. Keep the interim `pool-triage` chore bounded: it is retired or absorbed when
   the canonical pool management surface lands.

- **pool-metadata-model** — Define pool ADR metadata, staleness classes, supersession state, archive eligibility, and validation rules for managed pool state.
- **pool-triage-command** — Implement `gz pool triage --overlap --json` to report overlap clusters, stale items, superseded items, and newly unblocked candidates without mutating pool files.
- **pool-priority-registry** — Add the `.gzkit/pool-priority.json` schema and ledger snapshot contract for preserving computed ranking state and triage-run evidence.
- **pool-rank-command** — Implement `gz pool rank` and `gz pool rank --apply` with ADDRESS density, dependency blocking count, and cluster-size scoring.
- **pool-override-show** — Implement `gz pool override` and `gz pool show` so operator rank overrides persist with reasons across recomputation.
- **pool-docs-runbook** — Add manpages, runbook entries, command docs, and the retire-or-absorb decision for the interim `pool-triage` chore.

## Rationale

1. ADR-0.6.0 defines promotion mechanics, but mechanics alone do not answer
   "which pool item should be promoted next?" This ADR supplies the managed
   backlog layer that sits before promotion.
2. The existing interim chore in `src/gzkit/chores/pool-triage/CHORE.md`
   proves demand for drift signals, but a chore cannot own the canonical pool
   ranking contract or operator override state.
3. A mutable priority registry is acceptable only because it is explicitly a
   derived Layer-3 view. Source facts remain in `docs/design/adr/pool/*.md`
   and `.gzkit/ledger.jsonl`; the registry can be recomputed or discarded.
4. The design rejects the anti-pattern of semver pre-booking. Pool priority
   communicates execution intent without forcing future ADR numbers before the
   operator is ready to promote.

## Consequences

### Positive

- Promotion preserves backlog intent as executable ADR scope.
- Checklist items now map 1:1 to generated OBPI briefs immediately.

### Negative

- Promotion fails closed when the pool ADR lacks actionable execution scope.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 1
- Dimension Total: 9
- Baseline Range: 5+
- Baseline Selected: 6
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 6

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.46-01: **pool-metadata-model** — Define pool ADR metadata, staleness classes, supersession state, archive eligibility, and validation rules for managed pool state.
- [ ] OBPI-0.0.46-02: **pool-triage-command** — Implement `gz pool triage --overlap --json` to report overlap clusters, stale items, superseded items, and newly unblocked candidates without mutating pool files.
- [ ] OBPI-0.0.46-03: **pool-priority-registry** — Add the `.gzkit/pool-priority.json` schema and ledger snapshot contract for preserving computed ranking state and triage-run evidence.
- [ ] OBPI-0.0.46-04: **pool-rank-command** — Implement `gz pool rank` and `gz pool rank --apply` with ADDRESS density, dependency blocking count, and cluster-size scoring.
- [ ] OBPI-0.0.46-05: **pool-override-show** — Implement `gz pool override` and `gz pool show` so operator rank overrides persist with reasons across recomputation.
- [ ] OBPI-0.0.46-06: **pool-docs-runbook** — Add manpages, runbook entries, command docs, and the retire-or-absorb decision for the interim `pool-triage` chore.

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

### 8. Near-Term Implementation: `pool-triage` Chore (gzkit-internal)

**Scope.** A Lite-lane gzkit-internal chore that implements the drift-detection slice of this ADR as a stopgap until the full `gz pool rank` / `gz pool triage` / `gz pool override` CLI surface ships with promotion. The chore is read-only: it surfaces drift signals for operator triage during the between-ADR maintenance window but takes no automated actions.

**Contract.** The chore is subordinate to this ADR. Its design intent, governing artifact (`.gzkit/pool-priority.json` or a simpler placeholder), and heuristics are bounded by what this ADR defines. The chore is not a parallel implementation — it is a time-scoped, reduced-capability preview of one slice of this ADR's design.

**Heuristics (the chore's four drift signals).** Each is derivable from frontmatter + file system + ledger + pool-internal `Dependencies` sections without new data models:

1. **Stale** — pool ADRs with no git-tracked update in >6 months (matches the `Stale` threshold in section 3 above)
2. **Unarchived-superseded** — pool ADRs with `status: Superseded` in frontmatter that still sit in `docs/design/adr/pool/` instead of `docs/design/adr/pool/archive/` (matches section 4 archival requirement)
3. **Newly-unblocked** — pool ADRs whose `Dependencies` section references ADRs that are now `Completed` in the ledger, signaling promotion-readiness (matches section 5 promotion triggers)
4. **Duplicate-scope candidates** — pool ADRs whose titles, keywords, or path references overlap with other pool ADRs, flagged as consolidation candidates (matches section 1 overlap detection, but uses simple keyword heuristics rather than the fuller cluster-identification surface in section 2)

**Out of scope for the chore (deferred to ADR promotion).** Computed priority ranking (section 7 — requires ADDRESS density input from governance-chain evaluation, which the chore has no access to), operator override persistence (section 7 — requires `.gzkit/pool-priority.json` schema design), cluster naming and ADR-candidate boundary proposals (section 2 — requires judgment the chore cannot provide), and any mutation to pool state (the chore surfaces, it does not rewrite).

**Promotion outcome — retire-or-absorb decision.** When this ADR promotes and the full `gz pool rank` / `gz pool triage` surface ships, the chore's fate is decided explicitly:

- **Retire** if the ADR's implementation fully subsumes the chore's four heuristics as first-class CLI commands. The chore registry entry is removed; its scope note references this ADR as successor.
- **Absorb** if the chore's output format, heuristic implementation, or registry entry has become the operational muscle memory the ADR wants to preserve. In that case, the chore's code and output contract are pulled into the ADR's canonical implementation and the chore registry entry is rewritten as a thin wrapper around the new CLI.

The decision belongs to the ADR's promotion review, not to the chore's author. The chore exists under the understanding that its entire lifetime is bounded by this ADR's promotion cycle.

**Not a framework feature.** The `pool-triage` chore is a gzkit-internal maintenance item — it targets gzkit's own pool, runs in gzkit's own chore suite, and serves gzkit's own operator. Downstream projects that adopt gzkit will have their own pools and may author their own triage chores using gzkit's chore framework, but this specific chore is not packaged as a framework deliverable or a template. The tooling-layer-vs-consumer-layer distinction (see OBPI-0.25.0-29 Exclude precedent) governs here: gzkit ships the *chore framework*, not a catalog of chores for downstream consumers.

---

## Non-Goals

- Changing the promotion mechanics (ADR-0.6.0 covers that).
- Auto-promoting pool ADRs (promotion requires human judgment).
- Limiting pool size artificially (the pool is a managed backlog, not a WIP-limited queue).
- Replacing operator judgment with a formula (computed scores inform ranking, they don't determine it).

---

## Dependencies

- ADR-0.6.0-pool-promotion-protocol (promotion mechanics)
- `gz adr promote` CLI surface (existing)
- Governance chain evaluation framework (produces ADDRESS density input)

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.pool-management` on 2026-05-16; executable scope was carried forward from the pool ADR instead of reseeded as placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

### A. Keep pool management as the interim chore only

Rejected. The chore reports drift but cannot define a durable ranking schema,
operator override contract, or promotion-readiness state. Leaving it as the
only surface would preserve the current manual planning gap.

### B. Pre-book the next pool ADRs into SemVer sequence

Rejected. Pre-booking was the failure that motivated this ADR: it creates
numbering commitment before execution commitment and makes later reprioritizing
look like drift.

### C. Let agents rank the pool from prose on demand

Rejected. That is exactly the stochastic-vibing surface gzkit is designed to
make inert. Ranking must be grounded in explicit metadata, ledger facts,
computed dimensions, and recorded operator overrides.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.46 | Pending | | | |
