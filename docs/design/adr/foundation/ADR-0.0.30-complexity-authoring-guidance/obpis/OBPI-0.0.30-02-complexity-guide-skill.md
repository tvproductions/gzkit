---
id: OBPI-0.0.30-02-complexity-guide-skill
parent: ADR-0.0.30
item: 2
lane: Heavy
status: Draft
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

- `.gzkit/skills/complexity-guide/SKILL.md`
- `.claude/skills/complexity-guide/`, `.agents/skills/complexity-guide/`, `.github/skills/complexity-guide/` — vendor mirrors via `gz agent sync control-surfaces`
- `tests/skills/test_complexity_guide.py`
- `docs/design/adr/foundation/ADR-0.0.30-complexity-authoring-guidance/obpis/OBPI-0.0.30-02-complexity-guide-skill.md` — this brief's evidence section only

## Denied Paths

- `src/gzkit/commands/complexity_guide.py` — CLI is OBPI-01 (consumed, not edited)
- `src/gzkit/complexity/authoring/**` — engine/protocol are OBPI-03/04
- `.gzkit/skills/gz-justify/**` — justify integration is OBPI-05
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `SKILL.md` carries valid frontmatter per the skill schema, including `skill-version: 0.1.0`, `gz_command: complexity-guide`, `description:` triggering on operator phrases ("authoring-time complexity hint", "complexity guide preview", "preview before commit", "advise-band hints").
2. REQUIREMENT: The skill body documents the operator moment: ad-hoc authoring-time review (`gz complexity-guide <path>`) BEFORE running `gz complexity-advise` or attempting commit. The skill names this as the first-stop authoring surface; the trigger-time advisor (ADR-0.0.29) is the second stop if the developer's commit reaches gate time.
3. REQUIREMENT: The skill body declares an Output Contract per `.gzkit/rules/tool-skill-runbook-alignment.md` § Invariant 3: the destination verb's default human-readable output is in-line hint prose with one block per advise-band hint (archetype, doctrinal-frame headline, recommended-move headline). The `--json` mode emits canonical Pydantic serialization.
4. REQUIREMENT: The skill body cross-references ADR-0.0.29's `complexity-advisor` skill and explains the trigger-time vs. authoring-time distinction (when to use which). The cross-reference is short-form (a one-paragraph note pointing at the sister skill), not a duplication of the sister skill's content.
5. REQUIREMENT: The skill is operator-runnable ad-hoc; its `gz_command` field resolves to a registered CLI verb per Invariant 1 of the tool-skill-runbook-alignment rule.
6. REQUIREMENT: `uv run gz agent sync control-surfaces` propagates the skill to all three vendor mirrors with empty post-sync diff.
7. REQUIREMENT: Tests cover SKILL.md frontmatter validates against schema; skill body declares the operator moment; Output Contract names in-line hint prose form; `gz_command` target resolves; cross-reference to `complexity-advisor` is present; vendor mirrors are byte-identical after sync. Each test decorated with `@covers(REQ-0.0.30-02-NN)`.
8. REQUIREMENT: TDD discipline; tests do NOT spawn the actual hint pipeline (mocked at the subprocess boundary).
9. REQUIREMENT: NEVER include the operator's personal email in skill body, frontmatter, or fixtures.

> STOP-on-BLOCKERS: if OBPI-01's CLI verb is not registered, STOP — the skill's `gz_command` resolution fails Invariant 1.

## Discovery Checklist

- [ ] OBPI-01 CLI verb registration
- [ ] OBPI-01 manpage for cross-reference shape
- [ ] OBPI-0.0.29-04 sister skill (`.gzkit/skills/complexity-advisor/SKILL.md`) for cross-reference target
- [ ] `.gzkit/rules/tool-skill-runbook-alignment.md` Invariants 1, 2, 3
- [ ] `.gzkit/rules/skill-surface-sync.md`

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

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

### Closing Argument

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>`
- Attestation: substantive attestation text
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
