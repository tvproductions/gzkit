# Plan: OBPI-0.27.0-01-router-skill-files

**OBPI:** OBPI-0.27.0-01-router-skill-files
**ADR:** ADR-0.27.0-namespace-router-product-surface
**Lane:** Lite
**Date:** 2026-05-23 (implemented), 2026-05-24 (plan record authored retroactively)

## Context

ADR-0.27.0 § Decision item #1:
> "OBPI-0.27.0-01: **router-skill-files** — Author the six namespace-router skill files (`gz-workflow`, `gz-governance`, `gz-quality`, `gz-project`, `gz-context`, `gz-manage`) under `.gzkit/skills/`. Each ≤ 500 bytes, intent-to-skill table only, no duplicated procedure or ceremony."

The current flat skill catalog exposes gzkit's internal governance ontology (ADR, OBPI, ARB, ledger, Gate 5, reconcile, attest) at the top level. Operators and models face a 60+ skill surface before they can express a first-stage intent. Six namespace router files with intent-to-skill tables solve this as a lightweight additive layer.

## Files

**Created:**
- `.gzkit/skills/gz-workflow/SKILL.md` — routes: design, plan, implement, verify, attest, release
- `.gzkit/skills/gz-governance/SKILL.md` — routes: adr create/promote/audit/status/sync, obpi specify/reconcile, ledger receipt, validate
- `.gzkit/skills/gz-quality/SKILL.md` — routes: check, complexity preview/authoring/distill, tech debt, arb receipts
- `.gzkit/skills/gz-project/SKILL.md` — routes: init, prd, constitution, status, state
- `.gzkit/skills/gz-context/SKILL.md` — routes: handoff, session resume, adr map, parity, docs
- `.gzkit/skills/gz-manage/SKILL.md` — routes: git sync, issue author/close/triage, patch release, agent sync, tidy
- `tests/skills/test_namespace_routers.py` — 3 tests, one per REQ

**Modified:**
- `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/obpis/OBPI-0.27.0-01-router-skill-files.md` — evidence sections, REQ derivation, byte-budget reconciliation

## Steps

1. Read ADR-0.27.0 § Decision and § Checklist item #1.
2. Derive three REQs from the checklist item:
   - REQ-0.27.0-01-01: Six router slugs have canonical SKILL.md files
   - REQ-0.27.0-01-02: Each SKILL.md frontmatter is valid (name, description, model)
   - REQ-0.27.0-01-03: Each body has exactly one intent table with valid routed skill slugs
3. Author `tests/skills/test_namespace_routers.py` — one test per REQ, RED first.
4. Author each of the six router SKILL.md files under `.gzkit/skills/`, targeting ≤700 bytes (operator-reconciled from plan's ≤500 byte target given schema-required frontmatter).
5. Run `uv run -m unittest tests.skills.test_namespace_routers` — confirm GREEN.
6. Run `uv run ruff check && uv run ruff format` — confirm clean.
7. Record Gate 2 evidence in OBPI brief.
8. Run `uv run gz covers OBPI-0.27.0-01-router-skill-files --plain` — confirm all REQs covered.

## Verification

```bash
# REQ coverage
uv run gz covers OBPI-0.27.0-01-router-skill-files --plain

# Tests
uv run -m unittest tests.skills.test_namespace_routers -v

# Size audit (≤700 bytes per router)
find .gzkit/skills/gz-{workflow,project,governance,quality,context,manage} -name SKILL.md -printf "%s\t%p\n" | sort -n

# Lint
uv run ruff check .
```

## Destination-in-mind disclosure (Step 6a)

The implementation approach was clear before authoring: six SKILL.md files with frontmatter + a single `| Intent | Skill |` table, no procedure duplication. The primary alternative considered and rejected was adding routing hints to the existing `gz-skill-router` skill rather than creating new namespace-router skills. This was rejected because namespace routers are additive (concrete skills remain directly invocable) and mirror GSD's architecture directly.

## Rejected alternatives

1. **Augment gz-skill-router with intent groups** — single skill, grouped table. Rejected: a single 60-entry table is not a router; it is the same flat catalog with cosmetic grouping.
2. **Alphabetical sub-categories in skill list** — CLI-side filtering only. Rejected: does not reduce token load at the model's skill-discovery step; models see the full list at skill load time.
3. **Single gz-router skill** — one skill, six sub-tables. Rejected: loads all routing at once; namespace routers are only effective if each is loaded independently.
