---
id: OBPI-0.0.27-06-distill-skill
parent: ADR-0.0.27
item: 6
lane: Heavy
status: Draft
---

# OBPI-0.0.27-06-distill-skill: gz-complexity-distill Skill

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/ADR-0.0.27-exemplar-corpus-doctrine.md`
- **Checklist Item:** #6 — "`gz-complexity-distill` skill (ad-hoc + scheduled invocation, vendor-mirrored)"

**Status:** Draft

## Objective

Author the `gz-complexity-distill` skill at `.gzkit/skills/gz-complexity-distill/` and propagate it to the three vendor mirrors. The skill carries the corpus list, per-project path filters, methodology rationale, and the three distillation-cadence triggers (annual calendar, drift-signal > 25%, judgment); it is operator-invocable ad-hoc and is the canonical surface for OBPI-04's distillation pass.

## Lane

**Heavy** — New operator-facing skill is a surface contract per `.gzkit/rules/cli.md` § "New Subcommand (Heavy Lane)" semantics; foundation-kind brief-level Gate 5 attestation.

## Allowed Paths

- `.gzkit/skills/gz-complexity-distill/SKILL.md` — canonical skill body
- `.gzkit/skills/gz-complexity-distill/scripts/` — optional helper scripts (only if a script-backed surface is materially better than direct CLI invocation per Operator Economy of Effort)
- `.claude/skills/gz-complexity-distill/`, `.agents/skills/gz-complexity-distill/`, `.github/skills/gz-complexity-distill/` — vendor mirrors emitted by `gz agent sync control-surfaces`
- `tests/skills/test_gz_complexity_distill.py` — REQ-derived assertions
- `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/**` — brief evidence updates only

## Denied Paths

- `data/exemplar_corpus.json` — corpus is OBPI-02 (skill references it, does not edit)
- `src/gzkit/complexity/measurement.py` — measurement is OBPI-03
- `docs/governance/complexity/distilled-characteristics-*.md` — distillation outputs are produced when the skill runs (OBPI-04's contract), not authored here
- `src/gzkit/governance/trust_audits.py` — link validator is OBPI-07
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `SKILL.md` carries valid frontmatter per the skill schema (`src/gzkit/skills/schema.py` or equivalent), including `skill-version: 0.1.0`, `gz_command:` field naming the canonical CLI invocation, `description:` triggering on the operator phrases the design dialogue identified ("run distillation", "refresh complexity corpus", "distill complexity").
2. REQUIREMENT: The skill body documents the three cadence triggers verbatim from the parent ADR § Decision: (a) annual calendar default with rationale, (b) advisor verdict-frequency drift > 25% from baseline of last distillation with 6-month minimum re-distillation guard, (c) operator-judgment trigger for ground-breaking projects.
3. REQUIREMENT: The skill body lists the corpus by reference (`data/exemplar_corpus.json`) — the skill does not duplicate corpus content (single source of truth) and points the operator at the canonical file.
4. REQUIREMENT: The skill body declares per-project path filters by reference to the corpus entries (corpus is the source of truth); never duplicates the filter content.
5. REQUIREMENT: The skill body documents the methodology rationale (why distillation is agent-driven + operator-attested per OEE) and the OBPI-04 brief shape it is bound to produce.
6. REQUIREMENT: The skill body declares an Output Contract per `.gzkit/rules/tool-skill-runbook-alignment.md` § Invariant 3 — the output form of the destination CLI verb is named (e.g. "writes a dated distilled-characteristics document under `docs/governance/complexity/`").
7. REQUIREMENT: `uv run gz agent sync control-surfaces` propagates the skill to all three vendor mirrors with empty post-sync diff.
8. REQUIREMENT: Tests cover: SKILL.md frontmatter validates against the schema; rule-version + body-marker discipline (if rule-style markers apply); skill body declares all three cadence triggers; skill body cites corpus by reference (does not duplicate content); the three vendor-mirror copies have identical content after sync; the `gz_command` target resolves to a registered CLI verb (Invariant 1 of `.gzkit/rules/tool-skill-runbook-alignment.md`). Each test decorated with `@covers(REQ-0.0.27-06-NN)`.
9. REQUIREMENT: Tool / Skill / Runbook alignment per `.gzkit/rules/tool-skill-runbook-alignment.md` Invariants 1, 2, 3 holds; if the destination CLI verb does not yet exist, this OBPI either authors it (within `Allowed Paths`) or registers a follow-up GHI under `Tracked Defects`.
10. REQUIREMENT: TDD discipline; `tempfile`-backed fixtures; tests do NOT spawn the actual measurement pipeline (mocked at the subprocess boundary).
11. REQUIREMENT: NEVER include the operator's personal email in skill body, frontmatter, or fixtures.

> STOP-on-BLOCKERS: if the destination CLI verb the skill routes to is not registered in `src/gzkit/cli/parser_artifacts.py`, surface the gap in `Tracked Defects` and either resolve in this OBPI or open a GHI before merge.

## Discovery Checklist

- [ ] OBPI-02 corpus file (`data/exemplar_corpus.json`) — referenced, not duplicated
- [ ] OBPI-03 measurement pipeline — invoked by the destination CLI verb
- [ ] OBPI-04 distillation pass contract — the brief shape this skill is bound to produce
- [ ] `.gzkit/rules/tool-skill-runbook-alignment.md` § Invariants 1–3
- [ ] `.gzkit/rules/skill-surface-sync.md` — version discipline + mirror sync protocol
- [ ] `.gzkit/skills/gz-adr-create/SKILL.md` — exemplar of a foundation-aligned skill body for shape reference

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle; tests pass with `@covers`

### Code Quality
- [ ] Lint/type clean

### Gate 3: Docs (Heavy)
- [ ] mkdocs --strict clean
- [ ] Runbook entry under "Complexity doctrine surfaces" cites `gz-complexity-distill`

### Gate 4: BDD (Heavy)
- [ ] BDD scenario tagged `@REQ-0.0.27-06-NN` covers a skill invocation against fixture corpus + fixture baseline (or registered as waived if OBPI-04's BDD scenario covers it transitively)

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST` confirmation

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents --surfaces
uv run gz agent sync control-surfaces  # post-sync diff empty
uv run gz arb step --name unittest -- uv run -m unittest tests/skills/test_gz_complexity_distill.py -v
```

## Acceptance Criteria

- [ ] REQ-0.0.27-06-01: Given the canonical skill, when its frontmatter is parsed, then the schema validates and the `skill-version` is `0.1.0`.
- [ ] REQ-0.0.27-06-02: Given the skill body, when the cadence section is parsed, then all three triggers (annual calendar, drift > 25%, judgment) are present with the 6-month minimum re-distillation guard.
- [ ] REQ-0.0.27-06-03: Given the skill body, when the corpus reference is parsed, then it points at `data/exemplar_corpus.json` and does not duplicate the corpus content.
- [ ] REQ-0.0.27-06-04: Given the skill's Output Contract, when the destination CLI verb's default human-readable output is observed against a fixture corpus + baseline, then the observed output matches the form the skill declares.
- [ ] REQ-0.0.27-06-05: Given the skill's `gz_command` field, when resolved against `src/gzkit/cli/parser_artifacts.py`, then a registered CLI verb exists and the runbook prescribes it.
- [ ] REQ-0.0.27-06-06: Given a clean working tree, when `uv run gz agent sync control-surfaces` runs, then the three vendor-mirror copies are byte-identical to the canonical and the post-sync diff is empty.

## Completion Checklist

- [ ] Gate 1: Intent recorded
- [ ] Gate 2: RGR cycle; tests pass with `@covers`
- [ ] Code Quality: lint/type clean
- [ ] Gate 3: mkdocs --strict clean; runbook entry added
- [ ] Gate 4: BDD scenario or waiver
- [ ] Gate 5: TTY + `ATTEST` captured

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)
```text
# Paste RGR observations + final unittest output
```

### Code Quality
```text
# Paste lint/typecheck output
```

### Gate 3 (Docs)
```text
# Paste mkdocs --strict output + runbook diff hunk
```

### Gate 4 (BDD)
```text
# Paste behave output or waiver entry
```

### Gate 5 (Human)
```text
# Record attestation text + receipt IDs
```

### Value Narrative

<!-- Problem before: distillation cadence existed only as ADR § Decision prose with no operator-runnable surface; running distillation required reconstructing the corpus + filters + methodology from memory each time. Capability now: a vendor-mirrored skill that carries the corpus reference, cadence triggers, and methodology rationale, invocable ad-hoc by the operator and aligned with OBPI-04's brief contract. -->

### Key Proof

<!-- Paste the SKILL.md frontmatter + cadence-trigger section + post-sync mirror-equality verification. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

### Closing Argument

<!-- One paragraph: why the operator-runnable skill (vs CLI-verb-only) is the load-bearing surface for cadence triggers — the skill carries methodology rationale and corpus references the CLI flag cannot — and why mirror sync discipline is the structural defense against vendor-surface drift. -->

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` (heavy + foundation requires TTY + ATTEST)
- Attestation: substantive attestation text
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
