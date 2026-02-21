---
id: OBPI-0.4.0-02-agent-native-mirror-contracts
parent: ADR-0.4.0-skill-capability-mirroring
item: 2
lane: Heavy
status: Completed
---

# OBPI-0.4.0-02-agent-native-mirror-contracts

**Brief Status:** Completed

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

- [x] Command and module tests added for mirror contract checks.

### Gate 3: Docs

- [x] Operator docs updated for mirror contract behavior.

### Gate 4: BDD

- [x] N/A when `features/` is absent.

### Gate 5: Human

- [ ] Human attestation pending at ADR closeout.

## Acceptance Criteria

- [x] Mirror contract rules are documented and enforced.
- [x] Drift between canonical and mirror metadata is blocking.
- [x] Contract behavior is covered by tests.

## Evidence

### Implementation Summary

- Files created/modified: `src/gzkit/skills.py`, `tests/test_skills_audit.py`, `docs/user/commands/skill-audit.md`, `.agents/skills/**/SKILL.md`, `.claude/skills/**/SKILL.md`, `.github/skills/**/SKILL.md`
- Contract enforcement: mirror identity fields (`name`, `description`, `lifecycle_state`, `owner`, `last_reviewed`) are fail-closed parity checks; mirror name must match mirror directory name
- Drift remediation: ran `uv run gz agent sync control-surfaces` and removed legacy mirror-only `.claude/skills/commit`
- Validation commands run: `uv run -m unittest tests.test_skills_audit tests.test_cli.TestSkillCommands tests.test_sync.TestSyncControlSurfaces`, `uv run gz skill audit --json`, `uv run gz lint`, `uv run gz typecheck`, `uv run -m unittest`
- Date completed: 2026-02-21
