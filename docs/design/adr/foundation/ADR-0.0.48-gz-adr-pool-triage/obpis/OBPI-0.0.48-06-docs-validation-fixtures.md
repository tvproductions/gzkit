---
id: OBPI-0.0.48-06-docs-validation-fixtures
parent: ADR-0.0.48-gz-adr-pool-triage
item: 6
lane: Heavy
status: Draft
---

# OBPI-0.0.48-06-docs-validation-fixtures: **docs-validation-fixtures** — Add docs, examples, fixtures, and validation coverage for full-pool and tag-filtered pool triage runs.

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.48-gz-adr-pool-triage/ADR-0.0.48-gz-adr-pool-triage.md`
- **Checklist Item:** #6 - "OBPI-0.0.48-06: **docs-validation-fixtures** — Add docs, examples, fixtures, and validation coverage for full-pool and tag-filtered pool triage runs."

**Status:** Draft

## Objective

**docs-validation-fixtures** — Add docs, examples, fixtures, and validation coverage for full-pool and tag-filtered pool triage runs.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/user/manpages/pool-triage.md` — operator-facing manpage for the skill (mirrors existing manpage convention under `docs/user/manpages/`)
- `docs/user/runbook.md` — add `pool-triage` invocation flow alongside `ghi-triage`
- `docs/governance/governance_runbook.md` — add `pool-triage` to governance-maintainer planning workflow
- `features/pool_triage.feature` — BDD scenarios for full-pool and `--tags`-filtered runs (heavy lane Gate 4)
- `tests/fixtures/pool_triage_e2e/full_pool/` — end-to-end fixture (multi-candidate pool, mixed staleness, one blocked, one reclassify-foundation)
- `tests/fixtures/pool_triage_e2e/tag_filtered/` — fixture restricting to a single thematic tag
- `tests/test_pool_triage_e2e.py` — end-to-end integration tests exercising the full skill chain (prepass + cognitive + filter + renderer) on the fixtures
- `docs/design/adr/foundation/ADR-0.0.48-gz-adr-pool-triage/obpis/OBPI-0.0.48-06-docs-validation-fixtures.md` — this brief (evidence updates only)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/pool/**` — module surfaces are OBPI-01/02/03/04's territory (this OBPI imports them, does not edit)
- `.gzkit/skills/pool-triage/SKILL.md` — skill body is OBPI-0.0.48-05's surface
- `docs/user/manpages/pool-management.md`, `docs/user/manpages/pool-graph.md` — upstream CLI manpages owned by ADR-0.0.46/47
<!-- gz-validate-skip: command-shape -->
- Edits to `gz pool *` CLI verbs — upstream contract is ADR-0.0.46/47's surface
- New runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `docs/user/manpages/pool-triage.md` MUST satisfy the manpage template (description, usage, options, examples, exit codes per `.claude/rules/cli.md` § Help Text Requirements).
2. REQUIREMENT: Every `gz <verb>` reference appearing in the manpage, runbook updates, or BDD feature MUST resolve to a registered parser verb — `gz validate --cli-alignment` MUST exit 0 (governance-core rule).
3. REQUIREMENT: `features/pool_triage.feature` MUST encode at least two scenarios — full-pool triage and `--tags <theme>` filter — and `uv run -m behave features/pool_triage.feature` MUST pass (Gate 4 for heavy lane).
4. REQUIREMENT: End-to-end fixtures MUST exercise all four upstream OBPIs: a pool ADR triggering OBPI-01 signal counters, an OBPI-02 reclassify-foundation case, an OBPI-04 blocked-foundation case, and OBPI-03 renderer determinism.
5. REQUIREMENT: `uv run mkdocs build --strict` MUST exit 0 after manpage and runbook additions (Gate 3 for heavy lane).
6. NEVER: Embed expected output strings in BDD scenarios that drift from the deterministic renderer's golden outputs (OBPI-03); reference golden files instead.
7. ALWAYS: Update both `docs/user/runbook.md` (operator) and `docs/governance/governance_runbook.md` (maintainer) in the same edit per `.claude/rules/gate5-runbook-code-covenant.md` (three-layer documentation model).

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.


## Creates these files

<!-- Net-new files this OBPI creates. Path existence is exempt for these entries per GHI #419. -->

- `docs/user/manpages/pool-triage.md` **CREATE**
- `features/pool_triage.feature` **CREATE**
- `tests/fixtures/pool_triage_e2e/full_pool/` **CREATE**
- `tests/fixtures/pool_triage_e2e/tag_filtered/` **CREATE**
- `tests/test_pool_triage_e2e.py` **CREATE**

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.48-gz-adr-pool-triage/ADR-0.0.48-gz-adr-pool-triage.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.48-gz-adr-pool-triage/ADR-0.0.48-gz-adr-pool-triage.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.48-gz-adr-pool-triage/**`
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
uv run gz arb step --name unittest -- uv run -m unittest -q tests.test_pool_triage_e2e
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run -m behave features/pool_triage.feature

# OBPI-specific surface checks
test -f docs/user/manpages/pool-triage.md
grep -q "pool-triage" docs/user/runbook.md
grep -q "pool-triage" docs/governance/governance_runbook.md
ls tests/fixtures/pool_triage_e2e/{full_pool,tag_filtered}/
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Render the manpage to verify formatting
uv run mkdocs serve & sleep 2; curl -s http://localhost:8000/user/manpages/pool-triage/ | head -40; kill %1

# Run the end-to-end test on the full-pool fixture
uv run python -m unittest -v tests.test_pool_triage_e2e.TestFullPool

# Run the BDD scenarios
uv run -m behave features/pool_triage.feature --no-capture

# Walk an operator through the runbook section
sed -n '/^## Pool triage$/,/^## /p' docs/user/runbook.md
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.48-06-01: Given `docs/user/manpages/pool-triage.md` exists, when `gz cli audit` runs, then the manpage is covered across manpage/command-doc/index (exit 0).
- [ ] REQ-0.0.48-06-02: Given the manpage and runbook updates, when `gz validate --cli-alignment` runs, then every `gz <verb>` reference resolves to a registered parser verb (exit 0).
- [ ] REQ-0.0.48-06-03: Given `features/pool_triage.feature`, when `uv run -m behave features/pool_triage.feature` runs, then at least the `full-pool triage` and `--tags <theme> filter` scenarios pass.
- [ ] REQ-0.0.48-06-04: Given the end-to-end fixtures, when `tests/test_pool_triage_e2e.py` runs, then OBPI-01 signal counters, OBPI-02 reclassify-foundation surfacing, OBPI-03 renderer determinism, and OBPI-04 blocked-foundation annotation are each exercised by at least one test case.
- [ ] REQ-0.0.48-06-05: Given the docs additions, when `uv run mkdocs build --strict` runs, then exit code is 0 with no warnings.
- [ ] REQ-0.0.48-06-06: Given the documentation updates, when reading `docs/user/runbook.md` AND `docs/governance/governance_runbook.md`, then both contain a `pool-triage` section consistent with the manpage (three-layer doc covenant).

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
