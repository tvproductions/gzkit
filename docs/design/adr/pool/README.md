# ADR Pool

Planned ADRs awaiting prioritization. Pool entries are lightweight intent documents—not full ADRs.

---

## Rules

1. **Pool entries are placeholders**, not commitments
2. **No OBPIs** until promoted from pool
3. **No folder structure** until promoted
4. **Naming (current)**: `ADR-pool.{slug}.md`
5. **Legacy compatibility**: semver-labeled pool IDs are tolerated for older entries
6. **Status**: "Pool" while active in pool; promoted entries become archived/superseded records

---

## Promotion

When a pool entry is prioritized:

1. Assign next available version in the target series
2. Create full ADR folder: `docs/design/adr/{foundation|pre-release|<major>.0}/ADR-X.Y.Z-{slug}/`
3. Write complete ADR with feature checklist
4. Co-create all OBPIs (one per checklist item)
5. Delete or archive the pool file
6. Update registries

Canonical command:

```bash
uv run gz adr promote ADR-pool.<slug> --semver X.Y.Z [--dry-run]
```

---

## Current Pool

| Entry | Target | Status | Dependency |
|-------|--------|--------|------------|
| [ADR-pool.heavy-lane](ADR-pool.heavy-lane.md) | 0.4.x | Waiting | ADR-0.3.0 |
| [ADR-pool.audit-system](ADR-pool.audit-system.md) | 0.6.x | Waiting | ADR-pool.heavy-lane |
| [ADR-pool.gz-chores-system](ADR-pool.gz-chores-system.md) | 0.7.x | Waiting | ADR-0.2.0 |
| [ADR-pool.release-hardening](ADR-pool.release-hardening.md) | 1.0.x | Waiting | ADR-pool.audit-system |
| [ADR-pool.go-runtime-parity](ADR-pool.go-runtime-parity.md) | Foundation | Waiting | ADR-0.3.0 |
| [ADR-pool.ai-runtime-foundations](ADR-pool.ai-runtime-foundations.md) | Phase 7+ runtime track | Waiting | ADR-pool.release-hardening |
| [ADR-pool.constraint-library](ADR-pool.constraint-library.md) | Rejection-derived constraint corpus | Waiting | None |
| [ADR-pool.constraint-cli-surfaces](ADR-pool.constraint-cli-surfaces.md) | CLI capture/query/apply surfaces | Waiting | ADR-pool.constraint-library |
| [ADR-pool.evaluation-infrastructure](ADR-pool.evaluation-infrastructure.md) | Phase 8 eval track | Waiting | ADR-pool.ai-runtime-foundations |
| [ADR-pool.controlled-agency-recovery](ADR-pool.controlled-agency-recovery.md) | Phase 9 agency track | Waiting | ADR-pool.evaluation-infrastructure |
| [ADR-pool.storage-simplicity-profile](ADR-pool.storage-simplicity-profile.md) | Runtime posture | Waiting | ADR-0.0.2-stdlib-cli-and-agent-sync |
| [ADR-pool.execution-memory-graph](ADR-pool.execution-memory-graph.md) | Runtime execution memory | Waiting | ADR-pool.storage-simplicity-profile, ADR-0.7.0-obpi-first-operations |
| [ADR-pool.prime-context-hooks](ADR-pool.prime-context-hooks.md) | CLI+hooks context runtime | Waiting | ADR-pool.execution-memory-graph |
| [ADR-pool.obpi-pipeline-runtime-surface](ADR-pool.obpi-pipeline-runtime-surface.md) | First-class launch/resume runtime for OBPI execution | Waiting | ADR-0.11.0-airlineops-obpi-completion-pipeline-parity |
| [ADR-pool.pause-resume-handoff-runtime](ADR-pool.pause-resume-handoff-runtime.md) | Runtime pause/resume and handoff lifecycle | Waiting | ADR-pool.obpi-pipeline-runtime-surface |
| [ADR-pool.obpi-pipeline-enforcement-parity](ADR-pool.obpi-pipeline-enforcement-parity.md) | AirlineOps-style hook enforcement for `gz-obpi-pipeline` | Waiting | ADR-0.11.0-airlineops-obpi-completion-pipeline-parity |
| [ADR-pool.structured-blocker-envelopes](ADR-pool.structured-blocker-envelopes.md) | Machine-readable blocker and retry envelopes | Waiting | ADR-0.10.0-obpi-runtime-surface |
| [ADR-pool.channel-agnostic-human-triggers](ADR-pool.channel-agnostic-human-triggers.md) | Transport-independent approval and attestation events | Waiting | ADR-pool.pause-resume-handoff-runtime |
| [ADR-pool.airlineops-surface-breadth-parity](ADR-pool.airlineops-surface-breadth-parity.md) | Canonical `.claude/**` + `.gzkit/**` breadth parity | Waiting | ADR-0.3.0-airlineops-canon-reconciliation |
| [ADR-pool.spec-triangle-sync](ADR-pool.spec-triangle-sync.md) | Spec-test-code process synchronization | Waiting | ADR-0.7.0-obpi-first-operations, ADR-pool.execution-memory-graph |
| [ADR-pool.tests-for-spec](ADR-pool.tests-for-spec.md) | Requirement-level test traceability | Waiting | ADR-pool.spec-triangle-sync |
| [ADR-pool.session-productivity-metrics](ADR-pool.session-productivity-metrics.md) | Quantitative session telemetry ledger | Waiting | None |
| [ADR-pool.universal-agent-onboarding](ADR-pool.universal-agent-onboarding.md) | Vendor-neutral agent cold-start protocol | Waiting | None |
| [ADR-pool.agent-role-specialization](ADR-pool.agent-role-specialization.md) | Abstract role taxonomy for multi-agent work | Waiting | None |
| [ADR-pool.agentic-security-review](ADR-pool.agentic-security-review.md) | Static security scanning in gate pipeline | Waiting | None |
| [ADR-pool.graduated-oversight-model](ADR-pool.graduated-oversight-model.md) | Three-tier oversight replacing binary Normal/Exception | Waiting | None |
| [ADR-pool.airlineops-direct-governance-migration](ADR-pool.airlineops-direct-governance-migration.md) | AirlineOps adopts gzkit as primary governance authority | Waiting | ADR-pool.constraint-library, ADR-pool.universal-agent-onboarding |

