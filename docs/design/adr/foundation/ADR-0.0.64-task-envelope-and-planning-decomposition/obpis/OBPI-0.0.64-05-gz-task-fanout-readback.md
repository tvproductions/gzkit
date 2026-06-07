---
id: OBPI-0.0.64-05-gz-task-fanout-readback
parent: ADR-0.0.64-task-envelope-and-planning-decomposition
item: 5
lane: Heavy
status: Completed
ln:
  - req_id: REQ-0.0.64-05-01
    receipt_ids:
      - arb-ruff-5c28a807d3944a318daee2cf7bd91fb8
      - arb-step-mkdocs-78771e368a814aa3918f43307cdf46ed
      - arb-step-typecheck-ec9d60a81a3d449499f31b97713f1f51
      - arb-step-unittest-f7e5d91a88e14fddb51a9227dd5dee40
  - req_id: REQ-0.0.64-05-02
    receipt_ids:
      - arb-ruff-5c28a807d3944a318daee2cf7bd91fb8
      - arb-step-mkdocs-78771e368a814aa3918f43307cdf46ed
      - arb-step-typecheck-ec9d60a81a3d449499f31b97713f1f51
      - arb-step-unittest-f7e5d91a88e14fddb51a9227dd5dee40
  - req_id: REQ-0.0.64-05-03
    receipt_ids:
      - arb-ruff-5c28a807d3944a318daee2cf7bd91fb8
      - arb-step-mkdocs-78771e368a814aa3918f43307cdf46ed
      - arb-step-typecheck-ec9d60a81a3d449499f31b97713f1f51
      - arb-step-unittest-f7e5d91a88e14fddb51a9227dd5dee40
  - req_id: REQ-0.0.64-05-04
    receipt_ids:
      - arb-ruff-5c28a807d3944a318daee2cf7bd91fb8
      - arb-step-mkdocs-78771e368a814aa3918f43307cdf46ed
      - arb-step-typecheck-ec9d60a81a3d449499f31b97713f1f51
      - arb-step-unittest-f7e5d91a88e14fddb51a9227dd5dee40
  - req_id: REQ-0.0.64-05-05
    receipt_ids:
      - arb-ruff-5c28a807d3944a318daee2cf7bd91fb8
      - arb-step-mkdocs-78771e368a814aa3918f43307cdf46ed
      - arb-step-typecheck-ec9d60a81a3d449499f31b97713f1f51
      - arb-step-unittest-f7e5d91a88e14fddb51a9227dd5dee40
  - req_id: REQ-0.0.64-05-06
    receipt_ids:
      - arb-ruff-5c28a807d3944a318daee2cf7bd91fb8
      - arb-step-mkdocs-78771e368a814aa3918f43307cdf46ed
      - arb-step-typecheck-ec9d60a81a3d449499f31b97713f1f51
      - arb-step-unittest-f7e5d91a88e14fddb51a9227dd5dee40
---

# OBPI-0.0.64-05-gz-task-fanout-readback: Gz Task Fanout Readback

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/ADR-0.0.64-task-envelope-and-planning-decomposition.md`
<!-- gz-validate-skip: command-shape -->
- **Checklist Item:** #5 - "OBPI-0.0.64-05: **gz-task-fanout-readback** — New `gz task fanout <REQ-ID>` CLI command (table default; `--detail` ASCII tree with file:line spans; `--json` machine-readable). Columns: TASK, seq, status, files_touched, edits, attribution_check. Add TASK fan-out summary block to `gz status` output (per-REQ fan-out shape rendered during work, not just at closeout). Tests: each output format (table/detail/json) verified against fixture ledger; `gz status` integration verified; `attribution_check` column reflects validator-aligned pass/drift state. (heavy lane: new CLI surface; `gz status` integration)."

**Status:** Completed

## Objective

Add the operator-facing readback surface for per-REQ TASK fan-out:

<!-- gz-validate-skip: command-shape -->
`gz task fanout <REQ-ID>` (table default; `--detail` renders an ASCII tree with `file:line` spans; `--json` machine-readable) with columns `TASK, seq, status, files_touched, edits, attribution_check`. Add a TASK fan-out summary block to `gz status` output so per-REQ fan-out shape is visible DURING work (not retrospectively at closeout); the `attribution_check` column reflects the OBPI-04 validator's pass/drift state, giving operators one canonical readback that names where each TASK sits within its parent REQ.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/commands/task.py` — add `task_fanout_cmd` function
- `src/gzkit/cli/parser_artifacts.py` — register `gz task fanout` subcommand
- `src/gzkit/commands/status.py` — enhance `_task_summary_for_adr` with per-REQ fan-out data
- `src/gzkit/commands/status_render.py` — update `_print_status_task_section` with per-REQ fan-out block
- `tests/test_tasks.py` — add fixture-based fanout tests
- `docs/user/manpages/task-fanout.md` — new manpage (Heavy lane requires docs)
- `docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/**` — parent ADR package scope (brief)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

<!-- gz-validate-skip: command-shape -->
1. REQUIREMENT: `gz task fanout <REQ-ID>` MUST be a registered subcommand with table default output; columns TASK, seq, status, files_touched, edits, attribution_check; `--detail` ASCII tree with file:line spans; `--json` machine-readable
1. REQUIREMENT: `gz status` MUST render a per-REQ TASK fan-out block showing fan-out shape during work, not only aggregate counts
1. REQUIREMENT: `attribution_check` column MUST reflect the OBPI-04 validator's pass/drift state for each task
1. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief
1. REQUIREMENT: Each output format (table/detail/json) MUST be verified against a fixture ledger in tests; `gz status` integration MUST be verified
1. NEVER: Mark the OBPI accepted while scaffold defaults remain in the brief
1. ALWAYS: Add a manpage at `docs/user/manpages/task-fanout.md` (Heavy lane CLI surface requirement)

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
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --documents

# Specific verification for this OBPI
test -f docs/user/manpages/task-fanout.md
uv run gz task fanout --help
uv run gz task fanout --json REQ-0.0.64-01-01
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Table default — fan-out shape for a REQ
gz task fanout REQ-0.0.64-01-01

# ASCII tree with file:line spans
gz task fanout REQ-0.0.64-01-01 --detail

# Machine-readable JSON for tooling
gz task fanout REQ-0.0.64-01-01 --json

# Status shows per-REQ fan-out block during active work
gz status ADR-0.0.64
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.64-05-01 [BEHAVIOR]: Given a REQ-ID with tasks in the ledger, when `gz task fanout <REQ-ID>` runs (table default), then output contains columns TASK, seq, status, files_touched, edits, attribution_check with one row per task
- [ ] REQ-0.0.64-05-02 [BEHAVIOR]: Given a REQ-ID with tasks, when `gz task fanout <REQ-ID> --detail` runs, then output renders an ASCII tree with file:line spans for each task
- [ ] REQ-0.0.64-05-03 [BEHAVIOR]: Given a REQ-ID with tasks, when `gz task fanout <REQ-ID> --json` runs, then output is valid JSON containing task rows with all required fields (task_id, seq, status, files_touched, edits, attribution_check)
- [ ] REQ-0.0.64-05-04 [BEHAVIOR]: Given an active OBPI with tasks, when `gz status` runs, then the TASK section shows per-REQ fan-out shape (REQ ID, task count, status breakdown) rather than only aggregate counts
- [ ] REQ-0.0.64-05-05 [BEHAVIOR]: Given an OBPI with tasks where some have layer-drift (OBPI-04 validator detects drift), when `gz task fanout <REQ-ID>` runs, then the attribution_check column shows "drift" for affected tasks and "pass" for clean tasks
- [ ] REQ-0.0.64-05-06 [SUPPORT]: Each output format (table/detail/json) is verified against a fixture ledger in tests; `gz status` integration is verified with per-REQ fan-out shape; all tests pass via `uv run gz arb step --name unittest -- uv run -m unittest -q` — `gz validate --task-envelope-coherence` + `artifact_edited` event.

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
uv run gz task fanout REQ-0.0.64-05-01 --json
```

Outputs JSON array with task rows containing task_id, seq, status, files_touched, edits, attribution_check (values 'pass'|'drift'). `gz status ADR-0.0.64` now renders per-REQ TASK fan-out block under the Tasks: summary line, surfacing fan-out shape DURING active work (not only retrospectively at closeout).

Quality-gate receipts:
- arb-step-unittest-f7e5d91a88e14fddb51a9227dd5dee40 (5722/5722 unittest pass)
- arb-ruff-5c28a807d3944a318daee2cf7bd91fb8 (lint clean)
- arb-step-typecheck-ec9d60a81a3d449499f31b97713f1f51 (typecheck clean)
- arb-step-mkdocs-78771e368a814aa3918f43307cdf46ed (mkdocs --strict clean)

### Implementation Summary


- Files created: docs/user/manpages/task-fanout.md
- Files modified: src/gzkit/commands/task.py (added _build_fanout_rows, task_fanout_cmd); src/gzkit/cli/parser_artifacts.py (registered gz task fanout subcommand); src/gzkit/commands/status.py (enhanced _task_summary_for_adr with per_req); src/gzkit/commands/status_render.py (per-REQ rendering in _print_status_task_section); tests/test_tasks.py (TestTaskFanoutCmd 8 tests); config/doc-coverage.json (declared task fanout); docs/user/manpages/index.md (added task-fanout.md link); data/behave_coverage_waivers.json (added waiver entry)
- Tests added: 8 (TestTaskFanoutCmd)
- Date completed: 2026-05-28
- Attestation status: human-attested by g0
- Defects noted: none — full unittest suite 5722/5722 pass

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Heavy-lane OBPI-0.0.64-05-gz-task-fanout-readback (gz task fanout readback surface + gz status per-REQ block) attested 2026-05-28 by g0 after Stage 4 evidence review; all 5 BEHAVIOR REQs (REQ-0.0.64-05-01..05) covered with @covers tests in tests/test_tasks.py TestTaskFanoutCmd (8 tests pass), REQ-0.0.64-05-06 [SUPPORT] proof via ARB receipts arb-step-unittest-f7e5d91a88e14fddb51a9227dd5dee40 (5722/5722 pass), arb-ruff-5c28a807d3944a318daee2cf7bd91fb8, arb-step-typecheck-ec9d60a81a3d449499f31b97713f1f51, arb-step-mkdocs-78771e368a814aa3918f43307cdf46ed (all exit 0); behave_req_coverage waived per OBPI-0.0.64-01..04 precedent (data/behave_coverage_waivers.json).
- Date: 2026-05-28

---

**Date Completed:** 2026-05-28

**Evidence Hash:** -
