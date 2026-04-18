---
id: ADR-0.30.0-config-schema-settings-absorption
status: Pending
semver: 0.30.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-21
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.30.0: Config Schema and Settings Absorption

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Audit gzkit's `config.py` (171 lines) to understand its current capabilities, configuration loading model, and extension points.
  1. Audit opsdev's `config/schema.py` (590 lines) and `config/doctrine.py` (745 lines) to catalog Pydantic settings models, doctrine enforcement rules, and validation patterns.
  1. Audit opsdev's config data files (`chores.json`, `git_sync.json`, `test_suites.json`) to understand their schemas and how they drive runtime behavior.
  1. Create a gap analysis mapping gzkit's 171-line config surface against opsdev's 1,335-line config layer.

**Date Added:** 2026-03-21
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.30.0
**Area:** Configuration Infrastructure --- Companion Absorption (Tier 1 Foundation)

## Agent Context Frame --- MANDATORY

**Role:** Absorption evaluator --- comparing opsdev's configuration infrastructure against gzkit's minimal config.py, determining what must be absorbed to close the gap honestly.

**Purpose:** When this ADR is complete, gzkit's configuration layer is at least as capable as opsdev's for all governance-generic patterns. The 171-line vs 1,335-line disparity is resolved through deliberate absorption, with each component evaluated individually. gzkit owns Pydantic settings models, doctrine enforcement, config file schemas, workspace patterns, and settings validation --- or has documented rationale for excluding each.

**Goals:**

- Every opsdev config component is examined individually with a documented decision
- gzkit's config layer closes the 1,164-line gap through absorption of governance-generic patterns
- Config data files (chores.json, git_sync.json, test_suites.json) are evaluated for schema generality
- The subtraction test holds: opsdev's config layer after absorption contains only project-specific settings

**Critical Constraint:** gzkit's config.py is 171 lines; opsdev's config layer is 1,335 lines. The gap is real and must be closed honestly. Do not rationalize the gap away by claiming gzkit's minimal config is "sufficient by design" without reading what opsdev's 1,335 lines actually provide.

**Anti-Pattern Warning:** A failed implementation looks like: declaring gzkit's 171-line config.py "sufficient" without reading opsdev's schema.py (590 lines of Pydantic settings models that gzkit lacks) and doctrine.py (745 lines of doctrine enforcement that gzkit has no equivalent for). Equally bad: blindly copying all 1,335 lines without evaluating which parts are airline/project-specific.

**Integration Points:**

- `src/gzkit/config.py` --- current configuration loading (171 lines)
- `src/gzkit/commands/` --- commands that consume configuration
- `.gzkit/manifest.json` --- artifact paths and project settings
- `config/` --- config data files directory

---

## Feature Checklist --- Appraisal of Completeness

- Scope and surface
  - External contract may change (Heavy lane) --- config schema changes affect all commands that consume configuration
- Tests
  - Each absorbed component must have unit tests; coverage >= 40%
- Docs
  - Decision rationale documented per OBPI (absorb/confirm/exclude)
- OBPI mapping
  - Each numbered checklist item maps to one brief; 8 items = 8 briefs

## Intent

opsdev contains a mature configuration infrastructure spanning 1,335 lines across `config/schema.py` (Pydantic settings models), `config/doctrine.py` (doctrine enforcement), and multiple config data files. gzkit's `config.py` at 171 lines is significantly smaller, lacking Pydantic settings models, doctrine enforcement, and structured config file schemas. This ADR governs the item-by-item evaluation and absorption of opsdev's configuration components, ensuring gzkit's config layer becomes comprehensive enough to govern any project --- not just projects with minimal configuration needs.

## Decision

- Each of the 8 opsdev config components gets individual OBPI examination
- For each component: read both implementations, compare maturity/completeness/robustness, document decision
- Three possible outcomes per component: **Absorb** (opsdev is better), **Confirm** (gzkit is sufficient), **Exclude** (project-specific, does not belong in gzkit)
- Absorbed components must follow gzkit conventions: Pydantic BaseModel, pathlib.Path, UTF-8 encoding, no bare except

## Interfaces

- **CLI (external contract):** `uv run gz {command}` --- config changes may affect command behavior and flags
- **Config keys consumed (read-only):** `.gzkit/manifest.json`, `config/*.json` --- schema-validated configuration files
- **Internal APIs:** Enhanced `src/gzkit/config.py` and new config modules providing settings and doctrine enforcement

## OBPI Decomposition --- Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.30.0-01 | Evaluate and absorb `config/schema.py` (590 lines) --- Pydantic settings models and schema validation | Heavy | Pending |
| 2 | OBPI-0.30.0-02 | Evaluate and absorb `config/doctrine.py` (745 lines) --- doctrine enforcement and compliance rules | Heavy | Pending |
| 3 | OBPI-0.30.0-03 | Evaluate and absorb `config/opsdev/chores.json` --- chore configuration schema and data | Heavy | Pending |
| 4 | OBPI-0.30.0-04 | Evaluate and absorb `config/opsdev/git_sync.json` --- git-sync configuration schema and data | Heavy | Pending |
| 5 | OBPI-0.30.0-05 | Evaluate and absorb `config/opsdev/test_suites.json` --- test suite configuration schema and data | Heavy | Pending |
| 6 | OBPI-0.30.0-06 | Evaluate and absorb workspace pointer patterns --- workspace discovery and multi-project support | Heavy | Pending |
| 7 | OBPI-0.30.0-07 | Evaluate and absorb legacy adapter bridges --- backward-compatible config migration | Heavy | Pending |
| 8 | OBPI-0.30.0-08 | Evaluate and absorb settings validation and env loading --- environment variable integration and validation | Heavy | Pending |

**Briefs location:** `obpis/OBPI-0.30.0-*.md`

**WBS Completeness Rule:** Every row in this table has a corresponding brief file.

**Lane definitions:**

- **Heavy** --- All OBPIs are Heavy because config infrastructure changes affect all downstream commands

---

## Rationale

The 171-line vs 1,335-line disparity between gzkit and opsdev's configuration layers is the most significant infrastructure gap identified in the absorption audit. opsdev's `schema.py` provides Pydantic-based settings models that validate configuration at load time --- gzkit has no equivalent. opsdev's `doctrine.py` enforces governance doctrine rules programmatically --- gzkit relies on documentation alone. The config data files (`chores.json`, `git_sync.json`, `test_suites.json`) demonstrate a pattern of schema-validated, file-driven configuration that gzkit should adopt for governance generality. Closing this gap is prerequisite to absorbing CLI commands (ADR-0.31.0) that depend on robust configuration.

## Consequences

- gzkit's config layer becomes comprehensive, supporting Pydantic settings models and doctrine enforcement
- All commands benefit from validated, typed configuration instead of ad-hoc config loading
- Config data files establish a pattern for schema-validated, file-driven governance configuration
- opsdev can depend on gzkit's config layer, reducing its own infrastructure footprint
- Migration path needed for existing gzkit config consumers to adopt new patterns

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/test_config_*.py` --- unit tests for each absorbed component
- **BDD (Heavy):** `features/config_infrastructure.feature` --- if config changes surface as CLI behavior changes
- **Docs:** Decision rationale documented per OBPI brief

---

## OBPI Acceptance Note (Human Acknowledgment)

- Each OBPI documents the comparison result and decision (Absorb/Confirm/Exclude)
- Human attestation required for all OBPIs (Heavy lane, parent ADR is Heavy)
- Attestation command: `uv run gz gates --adr ADR-0.30.0`

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.30.0`
- **Dependencies:** ADR-0.25.0

### Source & Contracts

- opsdev source: `config/schema.py` (590 lines), `config/doctrine.py` (745 lines), `config/opsdev/*.json`
- gzkit target: `src/gzkit/config.py` --- enhanced, plus new config modules

### Tests

- Unit: `tests/test_config_*.py` (per absorbed component)

### Docs

- Decision rationale: per OBPI brief in `obpis/`
- Governance: this ADR

---

## Completion Checklist --- Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|-------------------|----------|-------|
| `src/gzkit/config.py` | M | Enhanced config layer integrated | Test output | |
| `tests/` | M | All absorbed components tested | `uv run gz test` | |
| `obpis/` | P | All 8 OBPIs have decisions documented | Brief review | |

### SIGN-OFF --- Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes
