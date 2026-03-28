---
id: ADR-0.36.0-instruction-file-reconciliation
status: Proposed
semver: 0.36.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-21
dependencies:
  - ADR-0.32.0
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.36.0: Instruction File Reconciliation

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Audit airlineops's `.github/instructions/` directory to catalog all 14 instruction files, their content depth, and governance patterns.
  1. Audit gzkit's `.claude/rules/` directory to catalog all 11 rules files, their content depth, and governance patterns.
  1. Create a cross-reference matrix mapping each airlineops instruction file to its gzkit counterpart (or lack thereof), noting content gaps in both directions.

**Date Added:** 2026-03-21
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.36.0
**Area:** Instruction Files — Companion Reconciliation (Agent Governance Surface)

## Agent Context Frame — MANDATORY

**Role:** Reconciliation evaluator — comparing every airlineops `.github/instructions/` file against its gzkit `.claude/rules/` counterpart, determining completeness gaps, identifying content gzkit should absorb, and evaluating domain-specific files for governance-generality.

**Purpose:** When this ADR is complete, every airlineops instruction file has been compared against its gzkit counterpart (where one exists) with documented gap analysis. For the 3 airlineops-only files (sql_hygiene, warehouse, calendars), domain-specific content has been separated from generic governance patterns, and any generic patterns have been absorbed into gzkit. gzkit's rules are at least as comprehensive as airlineops's instructions for all non-domain-specific governance.

**Goals:**

- Every airlineops instruction file is compared against its gzkit counterpart with documented gap analysis
- Content gaps in gzkit rules are identified and remediated
- Domain-specific instruction files are evaluated for extractable generic patterns
- gzkit's rules surface is at least as comprehensive as airlineops's for all generic governance
- The subtraction test holds: `airlineops instructions - gzkit rules = pure airline domain`

**Critical Constraint:** airlineops has 14 instruction files; gzkit has 11 rules. Some map 1:1 (cli, tests, models), some exist only in airlineops (sql_hygiene, warehouse, calendars). The domain-specific ones must be evaluated — sql_hygiene may have generic patterns worth extracting (e.g., parameterized queries, injection prevention). Do not assume domain-named files are entirely domain-specific without reading them.

**Anti-Pattern Warning:** A failed implementation looks like: assuming domain-named files (warehouse.instructions.md, calendars.instructions.md) are entirely domain-specific without reading them. Equally bad: declaring 1:1 mapped files as "identical" without actually diffing the content to find gaps in either direction.

**Integration Points:**

- `.claude/rules/` — gzkit's rules directory (target for reconciled content)
- `.github/instructions/` — airlineops's instructions directory (source for comparison)
- `CLAUDE.md` — may need updates if new rules files are added
- `config/` — rule path configurations

---

## Feature Checklist — Appraisal of Completeness

- Scope and surface
  - External contract may change (Heavy lane) — new or enhanced rules may change agent governance behavior
- Tests
  - Rules file structure validation tests; coverage >= 40%
- Docs
  - Decision rationale documented per OBPI (absorb/confirm/exclude with gap analysis)
- OBPI mapping
  - Each numbered checklist item maps to one brief; 13 items = 13 briefs

## Intent

gzkit must own all reusable agent governance patterns. airlineops's `.github/instructions/` directory has 14 instruction files governing CLI design, testing policy, cross-platform development, data models, code style, documentation covenants, audit procedures, and domain-specific workflows. gzkit's `.claude/rules/` has 11 files covering overlapping ground — but the overlap has never been systematically verified. Content may have diverged, gaps may exist in either direction, and domain-specific files may contain extractable generic patterns. This ADR governs the file-by-file reconciliation to ensure gzkit's agent governance surface is authoritative and complete.

## Decision

