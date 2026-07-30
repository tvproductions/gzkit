---
id: OBPI-0.0.57-05-docs-runbook-fixtures
parent: ADR-0.0.57-foundation-adr-nominal-id-triage
item: 5
lane: Heavy
status: Completed
---

# OBPI-0.0.57-05-docs-runbook-fixtures: Docs Runbook Fixtures

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.57-foundation-adr-nominal-id-triage/ADR-0.0.57-foundation-adr-nominal-id-triage.md`
- **Checklist Item:** #5 - "OBPI-0.0.57-05: **docs-runbook-fixtures** — Update gz-adr-create manpage and governance runbook for nominal-ID allocation; add examples and fixtures for Foundation Triage invocation."

**Status:** Completed

## Objective

**docs-runbook-fixtures** — Update gz-adr-create manpage and governance runbook for nominal-ID allocation; add examples and fixtures for Foundation Triage invocation.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/user/manpages/plan-create.md` (or whichever manpage governs `gz plan create`) — finalize nominal-allocator description started in OBPI-02; include worked nominal-allocation example
- `docs/user/manpages/foundation-triage.md` — new manpage describing `gz-foundation-triage` skill invocation (note: the surface is a skill, not a CLI verb, so manpage convention may treat it as a docs/skill page; author wherever the existing skill-doc convention sits)
- `docs/user/runbook.md` — add nominal-ID allocation workflow + foundation-triage invocation flow alongside existing pool-triage and ghi-triage flows
- `docs/governance/governance_runbook.md` — add foundation-triage to governance-maintainer planning workflow + nominal allocation guidance
- `features/foundation_triage.feature` — BDD scenarios covering nominal allocation (gap-allocation case) AND foundation-triage skill invocation (heavy lane Gate 4)
- `tests/fixtures/foundation_triage_e2e/` — end-to-end fixture: foundation backlog with mixed priority signals, gap in nominal IDs, port/adapter reclassify candidate
- `tests/test_foundation_triage_e2e.py` — end-to-end integration tests exercising allocator (OBPI-02) + rubric (OBPI-04) + skill body (OBPI-03) against the fixture
- `docs/design/adr/foundation/ADR-0.0.57-foundation-adr-nominal-id-triage/obpis/OBPI-0.0.57-05-docs-runbook-fixtures.md` — this brief (evidence updates only)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/commands/plan.py` — allocator implementation is OBPI-0.0.57-02's surface (this OBPI documents it, does not implement)
- `src/gzkit/foundation/**` — rubric + composer are OBPI-04 / OBPI-03 surfaces
- `.gzkit/skills/gz-foundation-triage/SKILL.md` — skill body is OBPI-03's surface
- `docs/design/adr/foundation/ADR-0.0.17-*/**`, `docs/design/adr/foundation/ADR-0.0.18-*/**` — doctrine amendments are OBPI-01's surface
- `docs/user/manpages/pool-triage.md` — owned by ADR-pool.gz-adr-pool-triage
- New runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `docs/user/manpages/plan-create.md` MUST be updated to describe nominal-allocator semantics, include a worked gap-allocation example, AND satisfy the manpage template (description, usage, options, examples, exit codes per `.claude/rules/cli.md`).
2. REQUIREMENT: `docs/user/manpages/foundation-triage.md` MUST exist with the same template form, describing skill invocation, the three steps, the ephemeral-output property, and the rubric signal dimensions (cross-references OBPI-04).
3. REQUIREMENT: Every `gz <verb>` reference in the manpage and runbook updates MUST resolve to a registered parser verb — `gz validate --cli-alignment` MUST exit 0.
4. REQUIREMENT: `features/foundation_triage.feature` MUST encode at least two scenarios — nominal-allocator gap-allocation case AND foundation-triage skill invocation — and `uv run -m behave features/foundation_triage.feature` MUST pass (Gate 4 for heavy lane).
5. REQUIREMENT: `uv run mkdocs build --strict` MUST exit 0 after manpage and runbook additions (Gate 3 for heavy lane).
6. REQUIREMENT: Both `docs/user/runbook.md` (operator) and `docs/governance/governance_runbook.md` (maintainer) MUST be updated in the same OBPI per `.claude/rules/gate5-runbook-code-covenant.md` (three-layer documentation model).
7. NEVER: Use placeholder output examples in manpages — manpage EXAMPLES sections MUST contain real CLI output (Prime Directive 2).
8. ALWAYS: Render any relative path in fixtures via forward slashes — cross-platform invariant.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.


## Creates these files

<!-- Net-new files this OBPI creates. Path existence is exempt for these entries per GHI #419. -->

- `docs/user/manpages/foundation-triage.md` **CREATE**
- `features/foundation_triage.feature` **CREATE**
- `tests/fixtures/foundation_triage_e2e/` **CREATE**
- `tests/test_foundation_triage_e2e.py` **CREATE**

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.57-foundation-adr-nominal-id-triage/ADR-0.0.57-foundation-adr-nominal-id-triage.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.57-foundation-adr-nominal-id-triage/ADR-0.0.57-foundation-adr-nominal-id-triage.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.57-foundation-adr-nominal-id-triage/**`
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
uv run gz arb step --name unittest -- uv run -m unittest -q tests.test_foundation_triage_e2e
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run -m behave features/foundation_triage.feature

# OBPI-specific surface checks
test -f docs/user/manpages/plan-create.md
test -f docs/user/manpages/foundation-triage.md
grep -q "foundation-triage" docs/user/runbook.md
grep -q "foundation-triage" docs/governance/governance_runbook.md
grep -q "nominal" docs/user/manpages/plan-create.md
ls tests/fixtures/foundation_triage_e2e/ > /dev/null
uv run gz cli audit
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Walk through the operator runbook section
sed -n '/^## Foundation triage$/,/^## /p' docs/user/runbook.md

# Show the maintainer runbook section
sed -n '/^## Nominal ADR allocation$/,/^## /p' docs/governance/governance_runbook.md

# Run BDD scenarios — nominal gap allocation + skill invocation
uv run -m behave features/foundation_triage.feature --no-capture

# Run the end-to-end test exercising allocator + rubric + skill body
uv run python -m unittest -v tests.test_foundation_triage_e2e
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.57-05-01: Given `docs/user/manpages/plan-create.md` and `docs/user/manpages/foundation-triage.md` exist, when `gz cli audit` runs, then both manpages are covered across manpage/command-doc/index (exit 0).
- [ ] REQ-0.0.57-05-02: Given the manpage and runbook updates, when `gz validate --cli-alignment` runs, then every `gz <verb>` reference resolves to a registered parser verb (exit 0).
- [ ] REQ-0.0.57-05-03: Given `features/foundation_triage.feature`, when `uv run -m behave features/foundation_triage.feature` runs, then both the `nominal-allocator gap allocation` scenario and the `foundation-triage skill invocation` scenario pass.
- [ ] REQ-0.0.57-05-04: Given the end-to-end fixtures, when `tests/test_foundation_triage_e2e.py` runs, then OBPI-02 nominal allocator, OBPI-04 rubric scoring, and OBPI-03 skill orchestration are each exercised by at least one test case.
- [ ] REQ-0.0.57-05-05: Given the docs additions, when `uv run mkdocs build --strict` runs, then exit code is 0 with no warnings.
- [ ] REQ-0.0.57-05-06: Given both `docs/user/runbook.md` AND `docs/governance/governance_runbook.md`, when read, then both contain a `foundation-triage` section consistent with the manpage (three-layer doc covenant).
- [ ] REQ-0.0.57-05-07: Given the manpages, when the EXAMPLES sections are read, then they contain real CLI output captured from a fixture run — no placeholder text (Prime Directive 2).

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


The nominal allocator's gap-suggestion is reproducible — `gz plan create my-adr --kind foundation --semver 99.0.0` against a workspace with foundation IDs 0.0.1, 0.0.2, and 0.0.4 emits `"ERROR: --kind foundation requires --semver matching 0.0.x (got '99.0.0'). Next free nominal foundation ID: 0.0.3."`. That verbatim output now lives in `docs/user/manpages/plan-create.md` § Nominal Allocator — Gap-Filling Example (REQ-7, no placeholders), is exercised by BDD scenario `nominal-allocator gap-allocation suggests lowest free integer` (receipt `arb-step-behave-263d0f196f204ec6b1973d6bb7a27ce2`), and is verified by `TestNominalAllocatorE2E.test_gap_fill_suggests_0_0_3`. The triage script's `--format json` output is reproducible from `tests/fixtures/foundation_triage_e2e/` and is embedded verbatim in `docs/user/skills/gz-foundation-triage.md` Step 1 Output Example. All five quality receipts (lint/typecheck/unittest/mkdocs/behave) exited 0.

### Implementation Summary


- Files created: `tests/fixtures/foundation_triage_e2e/` (3 foundation ADR stubs at IDs 0.0.1/0.0.2/0.0.4 with gap at 3, insights.jsonl, 2 pool ADRs), `tests/test_foundation_triage_e2e.py` (11 tests across 4 classes), `features/foundation_triage.feature` (2 BDD scenarios @REQ-0.0.57-05-03), `features/steps/foundation_triage_steps.py` (BDD steps for triage script invocation)
- Files modified: `docs/user/manpages/plan-create.md` (Nominal Allocator gap-filling example with real CLI output), `docs/user/skills/gz-foundation-triage.md` (signal dimensions table, ephemeral output property, step-1 example with real fixture JSON), `docs/user/runbook.md` (Foundation Triage section), `docs/governance/governance_runbook.md` (nominal ID allocation note + Foundation-Triage Planning Workflow section), `data/behave_coverage_waivers.json` (OBPI-05 waiver: 6 docs/structural REQs waived to unit-tier TestDocsFixturesCoverageE2E, REQ-03 covered by 2 BDD scenarios)
- Tests added: 11 (5 e2e covering OBPI-02/03/04 surfaces + 5 docs-coverage assertions for REQs 01/02/05/06/07); 2 BDD scenarios covering REQ-03
- Date completed: 2026-05-23
- Attestation status: attested by operator (`attest completed`)
- Defects noted: none

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.57-05-docs-runbook-fixtures heavy-lane delivery verified against 7/7 REQs (gz covers 100%), 5494/5494 unittest pass (arb-step-unittest-659b28ee3fef42c39b500da1a65a3ffa), lint+typecheck clean (arb-ruff-29dd713b50af4ce1aea5d91af5490142, arb-step-typecheck-e9d07de99d6042fcb1bb55be91f293fd), mkdocs --strict clean (arb-step-mkdocs-0593689e0cf447e3bcb8db94e0d7ae0a), behave 2/2 scenarios pass (arb-step-behave-263d0f196f204ec6b1973d6bb7a27ce2), cli audit 101/101 commands covered.
- Date: 2026-05-23

---

**Date Completed:** 2026-05-23

**Evidence Hash:** -
