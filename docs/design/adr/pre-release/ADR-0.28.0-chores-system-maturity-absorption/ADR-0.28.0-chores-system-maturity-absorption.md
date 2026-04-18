---
id: ADR-0.28.0-chores-system-maturity-absorption
status: Pending
semver: 0.28.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-21
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.28.0: Chores System Maturity Absorption

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Audit gzkit's existing chores system (`commands/chores.py`, 667 lines) to understand current capabilities, executor model, and planner logic.
  1. Audit opsdev's full chores system (~3,750 lines across 19 modules in `chores_tools/`) to catalog every capability and its maturity level.
  1. Create a cross-reference matrix mapping each opsdev chores module to its gzkit equivalent (or lack thereof).

**Date Added:** 2026-03-21
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.28.0
**Area:** Chores System — Companion Absorption (Executor Pipeline Maturity)

## Agent Context Frame — MANDATORY

**Role:** Absorption evaluator — comparing opsdev's decomposed chores system against gzkit's monolithic equivalent, determining which implementation is superior per component, and absorbing the best into gzkit.

**Purpose:** When this ADR is complete, gzkit owns a chores system at least as capable as opsdev's. The current 667-line monolith in `commands/chores.py` is replaced or augmented by a properly decomposed system with rich executor pipelines (run/log/summary/recommendations/finalize), a sophisticated planner, config-driven lane selection, and modular CLI subcommands. For each of the 19 modules, gzkit either absorbed the opsdev implementation (because it was superior), confirmed its own implementation is sufficient (with documented rationale), or explicitly excluded the module as domain-specific.

**Goals:**

- Every chores module in opsdev is examined individually with a documented decision
- gzkit's chores system achieves at least opsdev-level executor pipeline depth (progress, recommendations, finalization)
- The monolithic `commands/chores.py` is decomposed into focused, testable modules
- Config-driven chore definitions and lane selection are properly absorbed
- The subtraction test holds: `opsdev - gzkit = pure opsdev domain`

**Critical Constraint:** opsdev's chores system is significantly more mature than gzkit's. Each component must be evaluated individually — some gzkit simplifications may be intentional, but the depth of opsdev's executor pipeline (progress, recommendations, finalization) likely needs to come upstream. Do not assume gzkit's simpler implementation is "good enough" without examining what opsdev's `executor_recommendations.py` and `executor_finalize.py` actually provide.

**Anti-Pattern Warning:** A failed implementation looks like: assuming gzkit's simpler chores implementation is "good enough" without examining what opsdev's executor_recommendations.py and executor_finalize.py actually provide. Equally bad: blindly copying opsdev code without adapting it to gzkit's architecture (Pydantic models, pathlib paths, UTF-8 encoding).

**Integration Points:**

- `src/gzkit/commands/chores.py` — current monolithic chores implementation (667 lines)
- `src/gzkit/chores_tools/` — target for decomposed chores modules
- `config/chores.json` — chore definitions and lane configuration

---

## Feature Checklist — Appraisal of Completeness

- Scope and surface
  - External contract may change (Heavy lane) — new subcommands (audit, ack, register, status) and executor pipeline stages will introduce new CLI capabilities
- Tests
  - Each absorbed module must have unit tests; coverage >= 40%
- Docs
  - Decision rationale documented per OBPI (absorb/confirm/exclude)
- OBPI mapping
  - Each numbered checklist item maps to one brief; 19 items = 19 briefs

## Intent

gzkit's chores system is a 667-line monolith handling CLI, planning, execution, and output in a single file. opsdev has decomposed the same problem space into 19 focused modules totaling ~3,750 lines, with a sophisticated executor pipeline (run/log/summary/recommendations/finalize), a planner with config-driven lane selection, and modular CLI subcommands for plan, run, advise, audit, status, ack, and register. This ADR governs the item-by-item evaluation and absorption of these 19 modules into gzkit, ensuring the chores system achieves production-grade maturity with proper separation of concerns.

## Decision

- Each of the 19 opsdev chores modules gets individual OBPI examination
- For each module: read both implementations, compare maturity/completeness/robustness, document decision
- Three possible outcomes per module: **Absorb** (opsdev is better), **Confirm** (gzkit is sufficient), **Exclude** (domain-specific, does not belong in gzkit)
- Absorbed modules must follow gzkit conventions: Pydantic BaseModel, pathlib.Path, UTF-8 encoding, no bare except
- The monolithic `commands/chores.py` should be decomposed as part of absorption

## Interfaces

