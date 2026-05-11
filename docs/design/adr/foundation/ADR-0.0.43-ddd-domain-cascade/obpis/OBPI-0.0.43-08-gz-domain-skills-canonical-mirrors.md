---
id: OBPI-0.0.43-08-gz-domain-skills-canonical-mirrors
parent: ADR-0.0.43
item: 8
lane: Heavy
status: Draft
---

# OBPI-0.0.43-08-gz-domain-skills-canonical-mirrors: gz-domain-enumerate + gz-domain-model skills

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.43-ddd-domain-cascade/ADR-0.0.43-ddd-domain-cascade.md`
- **Checklist Item:** #8 — "gz-domain-enumerate + gz-domain-model skills (canonical + mirrors) — Two new skills authored at `.gzkit/skills/gz-domain-enumerate/` and `.gzkit/skills/gz-domain-model/`; both follow gz-design conversational shape; both opus-tier; sync through `gz agent sync control-surfaces`."

**Status:** Draft

## Objective

Land two new skills under `.gzkit/skills/` — `gz-domain-enumerate` (strategic BC enumeration + context-map authoring, conversational) and `gz-domain-model` (per-BC tactical DM authoring, conversational). Both follow the `gz-design` skill's draft-first-then-ask conversational pattern, both are opus-tier, and both sync through `gz agent sync control-surfaces` to `.claude/skills/` and `.agents/skills/` mirrors.

## Lane

**Heavy** — introduces two new canonical skills with cross-surface mirroring. Skill surface is a public operator contract.

## Allowed Paths

- `.gzkit/skills/gz-domain-enumerate/SKILL.md` — NEW
- `.gzkit/skills/gz-domain-enumerate/agents/` — NEW (if subagent assets needed)
- `.gzkit/skills/gz-domain-model/SKILL.md` — NEW
- `.gzkit/skills/gz-domain-model/agents/` — NEW (if subagent assets needed)
- `.claude/skills/gz-domain-enumerate/SKILL.md` — NEW (synced)
- `.claude/skills/gz-domain-model/SKILL.md` — NEW (synced)
- `.agents/skills/gz-domain-enumerate/SKILL.md` — NEW (synced)
- `.agents/skills/gz-domain-model/SKILL.md` — NEW (synced)
- `.github/skills/gz-domain-enumerate/SKILL.md` — NEW (synced)
- `.github/skills/gz-domain-model/SKILL.md` — NEW (synced)
- `.gzkit/manifest.json` — EXTEND with two new skill entries
- `tests/skills/test_gz_domain_enumerate.py` — NEW (structural test: frontmatter, version, model)
- `tests/skills/test_gz_domain_model.py` — NEW

## Denied Paths

- Existing skills under `.gzkit/skills/*/SKILL.md` — OBPI-09 / 10 own extensions to existing skills
- `src/gzkit/**` — source surface
- `docs/**` — OBPI-12 owns documentation
- `src/gzkit/governance/**` — other OBPI scopes
- Runtime dependencies

## Requirements (FAIL-CLOSED)

1. **REQUIREMENT (`gz-domain-enumerate` SKILL.md).** Frontmatter declares `name: gz-domain-enumerate`, `persona: main-session`, `description` triggering on "enumerate BCs / bounded contexts / context map / domain map", `category: governance-infrastructure`, `model: opus`, `lifecycle_state: active`, `owner: gzkit-governance`, `skill-version: "1.0.0"`. Body conforms to skill schema (Step 0–N procedure, hard gates, anti-patterns, output contract).
2. **REQUIREMENT (`gz-domain-enumerate` workflow).** Step 1: read state. Step 2: clarify operator intent (one question at a time). Step 3: propose BCs / context-map entries from session evidence (draft-first). Step 4: section-by-section approval (BC list, then context-map entries). Step 5: write PRD § 2.2 and § 2.3 changes. Step 6: emit `bounded_context_created` and `context_map_updated` events.
3. **REQUIREMENT (`gz-domain-enumerate` first-run mode).** When `legacy-adr-bc-mapping.yaml` exists (OBPI-07 ratified), the skill's first-run mode reads it and proposes the bootstrap BC list pre-populated. When the mapping doesn't exist, the skill drives a from-scratch enumeration (used for fresh PRDs, not the gzkit project itself).
4. **REQUIREMENT (`gz-domain-model` SKILL.md).** Frontmatter parallel to `gz-domain-enumerate`. Triggers on "design DM-X / domain model for X / tactical DDD for X / aggregates for X". Body procedure mirrors gz-design's shape.
5. **REQUIREMENT (`gz-domain-model` workflow).** Step 1: confirm BC exists in PRD § 2.2. Step 2: read state for the BC (existing DM if any, ADRs / OBPIs / GHIs scoped to BC). Step 3: clarify scope (one aggregate at a time). Step 4: propose `Aggregate` + `Entity` + `ValueObject` + `DomainEvent` + `ImplementationSurface` + contracts. Step 5: section-by-section approval. Step 6: write DM file via `gz domain init` if new, or in-place edit if existing. Step 7: emit `domain_model_created` or `domain_model_revised`.
6. **REQUIREMENT (opus-tier discipline).** Both skills declare `model: opus`. Self-escalation directive present: "Spawn an `Agent` with `model='opus'` to execute this skill" — for non-opus sessions.
7. **REQUIREMENT (mirror sync).** Running `uv run gz agent sync control-surfaces` after authoring canonical SKILL.md propagates content to four mirror locations (`.claude/`, `.agents/`, `.github/`). No mirror authored directly.
8. **REQUIREMENT (manifest entry).** `.gzkit/manifest.json` lists both new skills under the canonical surface inventory. `gz validate --surfaces` clean post-sync.
9. **REQUIREMENT (skill-version bump rationale).** Both new skills start at `skill-version: "1.0.0"` per ADR-0.0.43 framework version (GovZero v6, skill-major 6 per skill-version contract). Format: `{govzero_major}.{skill_minor}.{skill_patch}` → `6.0.0` is also valid; align with project convention chosen during implementation.

> STOP-on-BLOCKERS: if `gz agent sync control-surfaces` fails to detect the new skills (manifest schema mismatch, validation failure), STOP and resolve manifest-extension semantics before authoring the SKILL.md content.

## Discovery Checklist

**Parent ADR:**

- [ ] Parent ADR § Decision item #8 quoted
- [ ] Parent ADR § Intent
- [ ] Parent ADR file

**Governance:**

- [ ] `AGENTS.md` § Skills, § Pattern Discovery
- [ ] `.gzkit/rules/skill-surface-sync.md` — sync invariant + version bump rules
- [ ] `.gzkit/rules/model-selection.md` — model tier doctrine

**Context:**

- [ ] `.gzkit/skills/gz-design/SKILL.md` — conversational pattern reference
- [ ] `.gzkit/skills/gz-adr-create/SKILL.md` — interview pattern reference
- [ ] Existing skill canon + mirror layout
- [ ] OBPI-07 ratification ceremony (for first-run mode coupling)

**Prerequisites:**

- [ ] OBPI-01 / OBPI-02 / OBPI-03 / OBPI-04 / OBPI-05 / OBPI-06 / OBPI-07 landed (or stubbed) — skills invoke CLI/validator/ledger surfaces
- [ ] `.gzkit/skills/` exists with sync infrastructure

**Existing Code:**

- [ ] `src/gzkit/skills/` for skill loader behavior
- [ ] `gz agent sync control-surfaces` for sync invocation

## Quality Gates

### Gate 1: ADR

- [ ] Parent ADR checklist item #8 quoted
- [ ] Intent recorded

### Gate 2: TDD

- [ ] Both SKILL.md files parse against skill schema
- [ ] Frontmatter declares `model: opus` for both
- [ ] Sync test: `uv run gz agent sync control-surfaces` propagates to four mirrors
- [ ] Manifest test: `gz validate --surfaces` clean post-sync
- [ ] Skill version markers present and ≥`1.0.0`
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint / typecheck clean (skill markdown lint clean)

### Gate 3: Docs (Heavy only)

- [ ] mkdocs build --strict clean (skill mirrors render correctly)

### Gate 4: BDD (Heavy only)

- [ ] No new behave scenarios required (skill workflows are procedural; tested via skill-schema validation + sync)

### Gate 5: Human (Heavy + Foundation)

- [ ] Attestation recorded

## Verification

```bash
uv run gz validate --documents --surfaces
uv run gz lint
uv run gz typecheck
uv run gz test

uv run gz agent sync control-surfaces

# Confirm canonical exists
test -f .gzkit/skills/gz-domain-enumerate/SKILL.md
test -f .gzkit/skills/gz-domain-model/SKILL.md

# Confirm mirrors synced
test -f .claude/skills/gz-domain-enumerate/SKILL.md
test -f .claude/skills/gz-domain-model/SKILL.md
test -f .agents/skills/gz-domain-enumerate/SKILL.md
test -f .agents/skills/gz-domain-model/SKILL.md
test -f .github/skills/gz-domain-enumerate/SKILL.md
test -f .github/skills/gz-domain-model/SKILL.md
```

## Demo

```bash
# Invoke the new skill via Claude Code's skill list (verify it appears)
uv run gz skill list | grep -E 'gz-domain-(enumerate|model)'

# Invoke gz-domain-model dialogue (operator-driven, demos in-session)
# Example trigger phrase: "design DM for experimentation BC"
```

## Acceptance Criteria

- [ ] REQ-0.0.43-08-01: Given `.gzkit/skills/gz-domain-enumerate/SKILL.md`, when parsed against skill schema, then valid
- [ ] REQ-0.0.43-08-02: Given `.gzkit/skills/gz-domain-model/SKILL.md`, when parsed against skill schema, then valid
- [ ] REQ-0.0.43-08-03: Given both SKILL.md frontmatters, when inspected, then `model: opus` present in both
- [ ] REQ-0.0.43-08-04: Given canonical authored and sync invoked, when mirror directories inspected, then SKILL.md present in `.claude/skills/`, `.agents/skills/`, `.github/skills/` for both skills with byte-equal content
- [ ] REQ-0.0.43-08-05: Given `.gzkit/manifest.json` after sync, when inspected, then both new skills listed under canonical surface inventory
- [ ] REQ-0.0.43-08-06: Given `gz validate --surfaces` post-sync, when invoked, then exit 0
- [ ] REQ-0.0.43-08-07: Given `gz-domain-enumerate` SKILL.md body, when inspected, then workflow steps for first-run mode (legacy-mapping bootstrap) and subsequent-run mode are both documented
- [ ] REQ-0.0.43-08-08: Given `gz-domain-model` SKILL.md body, when inspected, then workflow references the DM template + Aggregate / Entity / ValueObject / DomainEvent / ImplementationSurface / contracts surface
- [ ] REQ-0.0.43-08-09: Given both SKILL.md frontmatters, when version bumped post-edit, then sync detects and propagates
- [ ] REQ-0.0.43-08-10: Given both skills, when triggers documented in description match operator phrasing (`"enumerate BCs"`, `"design DM for X"`), then the skill loader matches them

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** RGR followed
- [ ] **Code Quality:** Markdown lint clean
- [ ] **Gate 3 (Docs):** mkdocs clean
- [ ] **Gate 5 (Human):** Attestation recorded
- [ ] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [ ] Intent recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/markdownlint output here
```

### Gate 3 (Docs)

```text
# Paste mkdocs output here
```

### Gate 4 (BDD)

```text
# N/A
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
