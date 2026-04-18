---
id: ADR-0.35.0-pre-commit-hook-absorption
status: Pending
semver: 0.35.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-21
dependencies:
  - ADR-0.27.0
  - ADR-0.31.0
  - ADR-0.32.0
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.35.0: Pre-commit Hook Absorption

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Audit opsdev's `.pre-commit-config.yaml` to catalog all 20 hooks, their configurations, arguments, and enforcement behavior.
  1. Audit gzkit's `.pre-commit-config.yaml` and `.claude/hooks/` to catalog existing hook coverage and enforcement timing.
  1. Create a cross-reference matrix mapping each opsdev hook to its gzkit equivalent (or lack thereof), noting enforcement timing (pre-commit vs. Claude hook vs. both).

**Date Added:** 2026-03-21
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.35.0
**Area:** Pre-commit Hooks — Companion Absorption (Enforcement Infrastructure)

## Agent Context Frame — MANDATORY

**Role:** Absorption evaluator — comparing opsdev's 20 pre-commit hooks against gzkit's existing hooks, determining which enforcement belongs in pre-commit (every commit), which belongs in Claude hooks (agent sessions), and which belongs in both.

**Purpose:** When this ADR is complete, gzkit has evaluated all 20 opsdev pre-commit hooks and made explicit decisions for each: absorb into gzkit's pre-commit config, absorb into Claude hooks, absorb into both, confirm gzkit's existing version is sufficient, or exclude as domain-specific. The enforcement timing question (pre-commit vs. Claude hook) is answered definitively for every hook.

**Goals:**

- Every opsdev pre-commit hook is examined individually with a documented decision
- gzkit's enforcement layer is at least as comprehensive as opsdev's for all generic patterns
- Enforcement timing is correct: fast/cheap checks in pre-commit, expensive/context-dependent checks in Claude hooks
- No reusable enforcement pattern remains stranded in the opsdev codebase
- The subtraction test holds: `opsdev - gzkit = pure airline domain`

**Critical Constraint:** Pre-commit hooks and Claude hooks may overlap. The evaluation must determine the right mix — some enforcement belongs in pre-commit (runs on every commit), some in Claude hooks (runs during agent sessions). Do not assume all hooks should be in one place or the other.

**Anti-Pattern Warning:** A failed implementation looks like: assuming all pre-commit hooks should become Claude hooks (or vice versa) without evaluating the enforcement timing needs. Equally bad: rubber-stamping "Yes-compare" hooks as sufficient without actually reading and comparing the opsdev implementation's arguments, thresholds, and error handling.

**Integration Points:**

- `.pre-commit-config.yaml` — gzkit's pre-commit configuration
- `.claude/hooks/` — gzkit's Claude hook infrastructure
- `src/gzkit/hooks/` — hook implementation modules
- `config/` — threshold configurations referenced by hooks

---

## Feature Checklist — Appraisal of Completeness

- Scope and surface
  - External contract may change (Heavy lane) — new hooks may change commit-time enforcement behavior
- Tests
  - Each absorbed hook must have unit tests; coverage >= 40%
- Docs
  - Decision rationale documented per OBPI (absorb/confirm/exclude with enforcement timing)
- OBPI mapping
  - Each numbered checklist item maps to one brief; 20 items = 20 briefs

## Intent

gzkit must own all reusable enforcement hooks. opsdev's `.pre-commit-config.yaml` has 20 hooks covering ARB-wrapped linting, complexity ceilings, governance guards, security scans, documentation validation, and repository canonicalization. gzkit has fewer hooks — some overlap (ruff-format, ty-check, unittest, xenon-complexity, forbid-pytest, interrogate, check-todos-fixmes) and many are absent. This ADR governs the item-by-item evaluation and absorption of these 20 hooks, with particular attention to the enforcement timing question: pre-commit hooks run on every commit (fast, mandatory), while Claude hooks run during agent sessions (can be slower, context-aware). The right answer for each hook depends on its cost, reliability, and whether it needs agent context.

## Decision