- Each of the 13 comparison pairs (or singles) gets individual OBPI examination
- For each pair: read both files completely, diff content, document gaps in both directions
- Three possible outcomes per file: **Absorb** (airlineops content fills gaps in gzkit), **Confirm** (gzkit's version is complete), **Extract** (domain-specific file has generic patterns worth absorbing)
- For airlineops-only files: evaluate whether generic patterns exist and create new gzkit rules if warranted
- Reconciled content must follow gzkit conventions: `.claude/rules/` format with frontmatter paths

## Interfaces

- **Agent governance surface:** `.claude/rules/*.md` — loaded by Claude Code for session context
- **Config keys consumed (read-only):** Frontmatter `paths:` in each rules file
- **Sync pipeline:** `gz agent sync control-surfaces` — regenerates from canon

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.36.0-01 | Reconcile `cli.instructions.md` vs `.claude/rules/cli.md` | Heavy | Pending |
| 2 | OBPI-0.36.0-02 | Reconcile `tests.instructions.md` vs `.claude/rules/tests.md` | Heavy | Pending |
| 3 | OBPI-0.36.0-03 | Reconcile `cross-platform.instructions.md` vs `.claude/rules/cross-platform.md` | Heavy | Pending |
| 4 | OBPI-0.36.0-04 | Reconcile `models.instructions.md` vs `.claude/rules/models.md` | Heavy | Pending |
| 5 | OBPI-0.36.0-05 | Reconcile `pythonic.instructions.md` vs `.claude/rules/pythonic.md` | Heavy | Pending |
| 6 | OBPI-0.36.0-06 | Reconcile `gate5_runbook_code_covenant.instructions.md` vs `.claude/rules/gate5-runbook-code-covenant.md` | Heavy | Pending |
| 7 | OBPI-0.36.0-07 | Reconcile `adr_audit.instructions.md` vs `.claude/rules/adr-audit.md` | Heavy | Pending |
| 8 | OBPI-0.36.0-08 | Reconcile `arb.instructions.md` vs `.claude/rules/arb.md` | Heavy | Pending |
| 9 | OBPI-0.36.0-09 | Reconcile `chores.instructions.md` vs `.claude/rules/chores.md` | Heavy | Pending |
| 10 | OBPI-0.36.0-10 | Reconcile `gh_cli.instructions.md` vs `.claude/rules/gh-cli.md` | Heavy | Pending |
| 11 | OBPI-0.36.0-11 | Evaluate `sql_hygiene.instructions.md` for generic pattern extraction | Heavy | Pending |
| 12 | OBPI-0.36.0-12 | Evaluate `warehouse.instructions.md` for generic pattern extraction | Heavy | Pending |
| 13 | OBPI-0.36.0-13 | Evaluate `calendars.instructions.md` for generic pattern extraction | Heavy | Pending |

**Briefs location:** `obpis/OBPI-0.36.0-*.md`

**WBS Completeness Rule:** Every row in this table has a corresponding brief file.

**Lane definitions:**

- **Heavy** — All OBPIs are Heavy because reconciled rules may change agent governance behavior

---

## Rationale

airlineops's `.github/instructions/` and gzkit's `.claude/rules/` serve the same purpose: governing agent behavior during development sessions. They evolved independently and have never been systematically reconciled. The 10 overlapping files may have content gaps in either direction — airlineops may have added sections that gzkit lacks, or vice versa. The 3 airlineops-only files (sql_hygiene, warehouse, calendars) are nominally domain-specific but may contain generic patterns (e.g., SQL injection prevention, data pipeline testing, date handling) that belong in gzkit's governance surface. This ADR ensures nothing is missed by examining every file individually.

## Consequences

- gzkit's rules surface becomes the authoritative source for all generic agent governance
- Content gaps in gzkit rules are remediated from airlineops's battle-tested instructions
- Domain-specific patterns are cleanly separated from generic governance
- airlineops can depend on gzkit's rules for all non-domain governance, reducing duplication
- New rules files may require `gz agent sync control-surfaces` updates

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/test_rules_*.py` — validation tests for rules structure
- **BDD (Heavy):** N/A — rules files are documentation, not executable surfaces
- **Docs:** Decision rationale documented per OBPI brief

---

## OBPI Acceptance Note (Human Acknowledgment)

- Each OBPI documents the reconciliation result and decision (Absorb/Confirm/Extract)
- Human attestation required for all OBPIs (Heavy lane, parent ADR is Heavy)
- Attestation command: `uv run gz gates --adr ADR-0.36.0`

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.36.0`
- **Related:** ADR-0.32.0 (agent governance surface)

### Source & Contracts

- airlineops source: `../airlineops/.github/instructions/`
- gzkit target: `.claude/rules/` — reconciled or new rules files

### Tests

- Unit: `tests/test_rules_*.py` (structure validation)

### Docs

- Decision rationale: per OBPI brief in `obpis/`
- Governance: this ADR

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|-------------------|----------|-------|
| `.claude/rules/` | M | All reconciled rules integrated | Rule content review | |
| `tests/` | M | Rules structure validated | `uv run gz test` | |
| `obpis/` | P | All 13 OBPIs have decisions documented | Brief review | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes
