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
| [ADR-pool.obpi-runtime-surface](ADR-pool.obpi-runtime-surface.md) | Runtime ergonomics | Waiting | ADR-0.7.0-obpi-first-operations |

---

## Promoted from Pool

| Pool Entry | Promoted ADR | Date |
|---|---|---|
| [ADR-pool.airlineops-canon-reconciliation](ADR-pool.airlineops-canon-reconciliation.md) | [ADR-0.3.0](../pre-release/ADR-0.3.0-airlineops-canon-reconciliation/ADR-0.3.0-airlineops-canon-reconciliation.md) | 2026-02-13 |
| ADR-pool.skill-capability-mirroring | [ADR-0.4.0](../pre-release/ADR-0.4.0-skill-capability-mirroring/ADR-0.4.0-skill-capability-mirroring.md) | 2026-02-17 |
| [ADR-pool.pool-promotion-protocol](ADR-pool.pool-promotion-protocol.md) | [ADR-0.6.0-pool-promotion-protocol](../pre-release/ADR-0.6.0-pool-promotion-protocol/ADR-0.6.0-pool-promotion-protocol.md) | 2026-02-21 |
| [ADR-pool.obpi-first-operations](ADR-pool.obpi-first-operations.md) | [ADR-0.7.0-obpi-first-operations](../pre-release/ADR-0.7.0-obpi-first-operations/ADR-0.7.0-obpi-first-operations.md) | 2026-02-21 |

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
├── ADR-pool.go-runtime-parity (Foundation runtime track)
├── [ADR-0.7.0](../pre-release/ADR-0.7.0-obpi-first-operations/ADR-0.7.0-obpi-first-operations.md) (OBPI-first governance track) ← Active
└── ADR-pool.obpi-runtime-surface (OBPI-native runtime surfaces)
```

Parenting model:

- Foundation ADRs: `ADR-0.0.z`.
- Pre-release ADRs: `ADR-0.y.z` (where `y > 0`) and should chain by ADR parent (`ADR-0.y.z -> ADR-0.(y-1).z`).
- Release ADRs follow major-version progression: `ADR-1.y.z`, `ADR-2.y.z`, ...

## Foundational ADRs (0.0.x)

Foundational ADRs in the 0.0.x series do NOT appear in the pool. They establish governance and constraints that feature ADRs must follow. See:

- [ADR-0.0.1: Canonical GovZero Parity](../foundation/ADR-0.0.1-canonical-govzero-parity/ADR-0.0.1-canonical-govzero-parity.md) — locks AirlineOps as canonical
