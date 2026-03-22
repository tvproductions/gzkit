---
id: ADR-0.25.0-core-infrastructure-pattern-absorption
status: Proposed
semver: 0.25.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-21
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.25.0: Core Infrastructure Pattern Absorption

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Audit gzkit's existing infrastructure modules (`config.py`, `registry.py`, `quality.py`, `ledger.py`, `hooks/core.py`, `commands/common.py`) to understand current capabilities and patterns.
  1. Audit airlineops `src/airlineops/core/` and `common/` modules to catalog every reusable pattern and its maturity level.
  1. Create a cross-reference matrix mapping each airlineops core module to its gzkit equivalent (or lack thereof).

**Date Added:** 2026-03-21
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.25.0
**Area:** Core Infrastructure — Companion Absorption (Tier 1 Foundation)

## Agent Context Frame — MANDATORY

**Role:** Absorption evaluator — comparing airlineops core infrastructure patterns against gzkit equivalents, determining which implementation is superior, and absorbing the best into gzkit.

**Purpose:** When this ADR is complete, gzkit owns all reusable core infrastructure patterns that currently reside in `airlineops/src/airlineops/core/` and `common/`. For each of the 17 modules, gzkit either absorbed the airlineops implementation (because it was superior), confirmed its own implementation is sufficient (with documented rationale), or explicitly excluded the module as domain-specific.

**Goals:**

- Every core/common module in airlineops is examined individually with a documented decision
- gzkit's infrastructure layer is at least as capable as airlineops's for all generic patterns
- No reusable pattern remains stranded in the airlineops codebase
- The subtraction test holds: `airlineops - gzkit = pure airline domain`

**Critical Constraint:** Implementations MUST compare both codebases honestly — opsdev wins where it's more battle-tested. Do not assume gzkit is always better. The goal is MAX gzkit, not gzkit-by-default.

**Anti-Pattern Warning:** A failed implementation looks like: rubber-stamping gzkit's existing code as "sufficient" without actually reading and comparing the airlineops implementation. Equally bad: blindly copying airlineops code without adapting it to gzkit's architecture (Pydantic models, pathlib paths, UTF-8 encoding).

**Integration Points:**

- `src/gzkit/config.py` — configuration loading (compare with `airlineops/config/`)
- `src/gzkit/registry.py` — content type registry (compare with `airlineops/core/registry.py`)
- `src/gzkit/ledger.py` — event ledger (compare with `airlineops/core/ledger.py`)
- `src/gzkit/quality.py` — quality checks (compare with `airlineops/core/qc.py`)
- `src/gzkit/hooks/core.py` — hook infrastructure (compare with `airlineops/core/hooks.py`)
- `src/gzkit/commands/common.py` — console/output patterns (compare with `airlineops/common/console.py`)

---

## Feature Checklist — Appraisal of Completeness

- Scope and surface
  - External contract may change (Heavy lane) — new modules may introduce new CLI capabilities or change behavior of existing commands
- Tests
  - Each absorbed module must have unit tests; coverage >= 40%
- Docs
  - Decision rationale documented per OBPI (absorb/confirm/exclude)
- OBPI mapping
  - Each numbered checklist item maps to one brief; 17 items = 17 briefs

## Intent

gzkit must own all reusable core infrastructure patterns. airlineops's `core/` and `common/` packages contain battle-tested implementations of attestation, progress tracking, cryptographic signing, world-state hashing, registry patterns, error hierarchies, admission control, cross-platform file operations, and console output — none of which are airline-specific. This ADR governs the item-by-item evaluation and absorption of these 17 modules into gzkit, ensuring the subtraction test holds: after absorption, the only thing left in airlineops that isn't from gzkit is pure airline domain code.

## Decision

- Each of the 17 airlineops core/common modules gets individual OBPI examination
- For each module: read both implementations, compare maturity/completeness/robustness, document decision
- Three possible outcomes per module: **Absorb** (airlineops is better), **Confirm** (gzkit is sufficient), **Exclude** (domain-specific, does not belong in gzkit)
- Absorbed modules must follow gzkit conventions: Pydantic BaseModel, pathlib.Path, UTF-8 encoding, no bare except

## Interfaces

