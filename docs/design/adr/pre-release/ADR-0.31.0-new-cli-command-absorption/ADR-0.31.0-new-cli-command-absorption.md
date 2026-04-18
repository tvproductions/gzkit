---
id: ADR-0.31.0-new-cli-command-absorption
status: Pending
semver: 0.31.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-21
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.31.0: New CLI Command Absorption

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Audit opsdev's quality tooling commands to catalog every command, its arguments, output format, and line count.
  1. Audit gzkit's existing CLI surface to confirm these 10 commands have no equivalent in gzkit today.
  1. Create a portability matrix assessing each command's governance-generality vs project-specificity.

**Date Added:** 2026-03-21
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.31.0
**Area:** CLI Commands --- Companion Absorption (Quality Tooling)

## Agent Context Frame --- MANDATORY

**Role:** Absorption evaluator --- porting quality tooling commands from opsdev to gzkit, adapting each to gzkit's CLI conventions (argparse, exit codes, --json/--plain output).

**Purpose:** When this ADR is complete, gzkit owns 10 quality tooling commands that exist in opsdev but have no gzkit equivalent: SLOC analysis, cyclomatic complexity checking, per-test duration tracking, AST-based test quality metrics, code quality violation scanning, continuous monitoring, mutation testing, manpage validation, docstring sync, and docstring coverage. Each command has been ported with gzkit CLI conventions, unit tests, and documentation.

**Goals:**

- All 10 quality tooling commands are ported from opsdev to gzkit
- Each ported command follows gzkit's CLI conventions: argparse, exit codes 0/1/2/3, --json/--plain output
- Each ported command has unit tests with >= 40% coverage
- Each ported command has manpage documentation
- The subtraction test holds: opsdev's quality tooling after porting contains only project-specific wrappers

**Critical Constraint:** All 10 commands must be ported. These are genuinely generic quality tools (SLOC, complexity, test metrics, mutation testing, manpage validation) --- none are airline-specific. The question is not whether they belong in gzkit, but how to adapt them to gzkit's CLI conventions.

**Anti-Pattern Warning:** A failed implementation looks like: porting commands verbatim from opsdev without adapting them to gzkit's CLI conventions. Each ported command must use argparse (not click), return proper exit codes (0/1/2/3), support --json/--plain output, and include help text with examples. Equally bad: declaring a command "ported" without tests or documentation.

**Integration Points:**

- `src/gzkit/commands/` --- new command modules
- `src/gzkit/config.py` --- configuration consumed by quality tooling (depends on ADR-0.30.0)
- `docs/user/manpages/` --- manpage documentation for each ported command
- `tests/` --- unit tests for each ported command

---

## Feature Checklist --- Appraisal of Completeness

- Scope and surface
  - External contract will change (Heavy lane) --- 10 new CLI commands
- Tests
  - Each ported command must have unit tests; coverage >= 40%
- Docs
  - Each ported command must have manpage documentation and help text with examples
- OBPI mapping
  - Each numbered checklist item maps to one brief; 10 items = 10 briefs

## Intent

opsdev contains quality tooling commands that are genuinely governance-generic --- SLOC analysis (radon), cyclomatic complexity checking (xenon), per-test duration tracking, AST-based test quality metrics, code quality violation scanning, continuous monitoring, mutation testing (Cosmic Ray), manpage structure validation, docstring synchronization, and docstring coverage (interrogate). None of these are airline-specific or project-specific --- they are the kind of quality tooling that every gzkit-governed project should have access to. This ADR governs the porting of all 10 commands, adapting each to gzkit's CLI conventions.

## Decision

- Each of the 10 opsdev quality commands gets individual OBPI examination and porting
- For each command: read the implementation, adapt to gzkit CLI conventions, write tests, create documentation
- All commands must support: argparse, exit codes 0/1/2/3, --json/--plain output, help text with examples
- Ported commands must follow gzkit conventions: Pydantic models, pathlib.Path, UTF-8 encoding, no bare except

## Interfaces

- **CLI (external contract):** `uv run gz {command}` --- 10 new commands
- **Config keys consumed (read-only):** `.gzkit/manifest.json`, config files from ADR-0.30.0
- **Internal APIs:** New modules in `src/gzkit/commands/` providing quality tooling

