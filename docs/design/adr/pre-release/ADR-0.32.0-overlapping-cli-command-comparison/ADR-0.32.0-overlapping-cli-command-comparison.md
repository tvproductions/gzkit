---
id: ADR-0.32.0-overlapping-cli-command-comparison
status: Proposed
semver: 0.32.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-21
dependencies:
  - ADR-0.25.0
  - ADR-0.26.0
  - ADR-0.30.0
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.32.0: Overlapping CLI Command Comparison

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Catalog every CLI command that exists in BOTH opsdev and gzkit, with source file locations and line counts.
  1. For each overlapping command, identify the opsdev implementation file and the gzkit implementation file (or module).
  1. Build a comparison matrix with columns: command, opsdev lines, gzkit lines, feature parity, gap analysis.

**Date Added:** 2026-03-21
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.32.0
**Area:** CLI Command Comparison -- Companion Absorption (Overlapping Commands)

## Agent Context Frame -- MANDATORY

**Role:** Comparison evaluator -- performing line-by-line analysis of every CLI command that exists in both opsdev and gzkit, determining which implementation is superior for each, and absorbing improvements into gzkit.

**Purpose:** When this ADR is complete, every CLI command that exists in both opsdev and gzkit has been compared at the implementation level. For each of the 25 overlapping commands, the evaluator has read both codebases, documented the comparison, and either absorbed opsdev improvements into gzkit or documented why gzkit's implementation is sufficient.

**Goals:**

- Every overlapping command is compared at implementation depth (not just flag/help-text level)
- Line count disparities are explained -- larger opsdev implementations may contain features gzkit lacks
- gzkit absorbs any superior patterns, error handling, or features from opsdev
- Commands unique to opsdev (cwd-guard, yaml-guard) are evaluated for gzkit inclusion
- The subtraction test holds: `opsdev - gzkit = pure opsdev domain` for all CLI commands

**Critical Constraint:** Do not rubber-stamp gzkit as "sufficient" -- read both implementations and compare honestly. git-sync alone shows a 682 vs 199 line disparity that demands examination. The comparison must go beyond surface features (flags, help text) to the actual implementation code: error handling, edge cases, robustness, cross-platform behavior.

**Anti-Pattern Warning:** A failed implementation looks like: comparing only surface features (flags, help text) without reading the actual implementation code. Equally bad: declaring gzkit sufficient for a 682-line opsdev command when gzkit has 199 lines without documenting exactly what those 483 missing lines do and whether any of them matter.

**Integration Points:**

- `src/gzkit/commands/` -- primary CLI command implementations
- `src/gzkit/quality.py` -- lint/format/test/typecheck consolidation
- `src/gzkit/sync.py` -- sync-related commands
- `src/gzkit/hooks/` -- hooks infrastructure
- `../opsdev/src/opsdev/tools/` -- opsdev tool implementations

---

## Feature Checklist -- Appraisal of Completeness

- Scope and surface
  - External contract may change (Heavy lane) -- absorbed improvements may alter CLI behavior, flags, output, or error handling
- Tests
  - Each absorbed improvement must have unit tests; coverage >= 40%
- Docs
  - Comparison rationale documented per OBPI (absorb improvements / confirm sufficient / note gaps)
- OBPI mapping
  - Each numbered checklist item maps to one brief; 25 items = 25 briefs

## Intent

This is the largest ADR by OBPI count in the absorption series. Every CLI command that exists in BOTH opsdev and gzkit must be compared at the implementation level. opsdev's tools directory contains battle-tested implementations that in many cases are significantly larger than their gzkit equivalents (git-sync: 682 vs 199 lines; test: 389 lines in test_suites.py; audit: 453 lines in adr_evidence_audit.py). These line count disparities may represent missing features, better error handling, more robust edge-case coverage, or opsdev-specific logic that gzkit does not need. This ADR governs the item-by-item determination. Two commands (cwd-guard, yaml-guard) exist only in opsdev and must be evaluated for gzkit inclusion.

## Decision

- Each of the 25 overlapping commands gets individual OBPI examination
- For each command: read both implementations completely, compare at code level, document findings
- Possible outcomes per command: **Absorb Improvements** (opsdev has features/patterns gzkit should adopt), **Confirm Sufficient** (gzkit's implementation covers all generic needs), **Absorb New** (command does not exist in gzkit, should be added)
- All absorbed code must follow gzkit conventions: Pydantic BaseModel, pathlib.Path, UTF-8 encoding, no bare except

## Interfaces

- **CLI (external contract):** `uv run gz {command}` -- improvements may change behavior of existing commands
- **Config keys consumed (read-only):** `.gzkit/manifest.json` -- artifact paths, verification commands
- **Internal APIs:** Enhanced modules in `src/gzkit/` providing improved command implementations

## OBPI Decomposition -- Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.32.0-01 | Compare `git-sync` -- opsdev 682 lines vs gzkit 199 lines | Heavy | Pending |
| 2 | OBPI-0.32.0-02 | Compare `lint` -- opsdev lint_tools.py 69 lines vs gzkit quality.py | Heavy | Pending |
| 3 | OBPI-0.32.0-03 | Compare `format` -- opsdev format_tools.py 33 lines vs gzkit quality.py | Heavy | Pending |
| 4 | OBPI-0.32.0-04 | Compare `test` -- opsdev test_suites.py 389 lines vs gzkit quality.py | Heavy | Pending |
| 5 | OBPI-0.32.0-05 | Compare `typecheck` -- opsdev typing_tools.py 64 lines vs gzkit quality.py | Heavy | Pending |
| 6 | OBPI-0.32.0-06 | Compare `check-config-paths` -- opsdev 321 lines vs gzkit cli.py | Heavy | Pending |
| 7 | OBPI-0.32.0-07 | Compare `cli-audit` -- opsdev cli_tools.py 142 lines vs gzkit cli.py | Heavy | Pending |
| 8 | OBPI-0.32.0-08 | Compare `tidy/clean` -- opsdev clean_tools.py 57 lines vs gzkit cli.py | Heavy | Pending |
| 9 | OBPI-0.32.0-09 | Compare `gates` -- opsdev gates_tools.py 55 lines vs gzkit cli.py | Heavy | Pending |
| 10 | OBPI-0.32.0-10 | Compare `implement` -- opsdev dev_tools.py 40 lines vs gzkit cli.py | Heavy | Pending |
| 11 | OBPI-0.32.0-11 | Compare `closeout` -- opsdev governance lifecycle vs gzkit cli.py | Heavy | Pending |
| 12 | OBPI-0.32.0-12 | Compare `audit` -- opsdev adr_evidence_audit.py 453 lines vs gzkit cli.py | Heavy | Pending |
| 13 | OBPI-0.32.0-13 | Compare `attest` -- opsdev attestation surface vs gzkit commands/attest.py | Heavy | Pending |
| 14 | OBPI-0.32.0-14 | Compare `status/state` -- opsdev governance_tools.py 64 lines vs gzkit commands/status.py | Heavy | Pending |
| 15 | OBPI-0.32.0-15 | Compare `adr status/docs/map/check` -- opsdev adr_tools.py 218 lines vs gzkit cli.py | Heavy | Pending |
| 16 | OBPI-0.32.0-16 | Compare `adr recon/audit-check/emit-receipt` -- opsdev adr_evidence_audit.py vs gzkit cli.py | Heavy | Pending |
| 17 | OBPI-0.32.0-17 | Compare `adr evidence/autolink/sync/promote` -- opsdev adr_tools.py vs gzkit cli.py | Heavy | Pending |
| 18 | OBPI-0.32.0-18 | Compare `adr eval/report` -- opsdev adr_tools.py vs gzkit cli.py | Heavy | Pending |
| 19 | OBPI-0.32.0-19 | Compare `docs/docs-lint/md-lint/md-fix/md-tidy` -- opsdev docs_tools.py+md_docs.py vs gzkit cli.py | Heavy | Pending |
| 20 | OBPI-0.32.0-20 | Compare `sync-repo` -- opsdev sync_repo.py 81 lines vs gzkit cli.py | Heavy | Pending |
| 21 | OBPI-0.32.0-21 | Compare `sync-agents-skills/sync-claude-skills` -- opsdev skill_sync_tools.py 456 lines vs gzkit sync.py | Heavy | Pending |
| 22 | OBPI-0.32.0-22 | Compare `layout-verify` -- opsdev layout_tools.py 44 lines vs gzkit cli.py | Heavy | Pending |
| 23 | OBPI-0.32.0-23 | Evaluate `cwd-guard` -- opsdev cwd_guard_tools.py 56 lines, no gzkit equivalent | Heavy | Pending |
| 24 | OBPI-0.32.0-24 | Evaluate `yaml-guard` -- opsdev yaml_guard_tools.py 75 lines, no gzkit equivalent | Heavy | Pending |
| 25 | OBPI-0.32.0-25 | Compare `hooks subcommands` -- opsdev hooks_tools.py 81 lines vs gzkit hooks/ | Heavy | Pending |

**Briefs location:** `briefs/OBPI-0.32.0-*.md`

**WBS Completeness Rule:** Every row in this table has a corresponding brief file.

**Lane definitions:**

- **Heavy** -- All OBPIs are Heavy because absorbed improvements may change external CLI contracts

---

## Rationale

opsdev's tools directory contains 25 commands that overlap with gzkit's CLI surface. Many of these opsdev implementations are significantly larger and more mature than their gzkit equivalents. The git-sync disparity (682 vs 199 lines) is emblematic: gzkit may be missing error recovery, edge-case handling, or features that opsdev has developed through operational use. Rather than assuming gzkit is sufficient, this ADR mandates honest code-level comparison of every overlapping command, ensuring gzkit absorbs any improvements that make the governance toolkit more robust. Two opsdev-only commands (cwd-guard, yaml-guard) are evaluated for inclusion in gzkit.

## Consequences

- gzkit's CLI implementations become at least as robust as opsdev's for all shared commands
- Line count disparities are explained and addressed rather than hand-waved
- opsdev-only commands (cwd-guard, yaml-guard) get explicit inclusion/exclusion decisions
- Some gzkit commands may grow significantly as they absorb opsdev improvements
- The quality.py consolidation (lint/format/test/typecheck) must be evaluated against opsdev's separate-file approach

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/` -- unit tests for each absorbed improvement
- **BDD (Heavy):** `features/` -- if CLI contracts change
- **Docs:** Comparison rationale documented per OBPI brief

---

## OBPI Acceptance Note (Human Acknowledgment)

- Each OBPI documents the comparison result and decision (Absorb Improvements / Confirm Sufficient / Absorb New)
- Human attestation required for all OBPIs (Heavy lane, parent ADR is Heavy)
- Attestation command: `uv run gz gates --adr ADR-0.32.0`

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.32.0`
- **Related:** ADR-0.25.0 (core infrastructure), ADR-0.26.0 (companion), ADR-0.30.0

### Source & Contracts

- opsdev source: `../opsdev/src/opsdev/tools/` -- tool implementations
- gzkit target: `src/gzkit/` -- enhanced command implementations

### Tests

- Unit: `tests/` (per absorbed improvement)

### Docs

- Comparison rationale: per OBPI brief in `briefs/`
- Governance: this ADR

---

## Completion Checklist -- Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|-------------------|----------|-------|
| `src/gzkit/` | M | All absorbed improvements integrated | Test output | |
| `tests/` | M | All absorbed improvements tested | `uv run gz test` | |
| `briefs/` | P | All 25 OBPIs have comparison decisions documented | Brief review | |

### SIGN-OFF -- Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes
