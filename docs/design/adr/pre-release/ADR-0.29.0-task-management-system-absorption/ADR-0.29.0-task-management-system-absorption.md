---
id: ADR-0.29.0-task-management-system-absorption
status: Pending
semver: 0.29.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-21
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.29.0: Task Management System Absorption

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Audit opsdev's `tasks.py` (1,174 lines) to catalog every subcommand, its arguments, and its behavior contract.
  1. Audit gzkit's existing task-adjacent surfaces (OBPI briefs, chore tracking, ADR lifecycle) to understand where task management might overlap or conflict.
  1. Create a capability matrix mapping each opsdev task subcommand to any gzkit equivalent (or explicit gap).

**Date Added:** 2026-03-21
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.29.0
**Area:** Task Management — Companion Absorption (Evaluation)

## Agent Context Frame --- MANDATORY

**Role:** Absorption evaluator --- determining whether opsdev's task management CLI belongs in gzkit as governance-generic tooling or should remain as project-specific tooling.

**Purpose:** When this ADR is complete, every one of opsdev's 7 task management subcommands (list, show, sync, verify, test, discover, tidy) has a documented evaluation with a clear decision: Absorb (governance-generic, belongs in gzkit), Exclude (project-specific, stays in opsdev), or Adapt (the concept generalizes but the implementation needs redesign for gzkit's model).

**Goals:**

- Every task management subcommand is examined individually with a documented decision
- Overlap with gzkit's existing OBPI/chore/ADR tracking is explicitly mapped and resolved
- The subtraction test holds: absorbed commands are governance-generic, excluded commands are project-specific
- No governance-useful capability remains stranded in opsdev without documented rationale

**Critical Constraint:** gzkit has zero task management surface today. This is pure evaluation --- does task management belong in gzkit, or does it overlap with gzkit's existing OBPI/chore/ADR tracking surfaces? The answer cannot be assumed; it must be demonstrated through comparison.

**Anti-Pattern Warning:** A failed implementation looks like: absorbing task management wholesale without evaluating whether `tasks list` duplicates `gz chores list`, whether `tasks verify` duplicates `gz gates`, or whether `tasks sync` duplicates `gz implement`. Equally bad: dismissing task management as "project-specific" without reading the 1,174 lines to understand what it actually does.

**Integration Points:**

- `src/gzkit/commands/chores.py` --- chore management (potential overlap with `tasks list/show`)
- `src/gzkit/commands/implement.py` --- implementation tracking (potential overlap with `tasks sync`)
- `src/gzkit/commands/gates.py` --- gate verification (potential overlap with `tasks verify`)
- `src/gzkit/commands/adr.py` --- ADR lifecycle (potential overlap with `tasks discover`)

---

## Feature Checklist --- Appraisal of Completeness

- Scope and surface
  - External contract may change (Heavy lane) --- new task management commands may be introduced if evaluation determines they belong in gzkit
- Tests
  - Each absorbed command must have unit tests; coverage >= 40%
- Docs
  - Decision rationale documented per OBPI (absorb/adapt/exclude)
- OBPI mapping
  - Each numbered checklist item maps to one brief; 7 items = 7 briefs

## Intent

opsdev contains a mature task management CLI (`tasks.py`, 1,174 lines) with 7 subcommands covering task listing, display, synchronization, verification, testing, discovery, and tidying. gzkit has no equivalent surface. However, gzkit already has adjacent surfaces --- chore management, OBPI briefs, ADR lifecycle, gate verification --- that may overlap with some or all of these capabilities. This ADR governs the item-by-item evaluation of each task subcommand to determine whether it fills a genuine gap in gzkit's governance model or duplicates existing functionality under a different name.

## Decision

