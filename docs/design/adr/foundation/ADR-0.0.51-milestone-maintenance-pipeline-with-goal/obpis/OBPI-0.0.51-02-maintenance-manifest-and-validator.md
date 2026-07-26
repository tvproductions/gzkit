---
id: OBPI-0.0.51-02-maintenance-manifest-and-validator
parent: ADR-0.0.51-milestone-maintenance-pipeline-with-goal
item: 2
lane: Heavy
status: Draft
allowlist:
- docs/design/adr/foundation/ADR-0.0.51-milestone-maintenance-pipeline-with-goal/ADR-0.0.51-milestone-maintenance-pipeline-with-goal.md
- data/milestone_maintenance_skills.json
reqs:
- REQ-0.0.51-02-01
- REQ-0.0.51-02-02
- REQ-0.0.51-02-03
verification:
- uv run gz validate --documents
- uv run gz lint
- uv run gz typecheck
- uv run gz test
- uv run -m unittest tests/test_persona_schema.py -v
---

# OBPI-0.0.51-02-maintenance-manifest-and-validator: Per-ADR-kind aware sweep manifest + structural validator

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.51-milestone-maintenance-pipeline-with-goal/ADR-0.0.51-milestone-maintenance-pipeline-with-goal.md`
- **Checklist Item:** #2 - "OBPI-0.0.51-02: `data/milestone_maintenance_skills.json` manifest schema (per-ADR-kind aware with `by_kind` and `always` blocks); per-skill mechanical-routability metadata; `gz validate --milestone-maintenance-manifest` structural validator"

**Status:** Draft

## Objective

<!-- One-sentence concrete outcome. What does "done" look like? -->

`data/milestone_maintenance_skills.json` manifest schema (per-ADR-kind aware with `by_kind` and `always` blocks); per-skill mechanical-routability metadata; `gz validate --milestone-maintenance-manifest` structural validator.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.51-milestone-maintenance-pipeline-with-goal/ADR-0.0.51-milestone-maintenance-pipeline-with-goal.md` — parent ADR for intent and scope
- `data/milestone_maintenance_skills.json` — explicitly referenced by the checklist item

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: **Stages**: sweep-dispatch (parallel) → findings-collect → findings-route → convergence-check
1. REQUIREMENT: **Driver persona**: `pipeline-orchestrator`
1. REQUIREMENT: **Runtime engine**: `src/gzkit/milestone_maintenance_runtime.py`
1. REQUIREMENT: **Trigger**: `validation_pipeline_completed` ledger event (ADR-0.0.50 emits this; this pipeline consumes it as its trigger)
1. REQUIREMENT: **Per-stage receipts** at `.gzkit/receipts/milestone-maintenance-<ADR-ID>-<iso>.json`
1. REQUIREMENT: **Unified ledger event**: `milestone_maintenance_completed` on terminal-stage success
1. REQUIREMENT: **`--from=<stage>`** resume points (sweep-dispatch, findings-collect, findings-route, convergence-check)
1. REQUIREMENT: **No redteam terminal stage** — this pipeline's output is findings routing (GHIs filed, trivial fixes applied), not state transitions. Findings themselves get reviewed by humans through their normal GHI/fix lifecycle.
1. REQUIREMENT: **Goal condition shape**: Up to 4,000 chars. Names: every skill in the manifest, finding-count + disposition for each, "stop after 8 turns and report final state regardless."
1. REQUIREMENT: **Evaluator constraint**: `/goal`'s evaluator only sees what the agent surfaced in the conversation. This forces the sweep skill to **explicitly state** every finding and its disposition — exactly the anti-vibing posture (the agent cannot vibe its way through; it must surface evidence the evaluator can read).
1. REQUIREMENT: **Iron Law**: "Milestone maintenance pipeline is not complete until convergence-check returns PASS — every review skill invoked, every finding routed, or operator-bypassed via `--accept-maintenance-deferred`."
1. REQUIREMENT: **Fallback (Codex / Copilot harnesses)**: Bounded iteration loop in the runtime engine — max 8 iterations, exit on zero-outstanding-findings or iteration-cap with final-state report. Same canonical skill body branches on harness detection (ADR-0.0.31 distribution invariant satisfied).
1. REQUIREMENT: An ADR is `Validated` but lacks a `milestone_maintenance_completed` ledger event newer than the `validation_pipeline_completed` event (`gz validate --milestone-maintenance-receipts`).
1. REQUIREMENT: A maintenance run produced findings that were neither fixed nor routed (`gz validate --milestone-maintenance-findings-routed`).
1. REQUIREMENT: `gz check --accept-maintenance-deferred <ADR-ID> --reason <REASON>` — operator-attested deferral. Defers the maintenance pass for one ADR's cycle (next ADR's milestone re-runs the manifest including any deferred concerns).
1. REQUIREMENT: No bypass for missing receipts. If the maintenance run didn't happen, run it.
1. REQUIREMENT: **First-class for Claude Code**: `/goal`, parallel `Agent` subagent dispatch for review skills, inline Codex calls (consumed by review skills like `gz-architecture-review` for cross-vendor deep-module judgment if its design adopts that pattern).
1. REQUIREMENT: **Fallback for Codex/Copilot**: bounded-iteration semantics, sequential sub-skill invocation if parallel dispatch is not supported, per-harness branching in the skill body's `## Harness Detection` section.
1. REQUIREMENT: **ADR-0.0.31 distribution invariant satisfied**: single canonical SKILL.md, executes one branch based on detected harness.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.51-milestone-maintenance-pipeline-with-goal/ADR-0.0.51-milestone-maintenance-pipeline-with-goal.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.51-milestone-maintenance-pipeline-with-goal/ADR-0.0.51-milestone-maintenance-pipeline-with-goal.md`
- [ ] Required path exists or is intentionally created in this OBPI: `data/milestone_maintenance_skills.json`
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
test -f docs/design/adr/foundation/ADR-0.0.51-milestone-maintenance-pipeline-with-goal/ADR-0.0.51-milestone-maintenance-pipeline-with-goal.md
test -f data/milestone_maintenance_skills.json
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

- [ ] REQ-0.0.51-02-01: Given the parent ADR intent, when the OBPI implementation is complete, then the primary scoped artifacts exist and match the documented contract
- [ ] REQ-0.0.51-02-02: Given the Allowed Paths in this brief, when the OBPI is executed, then changes remain inside scope and denied paths remain untouched
- [ ] REQ-0.0.51-02-03: Given the Verification commands in this brief, when they run, then evidence is recorded before the OBPI is accepted

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
