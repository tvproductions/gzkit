---
id: ADR-0.27.0-arb-receipt-system-absorption
status: Proposed
semver: 0.27.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-21
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.27.0: ARB Receipt System Absorption

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Audit gzkit's existing ARB skill-only approach (`arb` command group, native quality commands) to understand current capabilities and patterns.
  1. Audit opsdev's full ARB receipt subsystem (`opsdev/arb/`, `opsdev/commands/arb_tools.py`, `data/schemas/arb_*.schema.json`) to catalog every module and its maturity level.
  1. Create a cross-reference matrix mapping each opsdev ARB module to its gzkit equivalent (or lack thereof).

**Date Added:** 2026-03-21
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.27.0
**Area:** ARB Receipt System — Companion Absorption (Tier 2 Middleware)

## Agent Context Frame — MANDATORY

**Role:** Absorption evaluator — comparing opsdev's full ARB receipt subsystem against gzkit's skill-only ARB approach, determining whether the full receipt system adds governance value that justifies the complexity, and absorbing the best into gzkit.

**Purpose:** When this ADR is complete, gzkit has made an explicit, documented decision for each of the 13 ARB modules currently residing in opsdev. For each module, gzkit either absorbed the opsdev implementation (because the receipt system adds governance value), confirmed its own skill-only approach is sufficient (with documented rationale), or explicitly excluded the module as environment-specific (e.g., Supabase sync).

**Goals:**

- Every ARB module in opsdev is examined individually with a documented decision
- gzkit's ARB layer is at least as capable as opsdev's for all governance-relevant receipt patterns
- No reusable receipt/QA-evidence pattern remains stranded in the opsdev codebase
- The evaluation honestly weighs governance value against complexity cost

**Critical Constraint:** opsdev's ARB system is battle-tested with Supabase sync and GitHub issue filing. gzkit's skill-only approach deliberately has no subcommands. The evaluation must determine whether the full receipt system adds governance value that justifies the complexity.

**Anti-Pattern Warning:** A failed implementation looks like: porting ARB modules blindly without evaluating whether gzkit's simpler approach (native quality commands) already provides sufficient evidence for governance. Equally bad: dismissing the receipt system without reading and understanding how structured JSON receipts enable deterministic validation and pattern analysis that raw command output cannot.

**Integration Points:**

- `src/gzkit/arb/` — target for absorbed ARB modules
- `src/gzkit/commands/arb.py` — existing ARB command group (skill-only)
- `data/schemas/` — JSON schemas for receipt validation
- `artifacts/receipts/` — receipt storage directory

---

## Feature Checklist — Appraisal of Completeness

- Scope and surface
  - External contract may change (Heavy lane) — new ARB subcommands may be introduced or existing behavior may change
- Tests
  - Each absorbed module must have unit tests; coverage >= 40%
- Docs
  - Decision rationale documented per OBPI (absorb/confirm/exclude)
- OBPI mapping
  - Each numbered checklist item maps to one brief; 13 items = 13 briefs

## Intent

gzkit must decide whether to absorb opsdev's full ARB (Agent Self-Reporting) receipt subsystem. opsdev's `arb/` package contains ~1,630 lines of battle-tested middleware for structured JSON receipt generation, schema validation, pattern analysis, receipt lifecycle management, and external integrations (Supabase sync, GitHub issue filing). gzkit currently uses ARB as a skill-only approach with native quality commands — no subcommands, no structured receipts, no persistent receipt artifacts. This ADR governs the item-by-item evaluation and absorption decision for these 13 modules, weighing governance value against complexity cost.

## Decision

- Each of the 13 opsdev ARB modules gets individual OBPI examination
- For each module: read both implementations (opsdev module vs. gzkit equivalent or gap), compare maturity/governance-value/complexity, document decision
- Three possible outcomes per module: **Absorb** (opsdev adds governance value), **Confirm** (gzkit's skill-only approach is sufficient), **Exclude** (environment-specific, does not belong in gzkit)
- Absorbed modules must follow gzkit conventions: Pydantic BaseModel, pathlib.Path, UTF-8 encoding, no bare except

## Interfaces

- **CLI (external contract):** `uv run -m gzkit arb {subcommand}` — new subcommands may be introduced for receipt management
- **Config keys consumed (read-only):** `.gzkit/manifest.json` — artifact paths, verification commands
- **Internal APIs:** New modules in `src/gzkit/arb/` providing receipt infrastructure to all QA commands
- **Schemas:** `data/schemas/arb_*.schema.json` — receipt validation schemas

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.27.0-01 | Evaluate and absorb `arb/ruff_reporter.py` (247 lines) — Ruff lint receipt generation with structured findings | Heavy | Pending |
| 2 | OBPI-0.27.0-02 | Evaluate and absorb `arb/step_reporter.py` (138 lines) — generic QA step receipt generation | Heavy | Pending |
| 3 | OBPI-0.27.0-03 | Evaluate and absorb `arb/validate.py` (154 lines) — receipt schema validation and integrity checks | Heavy | Pending |
| 4 | OBPI-0.27.0-04 | Evaluate and absorb `arb/advise.py` (196 lines) — receipt analysis and recurring pattern advice | Heavy | Pending |
| 5 | OBPI-0.27.0-05 | Evaluate and absorb `arb/patterns.py` (253 lines) — pattern detection across receipt history | Heavy | Pending |
| 6 | OBPI-0.27.0-06 | Evaluate and absorb `arb/tidy.py` (170 lines) — receipt cleanup and lifecycle management | Heavy | Pending |
| 7 | OBPI-0.27.0-07 | Evaluate and absorb `arb/expunge.py` (114 lines) — receipt expungement and hard deletion | Heavy | Pending |
| 8 | OBPI-0.27.0-08 | Evaluate and absorb `arb/github_issues.py` (149 lines) — GitHub issue filing from receipt evidence | Heavy | Pending |
| 9 | OBPI-0.27.0-09 | Implement configurable ARB receipt retention via Pydantic Logfire — replaces opsdev Supabase sync | Heavy | Pending |
| 10 | OBPI-0.27.0-10 | Evaluate and absorb `arb/paths.py` (43 lines) — ARB path resolution and directory layout | Heavy | Pending |
| 11 | OBPI-0.27.0-11 | Evaluate and absorb `arb_lint_receipt.schema.json` — JSON schema for lint receipt validation | Heavy | Pending |
| 12 | OBPI-0.27.0-12 | Evaluate and absorb `arb_step_receipt.schema.json` — JSON schema for step receipt validation | Heavy | Pending |
| 13 | OBPI-0.27.0-13 | Evaluate and absorb `commands/arb_tools.py` (282 lines) — CLI wiring for all ARB subcommands | Heavy | Pending |

**Briefs location:** `obpis/OBPI-0.27.0-*.md`

**WBS Completeness Rule:** Every row in this table has a corresponding brief file.

**Lane definitions:**

- **Heavy** — All OBPIs are Heavy because absorbed ARB infrastructure may change external contracts or introduce new subcommands

---

## Rationale

opsdev's `arb/` package represents ~1,630 lines of battle-tested QA middleware. It goes significantly beyond gzkit's current skill-only ARB approach by providing: structured JSON receipts with schema validation, persistent receipt storage and lifecycle management, pattern analysis across receipt history, and external integrations (GitHub issues, Supabase sync). The governance question is whether structured receipts provide deterministic validation evidence that raw command output cannot, or whether the simpler approach is sufficient. This ADR ensures every module is examined individually with an honest complexity-vs-value assessment.

## Consequences

- If absorbed: gzkit gains a full receipt subsystem with deterministic validation, pattern analysis, and audit trails
- If confirmed: gzkit maintains its simpler skill-only approach with documented rationale for the decision
- Some modules (Supabase sync, GitHub issues) may be excluded as environment-specific integrations
- New modules in gzkit may require new tests, documentation, CLI subcommands, and JSON schemas
- Dependencies on ADR-0.25.0 (core infrastructure) and ADR-0.26.0 must be satisfied first

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/test_arb_*.py` — unit tests for each absorbed module
- **BDD (Heavy):** `features/arb_receipt.feature` — if new CLI surfaces are introduced
- **Docs:** Decision rationale documented per OBPI brief

---

## OBPI Acceptance Note (Human Acknowledgment)

- Each OBPI documents the comparison result and decision (Absorb/Confirm/Exclude)
- Human attestation required for all OBPIs (Heavy lane, parent ADR is Heavy)
- Attestation command: `uv run gz gates --adr ADR-0.27.0`

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.27.0`
- **Dependencies:** ADR-0.25.0, ADR-0.26.0

### Source & Contracts

- opsdev source: `../opsdev/src/opsdev/arb/`, `../opsdev/src/opsdev/commands/arb_tools.py`
- opsdev schemas: `../opsdev/data/schemas/arb_*.schema.json`
- gzkit target: `src/gzkit/arb/` — new or enhanced modules

### Tests

- Unit: `tests/test_arb_*.py` (per absorbed module)

### Docs

- Decision rationale: per OBPI brief in `obpis/`
- Governance: this ADR

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|-------------------|----------|-------|
| `src/gzkit/arb/` | M | All absorbed modules integrated | Test output | |
| `tests/` | M | All absorbed modules tested | `uv run gz test` | |
| `obpis/` | P | All 13 OBPIs have decisions documented | Brief review | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes
