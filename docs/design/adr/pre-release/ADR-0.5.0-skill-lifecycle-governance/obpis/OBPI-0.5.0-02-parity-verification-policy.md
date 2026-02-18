---
id: OBPI-0.5.0-02-parity-verification-policy
parent: ADR-0.5.0-skill-lifecycle-governance
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.5.0-02-parity-verification-policy

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.5.0-skill-lifecycle-governance/ADR-0.5.0-skill-lifecycle-governance.md`
- **Checklist Item:** #2 -- "Define parity verification policy and runtime checks."

## Objective

Define and implement policy-backed parity checks so mirror drift and metadata violations are surfaced as explicit governance failures.

## Lane

**Heavy**

## Allowed Paths

- `src/gzkit/skills.py`
- `src/gzkit/cli.py`
- `src/gzkit/quality.py`
- `docs/user/commands/**`
- `tests/**`

## Denied Paths

- `src/gzkit/ledger.py`
- `features/**`

## Requirements (FAIL-CLOSED)

1. Parity policy MUST define blocking vs non-blocking findings.
2. Runtime command surface MUST expose parity checks for operators.
3. Aggregate quality checks MUST include parity audit execution.

## Quality Gates

### Gate 1: ADR

- [x] Scope is linked to parent ADR item.

### Gate 2: TDD

- [ ] CLI and parity-policy tests added and passing.

### Gate 3: Docs

- [ ] Command docs updated for parity policy behavior.

### Gate 4: BDD

- [x] N/A when `features/` is absent.

### Gate 5: Human

- [ ] Human attestation pending at ADR closeout.

## Acceptance Criteria

- [ ] `gz skill audit` reports parity findings deterministically.
- [ ] `gz check` includes skill parity audit.
- [ ] Policy behavior is documented and validated by tests.
