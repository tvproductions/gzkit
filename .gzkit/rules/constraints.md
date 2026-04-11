---
id: constraints
paths:
  - "**"
description: Consolidated negative constraints — what agents must NOT do
---

# Negative Constraints (Consolidated)

> Positive specs leave an implied gap. Negative constraints close that gap.

This surface consolidates every "do not" rule scattered across gzkit's rules,
skills, and governance docs into one discoverable location. Agents read this
on every path. The source-of-truth remains the individual rule or skill —
this file is a cross-reference, not a replacement.

## TDD Discipline

Source: `.gzkit/rules/tests.md`

- Do not write tests after implementation that confirm what the code already does
- Do not write tests "alongside" without seeing them fail first (skipping Red)
- Do not batch all tests before any implementation (test-dump, not TDD)
- Do not refactor while tests are still failing (mixing Green and Refactor)
- Do not derive test cases from the implementation — derive from OBPI brief acceptance criteria

## Data Models

Source: `.gzkit/rules/models.md`

- Do not use stdlib `dataclass` for governance data — use Pydantic `BaseModel`
- Do not use Pydantic without `ConfigDict`
- Do not use `Optional`/`List` — use `| None` and `list[]`

## Surface Sync

Source: `.gzkit/rules/skill-surface-sync.md`

- Do not edit `.claude/rules/` directly — sync overwrites it from `.gzkit/rules/`
- Do not edit `.claude/skills/` directly — edit `.gzkit/skills/` and sync
- Do not edit a skill without bumping its `skill-version`
- Do not manually copy skill files between surfaces — use the sync command
- Do not skip sync because "both files look the same"

## Documentation Covenant

Source: `.gzkit/rules/gate5-runbook-code-covenant.md`

- Do not leave placeholder output examples
- Do not update code without docs when command output changes
- Do not declare completion without explicit human attestation for heavy/foundation scope

## Pipeline Lifecycle

Source: `.gzkit/skills/gz-obpi-pipeline/SKILL.md`

- Do not summarize after Stage 2 or 3 and stop — all 5 stages must run
- Do not treat "tests passing" as completion — that is Stage 3, not Stage 5
- Do not let the user "handle the rest" — the pipeline exists so they don't have to
- Do not work around hook blocks — diagnose the cause, never create marker files manually
- Do not derive tasks from the brief when no plan receipt exists — enter plan mode first
- Do not skip planning because the brief "seems clear enough"

## OBPI Completion

Source: `.gzkit/skills/gz-obpi-brief/assets/OBPI_BRIEF-template.md`

- Do not invent files outside the ALLOWED PATHS list
- Do not assume config keys exist — verify in `.gzkit.json` or `.gzkit/manifest.json`
- Do not reference test data not present in `fixtures/**` or `data/**`
- Do not commit `TODO`, `FIXME`, `@skip`, or incomplete implementations
- Do not stage private/hidden work — all work must be visible
- Do not mark a Heavy lane OBPI as completed before human attestation

## ADR Closeout

Source: `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md`

- Do not let agents decide completion — the human attests
- Do not accept vague acknowledgment ("ok", "looks good") as attestation
- Do not skip the walkthrough because OBPIs individually passed
- Do not work around CLI errors with prose or ad-hoc code — fix root cause
- Do not leave ceremony state uncommitted — sync the repo after attestation

## ADR Creation

Source: `.gzkit/skills/gz-adr-create/SKILL.md`

- Do not create ADR files first then "backfill" interview answers
- Do not fabricate interview answers without asking the human
- Do not skip the interview because "the intent is already clear"
- Do not run the interview after OBPI co-creation
- Do not leave ADR table showing "Pending" OBPIs with no actual brief files

## State Doctrine

Source: `docs/governance/state-doctrine.md`

- Do not read YAML frontmatter `status: Completed` as proof of completion — read the ledger
- Do not use pipeline marker existence as gate evidence — markers are L3, use ledger events
- Do not manually edit `.gzkit/ledger.jsonl` — use `gz` commands to emit events
- Do not treat reconciliation as optional maintenance — drift accumulates
- Do not block a gate check on a missing L3 artifact — only L1/L2 evidence can block gates

## Storage Tiers

Source: `docs/governance/storage-tiers.md`

- Do not let Tier B cache accumulate non-derivable state
- Do not let external services become prerequisites for `gz` commands
- Do not duplicate Tier A data in Tier B with potential divergence
- Do not store config in environment variables — config must be in git

## Architectural Boundaries

Source: `CLAUDE.md` (Architecture Planning Memo)

- Do not promote post-1.0 pool ADRs into active work
- Do not add more pool ADRs to the runtime track
- Do not build the graph engine without locking state doctrine first
- Do not let reconciliation remain a maintenance chore
- Do not let AirlineOps parity become perpetual catch-up
- Do not let derived views silently become source-of-truth
