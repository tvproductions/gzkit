# ADR Pool

Planned ADRs awaiting prioritization. Pool entries are lightweight intent documents—not full ADRs.

Groupings and sequencing derive from the [Architecture Planning Memo](../../ARCHITECTURE-PLANNING-MEMO.md)
(all 12 sections ratified 2026-03-29).

---

## Rules

1. **Pool entries are placeholders**, not commitments
2. **No OBPIs** until promoted from pool
3. **No folder structure** until promoted
4. **Naming (current)**: `ADR-pool.{slug}.md`
5. **Legacy compatibility**: semver-labeled pool IDs are tolerated for older entries
6. **Status**: "Pool" while active in pool; promoted entries become archived/superseded records

---

## Comparator-Strength Intake (2026-05-07)

Operator-approved posture:

> gzkit should not chase competitors by becoming lighter. Its edge is heavier:
> ledger, receipts, validators, doctrine, attestation. The way to absorb
> competitor strengths is to improve the front door and the compounding loop
> while making every borrowed workflow mechanically witnessed.

This intake does not promote any pool item. It sharpens existing destinations so
future promotion absorbs external strengths without weakening gzkit's identity.

| Strength | Comparator signal | Existing destination |
|---|---|---|
| Operator-simple spec entry | GitHub Spec Kit, Kiro, betterspec/specledger | `ADR-pool.operator-first-spec-workspace`, `ADR-pool.change-isolation-workspace`, `ADR-pool.spec-delta-markers`, `ADR-pool.pre-planning-interview`, `ADR-0.45.0` |
| Workflow as structured runtime | GitHub Spec Kit, Kiro, GSD | `ADR-pool.workflow-specification`, `ADR-pool.harness-agnostic-plan-capture`, `ADR-pool.agent-execution-intelligence` |
| Parallel task waves | Kiro, GSD, Superpowers | `ADR-pool.wave-dependency-execution`, `ADR-pool.obpi-pipeline-dispatch-attestation`, `ADR-0.44.0` |
| Content and prompt injection defense | GSD, broader agent-security practice | `ADR-pool.content-injection-scanning`, `ADR-pool.agentic-security-review`, `ADR-0.0.40` |
| Context packages and portable agent surfaces | Tessl, BMAD, GSD, Compound Engineering | `ADR-pool.context-package-registry`, `ADR-pool.skill-control-surface-contract`, `ADR-pool.vendor-capability-matrix`, `ADR-0.0.32`, `ADR-0.44.0` |
| First-stage namespace routing | GSD v1.40 namespace meta-skills | `ADR-pool.namespace-router-product-surface` |
| Executable contracts | Specmatic, OpenAPI-style ecosystems | `ADR-pool.contract-surface-mechanical-defenses`, `ADR-pool.tdd-receipt-stream`, `ADR-0.46.0` |
| Review-to-learning compounding | Compound Engineering, Superpowers | `ADR-pool.review-receipt-taxonomy`, `ADR-pool.skill-feedback-loop`, `ADR-pool.solved-problem-pattern-corpus`, `ADR-0.27.0`, `ADR-0.41.0` |
| Persona/workflow adoption UX | BMAD, Superpowers | `ADR-pool.universal-agent-onboarding`, `ADR-pool.agent-reliability-framework`, `ADR-0.0.34` |
| Bugfix-spec routing | Kiro, Spec Kit, GSD, Superpowers | `ADR-pool.bugfix-spec-routing`, `ADR-pool.spec-delta-markers`, `ADR-0.43.0` |
| Borrowed-workflow doctrine | All comparators | `ADR-pool.external-strength-absorption-doctrine`, `ADR-pool.workflow-specification`, `ADR-pool.design-references-bibliography` |

New pool destinations created by this intake:

- `ADR-pool.external-strength-absorption-doctrine` — foundation candidate for
  witnessed borrowing doctrine.
- `ADR-pool.operator-first-spec-workspace` — feature candidate for the
  operator-simple front door.
- `ADR-pool.bugfix-spec-routing` — feature candidate for observed/expected/
  unchanged defect specs tied to GHI/direct-fix/OBPI routing.
- `ADR-pool.review-receipt-taxonomy` — foundation or feature candidate for typed
  review evidence and compounding destinations.
- `ADR-pool.context-package-registry` — feature candidate for governed context
  packages and portable agent surfaces.

2026-05-14 GSD router follow-up:

- `ADR-pool.namespace-router-product-surface` — feature candidate for a small
  namespace-router front door that reduces first-stage skill-selection cost
  while preserving direct concrete skill invocation.

Validated ADRs are not edited for this intake. If a future improvement requires
changing a validated ADR rather than consuming it from an open ADR or pool
destination, route the change through a GHI and an explicit amendment or follow-up
ADR. The doctrine for absorbing comparator strengths into closed/validated
surfaces is captured in
[ADR-pool.external-strength-absorption-doctrine](ADR-pool.external-strength-absorption-doctrine.md);
each closed-ADR uplift files its own GHI and routes through that doctrine.

---

## Promotion

When a pool entry is prioritized:

