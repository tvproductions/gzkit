# ADR Lifecycle and Status Mapping

Status: Active
Last reviewed: 2026-01-30
Authority: Canon (defines ADR lifecycle states, pre-release identifiers, and closeout-to-status mapping)

This document canonizes ADR lifecycle states and their relationship to Gate 5 closeout attestation.
For gate definitions, see [charter.md](charter.md). For closeout ceremony behavior, see [audit-protocol.md](audit-protocol.md).

---

## ADR Lifecycle States

An ADR progresses through these states:

| State | Meaning | Transition Trigger |
|-------|---------|-------------------|
| **Pool** | Planned ADR awaiting prioritization; lightweight intent only | Author identifies future work need |
| **Draft** | ADR being authored; not yet ready for review | ADR pulled from pool; author creates full structure |
| **Proposed** | ADR submitted for review; awaiting acceptance | Author declares ready for review |
| **Accepted** | ADR approved; implementation work may begin | Human accepts the proposal |
| **Completed** | Implementation finished; Gate 5 attestation received | Human attests "Completed" or "Completed — Partial" |
| **Validated** | Post-attestation audit completed (Phase 2) | Audit passes and reconciliation recorded |
| **Superseded** | Replaced by a newer ADR | New ADR explicitly supersedes this one |
| **Abandoned** | Work stopped; ADR will not be completed | Human attests "Dropped" or declares abandonment |

### Lifecycle Diagram

```text
Pool → Draft → Proposed → Accepted → [implementation] → Closeout Ceremony → Completed → Validated
  │                                                                        → Abandoned (if Dropped)
  │                                                      ↓
  │                                                 Superseded (if replaced by new ADR)
  │
  └── (may remain in pool indefinitely until prioritized or dropped)
```

---

## Pre-Release Identifier Scheme (SemVer Compliant)

During development (0.y.z) and post-release (1.0.0+), SemVer pre-release identifiers provide
a unified namespace for tracking work items. The format is:

```text
{major}.{minor}.{patch}[-{type}.{identifier}]
```

### Identifier Types

| Type | Purpose | Example |
|------|---------|---------|
| `pool.{slug}` | Planned ADR in pool, awaiting prioritization | `0.2.0-pool.forecaster-core` |
| `obpi.{nn}` | OBPI brief in progress under an ADR | `0.1.15-obpi.03` |
| `ghi.{nn}` | GitHub Issue discovered during work | `0.1.15-ghi.67` |

### Precedence

Per SemVer, pre-release versions have **lower precedence** than the associated normal version:

```text
0.1.15-obpi.01 < 0.1.15-obpi.02 < 0.1.15-ghi.67 < 0.1.15
```

When an ADR completes (e.g., `0.1.15`), all work-item identifiers (`-obpi.*`, `-ghi.*`) are
"rolled up" into the completed version.

### Examples

**Pre-1.0.0 (initial development):**

| Version | Meaning |
|---------|---------|
| `0.1.15` | ADR-0.1.15 completed |
| `0.1.15-obpi.01` | OBPI-0.1.15-01 in progress |
| `0.1.15-ghi.67` | GHI #67 discovered during 0.1.15 work |
| `0.2.0-pool.exog-pipeline` | ADR planned for 0.2.x, not yet started |

**Post-1.0.0 (stable API):**

| Version | Meaning |
|---------|---------|
| `1.2.3` | Current stable release |
| `1.2.4-obpi.01` | Patch-level work in progress |
| `1.3.0-pool.forecaster` | Minor-level feature in planning pool |
| `2.0.0-pool.breaking-change` | Major-level breaking change planned |

### Pool Artifacts

Pool ADRs live in `docs/design/adr/pool/` with pre-release identifiers:

```text
docs/design/adr/pool/
  ADR-0.2.0-pool.exog-pipeline.md       # lightweight intent only
  ADR-0.2.0-pool.forecaster-core.md
  ADR-1.3.0-pool.scheduler-cadence.md
```

**Pool Status Constraint (Binding):**

ADRs in the `docs/design/adr/pool/` directory may **ONLY** have status `Pool`.

| Rule | Enforcement |
|------|-------------|
| Pool ADRs have status `Pool` only | No other status permitted while in pool/ |
| Pool ADRs are lightweight | Intent only; no OBPI briefs required |
| Pool ADRs cannot be Proposed/Accepted | Must be pulled from pool first |
| Pool directory is the only valid location for Pool status | ADRs outside pool/ cannot have status Pool |

**Rationale:** The pool is a backlog of planned work, not active governance artifacts.
Pool ADRs await prioritization and do not participate in the gate system until pulled.

When pulled from pool:

1. Assign the next available version number (e.g., `0.2.1`)
2. Create full ADR folder structure under `docs/design/adr/adr-X.Y.x/`
3. Change status to `Draft` (or `Proposed` if ready for review)
4. Write OBPI briefs (required before `Accepted`)
5. Delete or archive the pool file

---

## Closeout Attestation to Status Mapping

When a human provides Gate 5 attestation, the ADR status updates as follows:

| Closeout Attestation | ADR Status | Notes |
|---------------------|------------|-------|
| **Completed** | Completed | All claims verified; work finished |
| **Completed — Partial: [reason]** | Completed | Deferrals documented in ADR Consequences section; follow-on ADRs created for deferred scope |
| **Dropped — [reason]** | Abandoned | Rationale recorded; ADR does not count toward roadmap |

