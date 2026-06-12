---
id: OBPI-0.0.70-04-fourth-source-triangulation
parent: ADR-0.0.70-turn-end-feedback-and-correction-mining
item: 4
lane: Lite
status: Draft
---

# OBPI-0.0.70-04-fourth-source-triangulation: Fourth Source Triangulation

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.70-turn-end-feedback-and-correction-mining/ADR-0.0.70-turn-end-feedback-and-correction-mining.md`
- **Checklist Item:** #4 - "Fourth-source doctrine triangulation — Buetow section appended to `docs/governance/harness-engineering-appraisal.md` per the established per-thesis pattern (citation: Beyond Coding Podcast, 2026-06-10); campaign B.0 cross-link; `mkdocs build --strict` green"

**Status:** Draft

## Objective

The harness-engineering appraisal gains a fourth-source Buetow section per its
established per-thesis pattern — full citation (Beyond Coding Podcast,
2026-06-10; cracking-ai-engineering.com), the convergence inventory, and the adopted
deltas mapped to ADR-0.0.70's OBPIs — and the Magna Carta campaign records the
operator-verbatim amendment inserting B.0 (ADR-0.0.70); `mkdocs build --strict`
stays green.

## Lane

**Lite** - This OBPI remains internal to the promoted ADR implementation scope.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.70-turn-end-feedback-and-correction-mining/ADR-0.0.70-turn-end-feedback-and-correction-mining.md` — parent ADR for intent and scope
- `docs/governance/harness-engineering-appraisal.md` — fourth-source section
- `docs/governance/build-to-1.0-campaign-2026-06-10.md` — B.0 amendment with operator verbatim words (Magna Carta amendment discipline)
- `docs/design/adr/foundation/ADR-0.0.70-turn-end-feedback-and-correction-mining/obpis/OBPI-0.0.70-04-fourth-source-triangulation.md` — this brief (evidence recording)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: The appraisal section MUST follow the per-thesis pattern (source block, framing, triangulation, what-it-does/doesn't-unlock) and MUST state that the Buetow axis reinforces — never displaces — the Böckeler Wave-1/2 priorities (sidecar funded-not-displaced).
1. REQUIREMENT: The campaign amendment MUST quote the operator's verbatim words (2026-06-12) and insert B.0 referencing ADR-0.0.70, recorded in place per Magna Carta amendment discipline.
1. REQUIREMENT: The appraisal MUST reconcile the dangling `ADR-pool.harness-sidecar` reference (the pool file was planned, never drafted — flagged 2026-06-12).
1. REQUIREMENT: `uv run mkdocs build --strict` MUST exit 0 after the edits.
1. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.70-turn-end-feedback-and-correction-mining/ADR-0.0.70-turn-end-feedback-and-correction-mining.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.70-turn-end-feedback-and-correction-mining/ADR-0.0.70-turn-end-feedback-and-correction-mining.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/governance/harness-engineering-appraisal.md`
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
     yielded. The yielded product belongs in the `## Demo` section below.

     AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects. The
     OBPI-pipeline verify stage executes commands via shlex.split + shell=False
     (GHI #415); compound commands are blocked at authoring time by
     gz validate --brief-command-shape and rejected at the verify stage.
     Write multi-step verification as separate uv run ... lines. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run mkdocs build --strict

# Specific verification for this OBPI
test -f docs/governance/harness-engineering-appraisal.md
test -f docs/governance/build-to-1.0-campaign-2026-06-10.md
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# The landed fourth-source section and the recorded campaign amendment.
rg -n "Buetow" docs/governance/harness-engineering-appraisal.md
rg -n "B.0" docs/governance/build-to-1.0-campaign-2026-06-10.md
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.70-04-01 [support]: The appraisal's Buetow section lands per the per-thesis pattern with full citation and the adopted-deltas mapping to OBPI-01/02/03, including the sidecar funded-not-displaced statement and the `ADR-pool.harness-sidecar` dangling-reference reconciliation. Proof: `artifact_edited` ledger event + `gz validate --documents` exit 0 (structural scope admitting the doc) + `mkdocs build --strict` exit 0.
- [ ] REQ-0.0.70-04-02 [support]: The campaign records the operator-verbatim amendment and the B.0 item referencing ADR-0.0.70 (Magna Carta amendment discipline, recorded in place). Proof: `artifact_edited` ledger event + `gz validate --documents` exit 0 (structural scope admitting the campaign doc); demo anchors the B.0 row via rg.

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