1. Assign next available version in the target series
2. Create full ADR folder: `docs/design/adr/{foundation|pre-release|<major>.0}/ADR-X.Y.Z-{slug}/`
3. Write complete ADR with feature checklist
4. Co-create all OBPIs (one per checklist item)
5. Archive the pool file with forwarding frontmatter (`status: archived`, `superseded_by`, `archived_date`)
6. Update registries

Canonical command:

```bash
uv run gz adr promote ADR-pool.<slug> --semver X.Y.Z [--dry-run]
```

Promotion is fail-closed unless the pool ADR already contains actionable `## Target Scope`
bullets. On success, the command creates the promoted ADR plus matching OBPI brief files.

---

## Sequencing (from Architecture Planning Memo)

```text
Phase N (complete):
  [1] ADR-0.0.9  State Doctrine               PROMOTED
  [2] ADR-0.0.10 Storage Tiers                PROMOTED
      (authored as a pair, 2026-03-29)

Phase N+1 (after foundations locked):
  [3] Graph Engine (pre-release, Heavy)        deps: [1], [2]
  [4] Blocker Protocol (pre-release, Heavy)    zero deps, parallel with [3]

Phase N+2 (after graph engine):
  [5] Pipeline Lifecycle (pre-release, Heavy)  deps: [3]
  [6] Graduated Oversight (pre-release, Lite)  deps: [3]

Phase N+3 (pre-1.0):
  [7] Audit System (pre-release, Heavy)        deps: [3] (proof resolution)
  [8] Release Hardening                        deps: all above
```

---

## Group A: Foundations (0.0.x)

Promoted to foundation ADRs. No remaining pool entries.

| Entry | Action | Status |
|-------|--------|--------|
| [ADR-pool.storage-simplicity-profile](ADR-pool.storage-simplicity-profile.md) | Promoted to [ADR-0.0.10](../foundation/ADR-0.0.10-storage-tiers-simplicity-profile/ADR-0.0.10-storage-tiers-simplicity-profile.md) | Promoted 2026-03-29 |
| (new) State Doctrine | Authored as [ADR-0.0.9](../foundation/ADR-0.0.9-state-doctrine-source-of-truth/ADR-0.0.9-state-doctrine-source-of-truth.md) | Authored 2026-03-29 |

---

## Group B: Graph and Runtime (Phase N+1 / N+2)

The architectural center of gravity. Graph engine must be locked before pipeline
lifecycle, graduated oversight, or audit can be designed properly.

| Entry | Action | Sequencing | Dependency |
|-------|--------|-----------|------------|
| [ADR-pool.execution-memory-graph](ADR-pool.execution-memory-graph.md) | Promote (Heavy) | Phase N+1 [3] | ADR-0.0.9, ADR-0.0.10 |
| [ADR-pool.workflow-specification](ADR-pool.workflow-specification.md) | Assess (Heavy) | Phase N+2 candidate | ADR-0.13.0, harness-aware execution modes |
| [ADR-pool.prime-context-hooks](ADR-pool.prime-context-hooks.md) | Merge as OBPI under Graph Engine | Phase N+1 | Subsumed by [3] |
| [ADR-pool.universal-agent-onboarding](ADR-pool.universal-agent-onboarding.md) | Merge as OBPI under Graph Engine | Phase N+1 | Subsumed by [3] |
| [ADR-pool.structured-blocker-envelopes](ADR-pool.structured-blocker-envelopes.md) | Promote independently (Heavy) | Phase N+1 [4] | None (parallel with [3]) |
| [ADR-pool.pause-resume-handoff-runtime](ADR-pool.pause-resume-handoff-runtime.md) | Promote after Graph (Heavy) | Phase N+2 [5] | Graph Engine |
| [ADR-pool.channel-agnostic-human-triggers](ADR-pool.channel-agnostic-human-triggers.md) | Subordinate as future OBPI under pause/resume | Phase N+2 | Subsumed by [5] |
| [ADR-pool.obpi-pipeline-runtime-surface](ADR-pool.obpi-pipeline-runtime-surface.md) | Assess overlap with Pipeline Lifecycle | Phase N+2 | Graph Engine |
| [ADR-pool.obpi-pipeline-enforcement-parity](ADR-pool.obpi-pipeline-enforcement-parity.md) | Assess overlap with Pipeline Lifecycle | Phase N+2 | Graph Engine |

---

## Group C: Proof Chain (partially promoted)

| Entry | Action | Status |
|-------|--------|--------|
| [ADR-pool.spec-triangle-sync](ADR-pool.spec-triangle-sync.md) | Already promoted | ADR-0.20.0 |
| [ADR-pool.tests-for-spec](ADR-pool.tests-for-spec.md) | Already promoted | ADR-0.21.0 |
| [ADR-pool.constraint-library](ADR-pool.constraint-library.md) | Defer | Premature; proof architecture must stabilize first |
| [ADR-pool.constraint-cli-surfaces](ADR-pool.constraint-cli-surfaces.md) | Defer | Blocked by constraint-library |

---

## Group D: Agent Model (partially promoted)

