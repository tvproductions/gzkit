# ADR Pool

Planned ADRs awaiting prioritization. Pool entries are lightweight intent documents—not full ADRs.

---

## Rules

1. **Pool entries are placeholders**, not commitments
2. **No OBPIs** until promoted from pool
3. **No folder structure** until promoted
4. **Naming (current)**: `ADR-pool.{slug}.md`
5. **Legacy compatibility**: semver-labeled pool IDs are tolerated for older entries
6. **Status**: "Proposed" while active in pool; promoted entries become archived/superseded records

---

## Promotion

When a pool entry is prioritized:

1. Assign next available version in the target series
2. Create full ADR folder: `docs/design/adr/adr-X.Y.x/ADR-X.Y.Z-{slug}/`
3. Write complete ADR with feature checklist
4. Co-create all OBPIs (one per checklist item)
5. Delete or archive the pool file
6. Update registries

---

## Current Pool

| Entry | Target | Status | Dependency |
|-------|--------|--------|------------|
| [ADR-pool.heavy-lane](ADR-pool.heavy-lane.md) | 0.4.x | Waiting | ADR-0.3.0 |
| [ADR-pool.audit-system](ADR-pool.audit-system.md) | 0.5.x | Waiting | ADR-pool.heavy-lane |
| [ADR-pool.gz-chores-system](ADR-pool.gz-chores-system.md) | 0.6.x | Waiting | ADR-0.2.0 |
| [ADR-pool.release-hardening](ADR-pool.release-hardening.md) | 0.7.x | Waiting | ADR-pool.audit-system |
| [ADR-pool.go-runtime-parity](ADR-pool.go-runtime-parity.md) | Foundation | Waiting | ADR-0.3.0 |

---

## Promoted from Pool

| Pool Entry | Promoted ADR | Date |
|---|---|---|
| [ADR-pool.airlineops-canon-reconciliation](ADR-pool.airlineops-canon-reconciliation.md) | [ADR-0.3.0](../adr-0.3.x/ADR-0.3.0-airlineops-canon-reconciliation/ADR-0.3.0-airlineops-canon-reconciliation.md) | 2026-02-13 |

---

## Relationship to PRD

Pool entries derive from PRD phases:

```
PRD-GZKIT-1.0.0
├── ADR-0.1.0 (Phase 1: MVP) ← Active
├── [ADR-0.2.0](../adr-0.2.x/ADR-0.2.0-gate-verification/ADR-0.2.0-gate-verification.md) (Phase 2: Gates) ← Active
├── [ADR-0.3.0](../adr-0.3.x/ADR-0.3.0-airlineops-canon-reconciliation/ADR-0.3.0-airlineops-canon-reconciliation.md) (Phase 3) ← Active
├── ADR-pool.heavy-lane (Phase 4)
├── ADR-pool.audit-system (Phase 5)
├── ADR-pool.gz-chores-system (Parity backlog)
├── ADR-pool.release-hardening (Phase 6)
└── ADR-pool.go-runtime-parity (Foundation runtime track)
```

## Foundational ADRs (0.0.x)

Foundational ADRs in the 0.0.x series do NOT appear in the pool. They establish governance and constraints that feature ADRs must follow. See:

- [ADR-0.0.1: Canonical GovZero Parity](../adr-0.0.x/ADR-0.0.1-canonical-govzero-parity/ADR-0.0.1-canonical-govzero-parity.md) — locks AirlineOps as canonical