---

## Runtime Direction (BEADS + Plumb)

The runtime pool track converges two complementary patterns:

- BEADS pattern: dependency graph + ready/blocked queue + query-first operator surfaces.
- Plumb pattern: spec-test-code reconciliation with requirement-level proof.

gzkit target composition:

- Graph spine: `ADR -> OBPI -> REQ` with typed edges.
- Proof spine: `REQ -> test evidence` (e.g., `@covers` or equivalent metadata).
- State source: append-only ledger + deterministic derived views.
- Constraint: no mandatory Dolt/SQL runtime dependency in this track.

---

## Promoted from Pool

| Pool Entry | Promoted ADR | Date |
|---|---|---|
| [ADR-pool.airlineops-canon-reconciliation](ADR-pool.airlineops-canon-reconciliation.md) | [ADR-0.3.0](../pre-release/ADR-0.3.0-airlineops-canon-reconciliation/ADR-0.3.0-airlineops-canon-reconciliation.md) | 2026-02-13 |
| ADR-pool.skill-capability-mirroring | [ADR-0.4.0](../pre-release/ADR-0.4.0-skill-capability-mirroring/ADR-0.4.0-skill-capability-mirroring.md) | 2026-02-17 |
| [ADR-pool.pool-promotion-protocol](ADR-pool.pool-promotion-protocol.md) | [ADR-0.6.0-pool-promotion-protocol](../pre-release/ADR-0.6.0-pool-promotion-protocol/ADR-0.6.0-pool-promotion-protocol.md) | 2026-02-21 |
| [ADR-pool.obpi-first-operations](ADR-pool.obpi-first-operations.md) | [ADR-0.7.0-obpi-first-operations](../pre-release/ADR-0.7.0-obpi-first-operations/ADR-0.7.0-obpi-first-operations.md) | 2026-02-21 |
| [ADR-pool.obpi-runtime-surface](ADR-pool.obpi-runtime-surface.md) | [ADR-0.10.0-obpi-runtime-surface](../pre-release/ADR-0.10.0-obpi-runtime-surface/ADR-0.10.0-obpi-runtime-surface.md) | 2026-03-09 |

---

## Relationship to PRD

Pool entries derive from PRD phases:

