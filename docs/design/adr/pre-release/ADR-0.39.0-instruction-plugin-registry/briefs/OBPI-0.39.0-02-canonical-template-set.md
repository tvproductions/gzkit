---
id: OBPI-0.39.0-02-canonical-template-set
parent_adr: ADR-0.39.0-instruction-plugin-registry
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.39.0-02: Canonical Template Set

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.39.0-instruction-plugin-registry/ADR-0.39.0-instruction-plugin-registry.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.39.0-02 — "Canonical template set — extract gzkit's current rules into shippable, versioned templates"`

## OBJECTIVE

Extract gzkit's current instruction files (`.claude/rules/*.md`) into a shippable canonical template set. Each instruction must be cataloged, versioned, assigned a scope, and packaged so that downstream projects can receive them through the registry. The canonical set represents gzkit's authoritative governance rules that all projects must comply with (unless explicitly overridden through the extension mechanism).

## SOURCE MATERIAL

- **Current instructions:** `.claude/rules/*.md` — cross-platform.md, tests.md, models.md, pythonic.md, cli.md, arb.md, chores.md, governance-core.md, gh-cli.md, adr-audit.md, gate5-runbook-code-covenant.md
- **Mirror location:** `.github/instructions/` — same content, different vendor surface

## ASSUMPTIONS

- Every current instruction file is a candidate for the canonical set
- Some instructions may be gzkit-repo-specific (not canonical for all projects) — these must be identified and excluded from the canonical set
- Each canonical instruction needs: id, version, scope (path globs from frontmatter), description, content hash for change detection
- The canonical set must be versioned as a whole (set version) and individually (instruction version)

## NON-GOALS

- Designing the extension mechanism — that is OBPI-0.39.0-03
- Building the distribution mechanism (how templates reach projects) — that is a deployment concern
- Modifying instruction content — only packaging existing instructions into the registry format

## REQUIREMENTS (FAIL-CLOSED)

1. Catalog every instruction file in `.claude/rules/` with its scope, purpose, and line count
1. Classify each as canonical (framework-level, applies to all projects) or repo-specific (gzkit only)
1. For each canonical instruction: create a registry entry with id, version, scope, content hash
1. Package the canonical set with a set-level manifest (version, instruction list, compatibility)
1. Write unit tests verifying the canonical set is complete and all entries are valid
1. Document the canonical instruction catalog with purpose descriptions

## ALLOWED PATHS

- `src/gzkit/instructions/` — canonical template packaging
- `data/` — canonical instruction set storage
- `tests/` — unit tests
- `docs/design/adr/pre-release/ADR-0.39.0-instruction-plugin-registry/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Canonical catalog documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
