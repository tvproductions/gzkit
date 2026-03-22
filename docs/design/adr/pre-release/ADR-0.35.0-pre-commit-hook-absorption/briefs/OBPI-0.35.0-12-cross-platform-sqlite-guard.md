---
id: OBPI-0.35.0-12-cross-platform-sqlite-guard
parent_adr: ADR-0.35.0-pre-commit-hook-absorption
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.35.0-12: cross-platform-sqlite-guard

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/ADR-0.35.0-pre-commit-hook-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.35.0-12 — "Evaluate cross-platform-sqlite-guard — SQLite cross-platform enforcement (not in gzkit)"`

## OBJECTIVE

Evaluate opsdev's `cross-platform-sqlite-guard` pre-commit hook — enforces SQLite usage patterns that work correctly across Windows, macOS, and Linux. gzkit does not currently have this hook. Determine: Absorb-PreCommit (enforce at commit time), Absorb-Claude (enforce during agent sessions), Absorb-Both, or Exclude. The key question is whether gzkit's cross-platform policy needs SQLite-specific enforcement beyond the general cross-platform rules.

## SOURCE MATERIAL

- **opsdev:** `.pre-commit-config.yaml` entry for `cross-platform-sqlite-guard`, implementation script
- **gzkit equivalent:** None (cross-platform policy exists but no SQLite-specific hook)

## ASSUMPTIONS

- gzkit uses SQLite and has cross-platform requirements (Windows primary, macOS, Linux)
- The hook likely detects: hardcoded paths, platform-specific SQLite pragmas, missing encoding parameters
- Cross-platform SQLite issues are subtle and easy to introduce accidentally
- The concept is governance-generic — any Python project using SQLite benefits

## NON-GOALS

- Changing the SQLite usage patterns themselves
- Implementing cross-platform SQLite abstractions
- Modifying opsdev's implementation

## REQUIREMENTS (FAIL-CLOSED)

1. Read the opsdev `cross-platform-sqlite-guard` hook implementation completely
1. Document: what patterns it detects, which files it scans, how it reports violations
1. Evaluate whether the detection patterns are applicable to gzkit's SQLite usage
1. Determine enforcement timing: pre-commit, Claude hook, or both
1. Record decision with rationale: Absorb-PreCommit / Absorb-Claude / Absorb-Both / Exclude

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
