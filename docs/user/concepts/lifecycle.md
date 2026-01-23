# Lifecycle

ADRs move through defined states. Understanding the lifecycle prevents confusion about what's ready for work, what's in progress, and what's done.

---

## States

| State | Meaning |
|-------|---------|
| **Pool** | Planned intent, awaiting prioritization |
| **Draft** | Being authored, not ready for review |
| **Proposed** | Submitted for review |
| **Accepted** | Approved, implementation may begin |
| **Completed** | Implementation finished, Gate 5 attestation received |
| **Validated** | Post-attestation audit passed |
| **Superseded** | Replaced by a newer ADR |
| **Abandoned** | Work stopped, rationale documented |

---

## State Flow

```
Pool → Draft → Proposed → Accepted → [implement] → Completed → Validated
                                                 ↘
                                                  Abandoned (if Dropped)
                                                 ↘
                                                  Superseded (if replaced)
```

---

## Pool State

Pool is the staging area for planned work. Pool entries are lightweight—just intent, not full ADRs.

**What a pool entry contains:**

- Status (always "Proposed" while in pool)
- Intent statement
- Target scope (bullets)
- Dependencies (blocking ADRs)
- Notes (design questions, rough sizing)

**What a pool entry does NOT contain:**

- Feature checklist
- OBPIs
- Folder structure
- Detailed rationale

**Pool entry naming:**

```
ADR-{major}.{minor}.0-pool.{slug}.md
```

Example: `ADR-0.2.0-pool.gate-verification.md`

**Pool location:**

```
docs/design/adr/pool/
```

---

## Promotion from Pool

When a pool entry is prioritized:

1. Assign the next available version (e.g., `0.1.5`)
2. Create the full ADR folder structure
3. Write the complete ADR with feature checklist
4. Co-create all OBPIs (one per checklist item)
5. Move or delete the pool file
6. Update registries

The key rule: **OBPIs are co-created with the ADR, not deferred.**

---

## Pre-Release Identifiers

Work items use SemVer-compliant identifiers:

```
{major}.{minor}.{patch}[-{type}.{identifier}]
```

| Type | Purpose | Example |
|------|---------|---------|
| `pool.{slug}` | Planned ADR in pool | `0.2.0-pool.gate-verification` |
| `obpi.{nn}` | OBPI in progress | `0.1.5-obpi.03` |
| `ghi.{nn}` | GitHub issue discovered | `0.1.5-ghi.42` |

**Precedence:**

```
0.1.5-obpi.01 < 0.1.5-obpi.02 < 0.1.5-ghi.42 < 0.1.5
```

When an ADR completes, all work items roll up into that version.

---

## OBPIs vs GHIs

| Type | Nature | Origin |
|------|--------|--------|
| **OBPI** | Planned work | Scoped at ADR creation |
| **GHI** | Emergent work | Discovered during implementation |

OBPIs map 1:1 to ADR checklist items. GHIs are surprises found along the way.

---

## PRD to Pool Relationship

PRDs drive ADR creation:

```
PRD-1.0.0
  ├── ADR-0.1.0 (Phase 1: MVP)
  ├── ADR-0.2.0-pool.gates (Phase 2)
  ├── ADR-0.3.0-pool.heavy-lane (Phase 3)
  ├── ADR-0.4.0-pool.audit (Phase 4)
  └── ADR-1.0.0-pool.release (Phase 5)
```

The PRD defines the roadmap. Pool entries stage the work. ADRs execute it.

---

## Attestation to Status Mapping

Gate 5 attestation determines final status:

| Attestation | Status | Meaning |
|-------------|--------|---------|
| "Completed" | Completed | All work finished |
| "Completed—Partial: [reason]" | Completed | Subset done, deferrals documented |
| "Dropped—[reason]" | Abandoned | Work stopped, rationale recorded |

---

## Example Lifecycle

1. **Pool**: `ADR-0.2.0-pool.gate-verification` created
2. **Draft**: Prioritized, becomes `ADR-0.2.0-gate-verification`, folder created, OBPIs written
3. **Proposed**: Author declares ready for review
4. **Accepted**: Human approves, implementation begins
5. **[Implementation]**: OBPIs completed one by one
6. **Closeout**: Ceremony triggered, human observes directly
7. **Completed**: Human attests "Completed"
8. **Validated**: Post-attestation audit reconciles records

---

## Related

- [Workflow](workflow.md) — Daily development patterns
- [OBPIs](obpis.md) — Atomic work units
- [Closeout](closeout.md) — Completing ADRs
- [gz plan](../commands/plan.md) — Create ADRs
