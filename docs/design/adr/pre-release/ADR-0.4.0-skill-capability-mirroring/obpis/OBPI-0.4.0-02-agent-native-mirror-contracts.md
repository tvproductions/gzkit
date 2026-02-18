---
id: OBPI-0.4.0-02-agent-native-mirror-contracts
parent: ADR-0.4.0-skill-capability-mirroring
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.4.0-02-agent-native-mirror-contracts

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.4.0-skill-capability-mirroring/ADR-0.4.0-skill-capability-mirroring.md`
- **Checklist Item:** #2 -- "Define and enforce agent-native mirror contracts."

## Objective

Define a deterministic mirror contract for `.agents`, `.claude`, and `.github` skill surfaces, including required files, naming, and metadata invariants.

## Lane

**Heavy**

## Allowed Paths

- `.gzkit/skills/**`
- `.agents/skills/**`
- `.claude/skills/**`
- `.github/skills/**`
- `src/gzkit/sync.py`
- `src/gzkit/skills.py`
- `src/gzkit/cli.py`
- `docs/user/commands/**`
- `tests/**`

## Denied Paths

- `src/gzkit/ledger.py`
- `features/**`

## Requirements (FAIL-CLOSED)

1. Canonical skill IDs MUST be kebab-case and mirror directory names.
2. Canonical and mirrored skills MUST expose the same required frontmatter identity fields.
3. Mirror-specific drift MUST be treated as a blocking parity failure.

## Quality Gates

### Gate 1: ADR

- [x] Scope is linked to parent ADR item.

### Gate 2: TDD

- [ ] Command and module tests added for mirror contract checks.

### Gate 3: Docs

- [ ] Operator docs updated for mirror contract behavior.

### Gate 4: BDD

- [x] N/A when `features/` is absent.

### Gate 5: Human

- [ ] Human attestation pending at ADR closeout.

## Acceptance Criteria

- [ ] Mirror contract rules are documented and enforced.
- [ ] Drift between canonical and mirror metadata is blocking.
- [ ] Contract behavior is covered by tests.
