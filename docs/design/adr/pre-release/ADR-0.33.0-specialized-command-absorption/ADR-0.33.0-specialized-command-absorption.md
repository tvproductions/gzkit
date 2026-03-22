---
id: ADR-0.33.0-specialized-command-absorption
status: Proposed
semver: 0.33.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-21
dependencies:
  - ADR-0.25.0
  - ADR-0.26.0
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.33.0: Specialized Command and Governance Tooling Absorption

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Catalog every specialized governance command in opsdev that does NOT have a gzkit equivalent.
  1. For each command, identify the source file, line count, and governance purpose.
  1. Categorize each as: reference tooling, audit tooling, hygiene tooling, or orchestration tooling.

**Date Added:** 2026-03-21
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.33.0
**Area:** Specialized Commands -- Companion Absorption (Governance Tooling)

## Agent Context Frame -- MANDATORY

**Role:** Absorption evaluator -- examining opsdev's specialized governance commands that have no direct gzkit equivalent, determining which are governance-generic and should be absorbed into gzkit, and which are domain-specific and should remain in opsdev.

**Purpose:** When this ADR is complete, every specialized governance command in opsdev has been evaluated for gzkit inclusion. For each of the 10 commands, the evaluator has read the implementation, assessed its governance generality, and either absorbed it into gzkit or documented why it is domain-specific.

**Goals:**

- Every specialized opsdev command is examined individually with a documented decision
- Governance-generic commands are absorbed into gzkit with proper conventions
- Domain-specific commands are explicitly excluded with documented rationale
- gzkit's governance toolkit expands to cover reference management, instrumentation audit, agent review, hygiene enforcement, curation, and governance orchestration where appropriate

**Critical Constraint:** These commands are governance-generic despite being specialized. Evaluate each for gzkit inclusion on its merits. The refs-index/refs-citations system alone represents 834 lines of reference management infrastructure that may be universally useful for governance documentation.

**Anti-Pattern Warning:** A failed implementation looks like: dismissing specialized commands as "niche" without evaluating their governance value. The governance-setup/report/runners trio (1,242 lines combined) orchestrates the entire governance lifecycle and should be evaluated with particular care.

**Integration Points:**

- `src/gzkit/commands/` -- target for new command modules
- `src/gzkit/` -- target for new library modules
- `../opsdev/src/opsdev/tools/` -- source implementations

---

## Feature Checklist -- Appraisal of Completeness

- Scope and surface
  - External contract may change (Heavy lane) -- new commands will expand CLI surface
- Tests
  - Each absorbed command must have unit tests; coverage >= 40%
- Docs
  - Decision rationale documented per OBPI (absorb/exclude)
- OBPI mapping
  - Each numbered checklist item maps to one brief; 10 items = 10 briefs

## Intent

opsdev contains 10 specialized governance commands that have no direct equivalent in gzkit: reference indexing and citation checking (refs-index, refs-citations), instrumentation audit, agent review, hygiene enforcement, curation (inventory + guard), and governance orchestration (setup, report, runners). These commands total over 2,700 lines of implementation. Despite their specialized nature, many are governance-generic -- reference management, instrumentation audit, and hygiene enforcement apply to any governed codebase, not just airline operations. This ADR governs the evaluation of each command for gzkit absorption.

## Decision

- Each of the 10 specialized commands gets individual OBPI examination
- For each command: read the implementation, assess governance generality, document decision
- Two possible outcomes per command: **Absorb** (governance-generic, belongs in gzkit), **Exclude** (domain-specific or too niche for gzkit)
- Absorbed commands must follow gzkit conventions: Pydantic BaseModel, pathlib.Path, UTF-8 encoding, no bare except
- Partial absorption is acceptable -- extract generic patterns while leaving domain logic

## Interfaces

- **CLI (external contract):** `uv run gz {command}` -- new commands will expand gzkit's CLI surface
- **Config keys consumed (read-only):** `.gzkit/manifest.json` -- artifact paths
- **Internal APIs:** New modules in `src/gzkit/` for absorbed commands

## OBPI Decomposition -- Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.33.0-01 | Evaluate and absorb `refs-index` (37+797 lines) -- reference index building | Heavy | Pending |
| 2 | OBPI-0.33.0-02 | Evaluate and absorb `refs-citations` (37+797 lines) -- citation checking and validation | Heavy | Pending |
| 3 | OBPI-0.33.0-03 | Evaluate and absorb `instrumentation-audit` (122 lines) -- instrumentation coverage auditing | Heavy | Pending |
| 4 | OBPI-0.33.0-04 | Evaluate and absorb `agent-review` (231 lines) -- agent configuration review | Heavy | Pending |
| 5 | OBPI-0.33.0-05 | Evaluate and absorb `hygiene` (155 lines) -- repository hygiene enforcement | Heavy | Pending |
| 6 | OBPI-0.33.0-06 | Evaluate and absorb `curation inventory` (250 lines) -- curation inventory management | Heavy | Pending |
| 7 | OBPI-0.33.0-07 | Evaluate and absorb `curation guard` (250 lines) -- curation guard enforcement | Heavy | Pending |
| 8 | OBPI-0.33.0-08 | Evaluate and absorb `governance setup` (279 lines) -- governance initialization and setup | Heavy | Pending |
| 9 | OBPI-0.33.0-09 | Evaluate and absorb `governance report` (608 lines) -- governance status reporting | Heavy | Pending |
| 10 | OBPI-0.33.0-10 | Evaluate and absorb `governance runners` (355 lines) -- governance task runners | Heavy | Pending |

**Briefs location:** `briefs/OBPI-0.33.0-*.md`

**WBS Completeness Rule:** Every row in this table has a corresponding brief file.

**Lane definitions:**

- **Heavy** -- All OBPIs are Heavy because absorbed commands will expand external CLI surface

---

## Rationale

opsdev's specialized commands represent mature governance tooling that has evolved through operational use. The reference system (refs-index + refs-citations) provides documentation cross-referencing. The instrumentation-audit verifies that code instrumentation (logging, metrics) meets governance standards. Agent-review validates AI agent configurations. Hygiene enforces repository cleanliness standards. Curation manages content inventories and guards. The governance trio (setup/report/runners) orchestrates the entire governance lifecycle. These are not airline-specific -- they are governance-generic patterns that any governed codebase needs.

## Consequences

- gzkit's CLI surface expands with new specialized commands
- Reference management becomes a first-class gzkit capability (if absorbed)
- Governance orchestration may become self-hosted in gzkit (if setup/report/runners are absorbed)
- Some commands may be excluded as too domain-specific after evaluation
- New commands require documentation, manpages, and help text

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/` -- unit tests for each absorbed command
- **BDD (Heavy):** `features/` -- if new CLI surfaces are introduced
- **Docs:** Decision rationale documented per OBPI brief

---

## OBPI Acceptance Note (Human Acknowledgment)

- Each OBPI documents the evaluation result and decision (Absorb / Exclude)
- Human attestation required for all OBPIs (Heavy lane, parent ADR is Heavy)
- Attestation command: `uv run gz gates --adr ADR-0.33.0`

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.33.0`
- **Related:** ADR-0.25.0 (core infrastructure), ADR-0.26.0 (companion)

### Source & Contracts

- opsdev source: `../opsdev/src/opsdev/tools/` -- specialized tool implementations
- gzkit target: `src/gzkit/` -- new command modules

### Tests

- Unit: `tests/` (per absorbed command)

### Docs

- Decision rationale: per OBPI brief in `briefs/`
- Governance: this ADR

---

## Completion Checklist -- Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|-------------------|----------|-------|
| `src/gzkit/` | M | All absorbed commands implemented | Test output | |
| `tests/` | M | All absorbed commands tested | `uv run gz test` | |
| `briefs/` | P | All 10 OBPIs have decisions documented | Brief review | |

### SIGN-OFF -- Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes
