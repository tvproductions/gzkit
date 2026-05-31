---
id: OBPI-0.0.42-01-doctrine-and-canon
parent: ADR-0.0.42-storybook-doctrine
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.42-01-doctrine-and-canon: Storybook doctrine + directory contract + initial canon

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.42-storybook-doctrine/ADR-0.0.42-storybook-doctrine.md`
- **Checklist Item:** #1 — "Doctrine + directory contract + initial canon — Lands `docs/user/storybook/` shape, `arc-type` frontmatter schema, three template skeletons (journey, capability-bundle, capability-family), revises strawman to match doctrine, authors second arc fresh (capability-bundle on receipts capability), adds runbook cross-link."

**Status:** Draft

## Objective

Land the `docs/user/storybook/` directory contract, the `arc-type` frontmatter schema (`src/gzkit/schemas/storybook.json`), three arc-type template skeletons, the revised strawman as the canonical first journey arc, a second arc authored fresh against locked doctrine (capability-bundle on the receipts capability), and a runbook cross-link from `docs/user/runbook.md`.

## Lane

**Heavy** — introduces a new schema (`src/gzkit/schemas/storybook.json`) and a new directory contract consumed by downstream OBPIs (CLI surface, validator). External-contract changes per AGENTS.md.

## Allowed Paths

- `docs/user/storybook/` — directory exists; OBPI scaffolds `_templates/` subdirectory and second arc file inside it
- `docs/user/storybook/from-init-to-first-attested-release.md` — strawman to be revised in-place
- `docs/user/runbook.md` — single-section cross-link addition
- `src/gzkit/schemas/` — directory exists; OBPI authors new `storybook.json` schema inside it

## Denied Paths

- `src/gzkit/cli/**` — CLI surface is OBPI-02 scope
- `src/gzkit/storybook/**` — runtime module is OBPI-02 scope
- `src/gzkit/governance/trust_audits.py` — validator is OBPI-03 scope
- `.gzkit/skills/gz-adr-create/**` — STORY.md scaffolding is OBPI-04 scope
- Any per-ADR `STORY.md` file under `docs/design/adr/**` — STORY.md scaffolding is OBPI-04 scope
- New runtime dependencies, lockfiles, CI configuration

## Requirements (FAIL-CLOSED)

1. **REQUIREMENT (directory contract):** `docs/user/storybook/` MUST exist with at least the strawman arc and `_templates/` subdirectory containing three arc-type templates. The directory layout is the doctrine's load-bearing contract; downstream OBPIs (CLI, validator) read from this layout.
2. **REQUIREMENT (frontmatter schema):** `src/gzkit/schemas/storybook.json` MUST validate the canonical arc frontmatter (`id`, `status`, `arc-type`, `audience`, `anchored-adrs`, `anchored-skills`, `anchored-runbook-workflows`, `anchored-manpages`, `last-derived`). The `arc-type` field MUST be enum-restricted to `["journey", "capability-bundle", "capability-family"]`. No other values pass schema validation.
3. **REQUIREMENT (anchor block markers):** Every arc file MUST contain exactly one `<!-- BEGIN ANCHOR BLOCK -->` ... `<!-- END ANCHOR BLOCK -->` marker pair. The marker pair delimits the Layer-3 region the deriver (OBPI-02) is allowed to rewrite; everything outside the markers is Layer-1 authored canon.
4. **REQUIREMENT (strawman revision):** The existing strawman at `docs/user/storybook/from-init-to-first-attested-release.md` MUST be revised in-place to (a) declare `arc-type: journey` in frontmatter conforming to the schema, (b) carry the anchor block markers around its Layer-3 region, (c) preserve the operator-reviewed Layer-1 narrative without rewrite. If the strawman cannot be revised to fit the locked doctrine cleanly, archive it under `docs/user/storybook/archive/` and author a fresh first journey arc; do not force a poor fit (Negative consequence #8 fallback).
5. **REQUIREMENT (second arc — fresh authoring):** A capability-bundle arc on the receipts capability MUST be authored against the locked doctrine, not co-evolved with it. Anchored ADRs include at minimum ADR-0.0.24 (Attestation Receipt Binding) and ADR-0.0.27 (Exemplar-Corpus Doctrine, where applicable). Anchored skills include `gz-arb`. The bundle template is the survivorship-bias load-test (Negative consequence #9).
6. **REQUIREMENT (runbook cross-link):** `docs/user/runbook.md` MUST add a top-section cross-link directing operators to `docs/user/storybook/` for narrative-shape orientation distinct from procedural workflow.
7. **REQUIREMENT (no CLI/validator coupling yet):** Nothing in this OBPI's scope may presuppose `gz storybook` (OBPI-02) or `gz validate --storybook-fresh` (OBPI-03) being landed. The doctrine and canon must be inspectable and partially-usable without the runtime tooling.

> STOP-on-BLOCKERS: if the strawman cannot be cleanly revised AND a fresh first journey arc cannot be authored within scope, halt and surface the blocker; the doctrine cannot land without an exemplar journey arc.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into Implementation Summary.
- [ ] Parent ADR § Intent — the why-frame.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.42-storybook-doctrine/ADR-0.0.42-storybook-doctrine.md`

> **STOP:** If you cannot quote the parent ADR § Decision item this OBPI implements, STOP and re-read.

**Governance:**

- [ ] `AGENTS.md` § Lane Rules and § Behavior Rules
- [ ] `.gzkit/rules/governance-core.md`
- [ ] `docs/governance/state-doctrine.md` — Layer 1/2/3 doctrine

**Context:**

- [ ] Existing strawman: `docs/user/storybook/from-init-to-first-attested-release.md`
- [ ] Filed gaps: GHI #428 (runbook entry), GHI #429 (PRD→Constitution→Design wiring), GHI #430 (first-release ceremony)
- [ ] Sibling positioning: `docs/user/runbook.md`

**Prerequisites:**

- [ ] Parent ADR exists at `docs/design/adr/foundation/ADR-0.0.42-storybook-doctrine/`
- [ ] Strawman exists at `docs/user/storybook/from-init-to-first-attested-release.md`

**Existing Code:**

- [ ] Schema authoring conventions in `src/gzkit/schemas/`
- [ ] Existing Layer-3-derived-view precedent (e.g., `docs/governance/GovZero/adr-status.md` regeneration cycle)

## Quality Gates

### Gate 1: ADR

- [ ] Parent ADR checklist item #1 quoted in Implementation Summary
- [ ] Intent and scope recorded in this brief

### Gate 2: TDD

- [ ] Schema validation tests cover (a) valid frontmatter (b) invalid `arc-type` value (c) missing required field
- [ ] Anchor-block marker round-trip test (parser locates exactly one BEGIN/END pair)
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Strawman renders without broken anchors after revision
- [ ] Runbook cross-link renders

### Gate 4: BDD (Heavy)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`
- [ ] At minimum: a feature scenario exercising `arc-type` enum validation against an invalid arc file

### Gate 5: Human (Heavy + foundation)

- [ ] Human attestation recorded — foundation kind requires brief-level attestation regardless of lane

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

test -d docs/user/storybook
test -f docs/user/storybook/from-init-to-first-attested-release.md
test -f docs/user/storybook/_templates/journey.md
test -f docs/user/storybook/_templates/capability-bundle.md
test -f docs/user/storybook/_templates/capability-family.md
test -f src/gzkit/schemas/storybook.json
# expect ≥ 2 storybook .md files (strawman + receipts bundle)
ls docs/user/storybook/*.md
rg -n "BEGIN ANCHOR BLOCK" docs/user/storybook/*.md
rg -n "storybook" docs/user/runbook.md
```

## Demo

```bash
# Strawman renders as a valid arc-type=journey arc:
head -40 docs/user/storybook/from-init-to-first-attested-release.md

# Second arc is a fresh capability-bundle:
head -40 docs/user/storybook/receipts-capability.md

# Schema rejects invalid arc-type:
echo '{"arc-type": "invalid"}' | uv run python -c "import json,sys; from gzkit.schemas import validate_storybook; print(validate_storybook(json.load(sys.stdin)))"
```

## Acceptance Criteria

- [ ] REQ-0.0.42-01-01: Given the doctrine ADR's Decision section, when OBPI-01 is complete, then `docs/user/storybook/` exists with at least the strawman arc, three arc-type templates, and a second arc authored against the locked doctrine.
- [ ] REQ-0.0.42-01-02: Given a candidate arc file, when validated against `src/gzkit/schemas/storybook.json`, then frontmatter with `arc-type` outside the enum `[journey, capability-bundle, capability-family]` fails validation.
- [ ] REQ-0.0.42-01-03: Given any arc file in `docs/user/storybook/`, when scanned for anchor markers, then exactly one `<!-- BEGIN ANCHOR BLOCK -->` ... `<!-- END ANCHOR BLOCK -->` pair is present and properly nested.
- [ ] REQ-0.0.42-01-04: Given the strawman as it stands today, when revised under this OBPI, then either (a) the revision preserves the operator-reviewed Layer-1 narrative while adding marker-bounded Layer-3 anchor block, or (b) the strawman is archived under `docs/user/storybook/archive/` and a fresh first journey arc is authored — the fallback is exercised when revision-in-place is intractable.
- [ ] REQ-0.0.42-01-05: Given the receipts-capability bundle arc, when reviewed for survivorship-bias mitigation, then it is demonstrably authored against the locked doctrine (anchor block markers and frontmatter conform to schema), not against an earlier draft of the doctrine.
- [ ] REQ-0.0.42-01-06: Given `docs/user/runbook.md` after this OBPI, when read by an operator orienting to gzkit, then a top-section cross-link routes them to the storybook directory for narrative-shape orientation.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** RGR cycle followed; schema and marker tests pass
- [ ] **Code Quality:** Lint, type check clean
- [ ] **Gate 3 (Docs):** mkdocs --strict build clean
- [ ] **Gate 4 (BDD):** Behave scenarios pass
- [ ] **Gate 5 (Human):** Attestation recorded (foundation requires)
- [ ] **Value Narrative:** Documented below
- [ ] **Key Proof:** One concrete usage example below
- [ ] **OBPI Acceptance:** Evidence recorded

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste schema/marker test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste mkdocs build output here
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

<!-- Before: gzkit had no narrative-shape documentation surface; the artifact graph was rich but illegible as a value flow. After: the storybook directory exists with format contract, three arc-type templates, two canon arcs (one journey, one capability-bundle), and a runbook cross-link routing readers from procedure to narrative. -->

### Key Proof

<!-- Concrete usage: an operator reading docs/user/runbook.md sees the cross-link, navigates to docs/user/storybook/from-init-to-first-attested-release.md, and reads end-to-end value narrative anchored to specific ADRs and skills. The schema validates arc files; the marker pair delimits the future deriver's authority. -->

### Implementation Summary

- Files created/modified: `docs/user/storybook/` (new), `src/gzkit/schemas/storybook.json` (new), `docs/user/storybook/from-init-to-first-attested-release.md` (revised), `docs/user/storybook/receipts-capability.md` (new), `docs/user/storybook/_templates/{journey,capability-bundle,capability-family}.md` (new), `docs/user/runbook.md` (cross-link added)
- Tests added: schema validation, anchor marker round-trip, frontmatter enum enforcement
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked at brief authoring time. GHI #428/#429/#430 (filed during strawman authoring) are upstream of this OBPI and remain open as separate work._

## Human Attestation

- Attestor: `<name>` (foundation kind requires)
- Attestation: substantive attestation text
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