```
PRD-GZKIT-1.0.0
├── ADR-0.1.0 (Phase 1: MVP) ← Active
├── [ADR-0.2.0](../pre-release/ADR-0.2.0-gate-verification/ADR-0.2.0-gate-verification.md) (Phase 2: Gates) ← Active
├── [ADR-0.3.0](../pre-release/ADR-0.3.0-airlineops-canon-reconciliation/ADR-0.3.0-airlineops-canon-reconciliation.md) (Phase 3) ← Active
├── [ADR-0.4.0](../pre-release/ADR-0.4.0-skill-capability-mirroring/ADR-0.4.0-skill-capability-mirroring.md) (Phase 4: Skill parity) ← Active
├── [ADR-0.5.0](../pre-release/ADR-0.5.0-skill-lifecycle-governance/ADR-0.5.0-skill-lifecycle-governance.md) (Phase 5: Skill lifecycle governance) ← Active
├── [ADR-0.6.0](../pre-release/ADR-0.6.0-pool-promotion-protocol/ADR-0.6.0-pool-promotion-protocol.md) (Pool promotion protocol) ← Active
├── ADR-pool.heavy-lane (Backlog)
├── ADR-pool.audit-system (Phase 6)
├── ADR-pool.gz-chores-system (Parity backlog)
├── ADR-pool.release-hardening (Phase 7)
├── ADR-pool.ai-runtime-foundations (Phase 7: AI runtime foundations)
├── ADR-pool.constraint-library (Rejection-derived constraint model and lineage)
├── ADR-pool.constraint-cli-surfaces (CLI-native constraint capture and reuse)
├── ADR-pool.evaluation-infrastructure (Phase 8: Evaluation infrastructure)
├── ADR-pool.controlled-agency-recovery (Phase 9: Controlled agency and recovery)
├── ADR-pool.go-runtime-parity (Foundation runtime track)
├── ADR-pool.storage-simplicity-profile (Runtime storage posture)
├── [ADR-0.7.0](../pre-release/ADR-0.7.0-obpi-first-operations/ADR-0.7.0-obpi-first-operations.md) (OBPI-first governance track) ← Active
├── ADR-pool.execution-memory-graph (Typed runtime execution memory)
├── ADR-pool.prime-context-hooks (Dynamic runtime context via hooks)
├── ADR-pool.obpi-pipeline-runtime-surface (First-class OBPI pipeline command/runtime)
├── ADR-pool.pause-resume-handoff-runtime (Pause/resume and handoff lifecycle runtime)
├── ADR-pool.obpi-pipeline-enforcement-parity (Hook-enforced OBPI pipeline path parity)
├── ADR-pool.structured-blocker-envelopes (Machine-readable blocker envelopes)
├── ADR-pool.channel-agnostic-human-triggers (Transport-independent human approvals)
├── [ADR-0.10.0](../pre-release/ADR-0.10.0-obpi-runtime-surface/ADR-0.10.0-obpi-runtime-surface.md) (OBPI-native runtime surfaces) ← Active
├── ADR-pool.airlineops-surface-breadth-parity (Canonical `.claude/**` + `.gzkit/**` breadth parity)
├── ADR-pool.spec-triangle-sync (Spec-test-code synchronization process)
├── ADR-pool.tests-for-spec (Tests verify spec requirements)
├── ADR-pool.session-productivity-metrics (Quantitative session telemetry)
├── ADR-pool.universal-agent-onboarding (Vendor-neutral cold-start protocol)
├── ADR-pool.agent-role-specialization (Abstract role taxonomy)
├── ADR-pool.agentic-security-review (Static security scanning in gates)
├── ADR-pool.graduated-oversight-model (Three-tier oversight model)
└── ADR-pool.airlineops-direct-governance-migration (AirlineOps adopts gzkit governance)
```

Parenting model:

- Foundation ADRs: `ADR-0.0.z`.
- Pre-release ADRs: `ADR-0.y.z` (where `y > 0`) and should chain by ADR parent (`ADR-0.y.z -> ADR-0.(y-1).z`).
- Release ADRs follow major-version progression: `ADR-1.y.z`, `ADR-2.y.z`, ...

## Foundational ADRs (0.0.x)

Foundational ADRs in the 0.0.x series do NOT appear in the pool. They establish governance and constraints that feature ADRs must follow. See:

- [ADR-0.0.1: Canonical GovZero Parity](../foundation/ADR-0.0.1-canonical-govzero-parity/ADR-0.0.1-canonical-govzero-parity.md) — locks AirlineOps as canonical
