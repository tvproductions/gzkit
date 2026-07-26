---
id: OBPI-0.44.0-06-codex-instruction-budget-and-docs
parent: ADR-0.44.0-vendor-alignment-codex
item: 6
lane: Heavy
status: Draft
allowlist:
- docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/ADR-0.44.0-vendor-alignment-codex.md
- docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/obpis/OBPI-0.44.0-06-codex-instruction-budget-and-docs.md
- data/instructions_files_budget.json
- tests/governance/test_agents_md_map_doctrine.py
- tests/governance/test_agents_md_map_doctrine_application.py
- tests/governance/test_audit_instructions_files_budget.py
- docs/user/runbook.md
- docs/user/manpages/init.md
- docs/user/manpages/personas.md
- docs/user/manpages/validate.md
- docs/governance/harness-engineering-appraisal.md
reqs:
- REQ-0.44.0-06-01
- REQ-0.44.0-06-02
- REQ-0.44.0-06-03
- REQ-0.44.0-06-04
verification:
- gz validate --brief-command-shape and rejected at the verify stage.
- Write multi-step verification as separate uv run ... lines. -->
- uv run -m unittest tests.governance.test_agents_md_map_doctrine tests.governance.test_agents_md_map_doctrine_application tests.governance.test_audit_instructions_files_budget
- uv run gz validate --instructions-files-budget
- uv run gz validate --surfaces
- uv run mkdocs build --strict
---

# OBPI-0.44.0-06-codex-instruction-budget-and-docs: Codex Instruction Budget And Docs

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/ADR-0.44.0-vendor-alignment-codex.md`
- **Checklist Item:** #6 - "OBPI-0.44.0-06: **codex-instruction-budget-and-docs** — Prove Codex instruction-budget headroom and publish an observed-output runbook for the completed first-class surface"

**Status:** Draft

## Objective

The rendered root contract remains below Codex's default project-document byte
cap without a concealment override, and operators have one tested runbook for
config generation, hook trust, roles, pipeline state, parity validation, and
known hook interception limits.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/ADR-0.44.0-vendor-alignment-codex.md` — parent ADR and final fidelity evidence
- `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/obpis/OBPI-0.44.0-06-codex-instruction-budget-and-docs.md` — this contract and evidence
- `data/instructions_files_budget.json` — declared root contract budget
- `tests/governance/test_agents_md_map_doctrine.py` — Codex hard-cap proof
- `tests/governance/test_agents_md_map_doctrine_application.py` — rendered-byte proof
- `tests/governance/test_audit_instructions_files_budget.py` — budget validator coverage
- `README.md` — first-class vendor support summary
- `docs/user/runbook.md` — end-to-end Codex operator workflow
- `docs/user/manpages/init.md` — generated config behavior
- `docs/user/manpages/personas.md` — generated role behavior
- `docs/user/manpages/validate.md` — parity validation behavior
- `docs/governance/harness-engineering-appraisal.md` — 10-direct/2-substitute architecture record

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `AGENTS.md` and `.gzkit/corpus/**` — this increment proves the contract; it does not rewrite canon to chase a number
- `.codex/**`, `.agents/**`, and source runtime files — implementation belongs to OBPI-01 through -05
- `.gzkit/ledger.jsonl` direct edits
- GitHub issue state mutation — GHI #298 is already closed as superseded by this ADR, not as completion proof
- Paths not listed in Allowed Paths
- New dependencies, CI files, and lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: Prove rendered `AGENTS.md` is below both its declared budget and
   Codex's 32,768-byte default `project_doc_max_bytes` cap.
2. REQUIREMENT: Document observed config generation and preservation, project-hook
   hash review through `/hooks`, generated roles, harness-neutral plan state,
   and `gz validate --surfaces` recovery.
3. REQUIREMENT: Publish the 10-direct/2-runtime-substitute parity matrix and state that
   unified-exec and alternative-tool interception remains incomplete, so
   runtime validators retain authority.
4. NEVER: Raise `project_doc_max_bytes` merely to conceal growth, present GHI
   #298's promotion close as completion proof, or publish placeholder output.

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
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/**`
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
uv run -m unittest tests.governance.test_agents_md_map_doctrine tests.governance.test_agents_md_map_doctrine_application tests.governance.test_audit_instructions_files_budget
uv run gz validate --instructions-files-budget
uv run gz validate --surfaces
uv run mkdocs build --strict
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
uv run gz validate --instructions-files-budget
uv run gz validate --surfaces
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.44.0-06-01 [SUPPORT]: The committed root `AGENTS.md` byte count is below 32,768 and below the declared budget; proof is `gz validate --instructions-files-budget` plus the `artifact_edited` ledger event.
- [ ] REQ-0.44.0-06-02 [SUPPORT]: The runbook contains observed commands and outputs for config sync, hook trust, generated roles, harness-neutral plan state, and surface validation; proof is `gz validate --documents` plus the `artifact_edited` ledger event.
- [ ] REQ-0.44.0-06-03 [SUPPORT]: The architecture record enumerates ten direct hook behaviors and two runtime substitutes and names the remaining interception limitations; proof is `gz validate --surfaces` plus the `artifact_edited` ledger event.
- [ ] REQ-0.44.0-06-04 [SUPPORT]: Documentation links resolve, `mkdocs build --strict` passes, and GHI #298 is described only as promotion routing history; proof is `gz validate --documents` plus the `artifact_edited` ledger event.

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

- Parent Decision quote: **codex-instruction-budget-and-docs** — Prove Codex instruction-budget headroom and publish an observed-output runbook for the completed first-class surface
- Planned files: budget proof tests/data, README, runbook, manpages, and architecture record listed in Allowed Paths
- Tests added: pending proof execution
- Date completed: pending
- Attestation status: pending Gate 5
- Defects noted: GHI #298 was already closed at promotion and cannot serve as implementation-completion evidence

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