## OBPI Decomposition --- Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.31.0-01 | Port `sloc-scan` (159 lines) --- radon-based SLOC analysis | Heavy | Pending |
| 2 | OBPI-0.31.0-02 | Port `complexity-check` (122 lines) --- xenon cyclomatic complexity | Heavy | Pending |
| 3 | OBPI-0.31.0-03 | Port `test-times` (87 lines) --- per-test duration tracking | Heavy | Pending |
| 4 | OBPI-0.31.0-04 | Port `test-quality` (495 lines) --- AST-based test quality metrics | Heavy | Pending |
| 5 | OBPI-0.31.0-05 | Port `metrics scan` (429 lines) --- code quality violation scanning | Heavy | Pending |
| 6 | OBPI-0.31.0-06 | Port `metrics report/watch` (429 lines) --- continuous monitoring and reporting | Heavy | Pending |
| 7 | OBPI-0.31.0-07 | Port `mutate` (450 lines) --- Cosmic Ray mutation testing | Heavy | Pending |
| 8 | OBPI-0.31.0-08 | Port `validate-manpages` (473 lines) --- manpage structure validation | Heavy | Pending |
| 9 | OBPI-0.31.0-09 | Port `sync-manpage-docstrings` (473 lines) --- docstring synchronization | Heavy | Pending |
| 10 | OBPI-0.31.0-10 | Port `interrogate` (wrapper) --- docstring coverage integration | Heavy | Pending |

**Briefs location:** `obpis/OBPI-0.31.0-*.md`

**WBS Completeness Rule:** Every row in this table has a corresponding brief file.

**Lane definitions:**

- **Heavy** --- All OBPIs are Heavy because each introduces a new CLI command (external contract change)

---

## Rationale

opsdev's quality tooling represents approximately 3,100+ lines of governance-generic code that every project benefits from. SLOC analysis, complexity checking, test quality metrics, mutation testing, and manpage validation are not airline-specific --- they are fundamental code quality tools. gzkit as a governance framework must own these tools so that any gzkit-governed project gets quality tooling out of the box, rather than each project reimplementing these capabilities. This ADR depends on ADR-0.25.0 (core infrastructure) and ADR-0.30.0 (config schema) because ported commands consume infrastructure and configuration provided by those ADRs.

## Consequences

- gzkit gains 10 new CLI commands, significantly expanding its quality tooling surface
- Every gzkit-governed project gets access to SLOC, complexity, test quality, and mutation testing
- Manpage validation and docstring sync enforce documentation quality programmatically
- opsdev can replace its implementations with gzkit equivalents, reducing its own codebase
- New dependencies may be required (radon, xenon, cosmic-ray, interrogate) --- these must be managed as optional dependencies

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/test_cmd_*.py` --- unit tests for each ported command
- **BDD (Heavy):** `features/quality_tooling.feature` --- smoke tests for new CLI commands
- **Docs:** Manpages in `docs/user/manpages/`, help text with examples in each command

---

## OBPI Acceptance Note (Human Acknowledgment)

- Each OBPI documents the porting result with evidence of CLI convention compliance
- Human attestation required for all OBPIs (Heavy lane, parent ADR is Heavy)
- Attestation command: `uv run gz gates --adr ADR-0.31.0`

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.31.0`
- **Dependencies:** ADR-0.25.0, ADR-0.30.0

### Source & Contracts

- opsdev source: quality tooling commands (~3,100+ lines total)
- gzkit target: `src/gzkit/commands/` --- 10 new command modules

### Tests

- Unit: `tests/test_cmd_*.py` (per ported command)

### Docs

- Manpages: `docs/user/manpages/` (per ported command)
- Governance: this ADR
- Decision rationale: per OBPI brief in `obpis/`

---

## Completion Checklist --- Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|-------------------|----------|-------|
| `src/gzkit/commands/` | M | All 10 commands ported | Test output | |
| `tests/` | M | All ported commands tested | `uv run gz test` | |
| `docs/user/manpages/` | P | All ported commands documented | Manpage review | |
| `obpis/` | P | All 10 OBPIs have evidence documented | Brief review | |

### SIGN-OFF --- Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes
