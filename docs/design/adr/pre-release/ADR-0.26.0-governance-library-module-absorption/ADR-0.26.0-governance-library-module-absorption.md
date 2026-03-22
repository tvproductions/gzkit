---
id: ADR-0.26.0-governance-library-module-absorption
status: Proposed
semver: 0.26.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-21
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.26.0: Governance Library Module Absorption

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Audit gzkit's existing governance modules (`cli.py`, `ledger.py`, `validate.py`, `sync.py`) to understand current capabilities and their coverage of governance primitives.
  1. Audit opsdev `lib/` governance library modules to catalog every reusable governance primitive and its maturity level.
  1. Create a cross-reference matrix mapping each opsdev lib module to its gzkit equivalent (or lack thereof).

**Date Added:** 2026-03-21
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.26.0
**Area:** Governance Libraries — Companion Absorption (Tier 2 Domain-Agnostic)

## Agent Context Frame — MANDATORY

**Role:** Absorption evaluator — comparing opsdev governance library primitives against gzkit equivalents, determining which implementation is superior, and absorbing the best into gzkit.

**Purpose:** When this ADR is complete, gzkit owns all reusable governance library primitives that currently reside in `opsdev/lib/`. For each of the 12 modules, gzkit either absorbed the opsdev implementation (because it was superior), confirmed its own implementation is sufficient (with documented rationale), or explicitly excluded the module as domain-specific.

**Goals:**

- Every lib/ module in opsdev is examined individually with a documented decision
- gzkit's governance layer is at least as capable as opsdev's for all generic governance patterns
- No reusable governance primitive remains stranded in the opsdev codebase
- The subtraction test holds: `opsdev - gzkit = pure ops domain`

**Critical Constraint:** Implementations MUST compare both codebases honestly — opsdev wins where it has significant depth that gzkit lacks. Do not assume gzkit's monolithic cli.py already covers what these focused modules provide. The opsdev lib/ contains ~6,200 lines of domain-agnostic governance primitives for ADR management, drift detection, traceability, and validation receipts. gzkit may have partial coverage in some areas but likely lacks the depth and focus of dedicated library modules.

**Anti-Pattern Warning:** A failed implementation looks like: assuming gzkit's cli.py (which mixes command handling with governance logic) already covers what opsdev's focused, single-responsibility library modules provide. Equally bad: blindly copying opsdev code without adapting it to gzkit's architecture (Pydantic models, pathlib paths, UTF-8 encoding).

**Integration Points:**

- `src/gzkit/cli.py` — CLI command handling (compare with `opsdev/lib/adr.py`, `opsdev/lib/cli_audit.py`)
- `src/gzkit/ledger.py` — event ledger (compare with `opsdev/lib/adr_governance.py`, `opsdev/lib/ledger_schema.py`)
- `src/gzkit/validate.py` — validation (compare with `opsdev/lib/validation_receipt.py`)
- `src/gzkit/sync.py` — artifact sync (compare with `opsdev/lib/artifacts.py`)

---

## Feature Checklist — Appraisal of Completeness

- Scope and surface
  - External contract may change (Heavy lane) — absorbed governance libraries may introduce new CLI capabilities or change behavior of existing commands
- Tests
  - Each absorbed module must have unit tests; coverage >= 40%
- Docs
  - Decision rationale documented per OBPI (absorb/confirm/exclude)
- OBPI mapping
  - Each numbered checklist item maps to one brief; 12 items = 12 briefs

## Intent

gzkit must own all reusable governance library primitives. opsdev's `lib/` package contains ~6,200 lines of domain-agnostic governance implementations covering ADR management (1,588 lines), cross-references and traceability (797 + 277 lines), reconciliation and drift detection (607 + 384 lines), governance policy enforcement (535 lines), ledger schemas (501 lines), validation receipts (274 lines), audit ledger management (249 lines), CLI audit infrastructure (238 lines), artifact management (232 lines), and documentation generation (218 lines). These are focused, single-responsibility library modules — not CLI commands. gzkit has partial coverage for some of these in its monolithic cli.py and ledger.py, but lacks dedicated modules for references, reconciliation, drift detection, traceability, audit ledger, and documentation generation. This ADR governs the item-by-item evaluation and absorption of these 12 modules into gzkit.

## Decision

- Each of the 12 opsdev lib/ modules gets individual OBPI examination
- For each module: read both implementations, compare maturity/completeness/robustness, document decision
- Three possible outcomes per module: **Absorb** (opsdev is better), **Confirm** (gzkit is sufficient), **Exclude** (domain-specific, does not belong in gzkit)
- Absorbed modules must follow gzkit conventions: Pydantic BaseModel, pathlib.Path, UTF-8 encoding, no bare except

## Interfaces

