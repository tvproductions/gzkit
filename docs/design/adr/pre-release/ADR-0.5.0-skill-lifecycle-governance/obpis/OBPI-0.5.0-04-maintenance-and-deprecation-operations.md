---
id: OBPI-0.5.0-04-maintenance-and-deprecation-operations
parent: ADR-0.5.0-skill-lifecycle-governance
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.5.0-04-maintenance-and-deprecation-operations

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.5.0-skill-lifecycle-governance/ADR-0.5.0-skill-lifecycle-governance.md`
- **Checklist Item:** #4 -- "Define maintenance and deprecation operations."

## Objective

Define repeatable maintenance operations for skill lifecycle updates, deprecations, and parity hygiene so operations remain sustainable after initial migration.

## Lane

**Heavy**

## Allowed Paths

- `.gzkit/skills/**`
- `.agents/skills/**`
- `.claude/skills/**`
- `.github/skills/**`
- `docs/user/**`
- `docs/governance/**`
- `src/gzkit/skills.py`
- `src/gzkit/cli.py`
- `tests/**`

## Denied Paths

- `src/gzkit/ledger.py`
- `features/**`

## Requirements (FAIL-CLOSED)

1. Maintenance operations MUST define cadence and ownership for lifecycle metadata review.
2. Deprecation operations MUST define mirror behavior and operator communication requirements.
3. Maintenance workflow MUST preserve canonical-first synchronization semantics.

## Quality Gates

### Gate 1: ADR

- [x] Scope is linked to parent ADR item.

### Gate 2: TDD

- [ ] Maintenance/deprecation behavior tests added and passing.

### Gate 3: Docs

- [ ] Maintenance runbook and deprecation policy updated.

### Gate 4: BDD

- [x] N/A when `features/` is absent.

### Gate 5: Human

- [ ] Human attestation pending at ADR closeout.

## Acceptance Criteria

- [ ] Maintenance cadence and ownership are explicit.
- [ ] Deprecation semantics are documented and enforceable.
- [ ] Sync + audit behavior remains deterministic across lifecycle operations.
