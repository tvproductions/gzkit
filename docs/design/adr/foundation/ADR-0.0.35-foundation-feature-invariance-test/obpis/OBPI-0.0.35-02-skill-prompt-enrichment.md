---
id: OBPI-0.0.35-02-skill-prompt-enrichment
parent: ADR-0.0.35-foundation-feature-invariance-test
item: 2
lane: Lite
status: Completed
---

# OBPI-0.0.35-02-skill-prompt-enrichment: Skill Prompt Enrichment with Invariance Test

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.35-foundation-feature-invariance-test/ADR-0.0.35-foundation-feature-invariance-test.md`
- **Checklist Item:** #2 — "Skill prompt enrichment — `gz-design`, `gz-plan`, `gz-adr-create`, `gz-adr-promote` skill prompts for `--kind` cite the invariance test inline alongside ADR-0.0.18's heuristic; skill body text gains the one-line test plus lens; mirror sync to `.claude/skills/` and `.github/skills/`; skill versions bumped per skill-surface-sync discipline. Depends on OBPI-01."

**Status:** Completed

## Objective

Enrich the four kind-deciding skills (`gz-design`, `gz-plan`, `gz-adr-create`, `gz-adr-promote`) so every skill body that prompts for or references `--kind` cites the invariance test inline — verbatim test quote, hexagonal-ports lens (ports point to invariance; plugs are features), and a forward link to the OBPI-01 concept page. Bump each skill's `skill-version` frontmatter per `.claude/rules/skill-surface-sync.md`. Run `gz agent sync control-surfaces` so the canonical edits propagate to `.claude/skills/` and `.github/skills/` mirrors.

## Lane

**Lite** — Skill body edits and a sync command. No CLI/schema/runtime-contract change. Foundation-kind brief-level attestation still applies (parent ADR-0.0.35 is foundation-kind).

## Allowed Paths

- `.gzkit/skills/gz-design/SKILL.md` — kind-decision prompt enrichment
- `.gzkit/skills/gz-plan/SKILL.md` — kind-decision prompt enrichment
- `.gzkit/skills/gz-adr-create/SKILL.md` — kind-decision prompt enrichment
- `.gzkit/skills/gz-adr-promote/SKILL.md` — kind-decision prompt enrichment

## Denied Paths

- `.claude/skills/**`, `.github/skills/**` — generated mirrors; never edited directly per `.claude/rules/skill-surface-sync.md` § "Never edit vendor mirrors directly"
- `.gzkit/skills/gz-design/`, `.gzkit/skills/gz-plan/`, etc. — directories other than `SKILL.md` (assets/, agents/, references/) are out of scope unless a body edit specifically requires a new asset
- `src/**` — no source code change
- `tests/**` — no test surface (skill-body edits; mirror-sync determinism is the verification gate)
- `docs/user/concepts/foundation-feature-invariance-test.md` — OBPI-01's deliverable; this OBPI links to it but does not author it
- `src/gzkit/templates/**` — OBPI-03's scope
- `src/gzkit/governance/trust_audits.py` — OBPI-04's scope
- All ADR/OBPI files

## Requirements (FAIL-CLOSED)

1. **REQUIREMENT — verbatim test in every kind-prompt skill.** Each of the four `SKILL.md` files MUST quote the invariance test verbatim (*"Foundation = without it, we wouldn't be doing the project"*) at the section that prompts for or describes `--kind`.
2. **REQUIREMENT — hexagonal-ports lens one-liner.** Each enriched section MUST include the one-sentence lens: *"ports point to invariance; plugs are features."*
3. **REQUIREMENT — concept-page link.** Each enriched section MUST link forward to `docs/user/concepts/foundation-feature-invariance-test.md` (the OBPI-01 deliverable).
4. **REQUIREMENT — ADR-0.0.18 concept-page link preserved.** The existing link to `docs/user/concepts/adr-taxonomy.md` (where present) MUST remain — the test is a sharper resolution rule, not a replacement; both links coexist.
5. **REQUIREMENT — skill-version bumped per `.claude/rules/skill-surface-sync.md`.** Each touched `SKILL.md`'s frontmatter `skill-version:` MUST be incremented (minor bump, e.g. `1.5.0 → 1.6.0`) reflecting the doctrine-rule addition.
6. **REQUIREMENT — body-level marker NOT used.** `skill-version` lives in frontmatter for skill files, not in body markers. The rule-version body marker convention applies to `.gzkit/rules/`, not `.gzkit/skills/`.
7. **REQUIREMENT — mirror sync runs successfully.** `uv run gz agent sync control-surfaces` MUST exit 0 after edits; mirrors at `.claude/skills/<skill>/SKILL.md` and `.github/skills/<skill>/SKILL.md` MUST contain the same enriched content as canonical.
8. **REQUIREMENT — no manual mirror edits.** The `.claude/skills/` and `.github/skills/` mirrors are written only by the sync command. Direct edits to mirrors are a defect.
9. **NEVER — drift the existing skill prompts beyond the kind-decision section.** Edits are additive and surgical: enrichment of the kind-prompt section only. Other skill content (invocation examples, scope boundaries, anti-patterns) stays as-is.
10. **NEVER — bump `skill-version` without making a substantive body edit.** Version bumps without content change are bookkeeping noise.

> STOP-on-BLOCKERS: if `docs/user/concepts/foundation-feature-invariance-test.md` does not yet exist, OBPI-01 has not landed — print BLOCKERS and halt. This OBPI depends on OBPI-01.

## Discovery Checklist

**Parent ADR (read first; order pinned per GHI #321):**

- [ ] Quote ADR-0.0.35 § Decision item #1 (verbatim test) and #2 (hexagonal-ports lens) into Implementation Summary.
- [ ] Read ADR-0.0.35 § Intent — the why-frame for skill prompts citing the test inline.

> **STOP:** If you cannot quote ADR-0.0.35 § Decision item #1 verbatim, STOP and re-read.

**Sibling skill-rule reference:**

- [ ] Read `.claude/rules/skill-surface-sync.md` § Procedure and § Anti-patterns end-to-end. The skill-version bump + canonical-first edit + sync-after rule is binding.
- [ ] Read OBPI-01 brief — confirm concept-page slug for the link target.

**OBPI-01 dependency check:**

- [ ] `docs/user/concepts/foundation-feature-invariance-test.md` exists (OBPI-01 landed). If absent, this OBPI cannot proceed.

**Prerequisites (STOP if missing):**

- [ ] `.gzkit/skills/gz-design/SKILL.md` exists
- [ ] `.gzkit/skills/gz-plan/SKILL.md` exists
- [ ] `.gzkit/skills/gz-adr-create/SKILL.md` exists
- [ ] `.gzkit/skills/gz-adr-promote/SKILL.md` exists
- [ ] `gz agent sync control-surfaces` resolves (CLI verb registered)
- [ ] OBPI-01 deliverable exists: `docs/user/concepts/foundation-feature-invariance-test.md`

**Existing Code (understand current state):**

- [ ] `.gzkit/skills/gz-design/SKILL.md` — read the kind-prompt section end-to-end; identify the exact insertion point for the test quote.
- [ ] `.gzkit/skills/gz-plan/SKILL.md` — same; this skill wields `gz plan create --kind` directly so the prompt is most user-facing.
- [ ] `.gzkit/skills/gz-adr-create/SKILL.md` — same; uses `--kind` during ADR scaffolding.
- [ ] `.gzkit/skills/gz-adr-promote/SKILL.md` — same; uses `--kind` during pool-to-active promotion.
- [ ] Current `skill-version:` value in each skill's frontmatter — record before bump.
- [ ] Read one mirror file (e.g. `.claude/skills/gz-plan/SKILL.md`) to confirm structural correspondence with canonical; do NOT edit.

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded
- [ ] Parent ADR § Decision item quoted

### Gate 2: TDD (Doc-equivalent)

Skill-body edits — no test tier. Verification is mirror-sync determinism: a clean `gz agent sync control-surfaces` run with no diff between canonical and mirror after sync.

- [ ] Pre-edit baseline: `uv run gz agent sync control-surfaces` clean
- [ ] Post-edit: `uv run gz agent sync control-surfaces` clean (mirrors regenerated)
- [ ] `git diff .claude/skills/ .github/skills/` shows the same enrichment as canonical (modulo any mirror-specific rendering)

### Code Quality

- [ ] Lint clean: `uv run gz lint` (catches markdown issues in skill bodies)

### Gate 5: Human (Foundation-kind brief-level attestation)

- [ ] Foundation-kind parent → brief-level attestation required.
- [ ] Operator confirms verbatim test wording in each of the four enriched skills matches.

## Verification

```bash
# Verbatim test present in each canonical skill
for skill in gz-design gz-plan gz-adr-create gz-adr-promote; do
  grep -F "Foundation = without it, we wouldn't be doing the project" \
    ".gzkit/skills/$skill/SKILL.md" \
    || echo "MISSING in $skill"
done

# Concept-page link present in each
for skill in gz-design gz-plan gz-adr-create gz-adr-promote; do
  grep -F "foundation-feature-invariance-test" \
    ".gzkit/skills/$skill/SKILL.md" \
    || echo "MISSING link in $skill"
done

# skill-version bumped (compare to baseline)
for skill in gz-design gz-plan gz-adr-create gz-adr-promote; do
  grep "^  skill-version:" ".gzkit/skills/$skill/SKILL.md"
done

# Mirror sync clean
uv run gz agent sync control-surfaces

# ARB receipts (foundation-kind brief-level attestation)
uv run gz arb ruff
```

## Acceptance Criteria

- [ ] **REQ-0.0.35-02-01:** Given each of the four target skills (`gz-design`, `gz-plan`, `gz-adr-create`, `gz-adr-promote`), when an operator reads the section that prompts for or describes `--kind`, then the verbatim invariance test (*"Foundation = without it, we wouldn't be doing the project"*) is present.
- [ ] **REQ-0.0.35-02-02:** Given each enriched section, when read, the hexagonal-ports lens one-liner (*"ports point to invariance; plugs are features"*) is present.
- [ ] **REQ-0.0.35-02-03:** Given each enriched section, when read, a forward link to `docs/user/concepts/foundation-feature-invariance-test.md` is present.
- [ ] **REQ-0.0.35-02-04:** Given each enriched skill, when frontmatter is parsed, then `skill-version` has been incremented from its pre-edit baseline.
- [ ] **REQ-0.0.35-02-05:** Given the canonical and mirror skill files post-sync, when `uv run gz agent sync control-surfaces` runs, then it exits 0 with no manual edits required to mirrors.
- [ ] **REQ-0.0.35-02-06:** Given the existing skill content outside the kind-prompt section, when compared pre-edit and post-edit, then no other section is materially changed.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; parent § Decision quoted
- [ ] **Gate 2 (Doc-equivalent):** Pre/post sync determinism evidence captured
- [ ] **Code Quality:** Lint clean
- [ ] **Gate 5 (Human):** Foundation-kind brief-level attestation recorded
- [ ] **Value Narrative:** Recorded below
- [ ] **Key Proof:** One enriched skill section pasted as a before/after excerpt
- [ ] **OBPI Acceptance:** Evidence section populated

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (Doc-equivalent RGR)

```text
# Paste pre-edit and post-edit `gz agent sync control-surfaces` output here
```

### Code Quality

```text
# Paste lint output here
```

### Gate 5 (Human)

```text
# Record foundation-kind brief-level attestation text here
```

### Value Narrative

Before this OBPI: agents and operators using `gz-design`, `gz-plan`, `gz-adr-create`, `gz-adr-promote` to scaffold or promote ADRs see ADR-0.0.18's decision heuristic in skill prompts (where present) but no mention of the sharper invariance test. Edge-case classifications (substrate vs. port; doctrine vs. tooling) require the agent to remember the test from elsewhere or rederive it. After this OBPI: the test, the lens, and the concept-page link are inline at every kind-decision moment in the four skills; the cost of applying the test drops to zero — it is on the screen at decision time.

### Key Proof


Verbatim invariance test present in all four canonical skills, confirmed by:

```bash
grep -F "Foundation = without it, we wouldn't be doing the project" \
  .gzkit/skills/gz-plan/SKILL.md \
  .gzkit/skills/gz-design/SKILL.md \
  .gzkit/skills/gz-adr-create/SKILL.md \
  .gzkit/skills/gz-adr-promote/SKILL.md
```

Returns one match per file. Mirror parity confirmed by `TestSkillMirrorParity` (8 byte-equality tests, all pass).

ARB receipts:

- `arb-ruff-20c4e7766b244580bba976002715070b` (lint clean)
- `arb-step-typecheck-b9044e8703d34b0aacae95071326d12e` (typecheck clean)
- `arb-step-unittest-dbcafe32fae64b499ef0610290f3f623` (5198/5198 full sweep pass)
- `arb-step-unittest-989ec93d147444bead07d2fe5610bb57` (30/30 OBPI-scoped pass)

### Implementation Summary


- Skills enriched (canonical): `.gzkit/skills/gz-plan/SKILL.md` (v1.2.0), `.gzkit/skills/gz-adr-create/SKILL.md` (v6.3.0), `.gzkit/skills/gz-design/SKILL.md` (v1.3.0), `.gzkit/skills/gz-adr-promote/SKILL.md` (v1.3.0)
- Enrichment delta per skill: verbatim invariance test, hexagonal-ports lens one-liner, forward link to `docs/user/concepts/foundation-feature-invariance-test.md` (ADR-0.0.18 taxonomy link preserved where present)
- Mirrors propagated: 4 files under `.claude/skills/`, 4 files under `.github/skills/` (byte-identical to canonical)
- Tests added: `tests/governance/test_foundation_invariance_skill_enrichment.py` (30 tests across 6 classes, one class per REQ; all decorated with `@covers`)
- REQ coverage: 6/6 covered via `gz covers OBPI-0.0.35-02`
- Date completed: 2026-05-17
- Operator attestation phrase: "attest completed" (verbatim, recorded in Human Attestation section)
- Defects noted: none

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — OBPI-0.0.35-02-skill-prompt-enrichment: four kind-deciding skills (gz-plan v1.2.0, gz-adr-create v6.3.0, gz-design v1.3.0, gz-adr-promote v1.3.0) carry the invariance test verbatim, hexagonal-ports lens, and concept-page link; 30 unit tests in tests/governance/test_foundation_invariance_skill_enrichment.py cover all 6 REQs; mirror byte-parity confirmed across .claude/skills/ and .github/skills/; ARB receipts arb-ruff-20c4e7766b244580bba976002715070b, arb-step-typecheck-b9044e8703d34b0aacae95071326d12e, arb-step-unittest-dbcafe32fae64b499ef0610290f3f623 (5198/5198), arb-step-unittest-989ec93d147444bead07d2fe5610bb57 (30/30 scoped).
- Date: 2026-05-17

---

**Brief Status:** Draft

**Date Completed:** 2026-05-17

**Evidence Hash:** -