- **CLI (external contract):** `uv run gz {command}` — new infrastructure may surface as new commands or improve existing ones
- **Config keys consumed (read-only):** `.gzkit/manifest.json` — artifact paths, verification commands
- **Internal APIs:** New modules in `src/gzkit/` providing core infrastructure to all commands

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.25.0-01 | Evaluate and absorb `core/attestation.py` (511 lines) — evidence attestation and proof recording | Heavy | Pending |
| 2 | OBPI-0.25.0-02 | Evaluate and absorb `core/progress.py` (383 lines) — unified Rich progress API facade | Heavy | Pending |
| 3 | OBPI-0.25.0-03 | Evaluate and absorb `core/signature.py` (365 lines) — cryptographic content hashing and artifact fingerprinting | Heavy | Pending |
| 4 | OBPI-0.25.0-04 | Evaluate and absorb `core/world_state.py` (275 lines) — immutable world-state snapshots | Heavy | Pending |
| 5 | OBPI-0.25.0-05 | Evaluate and absorb `core/dataset_version.py` (246 lines) — version management utilities | Heavy | Pending |
| 6 | OBPI-0.25.0-06 | Evaluate and absorb `core/registry.py` (86 lines) — registry pattern implementation | Heavy | Pending |
| 7 | OBPI-0.25.0-07 | Evaluate and absorb `core/types.py` (40 lines) — core type definitions | Heavy | Pending |
| 8 | OBPI-0.25.0-08 | Evaluate and absorb `core/ledger.py` (91 lines) — ledger entry management | Heavy | Pending |
| 9 | OBPI-0.25.0-09 | Evaluate and absorb `core/schema.py` (90 lines) — schema definition utilities | Heavy | Pending |
| 10 | OBPI-0.25.0-10 | Evaluate and absorb `core/errors.py` (53 lines) — exception hierarchy | Heavy | Pending |
| 11 | OBPI-0.25.0-11 | Evaluate and absorb `core/hooks.py` (34 lines) — hook dispatch system | Heavy | Pending |
| 12 | OBPI-0.25.0-12 | Evaluate and absorb `core/admission.py` (34 lines) — admission control patterns | Heavy | Pending |
| 13 | OBPI-0.25.0-13 | Evaluate and absorb `core/qc.py` (18 lines) — quality control interfaces | Heavy | Pending |
| 14 | OBPI-0.25.0-14 | Evaluate and absorb `common/os.py` (241 lines) — cross-platform file operations | Heavy | Pending |
| 15 | OBPI-0.25.0-15 | Evaluate and absorb `common/manifests.py` (89 lines) — manifest loading and validation | Heavy | Pending |
| 16 | OBPI-0.25.0-16 | Evaluate and absorb `common/config.py` (73 lines) — configuration loading helpers | Heavy | Pending |
| 17 | OBPI-0.25.0-17 | Evaluate and absorb `common/console.py` (45 lines) — console I/O abstractions | Heavy | Pending |

**Briefs location:** `briefs/OBPI-0.25.0-*.md`

**WBS Completeness Rule:** Every row in this table has a corresponding brief file.

**Lane definitions:**

- **Heavy** — All OBPIs are Heavy because absorbed infrastructure may change external contracts

---

## Rationale

airlineops's `core/` and `common/` packages represent 1,700+ lines of battle-tested, domain-agnostic infrastructure. gzkit currently has partial equivalents for some of these (ledger, registry, quality, hooks, config) but lacks others entirely (attestation, signatures, world state, errors, admission control, cross-platform OS utilities). The subtraction test demands that all reusable patterns flow upstream to gzkit. This ADR ensures nothing is missed by examining every module individually.

## Consequences

- gzkit's infrastructure layer becomes comprehensive and self-sufficient
- airlineops can depend on gzkit for all core patterns, reducing its own infrastructure footprint
- New modules in gzkit may require new tests, documentation, and integration work
- Some airlineops modules may be excluded as domain-specific (e.g., dataset_version.py may have airline-specific semantics)

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/test_core_*.py` — unit tests for each absorbed module
- **BDD (Heavy):** `features/core_infrastructure.feature` — if new CLI surfaces are introduced
- **Docs:** Decision rationale documented per OBPI brief

---

## OBPI Acceptance Note (Human Acknowledgment)

- Each OBPI documents the comparison result and decision (Absorb/Confirm/Exclude)
- Human attestation required for all OBPIs (Heavy lane, parent ADR is Heavy)
- Attestation command: `uv run gz gates --adr ADR-0.25.0`

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.25.0`
- **Related:** airlineops ADR-0.0.36 (parked companion)

### Source & Contracts

- airlineops source: `../airlineops/src/airlineops/core/`, `../airlineops/src/airlineops/common/`
- gzkit target: `src/gzkit/` — new or enhanced modules

### Tests

- Unit: `tests/test_core_*.py` (per absorbed module)

### Docs

- Decision rationale: per OBPI brief in `briefs/`
- Governance: this ADR

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|-------------------|----------|-------|
| `src/gzkit/` | M | All absorbed modules integrated | Test output | |
| `tests/` | M | All absorbed modules tested | `uv run gz test` | |
| `briefs/` | P | All 17 OBPIs have decisions documented | Brief review | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes
