---
id: OBPI-0.0.29-04-complexity-advisor-skill
parent: ADR-0.0.29
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.29-04-complexity-advisor-skill: complexity-advisor Skill

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/ADR-0.0.29-complexity-advisor.md`
- **Checklist Item:** #4 — "`complexity-advisor` skill (vendor-mirrored; Output Contract declared; auto-chain + ad-hoc + intrinsic-attestation guidance)"

**Status:** Draft

## Objective

Author the `complexity-advisor` skill at `.gzkit/skills/complexity-advisor/SKILL.md` and propagate it to vendor mirrors. The skill carries invocation patterns for ad-hoc preview-before-fail (OBPI-06), references the auto-chain pathway (OBPI-05), documents the two-path intrinsic-complexity attestation (OBPI-07), and declares an Output Contract aligned with the destination CLI verb's default form.

## Lane

**Heavy** — New operator-facing skill is a contract surface per `.gzkit/rules/cli.md`-equivalent rules; vendor-mirror discipline per `.gzkit/rules/skill-surface-sync.md`. Foundation-kind brief-level Gate 5 attestation.

## Allowed Paths

- `.gzkit/skills/complexity-advisor/SKILL.md`
- `.claude/skills/complexity-advisor/`, `.agents/skills/complexity-advisor/`, `.github/skills/complexity-advisor/` — vendor mirrors via `gz agent sync control-surfaces`
- `tests/skills/test_complexity_advisor.py` — REQ-derived assertions
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-04-complexity-advisor-skill.md` — this brief's evidence section only

## Denied Paths

- `src/gzkit/commands/complexity_advise.py` — CLI is OBPI-03 (consumed, not edited)
- `src/gzkit/complexity/advisor/**` — engine/schema/intrinsic/timeout are other OBPIs
- `.gzkit/hooks/**` — auto-chain hook is OBPI-05
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `SKILL.md` carries valid frontmatter per the skill schema, including `skill-version: 0.1.0`, `gz_command: complexity-advise`, `description:` triggering on operator phrases ("preview complexity advisor", "complexity diagnosis", "advisor recommendation", "what does the advisor say", "intrinsic complexity attestation").
2. REQUIREMENT: The skill body documents the three operator moments: (a) ad-hoc preview-before-fail (`gz complexity-advise <path>`); (b) auto-chain context (when xenon-as-gate fails, the hook fires `gz complexity-advise --auto-chain`); (c) intrinsic-attestation guidance (when to use `@intrinsic_complexity` decorator vs `--attest-intrinsic` commit-time flag).
3. REQUIREMENT: The skill body declares an Output Contract per `.gzkit/rules/tool-skill-runbook-alignment.md` § Invariant 3: the destination verb's default human-readable output is structured prose with a per-diagnosis block (metric, crossing band, archetype, doctrinal frame, proof range, recommended move). The `--json` mode emits canonical Pydantic serialization.
4. REQUIREMENT: The skill body cross-references the runbook entry under "Complexity doctrine surfaces" and the manpage at `docs/user/manpages/gz-complexity-advise.md`.
5. REQUIREMENT: The skill is operator-runnable ad-hoc; its `gz_command` field resolves to a registered CLI verb per Invariant 1 of the tool-skill-runbook-alignment rule.
6. REQUIREMENT: `uv run gz agent sync control-surfaces` propagates the skill to all three vendor mirrors with empty post-sync diff.
7. REQUIREMENT: Tests cover: SKILL.md frontmatter validates against schema; skill body declares all three operator moments; Output Contract section names the destination verb's output form; the `gz_command` target resolves to a registered verb (Invariant 1); skill body cross-references runbook + manpage; vendor-mirror copies are byte-identical after sync. Each test decorated with `@covers(REQ-0.0.29-04-NN)`.
8. REQUIREMENT: TDD discipline; tests do NOT spawn the actual advisor pipeline (mocked at the subprocess boundary).
9. REQUIREMENT: NEVER include the operator's personal email in skill body, frontmatter, or fixtures.

> STOP-on-BLOCKERS: if OBPI-03's CLI verb (`gz complexity-advise`) is not registered, STOP — the skill's `gz_command` resolution fails Invariant 1.

## Discovery Checklist

- [ ] OBPI-03 CLI verb registration (`src/gzkit/cli/parser_artifacts.py`)
- [ ] OBPI-03 manpage (`docs/user/manpages/gz-complexity-advise.md`)
- [ ] Parent ADR § Decision — three-operator-moment guidance shape
- [ ] `.gzkit/rules/tool-skill-runbook-alignment.md` § Invariants 1, 2, 3
- [ ] `.gzkit/rules/skill-surface-sync.md` — version discipline + mirror sync protocol
- [ ] `.gzkit/skills/gz-complexity-distill/SKILL.md` (OBPI-0.0.27-06) — exemplar foundation-aligned skill body for shape reference

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
- [ ] BDD waiver registered: skill-only OBPI; CLI scenarios at OBPI-03

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents --surfaces
uv run gz agent sync control-surfaces  # post-sync diff empty
uv run gz arb step --name unittest -- uv run -m unittest tests/skills/test_complexity_advisor.py -v
```

## Acceptance Criteria

- [ ] REQ-0.0.29-04-01: Given the canonical skill, when frontmatter is parsed, then schema validates and `skill-version` is `0.1.0`.
- [ ] REQ-0.0.29-04-02: Given the skill body, when parsed, then all three operator moments (ad-hoc, auto-chain context, intrinsic-attestation guidance) are present.
- [ ] REQ-0.0.29-04-03: Given the Output Contract section, when parsed, then it names structured prose as the default form and `--json` as the machine-readable mode.
- [ ] REQ-0.0.29-04-04: Given the skill's `gz_command`, when resolved against the CLI parser, then a registered verb exists (Invariant 1).
- [ ] REQ-0.0.29-04-05: Given a clean working tree, when `uv run gz agent sync control-surfaces` runs, then the three vendor mirrors are byte-identical and the post-sync diff is empty.
- [ ] REQ-0.0.29-04-06: Given the destination verb's default output observed against a fixture, when compared to the skill's Output Contract, then the output form matches (Invariant 3).

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
# Waiver: data/behave_coverage_waivers.json — OBPI-0.0.29-04
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
