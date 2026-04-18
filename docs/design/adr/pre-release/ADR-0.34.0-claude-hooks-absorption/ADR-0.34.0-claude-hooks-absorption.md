---
id: ADR-0.34.0-claude-hooks-absorption
status: Pending
semver: 0.34.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-21
dependencies:
  - ADR-0.25.0
  - ADR-0.26.0
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.34.0: Claude Hooks Absorption

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Catalog all 13 airlineops Claude hook scripts in `.claude/hooks/` with their trigger events, line counts, and behavioral descriptions.
  1. Catalog gzkit's 5 hook modules in `src/gzkit/hooks/` with their generated hook behavior and coverage.
  1. Build a comparison matrix: which hooks exist in both (Compare), which are new (Absorb), and which need domain evaluation (Evaluate).

**Date Added:** 2026-03-21
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.34.0
**Area:** Claude Hooks -- Companion Absorption (Hook Infrastructure)

## Agent Context Frame -- MANDATORY

**Role:** Hook comparison evaluator -- analyzing all 13 airlineops Claude hook scripts against gzkit's existing hook infrastructure, determining which behaviors gzkit already covers, which should be absorbed, and which are domain-specific.

**Purpose:** When this ADR is complete, every Claude hook in airlineops has been compared against gzkit's hook infrastructure. For each of the 13 hooks, the evaluator has determined whether gzkit already covers the behavior (Compare), should absorb the behavior (Absorb), or should evaluate for domain-specificity (Evaluate). gzkit's hook infrastructure becomes at least as capable as airlineops's for all governance-generic hook behaviors.

**Goals:**

- Every airlineops Claude hook is examined individually with a documented decision
- gzkit's hook generation covers all governance-generic hook behaviors
- Domain-specific hooks are explicitly excluded with documented rationale
- The architectural difference (gzkit generates hooks from modules; airlineops has standalone scripts) is accounted for in every comparison
- The subtraction test holds: `airlineops hooks - gzkit hooks = pure airline domain hooks`

**Critical Constraint:** Hook implementations in airlineops are mature and battle-tested. gzkit generates hooks from its `src/gzkit/hooks/` modules (5 modules). The comparison must account for this architectural difference -- airlineops has 13 standalone Python scripts while gzkit generates hooks from a smaller number of modules. A module-to-module comparison misses the point; compare actual behaviors and coverage.

**Anti-Pattern Warning:** A failed implementation looks like: comparing hook file counts (13 vs 5) without comparing actual behavior and coverage. A gzkit module may generate hooks that cover multiple airlineops scripts. Equally bad: assuming all airlineops hooks are domain-specific without reading them.

**Integration Points:**

- `src/gzkit/hooks/` -- gzkit hook modules (5 existing)
- `.claude/hooks/` -- generated hook scripts
- `../airlineops/.claude/hooks/` -- airlineops hook scripts (13 scripts)

---

## Feature Checklist -- Appraisal of Completeness

- Scope and surface
  - External contract may change (Heavy lane) -- new hook behaviors may be generated
- Tests
  - Each absorbed hook behavior must have unit tests; coverage >= 40%
- Docs
  - Comparison rationale documented per OBPI (compare/absorb/evaluate outcome)
- OBPI mapping
  - Each numbered checklist item maps to one brief; 13 items = 13 briefs

## Intent

airlineops has 13 Claude hook scripts in `.claude/hooks/` that have been developed through operational use. gzkit has 5 hook modules in `src/gzkit/hooks/` that generate hooks for governed repositories. Some hooks exist in both systems with potentially different implementations (Compare action). Some hooks exist only in airlineops and should likely be absorbed into gzkit (Absorb action). One hook (dataset-guard) may be domain-specific and needs evaluation (Evaluate action). This ADR governs the item-by-item comparison and absorption of all 13 airlineops hooks, ensuring gzkit's hook infrastructure covers all governance-generic behaviors.

## Decision

- Each of the 13 airlineops hooks gets individual OBPI examination
- For each hook: read both implementations (or just airlineops for Absorb/Evaluate actions), compare behavior
- Three action types: **Compare** (exists in both, determine which is better), **Absorb** (new to gzkit, add it), **Evaluate** (may be domain-specific, needs assessment)
- Absorbed hook behaviors must be integrated into gzkit's module-based hook architecture
- Generated hooks must maintain behavioral parity with absorbed airlineops scripts

## Interfaces

- **Hook triggers:** PreToolUse, PostToolUse, Notification -- Claude Code hook lifecycle events
- **Config:** `.claude/hooks/` -- generated hook scripts
- **Internal APIs:** `src/gzkit/hooks/` -- hook modules that generate scripts

## OBPI Decomposition -- Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.34.0-01 | Compare `obpi-completion-validator.py` -- validates OBPI completion claims | Heavy | Pending |
| 2 | OBPI-0.34.0-02 | Absorb `obpi-completion-recorder.py` -- records OBPI completions to ledger | Heavy | Pending |
| 3 | OBPI-0.34.0-03 | Absorb `insight-harvester.py` -- harvests agent insights from conversations | Heavy | Pending |
| 4 | OBPI-0.34.0-04 | Compare `instruction-router.py` -- routes instructions based on context | Heavy | Pending |
| 5 | OBPI-0.34.0-05 | Compare `post-edit-ruff.py` -- runs ruff after file edits | Heavy | Pending |
| 6 | OBPI-0.34.0-06 | Compare `pipeline-router.py` -- routes pipeline execution | Heavy | Pending |
| 7 | OBPI-0.34.0-07 | Compare `plan-audit-gate.py` -- gates plan execution with audit checks | Heavy | Pending |
| 8 | OBPI-0.34.0-08 | Compare `pipeline-gate.py` -- gates pipeline progression | Heavy | Pending |
| 9 | OBPI-0.34.0-09 | Compare `session-staleness-check.py` -- checks for stale session state | Heavy | Pending |
| 10 | OBPI-0.34.0-10 | Absorb `hook-diag.py` -- hook diagnostics and debugging | Heavy | Pending |
| 11 | OBPI-0.34.0-11 | Evaluate `dataset-guard.py` -- guards dataset operations (domain-specific?) | Heavy | Pending |
| 12 | OBPI-0.34.0-12 | Compare `pipeline-completion-reminder.py` -- reminds about incomplete pipelines | Heavy | Pending |
| 13 | OBPI-0.34.0-13 | Absorb `insight-reminder.py` -- reminds about pending insights | Heavy | Pending |

**Briefs location:** `obpis/OBPI-0.34.0-*.md`

**WBS Completeness Rule:** Every row in this table has a corresponding brief file.

**Lane definitions:**

- **Heavy** -- All OBPIs are Heavy because hook behavior changes affect agent governance workflow

---

## Rationale

Claude hooks are the enforcement mechanism for agent governance. They intercept agent actions in real-time, validate compliance, record evidence, and route workflows. airlineops has 13 hooks developed through months of operational use; gzkit has 5 hook modules that generate hooks for governed repositories. The gap between 13 operational hooks and 5 generating modules suggests gzkit may be missing critical enforcement behaviors. This ADR ensures every airlineops hook behavior is accounted for in gzkit's infrastructure -- either already covered, newly absorbed, or explicitly excluded as domain-specific.

## Consequences

- gzkit's hook infrastructure becomes comprehensive for governance enforcement
- New hook modules may be added to `src/gzkit/hooks/`
- Generated hooks will cover more governance behaviors
- airlineops can depend on gzkit-generated hooks for all governance-generic behaviors
- Domain-specific hooks (if any) remain in airlineops

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/test_hooks_*.py` -- unit tests for each absorbed hook behavior
- **BDD (Heavy):** `features/hooks.feature` -- if new hook behaviors are introduced
- **Docs:** Comparison rationale documented per OBPI brief

---

## OBPI Acceptance Note (Human Acknowledgment)

- Each OBPI documents the comparison/absorption result and decision
- Human attestation required for all OBPIs (Heavy lane, parent ADR is Heavy)
- Attestation command: `uv run gz gates --adr ADR-0.34.0`

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.34.0`
- **Related:** ADR-0.25.0 (core infrastructure, OBPI-11 hooks pattern), ADR-0.26.0 (companion)

### Source & Contracts

- airlineops source: `../airlineops/.claude/hooks/` -- 13 hook scripts
- gzkit source: `src/gzkit/hooks/` -- 5 hook modules
- gzkit target: `src/gzkit/hooks/` -- enhanced hook modules

### Tests

- Unit: `tests/test_hooks_*.py` (per absorbed hook behavior)

### Docs

- Comparison rationale: per OBPI brief in `obpis/`
- Governance: this ADR

---

## Completion Checklist -- Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|-------------------|----------|-------|
| `src/gzkit/hooks/` | M | All absorbed hook behaviors integrated | Test output | |
| `tests/` | M | All absorbed hook behaviors tested | `uv run gz test` | |
| `obpis/` | P | All 13 OBPIs have comparison decisions documented | Brief review | |

### SIGN-OFF -- Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes
