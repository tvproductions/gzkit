---
id: OBPI-0.45.0-01-brief-prefill
parent: ADR-0.45.0-prefill-driven-authoring-scaffolding
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.45.0-01-brief-prefill: OBPI brief prefill scaffolding

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.45.0-prefill-driven-authoring-scaffolding/ADR-0.45.0-prefill-driven-authoring-scaffolding.md`
- **Checklist Item:** #1 — "Implement OBPI brief prefill in `gz obpi specify` skill / future CLI verb — section openers only, parent-ADR-Decision-pinned Discovery Checklist; backwards-compatible corpus-freeze waiver"

**Status:** Draft

## Objective

Replace placeholder tokens (`{intent}`, `{decision}`, etc.) in the OBPI brief skeleton with literal canonical section openers, with the parent-ADR-Decision read pinned as Discovery Checklist item #1.

## Lane

**Heavy** — Modifies the brief authoring template, which is a contract surface agents read.

## Allowed Paths

- `src/gzkit/skills/gz-obpi-specify/SKILL.md` — skill instruction updates
- `src/gzkit/skills/gz-obpi-specify/template.md` (or wherever the brief template lives) — section-opener replacement
- `data/prefill_conformance_waivers.json` — corpus-freeze waiver list of pre-existing briefs
- `tests/skills/test_obpi_brief_prefill.py`
- `docs/design/adr/pre-release/ADR-0.45.0-prefill-driven-authoring-scaffolding/**`

## Denied Paths

- `src/gzkit/commands/obpi.py` — attestation prefill in OBPI-02
- `src/gzkit/governance/trust_audits.py` — conformance validator in OBPI-03
- `features/**` — BDD coverage in OBPI-03
- Any path not listed

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The brief skeleton emitted by `gz obpi specify` (or its skill) replaces every `{<placeholder>}` token with the literal canonical opening line of that section, e.g.:
   - `## ADR Item\n- **Source ADR:** <auto-filled-path>\n- **Checklist Item:** ` (agent fills checklist item quote)
   - `## Objective\n\n` (agent fills one sentence)
   - `## Lane\n\n**<auto-filled>** — ` (agent fills rationale)
2. REQUIREMENT: The Discovery Checklist section's first item is `[ ] Parent ADR § Decision item — quote the line this OBPI implements`. The agent cannot proceed past Discovery Checklist authoring without filling this item.
3. REQUIREMENT: Section openers MUST NOT include example content (no "e.g.", no inline examples). The depth-discipline rule is binding.
4. REQUIREMENT: Pre-existing briefs (those authored before this ADR lands) are catalogued in `data/prefill_conformance_waivers.json` at corpus-freeze time. The list is closed at this OBPI's landing; no new entries permitted.
5. REQUIREMENT: Tests cover: skeleton emission produces canonical openers; placeholder tokens absent from output; Discovery Checklist item #1 is the parent-ADR-Decision pin; corpus-freeze waiver loads correctly.
6. REQUIREMENT: Tests use `tempfile`-backed parent-ADR fixtures; NEVER touch live ADRs.
7. REQUIREMENT: Each test decorated with `@covers(REQ-0.45.0-01-NN)`.
8. REQUIREMENT: NEVER include the operator's personal email.
9. REQUIREMENT: TDD discipline.

> STOP-on-BLOCKERS: if `gz obpi specify` does not exist as a CLI verb yet (skill-only), implement at the skill template layer and document the migration path for when the CLI verb lands.

## Discovery Checklist

- [ ] Parent ADR § Decision item 1 — quote the line this OBPI implements
- [ ] AGENTS.md § Skills protocol
- [ ] `.gzkit/skills/gz-obpi-specify/SKILL.md` — existing skill structure
- [ ] An existing brief (e.g., OBPI-0.0.22-01) — confirm canonical section structure
- [ ] `.claude/rules/skill-surface-sync.md` — version-bump discipline

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded
### Gate 2: TDD
- [ ] RGR; tests pass
### Code Quality
- [ ] Lint clean
### Gate 3: Docs (Heavy)
- [ ] In OBPI-03
### Gate 4: BDD (Heavy)
- [ ] In OBPI-03
### Gate 5: Human (Heavy)
- [ ] Required (heavy lane)

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz arb step --name unittest -- uv run -m unittest tests/skills/test_obpi_brief_prefill.py -v
```

## Acceptance Criteria

- [ ] REQ-0.45.0-01-01: Given the prefill scaffold, when emitted, then no `{<placeholder>}` token remains in the skeleton.
- [ ] REQ-0.45.0-01-02: Given the Discovery Checklist section, when the skeleton is emitted, then the first item is the parent-ADR-Decision-quote pin.
- [ ] REQ-0.45.0-01-03: Given the depth-discipline rule, when the skeleton is reviewed, then no section opener includes example content.
- [ ] REQ-0.45.0-01-04: Given a pre-existing brief catalogued in `data/prefill_conformance_waivers.json`, when the conformance validator runs (OBPI-03), then the brief is grandfathered.

## Completion Checklist

- [ ] **Gate 1:** Intent recorded
- [ ] **Gate 2:** RGR; tests pass
- [ ] **Code Quality:** clean
- [ ] **OBPI Acceptance:** Heavy = TTY + `ATTEST` required

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD)
```text
# RGR + unittest output
```

### Code Quality
```text
# lint/typecheck output
```

### Gate 5 (Human)
```text
# Record attestation text here at completion
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

- Attestor: `<name>` (heavy lane requires human)
- Attestation: substantive attestation text
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