- **CLI (external contract):** `uv run gz chores {subcommand}` — new subcommands (audit, ack, register, status) and enhanced existing ones (plan, run, advise)
- **Config keys consumed (read-only):** `config/chores.json` — chore definitions, lane selection, executor configuration
- **Internal APIs:** New modules in `src/gzkit/chores_tools/` providing decomposed chores infrastructure

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.28.0-01 | Evaluate and absorb `chores_tools/cli.py` (60 lines) — CLI entry point and subcommand registration | Heavy | Pending |
| 2 | OBPI-0.28.0-02 | Evaluate and absorb `chores_tools/cli_core.py` (61 lines) — shared CLI utilities and argument parsing | Heavy | Pending |
| 3 | OBPI-0.28.0-03 | Evaluate and absorb `chores_tools/cli_plan.py` (143 lines) — plan subcommand implementation | Heavy | Pending |
| 4 | OBPI-0.28.0-04 | Evaluate and absorb `chores_tools/cli_run.py` (247 lines) — run subcommand implementation | Heavy | Pending |
| 5 | OBPI-0.28.0-05 | Evaluate and absorb `chores_tools/cli_advise.py` (150 lines) — advise subcommand implementation | Heavy | Pending |
| 6 | OBPI-0.28.0-06 | Evaluate and absorb `chores_tools/cli_audit.py` (150 lines) — audit subcommand implementation | Heavy | Pending |
| 7 | OBPI-0.28.0-07 | Evaluate and absorb `chores_tools/cli_status.py` (125 lines) — status subcommand implementation | Heavy | Pending |
| 8 | OBPI-0.28.0-08 | Evaluate and absorb `chores_tools/cli_ack.py` (76 lines) — acknowledge subcommand implementation | Heavy | Pending |
| 9 | OBPI-0.28.0-09 | Evaluate and absorb `chores_tools/cli_register.py` (144 lines) — register subcommand implementation | Heavy | Pending |
| 10 | OBPI-0.28.0-10 | Evaluate and absorb `chores_tools/executor.py` (40 lines) — executor entry point and dispatch | Heavy | Pending |
| 11 | OBPI-0.28.0-11 | Evaluate and absorb `chores_tools/executor_run.py` (339 lines) — executor run stage with chore execution logic | Heavy | Pending |
| 12 | OBPI-0.28.0-12 | Evaluate and absorb `chores_tools/executor_log.py` (141 lines) — executor logging and output capture | Heavy | Pending |
| 13 | OBPI-0.28.0-13 | Evaluate and absorb `chores_tools/executor_summary.py` (161 lines) — executor summary generation | Heavy | Pending |
| 14 | OBPI-0.28.0-14 | Evaluate and absorb `chores_tools/executor_recommendations.py` (254 lines) — executor recommendations engine | Heavy | Pending |
| 15 | OBPI-0.28.0-15 | Evaluate and absorb `chores_tools/executor_finalize.py` (622 lines) — executor finalization and cleanup pipeline | Heavy | Pending |
| 16 | OBPI-0.28.0-16 | Evaluate and absorb `chores_tools/planner.py` (617 lines) — chore planning and dependency resolution | Heavy | Pending |
| 17 | OBPI-0.28.0-17 | Evaluate and absorb `chores_tools/parser.py` (302 lines) — chore definition parsing and validation | Heavy | Pending |
| 18 | OBPI-0.28.0-18 | Evaluate and absorb `chores_tools/models.py` (56 lines) — chores data models | Heavy | Pending |
| 19 | OBPI-0.28.0-19 | Evaluate and absorb `config/opsdev/chores.json` (config) — chore definitions and lane configuration | Heavy | Pending |

**Briefs location:** `obpis/OBPI-0.28.0-*.md`

**WBS Completeness Rule:** Every row in this table has a corresponding brief file.

**Lane definitions:**

- **Heavy** — All OBPIs are Heavy because absorbed chores infrastructure may change external contracts (new subcommands, executor stages, CLI output formats)

---

## Rationale

opsdev's chores system represents ~3,750 lines of battle-tested, properly decomposed infrastructure. gzkit currently has a 667-line monolith that handles everything in a single file — CLI parsing, planning, execution, output — with none of the executor pipeline depth (logging, summary, recommendations, finalization) that opsdev provides. The ratio is roughly 5.6:1 in opsdev's favor, suggesting gzkit is missing significant functionality. The decomposition alone (19 focused modules vs 1 monolith) represents a maturity gap that affects testability, maintainability, and extensibility.

## Consequences

- gzkit's chores system achieves production-grade decomposition and executor pipeline depth
- The monolithic `commands/chores.py` is replaced by focused, testable modules in `chores_tools/`
- New CLI subcommands (audit, ack, register, status) expand operator capabilities
- The executor pipeline gains recommendations and finalization stages that enable smarter chore outcomes
- opsdev can depend on gzkit for all chores infrastructure, reducing its own footprint
- Config-driven chore definitions allow project-specific customization without code changes

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/test_chores_*.py` — unit tests for each absorbed module
- **BDD (Heavy):** `features/chores_system.feature` — if new CLI surfaces are introduced
- **Docs:** Decision rationale documented per OBPI brief

---

## OBPI Acceptance Note (Human Acknowledgment)

- Each OBPI documents the comparison result and decision (Absorb/Confirm/Exclude)
- Human attestation required for all OBPIs (Heavy lane, parent ADR is Heavy)
- Attestation command: `uv run gz gates --adr ADR-0.28.0`

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.28.0`
- **Related:** ADR-0.25.0 (core infrastructure absorption), ADR-0.26.0
- **Dependencies:** ADR-0.25.0, ADR-0.26.0

### Source & Contracts

- opsdev source: `../opsdev/src/opsdev/chores_tools/`, `../opsdev/config/opsdev/chores.json`
- gzkit target: `src/gzkit/chores_tools/` — new decomposed modules; `src/gzkit/commands/chores.py` — existing monolith

### Tests

- Unit: `tests/test_chores_*.py` (per absorbed module)

### Docs

- Decision rationale: per OBPI brief in `obpis/`
- Governance: this ADR

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|-------------------|----------|-------|
| `src/gzkit/chores_tools/` | M | All absorbed modules integrated | Test output | |
| `tests/` | M | All absorbed modules tested | `uv run gz test` | |
| `obpis/` | P | All 19 OBPIs have decisions documented | Brief review | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes
