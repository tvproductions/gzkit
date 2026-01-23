# ADR Pool

Planned ADRs awaiting prioritization. Pool entries are lightweight intent documents—not full ADRs.

---

## Rules

1. **Pool entries are placeholders**, not commitments
2. **No OBPIs** until promoted from pool
3. **No folder structure** until promoted
4. **Naming**: `ADR-{major}.{minor}.0-pool.{slug}.md`
5. **Status**: Always "Proposed" while in pool

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
| [ADR-0.2.0-pool.gate-verification](ADR-0.2.0-pool.gate-verification.md) | 0.2.x | Waiting | ADR-0.1.0 |
| [ADR-0.3.0-pool.heavy-lane](ADR-0.3.0-pool.heavy-lane.md) | 0.3.x | Waiting | ADR-0.2.0 |
| [ADR-0.4.0-pool.audit-system](ADR-0.4.0-pool.audit-system.md) | 0.4.x | Waiting | ADR-0.3.0 |
| [ADR-1.0.0-pool.release-hardening](ADR-1.0.0-pool.release-hardening.md) | 1.0.0 | Waiting | ADR-0.4.0 |

---

## Relationship to PRD

Pool entries derive from PRD phases:

```
PRD-GZKIT-1.0.0
├── ADR-0.1.0 (Phase 1: MVP) ← Active
├── ADR-0.2.0-pool.gate-verification (Phase 2)
├── ADR-0.3.0-pool.heavy-lane (Phase 3)
├── ADR-0.4.0-pool.audit-system (Phase 4)
└── ADR-1.0.0-pool.release-hardening (Phase 5)
```