- Each of the 7 opsdev task subcommands gets individual OBPI examination
- For each subcommand: read the implementation, map it against gzkit equivalents, document the decision
- Three possible outcomes per subcommand: **Absorb** (governance-generic, no gzkit equivalent), **Adapt** (concept generalizes but needs redesign), **Exclude** (project-specific or duplicates existing gzkit surface)
- Absorbed commands must follow gzkit conventions: argparse, exit codes 0/1/2/3, --json/--plain output, Pydantic models

## Interfaces

- **CLI (external contract):** `uv run gz {command}` --- new task management commands only if evaluation determines they belong
- **Config keys consumed (read-only):** `.gzkit/manifest.json` --- artifact paths, task definitions
- **Internal APIs:** Potential new modules in `src/gzkit/` providing task management to governance workflows

## OBPI Decomposition --- Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.29.0-01 | Evaluate `tasks list` subcommand --- task enumeration and filtering | Heavy | Pending |
| 2 | OBPI-0.29.0-02 | Evaluate `tasks show` subcommand --- detailed task display | Heavy | Pending |
| 3 | OBPI-0.29.0-03 | Evaluate `tasks sync` subcommand --- task state synchronization | Heavy | Pending |
| 4 | OBPI-0.29.0-04 | Evaluate `tasks verify` subcommand --- task verification and validation | Heavy | Pending |
| 5 | OBPI-0.29.0-05 | Evaluate `tasks test` subcommand --- task-scoped test execution | Heavy | Pending |
| 6 | OBPI-0.29.0-06 | Evaluate `tasks discover` subcommand --- task discovery and cataloging | Heavy | Pending |
| 7 | OBPI-0.29.0-07 | Evaluate `tasks tidy` subcommand --- task cleanup and maintenance | Heavy | Pending |

**Briefs location:** `obpis/OBPI-0.29.0-*.md`

**WBS Completeness Rule:** Every row in this table has a corresponding brief file.

**Lane definitions:**

- **Heavy** --- All OBPIs are Heavy because absorbed task management may change external contracts

---

## Rationale

opsdev's `tasks.py` at 1,174 lines represents a substantial task management system. Before absorbing or dismissing it, gzkit must honestly evaluate whether its existing governance surfaces (chores, OBPIs, ADRs, gates) already cover the same ground. If task management is genuinely orthogonal to these surfaces --- managing discrete work items that don't map cleanly to OBPIs or chores --- then gzkit has a real gap. If task management substantially overlaps, the evaluation should document why and recommend whether the concept adds value even as a different interface to the same data.

## Consequences

- If absorbed: gzkit gains task management capabilities, expanding its governance surface
- If excluded: documented rationale prevents future re-evaluation without new evidence
- Overlap mapping clarifies the relationship between tasks, chores, OBPIs, and ADRs
- The evaluation creates a reusable template for future absorption decisions involving surface overlap

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/test_tasks_*.py` --- unit tests for each absorbed command
- **BDD (Heavy):** `features/task_management.feature` --- if new CLI surfaces are introduced
- **Docs:** Decision rationale documented per OBPI brief

---

## OBPI Acceptance Note (Human Acknowledgment)

- Each OBPI documents the evaluation result and decision (Absorb/Adapt/Exclude)
- Human attestation required for all OBPIs (Heavy lane, parent ADR is Heavy)
- Attestation command: `uv run gz gates --adr ADR-0.29.0`

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.29.0`
- **Dependencies:** ADR-0.26.0

### Source & Contracts

- opsdev source: `tasks.py` (1,174 lines)
- gzkit target: `src/gzkit/commands/` --- new or enhanced command modules

### Tests

- Unit: `tests/test_tasks_*.py` (per absorbed command)

### Docs

- Decision rationale: per OBPI brief in `obpis/`
- Governance: this ADR

---

## Completion Checklist --- Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|-------------------|----------|-------|
| `src/gzkit/commands/` | M | All absorbed commands integrated | Test output | |
| `tests/` | M | All absorbed commands tested | `uv run gz test` | |
| `obpis/` | P | All 7 OBPIs have decisions documented | Brief review | |

### SIGN-OFF --- Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes
