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

1. **OBPI-0.25.0-01:** Attestation pattern comparison and decision for
   `core/attestation.py`
2. **OBPI-0.25.0-02:** Progress facade comparison and decision for
   `core/progress.py`
3. **OBPI-0.25.0-03:** Signature and artifact-fingerprinting comparison and
   decision for `core/signature.py`
4. **OBPI-0.25.0-04:** World-state snapshot comparison and decision for
   `core/world_state.py`
5. **OBPI-0.25.0-05:** Dataset-version utility comparison and decision for
   `core/dataset_version.py`
6. **OBPI-0.25.0-06:** Registry pattern comparison and decision for
   `core/registry.py`
7. **OBPI-0.25.0-07:** Core types comparison and decision for `core/types.py`
8. **OBPI-0.25.0-08:** Ledger pattern comparison and decision for
   `core/ledger.py`
9. **OBPI-0.25.0-09:** Schema utility comparison and decision for
   `core/schema.py`
10. **OBPI-0.25.0-10:** Error hierarchy comparison and decision for
    `core/errors.py`
11. **OBPI-0.25.0-11:** Hook dispatch comparison and decision for
    `core/hooks.py`
12. **OBPI-0.25.0-12:** Admission-control comparison and decision for
    `core/admission.py`
13. **OBPI-0.25.0-13:** QC interface comparison and decision for `core/qc.py`
14. **OBPI-0.25.0-14:** Cross-platform OS utility comparison and decision for
    `common/os.py`
15. **OBPI-0.25.0-15:** Manifest loading/validation comparison and decision for
    `common/manifests.py`
16. **OBPI-0.25.0-16:** Configuration-helper comparison and decision for
    `common/config.py`
17. **OBPI-0.25.0-17:** Console abstraction comparison and decision for
    `common/console.py`

Support obligations for the checklist above:

- Parent ADR is Heavy because the program explicitly permits absorption into
  shared runtime and operator-facing surfaces
- Each numbered checklist item maps 1:1 to one brief and one module-comparison
  record
- `Absorb` outcomes require tests and, when operator-visible behavior changes,
  Gate 4 behavioral proof
- `Confirm` and `Exclude` outcomes still require comparison-based rationale
  grounded in both codebases

## Intent

gzkit must own all reusable core infrastructure patterns. airlineops's `core/` and `common/` packages contain battle-tested implementations of attestation, progress tracking, cryptographic signing, world-state hashing, registry patterns, error hierarchies, admission control, cross-platform file operations, and console output — none of which are airline-specific. This ADR governs the item-by-item evaluation and absorption of these 17 modules into gzkit, ensuring the subtraction test holds: after absorption, the only thing left in airlineops that isn't from gzkit is pure airline domain code.

## Decision

- Each of the 17 airlineops core/common modules gets individual OBPI examination
- For each module: read both implementations, compare maturity/completeness/robustness, document decision
- Three possible outcomes per module: **Absorb** (airlineops is better), **Confirm** (gzkit is sufficient), **Exclude** (domain-specific, does not belong in gzkit)
- Absorbed modules must follow gzkit conventions: Pydantic BaseModel, pathlib.Path, UTF-8 encoding, no bare except

### Alternatives Considered

| Alternative | Why rejected |
|-------------|-------------|
| **Single mega-OBPI for all 17 modules** | Too opaque. A monolithic absorption effort would hide per-module rationale, make partial progress hard to review, and break the subtraction-test audit trail. |
| **Group modules into a few broad domains instead of per-module decisions** | Better than one mega-OBPI, but still too coarse. Stronger modules would mask weaker ones, and reviewers could not see exactly which reusable patterns did or did not move upstream. |
| **Only absorb modules missing from gzkit and skip side-by-side comparisons where gzkit already has an implementation** | This would bias the program toward gzkit-by-default and violate the ADR's own critical constraint that airlineops wins where it is more battle-tested. |
| **Use file size or rough surface similarity as the sufficiency test** | Length is not proof of maturity, edge-case handling, or better abstractions. The anti-pattern here is deciding without reading both implementations completely. |

### Checklist Item Necessity Table

| # | OBPI | If removed, what specific capability is lost? |
|---|------|----------------------------------------------|
| 1 | Attestation | No explicit decision on whether gzkit is missing reusable attestation infrastructure. |
| 2 | Progress | No grounded decision on whether gzkit needs a unified progress facade. |
| 3 | Signature | No decision on cryptographic hashing/fingerprinting absorption, leaving a likely generic primitive stranded. |
| 4 | World state | No decision on immutable snapshot/state identity patterns. |
| 5 | Dataset version | No decision on whether airlineops version-management logic is reusable or airline-specific. |
| 6 | Registry | No explicit proof that gzkit's registry truly subsumes airlineops's pattern. |
| 7 | Types | No decision on whether shared type definitions belong upstream. |
| 8 | Ledger | No explicit comparison proving gzkit's ledger already covers airlineops needs. |
| 9 | Schema | No grounded decision on whether airlineops has reusable schema utilities. |
| 10 | Errors | No decision on whether gzkit should standardize around a core exception hierarchy. |
| 11 | Hooks | No explicit comparison of hook-dispatch patterns across repositories. |
| 12 | Admission | No decision on whether admission-control belongs in gzkit as generic governance infrastructure. |
| 13 | QC | No proof that gzkit's quality surface subsumes airlineops's QC interface ideas. |
| 14 | OS | No decision on whether cross-platform OS helpers should move upstream. |
| 15 | Manifests | No grounded decision on manifest loading/validation reuse. |
| 16 | Config | No explicit comparison proving gzkit config helpers are sufficient. |
| 17 | Console | No decision on whether airlineops has cleaner console abstractions worth extracting into gzkit. |

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

**Dependency Graph:**

```text
All 17 OBPIs can begin as comparison units once the tidy-first cross-reference
matrix is assembled.

Comparison tranche (parallelizable):
  01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17

Implementation / proof consequence:
  Any OBPI with an Absorb decision
    └──► module adaptation + tests
           └──► docs / Gate 4 proof when operator-visible behavior changes
```

**Critical path:** assemble the cross-reference matrix, complete the slowest
comparison tranche, then execute any absorb-path implementation and behavioral
verification required by the winning modules.

**Verification spine:**

- All OBPIs: comparison rationale recorded in the corresponding brief
- Absorb outcomes: module/tests exist and `uv run gz test` passes
- Heavy surface changes: `uv run -m behave features/core_infrastructure.feature`
  or equivalent module-level BDD proof passes when operator-visible behavior
  changes
- Whole package: `uv run gz lint` and `uv run gz validate --documents`

**Lane definitions:**

- **Heavy** — All OBPIs inherit Heavy scrutiny because every comparison may end
  in absorption into shared runtime or operator-facing surfaces. Gate 4 is
  required when the chosen path changes operator-visible behavior; a brief may
  record BDD as `N/A` only when the final decision is `Confirm` or `Exclude`
  with no external-surface change.

---

## Non-Goals

- No wholesale rewrite of gzkit infrastructure beyond the specific module
  selected by an `Absorb` decision.
- No assumption that airlineops always wins because it is older or more
  battle-tested, or that gzkit always wins because it is larger.
- No absorption of airline-specific semantics that fail the subtraction test.
- No bundling of multiple module decisions into one undocumented rationale.
- No uncontrolled refactor of unrelated gzkit command flows while evaluating a
  module comparison.

### Scope Creep Guardrails

- If a comparison exposes a larger architectural redesign beyond the target
  module, split that redesign into a follow-on ADR or OBPI instead of hiding it
  inside the absorption brief.
- If a module is confirmed as sufficient in gzkit, do not invent refactor work
  just to force an absorption outcome.
- If a module changes operator-visible behavior, attach Gate 4 proof to that
  module's brief instead of deferring behavioral verification to a later
  catch-all step.

## Rationale

airlineops's `core/` and `common/` packages represent 1,700+ lines of battle-tested, domain-agnostic infrastructure. gzkit currently has partial equivalents for some of these (ledger, registry, quality, hooks, config) but lacks others entirely (attestation, signatures, world state, errors, admission control, cross-platform OS utilities). The subtraction test demands that all reusable patterns flow upstream to gzkit. This ADR ensures nothing is missed by examining every module individually.

## Consequences

- gzkit's infrastructure layer becomes comprehensive and self-sufficient
- airlineops can depend on gzkit for all core patterns, reducing its own infrastructure footprint
- New modules in gzkit may require new tests, documentation, and integration work
- Some airlineops modules may be excluded as domain-specific (e.g., dataset_version.py may have airline-specific semantics)

## Long-Term Validity Guards

- The 17-brief matrix is the audit trail for the subtraction test; future
  companion absorption work should not skip per-module rationale.
- Any future reusable airlineops core/common module added without an upstream
  gzkit decision record is doctrinal drift.
- `Confirm` decisions are not permanent exemptions; if airlineops later grows a
  materially stronger generic pattern, the comparison should be re-opened.
- `Absorb` decisions must leave behind tests and, where relevant, behavioral
  proof so the upstreamed pattern remains verifiable after airlineops evolves.

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/test_core_*.py` — unit tests for each absorbed module
- **BDD (Heavy):** `features/core_infrastructure.feature` or module-specific
  behavioral proof when absorbed infrastructure changes operator-visible
  behavior; otherwise record `N/A` with rationale in the brief decision
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