---

## Audit Completion to Status Mapping

| Audit Outcome | ADR Status | Notes |
|--------------|------------|-------|
| Audit passes | Validated | Post-closeout reconciliation complete |
| Audit pending or failing | Completed | Remains in Phase 1 until resolved |

---

## State Transition Rules

1. **Pool → Draft**: ADR pulled from pool; author creates full structure in `adr-X.Y.x/`
2. **Draft → Proposed**: Author determines ADR is ready for review
3. **Proposed → Accepted**: Human reviews and accepts the proposal for implementation
4. **Accepted → Completed**: Human provides "Completed" or "Completed — Partial" attestation via closeout ceremony
5. **Accepted → Abandoned**: Human provides "Dropped" attestation or explicitly abandons work
6. **Any → Superseded**: A new ADR explicitly declares it supersedes this one (add `Superseded-By: ADR-X.Y.Z` to metadata)
7. **Completed → Validated**: Audit passes and reconciliation recorded

**Pool-specific constraints:**

- Pool ADRs cannot skip Draft (must be pulled and structured first)
- Pool ADRs may be abandoned directly (Pool → Abandoned) if deprioritized
- Pool is the only status valid in `pool/` directory; all other statuses require `adr-X.Y.x/`

---

## OBPI Completeness Requirement (Canonical)

**Binding rule:** OBPIs are co-created with the ADR, not deferred.

Before an ADR transitions to **Accepted** status:

- Each numbered checklist item in the Feature Checklist MUST have exactly one
  corresponding OBPI brief file in the `briefs/` directory
- Each brief MUST follow naming: `OBPI-{semver}-{nn}-{slug}.md`
- Each brief MUST reference its parent ADR and specific checklist item

**Rationale:** The Work Breakdown Structure (WBS) is a contract between ADR intent and
implementation. Orphaned checklist items (without briefs) create ambiguity about scope.
Co-creation ensures intent is locked with execution units at decision time.

**Verification:** The `gz-adr-manager` skill enforces this during ADR creation.
Manual verification: count checklist items in ADR, count brief files in `briefs/` — must match.

**Anti-pattern:** ADR tables listing OBPIs as "Pending" with no actual brief files.
This is a governance violation. All briefs must exist as files before Accepted.

---

## Deprecated Terms

The following terms have been used historically but are **not canonical**:

| Term | Disposition |
|------|-------------|
| Deprecated | Use "Superseded" with rationale, or "Abandoned" if no replacement |
| Pending | Use "Proposed" or "Accepted" depending on approval state |
| Retired | Use "Superseded" with backlink to replacement |
| Completed + Validated | Use "Validated" (legacy combined status) |

---

## ADR Status Table

The authoritative ADR status table lives at [adr-status.md](adr-status.md) (colocated in GovZero).

That table MUST use only the lifecycle states defined in this document.
Status values in that table are derived from this canon; if conflict exists, this document governs.

---

## ADR Series and Release Tagging

ADRs are organized into series by their minor version number. Each series has distinct governance characteristics.

### Series Classification

| Series | Name | Purpose | Release Tag Behavior |
|--------|------|---------|---------------------|
| **0.0.x** | Foundation | Infrastructure, governance, tooling | No release tags created |
| **0.1.x+** | Feature | User-facing capability, external contracts | Release tags created on validation |

**Foundation series (0.0.x):**

- Establishes project infrastructure, governance framework, and developer tooling
- Changes are internal/structural and do not constitute user-facing releases
- Validated foundation ADRs contribute to project maturity but do not trigger version bumps
- Example: ADR-0.0.21 (GovZero Layered Trust) — governance infrastructure, not a release

**Feature series (0.1.x and beyond):**

- Introduces user-facing capability, external API changes, or observable behavior changes
- Each validated ADR in a feature series represents a releasable increment
- Release tags track the highest validated feature-series ADR

### Release Tag Rule (Binding)

**The release tag SHALL be the highest validated non-foundation ADR.**

```text
Release Tag = v{highest validated ADR where series ≠ 0.0.x}
```

| Scenario | Highest Validated | Release Tag |
|----------|-------------------|-------------|
| ADR-0.1.14 validated | 0.1.14 | v0.1.14 |
| ADR-0.0.25 validated (foundation) | 0.1.14 (unchanged) | v0.1.14 (no change) |
| ADR-0.1.15 validated | 0.1.15 | v0.1.15 |

**Backfill validations:** When earlier ADRs are validated after later ones (e.g., 0.1.12 validated after 0.1.14), no new release tag is created — the release already advanced.

### Agent Enforcement

When validating an ADR, agents MUST:

1. Check if the ADR is in the foundation series (0.0.x)
2. If foundation: complete validation, no release tag action
3. If feature series: compare against current highest validated feature ADR
4. If this ADR > current highest: create release tag `v{ADR version}`
5. If this ADR ≤ current highest: no release tag action (backfill case)

---

## References

- Gate definitions: [charter.md](charter.md)
- Closeout ceremony: [audit-protocol.md](audit-protocol.md)
- Disposition rubric: [../ADR_DISPOSITION_RUBRIC.md](../ADR_DISPOSITION_RUBRIC.md)
- ADR status table: [adr-status.md](adr-status.md)
- Release doctrine: [releases/README.md](releases/README.md)
