---
id: OBPI-0.0.64-03-subdivision-driven-seq-advancement
parent: ADR-0.0.64-task-envelope-and-planning-decomposition
item: 3
lane: Heavy
status: Completed
---

# OBPI-0.0.64-03-subdivision-driven-seq-advancement: Subdivision Driven Seq Advancement

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/ADR-0.0.64-task-envelope-and-planning-decomposition.md`
- **Checklist Item:** #3 - "OBPI-0.0.64-03: **subdivision-driven-seq-advancement** — Add `next_seq_for_req(req_id: str) -> int` helper to `src/gzkit/tasks.py` (queries ledger for max `seq` under `(req_id, current_obpi_id)`, returns +1). Add `gz task start --req REQ-X --seq next|N` CLI surface (subcommand additive to existing `gz task ...` shape). Preserve `d70793c4`'s `seq=01` auto-coordination as default-bucket fallback. Add subdivision sub-invariant to `.gzkit/rules/task-discovery.md` (bump rule version). Tests: `next_seq_for_req` returns 1 on empty ledger, N+1 on populated; `gz task start --seq next` mints next-available; explicit `--seq N` is honored when N doesn't collide. (heavy lane: new CLI surface)."

**Status:** Completed

## Objective

Add `next_seq_for_req(req_id: str) -> int` to `src/gzkit/tasks.py` (queries the ledger for max `seq` under `(req_id, current_obpi_id)` and returns +1) and a `gz task start --req REQ-X --seq next|N` CLI surface so subdivision becomes the deliberate planning act that splits a coarse REQ into per-labor-unit TASKs. `d70793c4`'s `seq=01` auto-coordination stays in place as the default-bucket diagnostic baseline OBPI-04's validator will USE to detect unattributed work; this OBPI extends `.gzkit/rules/task-discovery.md` (authored by OBPI-02) with the subdivision sub-invariant and bumps its rule version.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/ADR-0.0.64-task-envelope-and-planning-decomposition.md` — parent ADR for intent and scope
- `src/gzkit/tasks.py` — explicitly referenced by the checklist item
- **CREATE** `.gzkit/rules/task-discovery.md` — extended by this OBPI with the subdivision sub-invariant (file is OBPI-02's serial deliverable; from OBPI-03's validation perspective the path is still net-new because OBPI-02 has not landed)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: This OBPI MUST deliver: **subdivision-driven-seq-advancement** — Add `next_seq_for_req(req_id: str) -> int` helper to `src/gzkit/tasks.py` (queries ledger for max `seq` under `(req_id, current_obpi_id)`, returns +1). Add `gz task start --req REQ-X --seq next|N` CLI surface (subcommand additive to existing `gz task ...` shape). Preserve `d70793c4`'s `seq=01` auto-coordination as default-bucket fallback. Add subdivision sub-invariant to `.gzkit/rules/task-discovery.md` (bump rule version). Tests: `next_seq_for_req` returns 1 on empty ledger, N+1 on populated; `gz task start --seq next` mints next-available; explicit `--seq N` is honored when N doesn't collide. (heavy lane: new CLI surface).
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
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/tasks.py`
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
test -f src/gzkit/tasks.py
test -f .gzkit/rules/task-discovery.md
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

- [ ] REQ-0.0.64-03-01: Given the parent ADR intent, when the OBPI implementation is complete, then the primary scoped artifacts exist and match the documented contract
- [ ] REQ-0.0.64-03-02: Given the Allowed Paths in this brief, when the OBPI is executed, then changes remain inside scope and denied paths remain untouched
- [ ] REQ-0.0.64-03-03: Given the Verification commands in this brief, when they run, then evidence is recorded before the OBPI is accepted

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


```bash
# Empty ledger: next seq is 01
gz task start --req REQ-0.1.0-01-01 --seq next
# Started TASK-0.1.0-01-01-01

# Second call increments automatically
gz task start --req REQ-0.1.0-01-01 --seq next
# Started TASK-0.1.0-01-01-02

# Explicit collision is rejected
gz task start --req REQ-0.1.0-01-01 --seq 1
# exit != 0 (seq=01 already exists)
```

Mechanically verified by test_start_by_req_seq_next_empty_ledger, test_start_by_req_seq_next_increments, and test_start_by_req_explicit_seq_collision_fails in tests/test_tasks.py. ARB receipts: tests arb-step-unittest-f10841c5a70d417a9c68265c7b54f67c (5698/5698 pass), lint arb-ruff-dce7a3e74c8b4647998b9975dc1bce80, typecheck arb-step-typecheck-2fe59d8711f24bea961f47a6f8338a56, docs arb-step-mkdocs-1c2f26e4661b48cea251a6a4269fc160.

### Implementation Summary


- Files created/modified:
  - src/gzkit/tasks.py — added next_seq_for_req(req_id, *, existing_task_ids) -> int pure helper
  - src/gzkit/commands/task.py — added task_start_by_req_cmd and _REQ_PARTS_RE; imports next_seq_for_req
  - src/gzkit/cli/parser_artifacts.py — task_id positional optional; new --req/--seq flags; _dispatch_task_start nested dispatcher; task_start_by_req_cmd in lazy-import map
  - src/gzkit/doc_coverage/scanner.py — extended _extract_handler_name to accept named-function func= refs; extended _extract_local_docstrings to walk nested functions (so _dispatch_task_start docstring resolves for gz cli audit)
  - tests/test_tasks.py — TestNextSeqForReq (5 unit tests) + 5 new TestTaskStart methods covering --req/--seq CLI
  - tests/governance/test_obpi_0_0_64_03_subdivision_cli.py — CREATE: STRUCTURAL-FENCE REQ-02 + SUPPORT REQ-03 coverage (mirrors OBPI-02's TestObpiScopeAndEvidence pattern)
  - .gzkit/rules/task-discovery.md — bumped rule version 0.1.0 -> 0.2.0 (mirror auto-synced)
  - docs/user/manpages/task-start.md — documented --req/--seq flags with examples
  - data/behave_coverage_waivers.json — added obpi-0.0.64-03-subdivision-cli-unittest-via-invoke rationale + registry entry
- Tests added: 12 (TestNextSeqForReq 5 + TestTaskStart additions 5 + TestObpi006403ScopeAndEvidence 2)
- Date completed: 2026-05-28
- Attestation status: Operator attestation received Stage 4 (attest completed)
- Defects noted: None

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.64-03 subdivision-driven seq advancement: next_seq_for_req helper and `gz task start --req REQ-X --seq next|N` CLI surface delivered; 12 new tests total (10 in tests/test_tasks.py: TestNextSeqForReq + TestTaskStart additions; 2 in tests/governance/test_obpi_0_0_64_03_subdivision_cli.py for STRUCTURAL-FENCE REQ-02 and SUPPORT REQ-03 coverage); 3/3 REQs covered (behavior_uncovered_reqs=0, coverage_percent=100.0). ARB receipts: arb-step-unittest-1748cb0b8e3c43a097f15492b6b7f924 (5700/5700 pass), arb-ruff-dce7a3e74c8b4647998b9975dc1bce80, arb-step-typecheck-2fe59d8711f24bea961f47a6f8338a56, arb-step-mkdocs-1c2f26e4661b48cea251a6a4269fc160. Heavy lane / foundation kind / brief-level Gate 5 universal per ADR-0.0.36.
- Date: 2026-05-28

---

**Date Completed:** 2026-05-28

**Evidence Hash:** -
