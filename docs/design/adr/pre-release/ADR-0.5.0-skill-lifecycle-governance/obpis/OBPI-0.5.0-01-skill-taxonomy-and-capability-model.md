---
id: OBPI-0.5.0-01-skill-taxonomy-and-capability-model
parent: ADR-0.5.0-skill-lifecycle-governance
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.5.0-01-skill-taxonomy-and-capability-model

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.5.0-skill-lifecycle-governance/ADR-0.5.0-skill-lifecycle-governance.md`
- **Checklist Item:** #1 -- "Define skill taxonomy and capability model."

## Objective

Define canonical skill identity, capability taxonomy, and required lifecycle metadata fields that all agent-native mirrors must preserve.

## Lane

**Heavy**

## Allowed Paths

- `.gzkit/skills/**`
- `src/gzkit/skills.py`
- `src/gzkit/templates/skill.md`
- `docs/user/**`
- `docs/governance/**`
- `tests/**`

## Denied Paths

- `src/gzkit/ledger.py`
- `features/**`

## Requirements (FAIL-CLOSED)

1. Taxonomy MUST distinguish identity fields from lifecycle and behavioral metadata.
2. Required lifecycle fields MUST be defined for all active canonical skills.
3. Taxonomy changes MUST remain backward-compatible with mirror synchronization.

## Quality Gates

### Gate 1: ADR

- [x] Scope is linked to parent ADR item.

### Gate 2: TDD

- [ ] Tests validate taxonomy-required fields.

### Gate 3: Docs

- [ ] Taxonomy contract documented for operators.

### Gate 4: BDD

- [x] N/A when `features/` is absent.

### Gate 5: Human

- [ ] Human attestation pending at ADR closeout.

## Acceptance Criteria

- [ ] Required lifecycle metadata contract is explicit and test-covered.
- [ ] Canonical taxonomy is reflected in skill template and docs.
- [ ] Mirrors preserve taxonomy fields.
