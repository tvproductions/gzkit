---
id: OBPI-0.0.64-04-gz-validate-task-envelope-coherence
parent: ADR-0.0.64-task-envelope-and-planning-decomposition
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.64-04-gz-validate-task-envelope-coherence: Gz Validate Task Envelope Coherence

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/ADR-0.0.64-task-envelope-and-planning-decomposition.md`
<!-- gz-validate-skip: command-shape -->
- **Checklist Item:** #4 - "OBPI-0.0.64-04: **gz-validate-task-envelope-coherence** — New `gz validate --task-envelope-coherence` validator with three Heavy-fail signatures: (a) worklog event under active TASK with no `task_id`; (b) OBPI default-bucket-only TASKs without `req_atomic` exemption; (c) layer-drift across four discovery channels. Brief frontmatter `req_atomic: list[str]` exemption surface added (operator-authored escape valve; inline rationale required; surfaced in attestation evidence). Add `gz task envelope diagnose <OBPI-ID>` subcommand showing per-channel side-by-side declarations. Heavy fail-close / Lite warn-only. Join `gz check` default pipeline. Pydantic `BriefStructure` schema additive for `req_atomic`. Tests: each of three signatures triggers in fixture, with `req_atomic` exemption suppression verified; layer-drift across all 4-channel combinations covered; `gz check` pipeline integration smoke. (heavy lane: new validator scope; new schema additive; pipeline integration)."

**Status:** Draft

## Objective

Add the `gz validate --task-envelope-coherence` validator with three Heavy-fail signatures — (a) worklog event under an active TASK with no `task_id`; (b) OBPI default-bucket-only TASKs (`seq=01` across all REQs) with no `req_atomic` exemption; (c) layer-drift across the four discovery channels (Python `@advances`, frontmatter `tasks:`, commit trailer, ledger `task_id`) — and join it to the default `gz check` pipeline (Heavy fail-close, Lite warn-only). Extend `BriefStructure` with a `req_atomic: list[str]` brief-frontmatter exemption (operator-authored escape valve; inline rationale required; surfaced through attestation evidence) and add the operator-facing diagnose subcommand:

<!-- gz-validate-skip: command-shape -->
`gz task envelope diagnose <OBPI-ID>` which renders per-channel TASK declarations side-by-side so 2am operators can name which channel needs the update when layer-drift fail-closes a closeout.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/ADR-0.0.64-task-envelope-and-planning-decomposition.md` — parent ADR for intent and scope
- `docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/**` — parent ADR package scope

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

<!-- gz-validate-skip: command-shape -->
1. REQUIREMENT: This OBPI MUST deliver: **gz-validate-task-envelope-coherence** — New `gz validate --task-envelope-coherence` validator with three Heavy-fail signatures: (a) worklog event under active TASK with no `task_id`; (b) OBPI default-bucket-only TASKs without `req_atomic` exemption; (c) layer-drift across four discovery channels. Brief frontmatter `req_atomic: list[str]` exemption surface added (operator-authored escape valve; inline rationale required; surfaced in attestation evidence). Add `gz task envelope diagnose <OBPI-ID>` subcommand showing per-channel side-by-side declarations. Heavy fail-close / Lite warn-only. Join `gz check` default pipeline. Pydantic `BriefStructure` schema additive for `req_atomic`. Tests: each of three signatures triggers in fixture, with `req_atomic` exemption suppression verified; layer-drift across all 4-channel combinations covered; `gz check` pipeline integration smoke. (heavy lane: new validator scope; new schema additive; pipeline integration).
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
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/ADR-0.0.64-task-envelope-and-planning-decomposition.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/ADR-0.0.64-task-envelope-and-planning-decomposition.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/**`
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
test -f docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/ADR-0.0.64-task-envelope-and-planning-decomposition.md
uv run -m unittest tests/test_persona_schema.py -v
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

- [ ] REQ-0.0.64-04-01: Given the parent ADR intent, when the OBPI implementation is complete, then the primary scoped artifacts exist and match the documented contract
- [ ] REQ-0.0.64-04-02: Given the Allowed Paths in this brief, when the OBPI is executed, then changes remain inside scope and denied paths remain untouched
- [ ] REQ-0.0.64-04-03: Given the Verification commands in this brief, when they run, then evidence is recorded before the OBPI is accepted

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
