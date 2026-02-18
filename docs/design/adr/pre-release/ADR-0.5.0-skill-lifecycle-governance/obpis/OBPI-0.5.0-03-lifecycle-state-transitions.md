---
id: OBPI-0.5.0-03-lifecycle-state-transitions
parent: ADR-0.5.0-skill-lifecycle-governance
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.5.0-03-lifecycle-state-transitions

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.5.0-skill-lifecycle-governance/ADR-0.5.0-skill-lifecycle-governance.md`
- **Checklist Item:** #3 -- "Define lifecycle state transitions and evidence semantics."

## Objective

Define lifecycle transition semantics for skill artifacts (`draft`, `active`, `deprecated`, `retired`) and the evidence expected for each transition.

## Lane

**Heavy**

## Allowed Paths

- `.gzkit/skills/**`
- `docs/governance/**`
- `docs/user/**`
- `src/gzkit/skills.py`
- `tests/**`

## Denied Paths

- `src/gzkit/ledger.py`
- `features/**`

## Requirements (FAIL-CLOSED)

1. Lifecycle states MUST have explicit transition rules.
2. Transition rules MUST identify required evidence and operator responsibilities.
3. Invalid or unsupported transitions MUST fail validation checks.

## Quality Gates

### Gate 1: ADR

- [x] Scope is linked to parent ADR item.

### Gate 2: TDD

- [ ] Transition validation tests added and passing.

### Gate 3: Docs

- [ ] Lifecycle transition policy documented.

### Gate 4: BDD

- [x] N/A when `features/` is absent.

### Gate 5: Human

- [ ] Human attestation pending at ADR closeout.

## Acceptance Criteria

- [ ] Lifecycle transition rules are explicit and test-covered.
- [ ] Invalid transition behavior is fail-closed.
- [ ] Operator evidence expectations are documented.
