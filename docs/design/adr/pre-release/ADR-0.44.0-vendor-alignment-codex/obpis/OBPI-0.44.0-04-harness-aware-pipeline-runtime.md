---
id: OBPI-0.44.0-04-harness-aware-pipeline-runtime
parent: ADR-0.44.0-vendor-alignment-codex
item: 4
lane: Heavy
status: Draft
sensitivity: security
---

# OBPI-0.44.0-04-harness-aware-pipeline-runtime: Harness Aware Pipeline Runtime

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/ADR-0.44.0-vendor-alignment-codex.md`
- **Checklist Item:** #4 - "OBPI-0.44.0-04: **harness-aware-pipeline-runtime** — Replace Claude-only `.claude/plans` authority with harness-neutral plan-audit and pipeline-transition state while retaining Claude compatibility"

**Status:** Draft

## Objective

Plan-audit receipts and pipeline markers use one configured harness-neutral
project workspace, while vendor plan locations remain discovery inputs and
both Claude and Codex must satisfy the same runtime transition checks before
governed mutation begins.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/ADR-0.44.0-vendor-alignment-codex.md` — parent ADR and runtime-authority invariant
- `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/obpis/OBPI-0.44.0-04-harness-aware-pipeline-runtime.md` — this contract and evidence
- `src/gzkit/config.py` — configured harness-neutral pipeline workspace
- `src/gzkit/pipeline_markers.py` — plan discovery, receipt, marker, and migration authority
- `src/gzkit/pipeline_runtime.py` — transition enforcement and public compatibility exports
- `src/gzkit/commands/plan_audit_cmd.py` — canonical plan and receipt writer
- `src/gzkit/commands/obpi_cmd.py` — pipeline launch enforcement
- `src/gzkit/commands/obpi_precomplete.py` — receipt consumer migration
- `src/gzkit/commands/preflight.py` — derived-state cleanup migration
- `src/gzkit/hooks/scripts` — Claude plan-exit compatibility adapters
- `.claude/hooks` — regenerated Claude compatibility hooks
- `.gzkit/skills/gz-plan-audit` — harness-neutral plan-audit workflow
- `.gzkit/skills/gz-obpi-pipeline` — harness-neutral pipeline workflow
- `tests/test_pipeline_runtime.py` — canonical workspace and migration coverage
- `tests/test_plan_audit_cmd.py` — plan discovery and receipt coverage
- `tests/commands/test_obpi_pipeline.py` — first-mutation and launch enforcement
- `tests/commands/test_obpi_precomplete.py` — completion consumer coverage
- `tests/commands/test_preflight.py` — legacy-state cleanup coverage
- `features/subagent_pipeline.feature` — cross-harness transition behavior
- `docs/governance/state-doctrine.md` — Layer-3 path and authority update
- `docs/user/runbook.md` — operator plan and pipeline paths

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `.claude/plans/**` — compatibility input only; never the new authority
- `.agents/**` and `.codex/**` — vendor delivery surfaces belong to other OBPIs
- `.claude/skills/**`, `.agents/skills/**`, and `.github/skills/**` — generated mirrors are never authored directly
- `.gzkit/ledger.jsonl` direct edits
- Paths not listed in Allowed Paths
- New dependencies, CI files, and lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: Place authoritative project plan copies, plan-audit receipts, and
   pipeline markers under one `PathConfig` workspace, defaulting beneath
   `.gzkit/`, with no vendor name in the canonical path.
2. REQUIREMENT: Discover plans from the canonical workspace, project-local
   `.claude/plans`, global Claude plans, and explicitly supplied Codex plans;
   the newest matching plan is copied into the canonical workspace.
3. REQUIREMENT: Dual-read legacy Claude receipts and markers, migrate them
   deterministically, and write new state only to the canonical workspace.
4. REQUIREMENT: Enforce a matching PASS plan-audit receipt at pipeline launch and at
   the first governed implementation mutation, supplying the two Codex
   substitutes for Claude's `ExitPlanMode` hooks while retaining Claude as a
   thin compatibility adapter.
5. NEVER: Treat Layer-3 marker presence as gate truth or leave canonical skills
   and docs naming `.claude/plans` as universal authority.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/ADR-0.44.0-vendor-alignment-codex.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/ADR-0.44.0-vendor-alignment-codex.md`
- [ ] Required path exists or is intentionally created in this OBPI: `.claude/plans`
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
uv run -m unittest tests.test_pipeline_runtime tests.test_plan_audit_cmd tests.commands.test_obpi_pipeline tests.commands.test_obpi_precomplete tests.commands.test_preflight
uv run -m behave features/subagent_pipeline.feature
uv run gz plan audit OBPI-0.44.0-04 --json
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
uv run gz plan audit OBPI-0.44.0-04 --json
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.44.0-04-01 [BEHAVIOR]: Given plans from canonical, project-Claude, global-Claude, or explicit Codex inputs, plan audit selects the newest matching plan and stores its authoritative copy and receipt in the configured harness-neutral workspace.
- [ ] REQ-0.44.0-04-02 [BEHAVIOR]: Given legacy Claude receipts or markers, the runtime dual-reads and migrates them without changing verdict, OBPI identity, nonce, or active stage.
- [ ] REQ-0.44.0-04-03 [BEHAVIOR]: Given no matching PASS receipt, pipeline launch and first governed mutation fail closed with the canonical plan-audit command; with a matching current receipt both proceed.
- [ ] REQ-0.44.0-04-04 [BEHAVIOR]: Given Claude `ExitPlanMode`, the compatibility hooks delegate to the same plan-audit and routing predicates used by the Codex runtime substitute.
- [ ] REQ-0.44.0-04-05 [BEHAVIOR]: Given deleted or stale Layer-3 markers, preflight and pipeline runtime rebuild or remove derived state without treating marker presence as gate evidence.

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

- Parent Decision quote: **harness-aware-pipeline-runtime** — Replace Claude-only `.claude/plans` authority with harness-neutral plan-audit and pipeline-transition state while retaining Claude compatibility
- Planned files: config, marker/runtime consumers, Claude compatibility adapters, canonical skills, tests, BDD, and doctrine/runbook updates listed in Allowed Paths
- Tests added: pending TDD execution
- Date completed: pending
- Attestation status: pending Gate 5
- Defects noted: current pipeline state and universal skill text hard-code `.claude/plans`

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
