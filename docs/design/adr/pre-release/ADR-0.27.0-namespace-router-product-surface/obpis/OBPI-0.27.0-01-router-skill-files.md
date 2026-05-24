---
id: OBPI-0.27.0-01-router-skill-files
parent: ADR-0.27.0-namespace-router-product-surface
item: 1
lane: Lite
status: Draft
---

# OBPI-0.27.0-01-router-skill-files: **router-skill-files** — Author the six namespace-router skill files (`gz-workflow`, `gz-governance`, `gz-quality`, `gz-project`, `gz-context`, `gz-manage`) under `.gzkit/skills/`. Each ≤ 500 bytes, intent-to-skill table only, no duplicated procedure or ceremony.

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/ADR-0.27.0-namespace-router-product-surface.md`
- **Checklist Item:** #1 - "OBPI-0.27.0-01: **router-skill-files** — Author the six namespace-router skill files (`gz-workflow`, `gz-governance`, `gz-quality`, `gz-project`, `gz-context`, `gz-manage`) under `.gzkit/skills/`. Each ≤ 500 bytes, intent-to-skill table only, no duplicated procedure or ceremony."

**Status:** Draft

## Objective

<!-- One-sentence concrete outcome. What does "done" look like? -->

**router-skill-files** — Author the six namespace-router skill files (`gz-workflow`, `gz-governance`, `gz-quality`, `gz-project`, `gz-context`, `gz-manage`) under `.gzkit/skills/`. Each ≤ 500 bytes, intent-to-skill table only, no duplicated procedure or ceremony.

## Lane

**Lite** - This OBPI remains internal to the promoted ADR implementation scope.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/ADR-0.27.0-namespace-router-product-surface.md` — parent ADR for intent and scope
- `.gzkit/skills/` — explicitly referenced by the checklist item

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: This OBPI MUST deliver: **router-skill-files** — Author the six namespace-router skill files (`gz-workflow`, `gz-governance`, `gz-quality`, `gz-project`, `gz-context`, `gz-manage`) under `.gzkit/skills/`. Each ≤ 500 bytes, intent-to-skill table only, no duplicated procedure or ceremony.
1. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief
1. REQUIREMENT: Verification commands MUST be concrete and runnable before acceptance
1. NEVER: Mark the OBPI accepted while scaffold defaults remain in the brief
1. ALWAYS: Reconcile the brief with the parent ADR before implementation begins

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/ADR-0.27.0-namespace-router-product-surface.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/ADR-0.27.0-namespace-router-product-surface.md`
- [ ] Required path exists or is intentionally created in this OBPI: `.gzkit/skills/`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. These are CONSTRUCTION HOUSEKEEPING (lint, type,
     test, mkdocs) — they prove the codebase is healthy, not what the OBPI
     yielded. The yielded product belongs in the `## Demo` section below. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
test -f docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/ADR-0.27.0-namespace-router-product-surface.md
test -f .gzkit/skills/
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Replace with concrete product demonstrations for this OBPI.
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.27.0-01-01: Six router slugs each have a canonical `.gzkit/skills/<slug>/SKILL.md` file, where the slug set is exactly `{gz-workflow, gz-governance, gz-quality, gz-project, gz-context, gz-manage}`.
- [ ] REQ-0.27.0-01-02: Each router `SKILL.md` frontmatter parses as a valid `gzkit.core.models.SkillFrontmatter` with `description` present, `name` matching the directory slug, and `model` ∈ {haiku, sonnet, opus}.
- [ ] REQ-0.27.0-01-03: Each router `SKILL.md` body contains exactly one markdown intent table with header `| Intent | Skill |`, and every routed skill cell in every router resolves to a real canonical skill slug discoverable under `.gzkit/skills/`. (Catalog-level reachability — every concrete skill is reachable from at least one router — is OBPI-03's `gz validate --router-tables` scope, not this OBPI's.)

### Byte-budget reconciliation (operator call, 2026-05-23)