| Entry | Action | Status |
|-------|--------|--------|
| [ADR-pool.agent-role-specialization](ADR-pool.agent-role-specialization.md) | Already superseded | Subsumed into ADR-0.18.0 |
| [ADR-pool.graduated-oversight-model](ADR-pool.graduated-oversight-model.md) | Defer until graph operational | Phase N+2 [6]; needs graph for risk scoring |

---

## Group E: Parity and Maintenance

| Entry | Action | Rationale |
|-------|--------|-----------|
| [ADR-pool.airlineops-surface-breadth-parity](ADR-pool.airlineops-surface-breadth-parity.md) | Already promoted | ADR-0.9.0 |
| [ADR-pool.airlineops-direct-governance-migration](ADR-pool.airlineops-direct-governance-migration.md) | Defer indefinitely | Not an architecture decision |
| [ADR-pool.session-productivity-metrics](ADR-pool.session-productivity-metrics.md) | Defer | Not architecturally load-bearing |
| [ADR-pool.agentic-security-review](ADR-pool.agentic-security-review.md) | Defer | Gate plugin; add after proof arch is stable |
| [ADR-pool.go-runtime-parity](ADR-pool.go-runtime-parity.md) | Defer | Multi-language is premature |
| [ADR-pool.gz-chores-system](ADR-pool.gz-chores-system.md) | Assess | May be covered by existing chores infrastructure |

---

## Group F: Release Track (Phase N+3 and post-1.0)

| Entry | Action | Sequencing |
|-------|--------|-----------|
| [ADR-pool.heavy-lane](ADR-pool.heavy-lane.md) | Promote when needed | Gate expansion, not architecture |
| [ADR-pool.audit-system](ADR-pool.audit-system.md) | Promote after Graph | Phase N+3 [7]; needs proof resolution chain |
| [ADR-pool.release-hardening](ADR-pool.release-hardening.md) | Last before 1.0 | Phase N+3 [8]; everything else must be done or deferred |
| [ADR-pool.ai-runtime-foundations](ADR-pool.ai-runtime-foundations.md) | Post-1.0 | Keep in pool |
| [ADR-pool.evaluation-infrastructure](ADR-pool.evaluation-infrastructure.md) | Stale | ADR-0.0.5 covers this; archive or update |
| [ADR-pool.controlled-agency-recovery](ADR-pool.controlled-agency-recovery.md) | Post-1.0 | Keep in pool |

---

## Promoted from Pool

| Pool Entry | Promoted ADR | Date |
|---|---|---|
| [ADR-pool.airlineops-canon-reconciliation](ADR-pool.airlineops-canon-reconciliation.md) | [ADR-0.3.0](../pre-release/ADR-0.3.0-airlineops-canon-reconciliation/ADR-0.3.0-airlineops-canon-reconciliation.md) | 2026-02-13 |
| ADR-pool.skill-capability-mirroring | [ADR-0.4.0](../pre-release/ADR-0.4.0-skill-capability-mirroring/ADR-0.4.0-skill-capability-mirroring.md) | 2026-02-17 |
| [ADR-pool.pool-promotion-protocol](ADR-pool.pool-promotion-protocol.md) | [ADR-0.6.0-pool-promotion-protocol](../pre-release/ADR-0.6.0-pool-promotion-protocol/ADR-0.6.0-pool-promotion-protocol.md) | 2026-02-21 |
| [ADR-pool.obpi-first-operations](ADR-pool.obpi-first-operations.md) | [ADR-0.7.0-obpi-first-operations](../pre-release/ADR-0.7.0-obpi-first-operations/ADR-0.7.0-obpi-first-operations.md) | 2026-02-21 |
| [ADR-pool.obpi-runtime-surface](ADR-pool.obpi-runtime-surface.md) | [ADR-0.10.0-obpi-runtime-surface](../pre-release/ADR-0.10.0-obpi-runtime-surface/ADR-0.10.0-obpi-runtime-surface.md) | 2026-03-09 |
| [ADR-pool.storage-simplicity-profile](ADR-pool.storage-simplicity-profile.md) | [ADR-0.0.10](../foundation/ADR-0.0.10-storage-tiers-simplicity-profile/ADR-0.0.10-storage-tiers-simplicity-profile.md) | 2026-03-29 |

---

## Foundational ADRs (0.0.x)

Foundational ADRs in the 0.0.x series do NOT appear in the pool. They establish governance and constraints that feature ADRs must follow. See:

- [ADR-0.0.1: Canonical GovZero Parity](../foundation/ADR-0.0.1-canonical-govzero-parity/ADR-0.0.1-canonical-govzero-parity.md) — locks AirlineOps as canonical
- [ADR-0.0.9: State Doctrine](../foundation/ADR-0.0.9-state-doctrine-source-of-truth/ADR-0.0.9-state-doctrine-source-of-truth.md) — three-layer state model, ledger is authoritative
- [ADR-0.0.10: Storage Tiers](../foundation/ADR-0.0.10-storage-tiers-simplicity-profile/ADR-0.0.10-storage-tiers-simplicity-profile.md) — three-tier simplicity profile
