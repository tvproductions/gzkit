---
id: OBPI-0.4.0-04-mirror-compat-migration
parent: ADR-0.4.0-skill-capability-mirroring
item: 4
lane: Heavy
status: Completed
---

# OBPI-0.4.0-04-mirror-compat-migration

**Brief Status:** Completed

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
- `src/gzkit/cli.py`
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

- [x] Regression checks cover migration outcomes.

### Gate 3: Docs

- [x] Governance and operator docs updated for post-migration terminology.

### Gate 4: BDD

- [x] N/A when `features/` is absent.

### Gate 5: Human

- [x] OBPI acceptance recorded (ADR-level Gate 5 closeout remains separate).

## Acceptance Criteria

- [x] Active control surfaces are opsdev-free.
- [x] Migration docs distinguish historical references from active surfaces.
- [x] Quality and governance checks pass after migration.

## Evidence

### Implementation Summary

- Files created/modified: `src/gzkit/cli.py`, `tests/test_cli.py`, `docs/user/commands/git-sync.md`, `docs/user/runbook.md`, `.gzkit/skills/git-sync/SKILL.md`, `.agents/skills/git-sync/SKILL.md`, `.claude/skills/git-sync/SKILL.md`, `.github/skills/git-sync/SKILL.md`
- Hard cutover delivered:
  - Removed CLI aliases `sync-repo`, `agent-control-sync`, and top-level `sync`.
  - Updated active operator docs to canonical command surfaces only.
  - Added explicit archival-vs-active command-surface distinction in `docs/user/runbook.md`.
- Validation commands run:
  - `uv run -m unittest tests.test_cli.TestGitSyncCommand tests.test_cli.TestSyncCommand`
  - `uv run gz agent sync control-surfaces`
  - `uv run gz lint`
  - `uv run gz typecheck`
  - `uv run gz cli audit`
  - `uv run gz check`
- Date implemented: 2026-02-21

## OBPI Acceptance Ceremony

### Value Narrative

Before this OBPI, active runtime/control surfaces still carried compatibility aliases and legacy migration language that blurred the canonical command contract. After this OBPI, active surfaces use canonical `gz` commands only, legacy alias entry points are removed from runtime and docs, and archival historical references are explicitly separated from active operator guidance.

### Key Proof

- Alias removal proof: `tests/test_cli.py` validates `sync-repo`, `agent-control-sync`, and `sync` now fail parse as invalid commands, while canonical commands continue to pass.
- Active-surface cleanup proof: `docs/user/commands/git-sync.md` no longer documents alias usage.
- Archival distinction proof: `docs/user/runbook.md` now states `docs/user/reference/**` is archival and non-normative for active command contracts.

### Human Attestation

- Attested by: Jeff (human operator)
- Attestation: Completed
- Method: explicit acceptance in session (`attest completed`)
- Date: 2026-02-21
