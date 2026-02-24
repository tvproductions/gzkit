---
id: OBPI-0.5.0-01-skill-taxonomy-and-capability-model
parent: ADR-0.5.0-skill-lifecycle-governance
item: 1
lane: Heavy
status: Completed
---

# OBPI-0.5.0-01-skill-taxonomy-and-capability-model

**Brief Status:** Completed

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

- [x] Tests validate taxonomy-required fields.

### Gate 3: Docs

- [x] Taxonomy contract documented for operators.

### Gate 4: BDD

- [x] N/A when `features/` is absent.

### Gate 5: Human

- [x] OBPI human attestation recorded (ADR-level Gate 5 closeout remains separate).

## Acceptance Criteria

- [x] Required lifecycle metadata contract is explicit and test-covered.
- [x] Canonical taxonomy is reflected in skill template and docs.
- [x] Mirrors preserve taxonomy fields.

## Evidence

### Implementation Summary

- Files created/modified: `src/gzkit/skills.py`, `src/gzkit/sync.py`, `src/gzkit/templates/skill.md`, `docs/user/commands/skill-audit.md`, `docs/governance/GovZero/layered-trust.md`, `tests/test_cli.py`, `tests/test_skills_audit.py`, `tests/test_sync.py`
- Tests added: `tests/test_skills_audit.py` (capability/metadata taxonomy and mirror parity scenarios), `tests/test_sync.py` (canonical preflight metadata validation scenarios)
- Validation commands run: `uv run gz format`, `uv run gz lint`, `uv run -m unittest discover tests`, `uv run gz skill audit --json`, `uv run gz check`
- Validation outcome: PASS (`Ran 233 tests`; lint/format/typecheck/test/skill-audit all passed)
- Human attestation: User accepted completion in-session ("attest completed") on 2026-02-24.
- Date completed: 2026-02-24