- **CLI (external contract):** `uv run gz {command}` — new governance libraries may surface as new commands or improve existing ones
- **Config keys consumed (read-only):** `.gzkit/manifest.json` — artifact paths, verification commands
- **Internal APIs:** New modules in `src/gzkit/` providing governance library infrastructure to all commands

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.26.0-01 | Evaluate and absorb `lib/adr.py` (1,588 lines) — ADR management primitives | Heavy | Pending |
| 2 | OBPI-0.26.0-02 | Evaluate and absorb `lib/references.py` (797 lines) — cross-reference resolution and link management | Heavy | Pending |
| 3 | OBPI-0.26.0-03 | Evaluate and absorb `lib/adr_recon.py` (607 lines) — ADR reconciliation and consistency checking | Heavy | Pending |
| 4 | OBPI-0.26.0-04 | Evaluate and absorb `lib/adr_governance.py` (535 lines) — ADR governance policy enforcement | Heavy | Pending |
| 5 | OBPI-0.26.0-05 | Evaluate and absorb `lib/ledger_schema.py` (501 lines) — ledger schema definitions and validation | Heavy | Pending |
| 6 | OBPI-0.26.0-06 | Evaluate and absorb `lib/drift_detection.py` (384 lines) — governance drift detection and alerting | Heavy | Pending |
| 7 | OBPI-0.26.0-07 | Evaluate and absorb `lib/adr_traceability.py` (277 lines) — ADR-to-artifact traceability chains | Heavy | Pending |
| 8 | OBPI-0.26.0-08 | Evaluate and absorb `lib/validation_receipt.py` (274 lines) — structured validation receipt generation | Heavy | Pending |
| 9 | OBPI-0.26.0-09 | Evaluate and absorb `lib/adr_audit_ledger.py` (249 lines) — audit ledger for ADR lifecycle events | Heavy | Pending |
| 10 | OBPI-0.26.0-10 | Evaluate and absorb `lib/cli_audit.py` (238 lines) — CLI audit infrastructure and contract verification | Heavy | Pending |
| 11 | OBPI-0.26.0-11 | Evaluate and absorb `lib/artifacts.py` (232 lines) — artifact management and sync primitives | Heavy | Pending |
| 12 | OBPI-0.26.0-12 | Evaluate and absorb `lib/docs.py` (218 lines) — documentation generation and validation | Heavy | Pending |

**Briefs location:** `briefs/OBPI-0.26.0-*.md`

**WBS Completeness Rule:** Every row in this table has a corresponding brief file.

**Lane definitions:**

- **Heavy** — All OBPIs are Heavy because absorbed governance libraries may change external contracts

---

## Rationale

opsdev's `lib/` package represents ~6,200 lines of domain-agnostic governance primitives. gzkit currently has partial equivalents for some of these (ADR management in cli.py, governance enforcement in ledger.py, validation in validate.py, artifact sync in sync.py) but lacks dedicated modules for cross-references, reconciliation, drift detection, traceability, audit ledger, and documentation generation. The subtraction test demands that all reusable governance patterns flow upstream to gzkit. This ADR ensures nothing is missed by examining every module individually. Critically, opsdev's focused library modules (single-responsibility, well-bounded) likely surpass gzkit's monolithic approach where governance logic is interleaved with CLI command handling.

## Consequences

- gzkit's governance library layer becomes comprehensive and self-sufficient
- opsdev can depend on gzkit for all governance primitives, reducing its own library footprint
- New modules in gzkit may require new tests, documentation, and integration work
- gzkit gains dedicated governance library modules instead of mixing governance logic into CLI commands
- Some opsdev modules may have overlap requiring careful merge rather than wholesale absorption

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/test_lib_*.py` — unit tests for each absorbed module
- **BDD (Heavy):** `features/governance_library.feature` — if new CLI surfaces are introduced
- **Docs:** Decision rationale documented per OBPI brief

---

## Dependencies

- **ADR-0.25.0** — Core Infrastructure Pattern Absorption must complete first; governance libraries depend on core infrastructure patterns (errors, types, registry, etc.)

---

## OBPI Acceptance Note (Human Acknowledgment)

- Each OBPI documents the comparison result and decision (Absorb/Confirm/Exclude)
- Human attestation required for all OBPIs (Heavy lane, parent ADR is Heavy)
- Attestation command: `uv run gz gates --adr ADR-0.26.0`

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.26.0`
- **Related:** ADR-0.25.0 (core infrastructure absorption — prerequisite)

### Source & Contracts

- opsdev source: `../opsdev/lib/`
- gzkit target: `src/gzkit/` — new or enhanced modules

### Tests

- Unit: `tests/test_lib_*.py` (per absorbed module)

### Docs

- Decision rationale: per OBPI brief in `briefs/`
- Governance: this ADR

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|-------------------|----------|-------|
| `src/gzkit/` | M | All absorbed modules integrated | Test output | |
| `tests/` | M | All absorbed modules tested | `uv run gz test` | |
| `briefs/` | P | All 12 OBPIs have decisions documented | Brief review | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes
