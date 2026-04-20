---
id: OBPI-0.0.18-05-skill-prompt-enrichment
parent: ADR-0.0.18-adr-taxonomy-doctrine
item: 5
lane: Lite
status: Completed
---

# OBPI-0.0.18-05-skill-prompt-enrichment: skill prompt updates for --kind

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md`
- **Checklist Item:** #5 — "Skill prompt enrichment"

**Status:** Draft

## Objective

Update `.gzkit/skills/gz-plan/SKILL.md` and `.gzkit/skills/gz-adr-create/SKILL.md` so their interview prompts ask for `--kind` explicitly, show the concise decision heuristic inline, and link to the concepts page (OBPI-01). Skill versions are bumped per `.gzkit/rules/skill-surface-sync.md`; mirrors (`.claude/skills/`, `.github/skills/`) are regenerated via `gz agent sync control-surfaces`.

## Lane

**Lite** — skill-layer updates, no CLI contract change.

## Allowed Paths

- `.gzkit/skills/gz-plan/SKILL.md`
- `.gzkit/skills/gz-adr-create/SKILL.md`
- `.claude/skills/gz-plan/SKILL.md` (mirror — regenerated via sync)
- `.claude/skills/gz-adr-create/SKILL.md` (mirror — regenerated via sync)
- `.github/skills/gz-plan/SKILL.md` (mirror)
- `.github/skills/gz-adr-create/SKILL.md` (mirror)
- `.agents/skills/gz-plan/SKILL.md` (mirror)
- `.agents/skills/gz-adr-create/SKILL.md` (mirror)

## Denied Paths

- Any other skill — scope is strictly `gz-plan` and `gz-adr-create`
- CLI command implementations (ADR-0.0.17 scope)
- Concept/runbook/policy pages (OBPI-01, 02, 03 of this ADR)

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md` and `CLAUDE.md` — agent operating contract
- [x] Parent ADR for intent and scope

**Context:**

- [x] Parent ADR: `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md`
- [x] Sibling OBPIs 01 (concepts page) and ADR-0.0.17 (CLI mechanical surface for `--kind`)

**Prerequisites (check existence, STOP if missing):**

- [x] `.gzkit/skills/gz-plan/SKILL.md` present
- [x] `.gzkit/skills/gz-adr-create/SKILL.md` present
- [x] `docs/user/concepts/adr-taxonomy.md` landed by OBPI-0.0.18-01

**Existing Code (understand current state):**

- [x] `.gzkit/rules/skill-surface-sync.md` § Version discipline — governance-rule change bumps minor
- [x] Surveyed sibling skills for `metadata.skill-version` convention

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this brief
- [x] Parent ADR checklist item #5 ("Skill prompt enrichment") quoted

### Gate 2: TDD

- [x] Pure skill-documentation OBPI — no `@covers` unit tests added
- [x] `uv run gz lint` (ruff) clean via ARB
- [x] `uv run gz validate --skill-alignment` clean

### Gate 3: Docs

- [x] `uv run gz agent sync control-surfaces` clean; mirrors regenerated
- [x] Both edited skills render consistently across canonical and mirror paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Both skills' interview sections prompt for `--kind` with the concise heuristic: "foundation (app/system invariant, always 0.0.x) / feature (release-carrying capability) / pool (noted, not committed)".
2. REQUIREMENT: Both skills cite `docs/user/concepts/adr-taxonomy.md` by path at the prompt for operators wanting deeper context.
3. REQUIREMENT: `skill-version` in frontmatter is bumped (minor, per governance-rule-change classification in `.gzkit/rules/skill-surface-sync.md` § Version discipline).
4. REQUIREMENT: `uv run gz agent sync control-surfaces` runs clean after edits — no drift between canonical `.gzkit/skills/` and mirrors.
5. REQUIREMENT: The skill prompts NEVER embed a default for `--kind`. The whole point of the no-default CLI design (ADR-0.0.17 OBPI-02 REQ-01) is to force an informed choice; skills must preserve that forcing function.
6. REQUIREMENT: Body language in the skill respects the vocabulary locked in ADR-0.0.17 — `pool`, `foundation`, `feature` only. No residual informal terms like "normal ADR", "work ADR", "versioned ADR".

## Verification

```bash
uv run gz agent sync control-surfaces
# Confirm no drift output; diff shows frontmatter version bump + prompt updates
uv run gz validate --skill-alignment  # skill must still have a wielded CLI verb
```

## Acceptance Criteria

<!--
Each checkbox carries a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [x] REQ-0.0.18-05-01: Both skills' interview sections prompt for `--kind` with the concise heuristic (foundation / feature / pool) inline.
- [x] REQ-0.0.18-05-02: Both skills cite `docs/user/concepts/adr-taxonomy.md` by path for deeper context.
- [x] REQ-0.0.18-05-03: `skill-version` bumped per `.gzkit/rules/skill-surface-sync.md` § Version discipline (gz-plan established at 1.0.0; gz-adr-create 6.0.3 → 6.1.0).
- [x] REQ-0.0.18-05-04: `uv run gz agent sync control-surfaces` runs clean; canonical and mirrors agree.
- [x] REQ-0.0.18-05-05: Skill prompts never embed a default for `--kind` — the no-default forcing function (ADR-0.0.17 OBPI-02 REQ-01) is preserved.
- [x] REQ-0.0.18-05-06: Body language respects the vocabulary locked in ADR-0.0.17 — only `pool`, `foundation`, `feature` in the edited files.

## Evidence

- Skill diff showing prompt additions + version bump
- Sync transcript showing no drift
- `gz validate --skill-alignment` clean output
- ARB receipts

### Implementation Summary


- gz-plan SKILL: Added metadata.skill-version 1.0.0 and new step-6 --kind prompt with foundation/feature/pool heuristic and link to docs/user/concepts/adr-taxonomy.md.
- gz-adr-create SKILL: Bumped metadata.skill-version 6.0.3 -> 6.1.0; added Tier 1 pro-forma --kind question with the same heuristic; flagged --kind as non-deducible.
- Mirrors: .claude/, .github/, .agents/ regenerated via uv run gz agent sync control-surfaces; no drift between canonical and mirror copies.
- Forcing function preserved: no default value proposed for --kind in either skill, honoring ADR-0.0.17 OBPI-02 REQ-01.
- Brief grooming (in-scope per Invariants 2/4): added Discovery Checklist, Quality Gates, Acceptance Criteria (REQ-0.0.18-05-01..06), Implementation Summary, Key Proof, Human Attestation, and Completion Checklist sections to satisfy Stage 5 precomplete brief_readiness.

### Key Proof


- grep -n 'What kind of ADR is this' .gzkit/skills/gz-adr-create/SKILL.md -> L174 shows the pro-forma line with the foundation/feature/pool heuristic and adr-taxonomy.md link.
- grep -n 'Ask the operator for' .gzkit/skills/gz-plan/SKILL.md -> L28 shows the explicit --kind prompt in the workflow.
- uv run gz validate --skill-alignment -> '+ All validations passed (1 scopes)'.
- uv run gz agent sync control-surfaces -> 'Sync complete.' with mirror parity confirmed by diff -q canonical vs .claude/ (no output).
- ARB receipts: arb-ruff-f23dbf1fab71456ca10f6f68cdeb1d9c (lint clean); arb-step-unittest-6e0ef24567374ec088a9a1e11babc9fc (3249 tests OK).

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — Confirm decision: skill interviews now force an explicit --kind choice with inline foundation/feature/pool heuristic and concepts-page link; gz-plan skill-version established at 1.0.0, gz-adr-create bumped 6.0.3 -> 6.1.0 (minor, governance-rule change per skill-surface-sync.md). Receipts: lint arb-ruff-f23dbf1fab71456ca10f6f68cdeb1d9c; tests arb-step-unittest-6e0ef24567374ec088a9a1e11babc9fc. Skill alignment passes; mirrors regenerated clean via gz agent sync control-surfaces.
- Date: 2026-04-20

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in this brief
- [ ] **Gate 2 (TDD):** Lint + skill-alignment + unittest clean (receipts captured)
- [ ] **Gate 3 (Docs):** `gz agent sync control-surfaces` clean; mirrors regenerated
- [ ] **Lane-appropriate attestation:** Lite lane — Gate 5 not required; foundation-kind walkthrough discipline applies at ADR closeout

## REQ Coverage

- REQ-0.0.18-05-01 through REQ-0.0.18-05-06