- Each of the 20 opsdev pre-commit hooks gets individual OBPI examination
- For each hook: read both implementations, compare maturity/completeness/robustness, document decision
- Four possible outcomes per hook: **Absorb-PreCommit** (add to gzkit pre-commit config), **Absorb-Claude** (add to Claude hooks), **Absorb-Both** (add to both enforcement points), **Confirm** (gzkit's existing version is sufficient), **Exclude** (domain-specific, does not belong in gzkit)
- Each decision must include enforcement timing rationale
- Absorbed hooks must follow gzkit conventions: Pydantic BaseModel, pathlib.Path, UTF-8 encoding, no bare except

## Interfaces

- **CLI (external contract):** Pre-commit hooks run via `pre-commit run --all-files`
- **Config keys consumed (read-only):** `.pre-commit-config.yaml`, `pyproject.toml` (tool configurations)
- **Internal APIs:** Hook scripts in `src/gzkit/hooks/` or standalone scripts referenced by pre-commit config

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.35.0-01 | Evaluate `arb-ruff` — ARB-wrapped linting (not in gzkit) | Heavy | Pending |
| 2 | OBPI-0.35.0-02 | Evaluate `ruff-format` — code formatting (compare with gzkit) | Heavy | Pending |
| 3 | OBPI-0.35.0-03 | Evaluate `ty-check` — type checking (compare with gzkit) | Heavy | Pending |
| 4 | OBPI-0.35.0-04 | Evaluate `unittest` — smoke tests (compare with gzkit) | Heavy | Pending |
| 5 | OBPI-0.35.0-05 | Evaluate `arb-validate` — ARB receipt validation (not in gzkit) | Heavy | Pending |
| 6 | OBPI-0.35.0-06 | Evaluate `xenon-complexity` — complexity ceilings (compare with gzkit) | Heavy | Pending |
| 7 | OBPI-0.35.0-07 | Evaluate `protect-copilot-instructions` — instruction file protection (not in gzkit) | Heavy | Pending |
| 8 | OBPI-0.35.0-08 | Evaluate `forbid-pytest` — pytest prohibition enforcement (compare with gzkit) | Heavy | Pending |
| 9 | OBPI-0.35.0-09 | Evaluate `normalize-adr-h1` — ADR heading normalization (not in gzkit) | Heavy | Pending |
| 10 | OBPI-0.35.0-10 | Evaluate `generate-adr-docs` — ADR documentation generation (not in gzkit) | Heavy | Pending |
| 11 | OBPI-0.35.0-11 | Evaluate `forbid-prod-db-in-tests` — production DB guard in tests (not in gzkit) | Heavy | Pending |
| 12 | OBPI-0.35.0-12 | Evaluate `cross-platform-sqlite-guard` — SQLite cross-platform enforcement (not in gzkit) | Heavy | Pending |
| 13 | OBPI-0.35.0-13 | Evaluate `validate-manpages` — manpage validation (not in gzkit) | Heavy | Pending |
| 14 | OBPI-0.35.0-14 | Evaluate `sync-manpage-docstrings` — manpage-docstring synchronization (not in gzkit) | Heavy | Pending |
| 15 | OBPI-0.35.0-15 | Evaluate `interrogate` — docstring coverage (compare with gzkit) | Heavy | Pending |
| 16 | OBPI-0.35.0-16 | Evaluate `check-todos-fixmes` — TODO/FIXME tracking (compare with gzkit) | Heavy | Pending |
| 17 | OBPI-0.35.0-17 | Evaluate `md-docs` — markdown tidy and lint (not in gzkit) | Heavy | Pending |
| 18 | OBPI-0.35.0-18 | Evaluate `repo-canonicalization` — repository structure enforcement (not in gzkit) | Heavy | Pending |
| 19 | OBPI-0.35.0-19 | Evaluate `sync-claude-skills` — Claude skills synchronization (not in gzkit) | Heavy | Pending |
| 20 | OBPI-0.35.0-20 | Evaluate `adr-drift-check` — ADR drift detection (not in gzkit) | Heavy | Pending |

**Briefs location:** `obpis/OBPI-0.35.0-*.md`

**WBS Completeness Rule:** Every row in this table has a corresponding brief file.

**Lane definitions:**

- **Heavy** — All OBPIs are Heavy because absorbed hooks may change commit-time enforcement behavior

---

## Rationale

opsdev's `.pre-commit-config.yaml` represents a mature enforcement layer with 20 hooks covering code quality, governance compliance, documentation validation, and repository hygiene. gzkit currently has partial overlap (7 hooks exist in some form) but lacks 13 hooks entirely. The enforcement timing dimension (pre-commit vs. Claude hooks) adds complexity: some checks are cheap and should run on every commit, while others need agent context or are expensive enough to run only during agent sessions. This ADR ensures every hook is evaluated individually with the timing question answered explicitly.

## Consequences

- gzkit's enforcement layer becomes comprehensive across both pre-commit and Claude hook surfaces
- Enforcement timing is documented and intentional, not accidental
- opsdev can depend on gzkit for all generic enforcement hooks, reducing its own hook footprint
- New hooks in gzkit may require new tests, documentation, and configuration
- Some opsdev hooks may be excluded as domain-specific (e.g., warehouse-specific guards)

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/test_hooks_*.py` — unit tests for each absorbed hook
- **BDD (Heavy):** `features/hooks.feature` — if new enforcement surfaces are introduced
- **Docs:** Decision rationale documented per OBPI brief

---

## OBPI Acceptance Note (Human Acknowledgment)

- Each OBPI documents the comparison result and decision (Absorb-PreCommit/Absorb-Claude/Absorb-Both/Confirm/Exclude)
- Human attestation required for all OBPIs (Heavy lane, parent ADR is Heavy)
- Attestation command: `uv run gz gates --adr ADR-0.35.0`

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.35.0`
- **Related:** ADR-0.27.0 (hook infrastructure), ADR-0.31.0, ADR-0.32.0

### Source & Contracts

- opsdev source: `../airlineops/.pre-commit-config.yaml`, `../airlineops/scripts/hooks/`
- gzkit target: `.pre-commit-config.yaml`, `src/gzkit/hooks/`, `.claude/hooks/`

### Tests

- Unit: `tests/test_hooks_*.py` (per absorbed hook)

### Docs

- Decision rationale: per OBPI brief in `obpis/`
- Governance: this ADR

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|-------------------|----------|-------|
| `.pre-commit-config.yaml` | M | All absorbed pre-commit hooks integrated | Hook execution output | |
| `.claude/hooks/` | M | All absorbed Claude hooks integrated | Agent session verification | |
| `tests/` | M | All absorbed hooks tested | `uv run gz test` | |
| `obpis/` | P | All 20 OBPIs have decisions documented | Brief review | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes
