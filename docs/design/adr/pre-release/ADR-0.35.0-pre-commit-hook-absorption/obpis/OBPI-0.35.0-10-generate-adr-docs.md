---
id: OBPI-0.35.0-10-generate-adr-docs
parent: ADR-0.35.0-pre-commit-hook-absorption
item: 10
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.35.0-10: generate-adr-docs

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/ADR-0.35.0-pre-commit-hook-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.35.0-10 — "Evaluate generate-adr-docs — ADR documentation generation (not in gzkit)"`

## OBJECTIVE

Evaluate opsdev's `generate-adr-docs` pre-commit hook — automatically generates or updates ADR index/summary documentation when ADR files change. gzkit does not currently have this hook. Determine: Absorb-PreCommit (auto-generate docs on commit), Absorb-Claude (generate during agent sessions), Absorb-Both, or Exclude. The key question is whether automated ADR documentation generation prevents drift between ADR files and their index.

## SOURCE MATERIAL

- **opsdev:** `.pre-commit-config.yaml` entry for `generate-adr-docs`, implementation script
- **gzkit equivalent:** None

## ASSUMPTIONS

- ADR documentation drift is a real problem as the ADR corpus grows
- The hook likely regenerates an ADR index, summary table, or mkdocs navigation
- gzkit's growing ADR corpus (35+ ADRs) would benefit from automated index maintenance
- Pre-commit timing ensures documentation is always in sync with ADR files

## NON-GOALS

- Changing the ADR documentation format
- Generating documentation for non-ADR artifacts
- Modifying opsdev's implementation

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev `generate-adr-docs` hook implementation completely
1. Document: what it generates, what triggers it, what files it modifies
1. Evaluate whether gzkit needs automated ADR documentation generation
1. Determine enforcement timing: pre-commit, Claude hook, or both
1. Record decision with rationale: Absorb-PreCommit / Absorb-Claude / Absorb-Both / Exclude

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.35.0-10-01: Read the opsdev `generate-adr-docs` hook implementation completely
- [x] REQ-0.35.0-10-02: Document: what it generates, what triggers it, what files it modifies
- [x] REQ-0.35.0-10-03: Evaluate whether gzkit needs automated ADR documentation generation
- [x] REQ-0.35.0-10-04: Determine enforcement timing: pre-commit, Claude hook, or both
- [x] REQ-0.35.0-10-05: Record decision with rationale: Absorb-PreCommit / Absorb-Claude / Absorb-Both / Exclude


## ALLOWED PATHS

- `.pre-commit-config.yaml` — hook configuration
- `src/gzkit/hooks/` — hook implementations
- `.claude/hooks/` — Claude hook configurations
- `tests/` — tests for absorbed hooks
- `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
