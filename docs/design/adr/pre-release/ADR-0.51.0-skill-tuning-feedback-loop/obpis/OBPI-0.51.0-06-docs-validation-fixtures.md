---
id: OBPI-0.51.0-06-docs-validation-fixtures
parent: ADR-0.51.0-skill-tuning-feedback-loop
item: 6
lane: Heavy
status: Draft
---

# OBPI-0.51.0-06-docs-validation-fixtures: **docs-validation-fixtures** — Add docs, examples, and validation fixtures for ad-hoc chore invocation patterns and skill coverage tracking.

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.51.0-skill-tuning-feedback-loop/ADR-0.51.0-skill-tuning-feedback-loop.md`
- **Checklist Item:** #6 - "OBPI-0.51.0-06: **docs-validation-fixtures** — Add docs, examples, and validation fixtures for ad-hoc chore invocation patterns and skill coverage tracking."

**Status:** Draft

## Objective

**docs-validation-fixtures** — Add docs, examples, and validation fixtures for ad-hoc chore invocation patterns and skill coverage tracking.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/user/manpages/skill-tuning-optimize.md` — new manpage describing the Optimize chore's invocation surface, both run-modes, the prose-improvement loop, and the report artifact location
- `docs/user/runbook.md` — add operator workflow section for ad-hoc Optimize invocations alongside other chore-runner flows
- `docs/governance/governance_runbook.md` — add governance-maintainer guidance: when to run Optimize, what the report artifact contains, how to read the genealogy in SKILL.md `optimize:` block
- `docs/governance/skill-tuning-coverage.md` — skill coverage tracking documentation: which skills have been evaluated, how to read the trail, cadence guidance (annual / new-model-landing)
- `features/skill_tuning_optimize.feature` — BDD scenarios covering trim-and-verify, recalibrate-verify, and prose-improvement-loop human gate (heavy lane Gate 4)
- `tests/fixtures/skill_tuning_optimize_e2e/` — end-to-end fixture: baseline skill + candidate patch + hard basket + expected episode + expected report artifact
- `tests/test_skill_tuning_optimize_e2e.py` — end-to-end integration tests exercising OBPI-01 episode + OBPI-02 builder + OBPI-03 frontmatter schema + OBPI-04 chore + OBPI-05 prose loop
- `docs/design/adr/pre-release/ADR-0.51.0-skill-tuning-feedback-loop/obpis/OBPI-0.51.0-06-docs-validation-fixtures.md` — this brief (evidence updates only)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/skills_tuning/**` — episode/rubric/evaluator modules are OBPI-01's surface
- `src/gzkit/chores/skill-authoring-quality/**`, `src/gzkit/chores/skill-trigger-testing/**` — chore extensions are OBPI-02's surface
- `src/gzkit/core/models.py` — `SkillFrontmatter.optimize` schema is OBPI-03's surface
- `src/gzkit/chores/skill-tuning-optimize/**` — Optimize chore implementation is OBPI-04's surface
- `src/gzkit/skills_tuning/prose_improvement.py`, `src/gzkit/skills_tuning/human_gate.py` — prose-loop modules are OBPI-05's surface
- Mutations to canonical SKILL.md files outside the Optimize chore's gated path
- New runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `docs/user/manpages/skill-tuning-optimize.md` MUST satisfy the manpage template (description, usage, options, examples, exit codes per `.claude/rules/cli.md`) AND document both run-modes AND the prose-improvement loop.
2. REQUIREMENT: Every `gz <verb>` reference in the manpage, runbook updates, and BDD feature MUST resolve to a registered parser verb — `gz validate --cli-alignment` MUST exit 0.
3. REQUIREMENT: `features/skill_tuning_optimize.feature` MUST encode at least three scenarios: trim-and-verify run, recalibrate-verify run, and prose-improvement-loop human-gate fail-closed; `uv run -m behave features/skill_tuning_optimize.feature` MUST pass (Gate 4).
4. REQUIREMENT: End-to-end fixtures MUST exercise all five upstream OBPIs: OBPI-01 episode shape, OBPI-02 hard basket, OBPI-03 `optimize:` block round-trip on a fixture skill, OBPI-04 chore both run-modes, OBPI-05 prose-improvement loop gate behavior.
5. REQUIREMENT: `uv run mkdocs build --strict` MUST exit 0 after manpage + runbook + coverage doc additions (Gate 3).
6. REQUIREMENT: Both `docs/user/runbook.md` (operator) and `docs/governance/governance_runbook.md` (maintainer) MUST be updated in the same OBPI per the three-layer documentation model.
7. REQUIREMENT: `docs/governance/skill-tuning-coverage.md` MUST describe cadence guidance (annual + new-model-landing) and how to read the `optimize:` genealogy.
8. NEVER: Use placeholder output examples in manpages — manpage EXAMPLES sections MUST contain real CLI output (Prime Directive 2).
9. ALWAYS: Render any relative path in fixtures via forward slashes — cross-platform invariant.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.


## Creates these files

<!-- Net-new files this OBPI creates. Path existence is exempt for these entries per GHI #419. -->

- `docs/user/manpages/skill-tuning-optimize.md` **CREATE**
- `docs/governance/skill-tuning-coverage.md` **CREATE**
- `features/skill_tuning_optimize.feature` **CREATE**
- `tests/fixtures/skill_tuning_optimize_e2e/` **CREATE**
- `tests/test_skill_tuning_optimize_e2e.py` **CREATE**

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.51.0-skill-tuning-feedback-loop/ADR-0.51.0-skill-tuning-feedback-loop.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/pre-release/ADR-0.51.0-skill-tuning-feedback-loop/ADR-0.51.0-skill-tuning-feedback-loop.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/pre-release/ADR-0.51.0-skill-tuning-feedback-loop/**`
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
uv run gz validate --cli-alignment
uv run gz lint
uv run gz typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q tests.test_skill_tuning_optimize_e2e
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run -m behave features/skill_tuning_optimize.feature
uv run gz cli audit

# OBPI-specific surface checks
test -f docs/user/manpages/skill-tuning-optimize.md
test -f docs/governance/skill-tuning-coverage.md
grep -q "skill-tuning-optimize" docs/user/runbook.md
grep -q "skill-tuning-optimize" docs/governance/governance_runbook.md
ls tests/fixtures/skill_tuning_optimize_e2e/ > /dev/null
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Show the operator runbook section
sed -n '/^## Skill tuning (Optimize)$/,/^## /p' docs/user/runbook.md

# Show the maintainer runbook section
sed -n '/^## Skill tuning governance$/,/^## /p' docs/governance/governance_runbook.md

# Run BDD scenarios — both run modes + prose-improvement gate
uv run -m behave features/skill_tuning_optimize.feature --no-capture

# Run the end-to-end test exercising all five upstream OBPIs
uv run python -m unittest -v tests.test_skill_tuning_optimize_e2e

# Show the cadence guidance from the coverage doc
sed -n '/^## Cadence/,/^## /p' docs/governance/skill-tuning-coverage.md
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.51.0-06-01: Given `docs/user/manpages/skill-tuning-optimize.md` exists, when `gz cli audit` runs, then the manpage is covered across manpage/command-doc/index (exit 0).
- [ ] REQ-0.51.0-06-02: Given the manpage and runbook updates, when `gz validate --cli-alignment` runs, then every `gz <verb>` reference resolves to a registered parser verb (exit 0).
- [ ] REQ-0.51.0-06-03: Given `features/skill_tuning_optimize.feature`, when `uv run -m behave features/skill_tuning_optimize.feature` runs, then `trim-and-verify`, `recalibrate-verify`, and `prose-improvement-loop fail-closed on empty attestation` scenarios all pass.
- [ ] REQ-0.51.0-06-04: Given the end-to-end fixtures, when `tests/test_skill_tuning_optimize_e2e.py` runs, then OBPI-01 episode, OBPI-02 builder, OBPI-03 frontmatter schema, OBPI-04 run-modes, and OBPI-05 prose loop are each exercised by at least one test case.
- [ ] REQ-0.51.0-06-05: Given the docs additions, when `uv run mkdocs build --strict` runs, then exit code is 0 with no warnings.
- [ ] REQ-0.51.0-06-06: Given both `docs/user/runbook.md` AND `docs/governance/governance_runbook.md`, when read, then both contain a `skill-tuning-optimize` section consistent with the manpage (three-layer doc covenant).
- [ ] REQ-0.51.0-06-07: Given `docs/governance/skill-tuning-coverage.md`, when read, then it describes the annual + new-model-landing cadence and includes a worked example of reading an `optimize:` genealogy block.
- [ ] REQ-0.51.0-06-08: Given the manpage, when the EXAMPLES section is read, then it contains real CLI output captured from a fixture run — no placeholder text (Prime Directive 2).

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

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
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

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

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