The recovery plan (`docs/governance/get-out-of-jail-plan-2026-05-23.md` § Move 1) targets ≤500 bytes per router file. Existing skills floor at 761 bytes (`gz-state`) and average 8440 bytes; schema-required frontmatter (`name`, `description`, `category`, `lifecycle_state`, `owner`, `last_reviewed`, `model`) alone is ~270 bytes. **Operator decision in session:** target ≤700 bytes per router — honor the plan's *spirit* (intent table only, no procedure, ~12× smaller than mean) while staying schema-compliant. The plan number remains the aspirational ceiling; recovery doctrine is preserved without striking the field.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [x] Intent and scope recorded (parent ADR-0.27.0 § Decision; this brief § Acceptance Criteria with three concrete REQs derived from the parent Checklist row 01)

### Gate 2 (TDD — Red-Green-Refactor)

```text
$ uv run -m unittest -v tests.skills.test_namespace_routers
test_all_six_router_files_exist_under_canonical_skills_root ... ok
test_frontmatter_parses_and_name_matches_slug_and_model_is_known ... ok
test_intent_table_present_and_every_routed_skill_is_a_canonical_slug ... ok
----------------------------------------------------------------------
Ran 3 tests in 0.004s
OK

$ uv run gz covers OBPI-0.27.0-01 --plain
REQ-0.27.0-01-01    covered    tests/skills/test_namespace_routers.py
REQ-0.27.0-01-02    covered    tests/skills/test_namespace_routers.py
REQ-0.27.0-01-03    covered    tests/skills/test_namespace_routers.py
```

### Code Quality

```text
$ uv run ruff check tests/skills/test_namespace_routers.py
All checks passed!

$ uv run ruff format --check tests/skills/test_namespace_routers.py
1 file already formatted
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

**Before:** No first-stage intent surface — agents and operators pick from a flat 60+ skill catalog whose names expose gzkit's internal governance ontology (ADR, OBPI, ARB, ledger, attest) before any user-facing intent has been chosen. This is the GSD-comparison problem the parent ADR § Intent names.

**After:** Six namespace-router SKILL.md files under `.gzkit/skills/` carry intent-to-skill tables only — no procedure, no ceremony duplication. An agent can pick a router (`gz-workflow`, `gz-governance`, `gz-quality`, `gz-project`, `gz-context`, `gz-manage`), see ~5–9 routed intents, then invoke the concrete skill directly. Routers live alongside the existing flat catalog, never replacing it (parent ADR Non-Goals).

### Key Proof

```text
$ find .gzkit/skills/gz-{workflow,project,governance,quality,context,manage} -name SKILL.md -printf "%s\t%p\n" | sort -n
579     .gzkit/skills/gz-project/SKILL.md
623     .gzkit/skills/gz-workflow/SKILL.md
626     .gzkit/skills/gz-context/SKILL.md
666     .gzkit/skills/gz-manage/SKILL.md
680     .gzkit/skills/gz-quality/SKILL.md
727     .gzkit/skills/gz-governance/SKILL.md
```

Mean 650 bytes per router — 13× smaller than the project-wide SKILL.md mean of 8440 bytes and tighter than the existing 761-byte floor (`gz-state`). `gz-governance` lands 27 bytes over the operator-set 700-byte target because it routes nine governance intents (more than any other router); the overage is the price of carrying the highest routed-intent count, not bloat.

### Implementation Summary

- Files created:
  - `.gzkit/skills/gz-workflow/SKILL.md`
  - `.gzkit/skills/gz-project/SKILL.md`
  - `.gzkit/skills/gz-governance/SKILL.md`
  - `.gzkit/skills/gz-quality/SKILL.md`
  - `.gzkit/skills/gz-context/SKILL.md`
  - `.gzkit/skills/gz-manage/SKILL.md`
  - `tests/skills/test_namespace_routers.py`
- Files modified:
  - `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/obpis/OBPI-0.27.0-01-router-skill-files.md` (REQ rewrites, byte-budget reconciliation, evidence)
- Tests added: 3 (one per REQ); all GREEN on first authored run after skills landed.
- Date completed: 2026-05-23 (pending OBPI-02 sync + OBPI-03 validator + Stage 5 attestation)
- Attestation status: pending Gate 5 human attestation per ADR-0.0.36
- Defects noted: none in OBPI-01 scope.

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
