---
id: OBPI-0.4.0-04-mirror-compat-migration
parent: ADR-0.4.0-skill-capability-mirroring
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.4.0-04-mirror-compat-migration

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.4.0-skill-capability-mirroring/ADR-0.4.0-skill-capability-mirroring.md`
- **Checklist Item:** #4 -- "Complete compatibility migration and cleanup."

## Objective

Complete transition from legacy opsdev-era assumptions to canonical `gz` skill parity semantics while preserving operability during migration.

## Lane

**Heavy**

## Allowed Paths

- `.gzkit/skills/**`
- `.agents/skills/**`
- `.claude/skills/**`
- `.github/skills/**`
- `AGENTS.md`
- `CLAUDE.md`
- `.github/copilot-instructions.md`
- `docs/governance/**`
- `docs/user/**`
- `tests/**`

## Denied Paths

- `src/gzkit/ledger.py`
- `features/**`

## Requirements (FAIL-CLOSED)

1. Active control surfaces MUST not reference obsolete opsdev runtime commands.
2. Migration updates MUST preserve canonical lineage and mirror synchronization semantics.
3. Cleanup MUST not rewrite historical evidence artifacts that are intentionally archival.

## Quality Gates

### Gate 1: ADR

- [x] Scope is linked to parent ADR item.

### Gate 2: TDD

- [ ] Regression checks cover migration outcomes.

### Gate 3: Docs

- [ ] Governance and operator docs updated for post-migration terminology.

### Gate 4: BDD

- [x] N/A when `features/` is absent.

### Gate 5: Human

- [ ] Human attestation pending at ADR closeout.

## Acceptance Criteria

- [ ] Active control surfaces are opsdev-free.
- [ ] Migration docs distinguish historical references from active surfaces.
- [ ] Quality and governance checks pass after migration.
