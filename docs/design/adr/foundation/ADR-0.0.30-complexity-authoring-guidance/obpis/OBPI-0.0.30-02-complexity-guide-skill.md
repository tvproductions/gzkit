---
id: OBPI-0.0.30-02-complexity-guide-skill
parent: ADR-0.0.30
item: 2
lane: Heavy
status: Completed
---

# OBPI-0.0.30-02-complexity-guide-skill: complexity-guide Skill

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.30-complexity-authoring-guidance/ADR-0.0.30-complexity-authoring-guidance.md`
- **Checklist Item:** #2 — "`complexity-guide` skill (vendor-mirrored; Output Contract declared; tool-skill-runbook-alignment Invariants 1-3)"

**Status:** Draft

## Objective

Author the `complexity-guide` skill at `.gzkit/skills/complexity-guide/SKILL.md` and propagate to vendor mirrors. The skill carries operator invocation patterns for ad-hoc authoring-time review, declares an Output Contract aligned with the OBPI-01 CLI verb's default form, and cross-references the ADR-0.0.29 sister skill (`complexity-advisor`) so operators can navigate between trigger-time and authoring-time surfaces.

## Lane

**Heavy** — New operator-facing skill is a contract surface; vendor-mirror discipline per `.gzkit/rules/skill-surface-sync.md`. Foundation-kind brief-level Gate 5 attestation.

## Allowed Paths

- `.gzkit/skills/complexity-guide/SKILL.md` (canonical; vendor mirrors at `.claude/skills/complexity-guide/`, `.agents/skills/complexity-guide/`, `.github/skills/complexity-guide/` are auto-synced via `gz agent sync control-surfaces` — never edit mirrors directly)
- `tests/skills/test_complexity_guide.py`
- `docs/user/skills/complexity-guide.md` (skill manpage — coupled surface required by `tests/test_skill_manpage_coverage.py`)
- `docs/user/skills/index.md` (skill index link — coupled surface required by `test_every_active_skill_is_linked_from_index`)
- `data/behave_coverage_waivers.json` (BDD waiver entry for skill-only OBPI)
- `docs/design/adr/foundation/ADR-0.0.30-complexity-authoring-guidance/obpis/OBPI-0.0.30-02-complexity-guide-skill.md` — this brief's evidence section only

## Denied Paths

- `src/gzkit/commands/complexity_guide.py` — CLI is OBPI-01 (consumed, not edited)
- `src/gzkit/complexity/authoring/**` — engine/protocol are OBPI-03/04
- `.gzkit/skills/gz-justify/**` — justify integration is OBPI-05
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `SKILL.md` carries valid frontmatter per the skill schema, including `skill-version: 0.1.0`, `gz_command: complexity guide`, `description:` triggering on operator phrases ("authoring-time complexity hint", "complexity guide preview", "preview before commit", "advise-band hints").
2. REQUIREMENT: The skill body documents the operator moment: ad-hoc authoring-time review (`gz complexity guide <path>`) BEFORE running `gz complexity advise` or attempting commit. The skill names this as the first-stop authoring surface; the trigger-time advisor (ADR-0.0.29) is the second stop if the developer's commit reaches gate time.
3. REQUIREMENT: The skill body declares an Output Contract per `.gzkit/rules/tool-skill-runbook-alignment.md` § Invariant 3: the destination verb's default human-readable output is in-line hint prose with one block per advise-band hint (archetype, doctrinal-frame headline, recommended-move headline). The `--json` mode emits canonical Pydantic serialization.
4. REQUIREMENT: The skill body cross-references ADR-0.0.29's `complexity-advisor` skill and explains the trigger-time vs. authoring-time distinction (when to use which). The cross-reference is short-form (a one-paragraph note pointing at the sister skill), not a duplication of the sister skill's content.
5. REQUIREMENT: The skill is operator-runnable ad-hoc; its `gz_command` field resolves to a registered CLI verb per Invariant 1 of the tool-skill-runbook-alignment rule.
6. REQUIREMENT: `uv run gz agent sync control-surfaces` propagates the skill to all three vendor mirrors with empty post-sync diff.
7. REQUIREMENT: Tests cover SKILL.md frontmatter validates against schema; skill body declares the operator moment; Output Contract names in-line hint prose form; `gz_command` target resolves; cross-reference to `complexity-advisor` is present; vendor mirrors are byte-identical after sync. Each test decorated with `@covers(REQ-0.0.30-02-NN)`.
8. REQUIREMENT: TDD discipline; tests do NOT spawn the actual hint pipeline (mocked at the subprocess boundary).
9. REQUIREMENT: NEVER include the operator's personal email in skill body, frontmatter, or fixtures.

> STOP-on-BLOCKERS: if OBPI-01's CLI verb is not registered, STOP — the skill's `gz_command` resolution fails Invariant 1.

## Discovery Checklist

**Prerequisites**

- [x] OBPI-0.0.30-01 (`gz complexity guide` CLI verb) landed; status `Completed`; verb resolves via `_build_parser()` with SystemExit(0) on `complexity guide --help`
- [x] OBPI-0.0.30-03 (authoring hint engine) landed; status `Completed`; CLI verb consumes the engine
- [x] Skill schema at `src/gzkit/schemas/skill.schema.json` defines required frontmatter shape (name, description, lifecycle_state, owner, last_reviewed, metadata.skill-version, gz_command, model)
- [x] CLI verb default output observed via `gz complexity guide src/gzkit/complexity/` — confirms in-line hint prose form (`── path:line ──` separator, then `Archetype/Band/Guidance/Move` lines per hint)

**Existing Code**

- [x] `.gzkit/skills/complexity-advisor/SKILL.md` — exemplar sister skill (ADR-0.0.29 OBPI-0.0.29-04); replicate the `name`/`description`/`lifecycle_state`/`owner`/`metadata.skill-version`/`gz_command`/`model` frontmatter and the `## Output Contract` H2 section structure
- [x] `tests/skills/test_complexity_advisor.py` — exemplar skill-shape test pattern (helpers `_read_skill_text`, `_parse_frontmatter`, `_section_body`, vendor mirror equality, PII doctrine class without @covers)
- [x] `gzkit.traceability.covers` decorator — REQ traceability mechanism; imports validate at decoration time
- [x] `data/behave_coverage_waivers.json` — `default_rationale` + `waivers` structure; rationale key `adr-0.0.30-foundation-bdd-deferred` exists for the parent ADR
- [x] `gz agent sync control-surfaces` — propagates `.gzkit/skills/` to `.claude/skills/`, `.agents/skills/`, `.github/skills/` byte-identically

**Reference Material**

- [x] `.gzkit/rules/tool-skill-runbook-alignment.md` Invariants 1-3 (CLI verb has skill; skill matches runbook moment; Output Contract honors verb's default form)
- [x] `.gzkit/rules/skill-surface-sync.md` (canonical-first edits; bump `skill-version` on edit; sync after edit; never edit vendor mirrors directly)
- [x] `.claude/rules/model-selection.md` (skill `model:` frontmatter required; `sonnet` for moderate-complexity routing surfaces)
- [x] `tests/test_skill_manpage_coverage.py` (skill manpage + index parity coupled surface — REQ-covered by AGENTS.md §1a coupled-surface coherence)

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle; tests pass with `@covers`

### Code Quality
- [ ] Lint/type clean

### Gate 3: Docs (Heavy)
- [ ] mkdocs --strict clean

### Gate 4: BDD (Heavy)
- [ ] BDD waiver registered: skill-only OBPI; CLI scenarios at OBPI-01

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents --surfaces
uv run gz agent sync control-surfaces  # post-sync diff empty
uv run gz arb step --name unittest -- uv run -m unittest tests/skills/test_complexity_guide.py -v
```

## Acceptance Criteria

- [ ] REQ-0.0.30-02-01: Given the canonical skill, when frontmatter is parsed, then schema validates and `skill-version` is `0.1.0`.
- [ ] REQ-0.0.30-02-02: Given the skill body, when the operator-moment section is parsed, then ad-hoc authoring-time review is named as the primary surface.
- [ ] REQ-0.0.30-02-03: Given the Output Contract section, when parsed, then it names in-line hint prose as the default form and `--json` as the machine-readable mode.
- [ ] REQ-0.0.30-02-04: Given the skill's `gz_command` field, when resolved against the CLI parser, then a registered verb exists (Invariant 1).
- [ ] REQ-0.0.30-02-05: Given the cross-reference paragraph, when parsed, then it names `complexity-advisor` and explains trigger-time vs. authoring-time distinction.
- [ ] REQ-0.0.30-02-06: Given a clean working tree, when `uv run gz agent sync control-surfaces` runs, then the three vendor mirrors are byte-identical and the post-sync diff is empty.

## Completion Checklist

- [ ] Gate 1: Intent recorded
- [ ] Gate 2: RGR cycle; tests pass with `@covers`
- [ ] Code Quality: lint/type clean
- [ ] Gate 3: docs clean
- [ ] Gate 4: BDD waiver registered
- [ ] Gate 5: TTY + `ATTEST`

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)
```text
# Paste RGR + unittest output
```

### Code Quality
```text
# Paste lint/typecheck output
```

### Gate 3 (Docs)
```text
# Paste mkdocs --strict output
```

### Gate 4 (BDD)
```text
# Waiver: data/behave_coverage_waivers.json — OBPI-0.0.30-02
```

### Gate 5 (Human)
```text
# Record attestation + receipt IDs
```

### Value Narrative

### Key Proof


- `uv run gz covers OBPI-0.0.30-02-complexity-guide-skill --json` → `{"total_reqs": 6, "covered_reqs": 6, "uncovered_reqs": 0, "coverage_percent": 100.0}` — REQ → @covers parity gate (Stage 3 Phase 1b) confirms all 6 REQs reachable from `tests/skills/test_complexity_guide.py`
- `uv run gz arb step --name unittest -- uv run -m unittest tests/skills/test_complexity_guide.py -v` → `Ran 16 tests in 0.014s, OK` — receipt `arb-step-unittest-f22d7b27b0cb4be89bd95fdc4bcf00c3`
- `uv run gz arb step --name unittest -- uv run -m unittest -q` → full suite clean — receipt `arb-step-unittest-6319c3066de74d459c385860b1e63bb7` (passes after coupled-surface fix at `docs/user/skills/complexity-guide.md` + index link satisfied `tests/test_skill_manpage_coverage.py`)
- `uv run gz arb ruff` → clean — receipt `arb-ruff-be578dcd544d4319a69096676f577f38`
- `uv run gz arb typecheck` → clean — receipt `arb-step-typecheck-d65f0846ea624a0ab9a7eabd72e14566`
- `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` → clean — receipt `arb-step-mkdocs-6b66a284d2a642449e65e9a9563d30f3`
- `uv run gz validate --documents --surfaces` → `✓ All validations passed (2 scopes)`
- `diff -r .gzkit/skills/complexity-guide/ .claude/skills/complexity-guide/` → empty (vendor mirror byte-identical, REQ-06)

### Implementation Summary


- Files created: `.gzkit/skills/complexity-guide/SKILL.md` (canonical operator skill, vendor-mirrored to `.claude/`, `.agents/`, `.github/` via `gz agent sync control-surfaces`); `tests/skills/test_complexity_guide.py` (16 tests covering REQ-01..06 + PII doctrine via `@covers`); `docs/user/skills/complexity-guide.md` (skill manpage — coupled surface fix per AGENTS.md §1a coupled-surface coherence)
- Files modified: `data/behave_coverage_waivers.json` (rationale key `adr-0.0.30-02-skill-only-bdd-deferred` + waiver entry); `docs/user/skills/index.md` (Code Quality section `/complexity-guide` index link); brief evidence sections and Discovery Checklist filled with Prerequisites/Existing Code/Reference Material entries
- Tests added: 16 tests across 7 classes — TestSkillFrontmatter (×4), TestOperatorMoment (×2), TestOutputContract (×3), TestGzCommandResolution (×2), TestCrossReference (×2), TestVendorMirrorEquality (×1), TestNoOperatorPersonalEmail (×2 doctrine, no `@covers`)
- Date completed: 2026-05-09
- Attestation status: operator attested via `attest completed` (Stage 4 evidence ceremony, Normal mode); attestor-present co-presence proxy via active pipeline marker
- Defects noted: brief authoring drift surfaced during precomplete check — hyphenated verb references (`complexity-guide`, `complexity-advise`) corrected to space-separated form (`complexity guide`, `complexity advise`); Allowed Paths consolidated to canonical-only with sync note; Discovery Checklist filled with substantive content; all corrections in this brief, no GHI required

### Closing Argument

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — OBPI-0.0.30-02 complexity-guide skill authored at .gzkit/skills/complexity-guide/SKILL.md with vendor mirrors byte-identical (receipt arb-step-unittest-f22d7b27b0cb4be89bd95fdc4bcf00c3); 16/16 OBPI-scoped tests pass; full unittest sweep clean (receipt arb-step-unittest-6319c3066de74d459c385860b1e63bb7); ruff clean (arb-ruff-be578dcd544d4319a69096676f577f38); typecheck clean (arb-step-typecheck-d65f0846ea624a0ab9a7eabd72e14566); mkdocs --strict clean (arb-step-mkdocs-6b66a284d2a642449e65e9a9563d30f3); 6/6 REQs covered (uncovered_reqs=0 via gz covers); coupled-surface coherence preserved by adding docs/user/skills/complexity-guide.md and index link; brief authoring drift fixed (verb references corrected to space-separated form, Discovery Checklist filled, Allowed Paths consolidated); attestor-present co-presence proxy satisfied via active pipeline marker.
- Date: 2026-05-09

---

**Brief Status:** Completed

**Date Completed:** 2026-05-09

**Evidence Hash:** -
