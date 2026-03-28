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

### Cross-Reference Matrix Summary

| Opsdev module | Current gzkit equivalent | Comparison posture |
|---------------|--------------------------|--------------------|
| `adr.py` | `src/gzkit/cli.py` (partial) | Decide whether ADR lifecycle logic should stay inline or move into a dedicated library |
| `references.py` | None | Strong absorption candidate unless link semantics are ops-specific |
| `adr_recon.py` | None | Strong absorption candidate unless reconciliation logic is ops-specific |
| `adr_governance.py` | `src/gzkit/ledger.py` (partial) | Decide whether current policy enforcement is sufficient or should be split into a dedicated library |
| `ledger_schema.py` | `src/gzkit/ledger.py` (partial) | Decide whether schema/versioning should remain inline or become a first-class module |
| `drift_detection.py` | None | Strong absorption candidate unless drift semantics are ops-specific |
| `adr_traceability.py` | None | Strong absorption candidate unless traceability semantics are ops-specific |
| `validation_receipt.py` | `src/gzkit/validate.py` (partial) | Decide whether current validation output already satisfies receipt-level audit requirements |
| `adr_audit_ledger.py` | None | Strong absorption candidate unless ADR-specific audit semantics should remain implicit |
| `cli_audit.py` | `src/gzkit/cli.py` (partial) | Decide whether reusable CLI-audit logic should stay inline or move into a dedicated library |
| `artifacts.py` | `src/gzkit/sync.py` (partial) | Decide whether artifact discovery/integrity belongs in a library rather than sync-only code |
| `docs.py` | None | Strong absorption candidate unless documentation logic is too ops-specific for gzkit |

**Matrix summary:** 6 modules have partial gzkit equivalents (`adr`,
`adr_governance`, `ledger_schema`, `validation_receipt`, `cli_audit`,
`artifacts`) and 6 currently have no gzkit equivalent (`references`,
`adr_recon`, `drift_detection`, `adr_traceability`, `adr_audit_ledger`,
`docs`). The matrix therefore justifies the 12-way comparison split and the
focus on dedicated-library versus inline-runtime decisions.

**Date Added:** 2026-03-21
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.26.0
**Area:** Governance Libraries — Companion Absorption (Tier 2 Domain-Agnostic)

## Agent Context Frame — MANDATORY

**Role:** Absorption evaluator — comparing opsdev governance library primitives against gzkit equivalents, determining which implementation is superior, and absorbing the best into gzkit.

**Purpose:** When this ADR is complete, gzkit owns all reusable governance library primitives that currently reside in `../airlineops/src/opsdev/lib/`. For each of the 12 modules, gzkit either absorbed the opsdev implementation (because it was superior), confirmed its own implementation is sufficient (with documented rationale), or explicitly excluded the module as domain-specific.

**Goals:**

- Every lib/ module in opsdev is examined individually with a documented decision
- gzkit's governance layer is at least as capable as opsdev's for all generic governance patterns
- No reusable governance primitive remains stranded in the opsdev codebase
- The subtraction test holds: `opsdev - gzkit = pure ops domain`

**Critical Constraint:** Implementations MUST compare both codebases honestly — opsdev wins where it has significant depth that gzkit lacks. Do not assume gzkit's monolithic cli.py already covers what these focused modules provide. The opsdev lib/ contains ~6,200 lines of domain-agnostic governance primitives for ADR management, drift detection, traceability, and validation receipts. gzkit may have partial coverage in some areas but likely lacks the depth and focus of dedicated library modules.

**Anti-Pattern Warning:** A failed implementation looks like: assuming gzkit's cli.py (which mixes command handling with governance logic) already covers what opsdev's focused, single-responsibility library modules provide. Equally bad: blindly copying opsdev code without adapting it to gzkit's architecture (Pydantic models, pathlib paths, UTF-8 encoding).

**Integration Points:**

- `src/gzkit/cli.py` — CLI command handling (compare with `../airlineops/src/opsdev/lib/adr.py`, `../airlineops/src/opsdev/lib/cli_audit.py`)
- `src/gzkit/ledger.py` — event ledger (compare with `../airlineops/src/opsdev/lib/adr_governance.py`, `../airlineops/src/opsdev/lib/ledger_schema.py`)
- `src/gzkit/validate.py` — validation (compare with `../airlineops/src/opsdev/lib/validation_receipt.py`)
- `src/gzkit/sync.py` — artifact sync (compare with `../airlineops/src/opsdev/lib/artifacts.py`)

---

## Feature Checklist — Appraisal of Completeness

1. **OBPI-0.26.0-01:** ADR-management comparison and decision for `lib/adr.py`
2. **OBPI-0.26.0-02:** Reference-resolution comparison and decision for
   `lib/references.py`
3. **OBPI-0.26.0-03:** ADR-reconciliation comparison and decision for
   `lib/adr_recon.py`
4. **OBPI-0.26.0-04:** Governance-policy comparison and decision for
   `lib/adr_governance.py`
5. **OBPI-0.26.0-05:** Ledger-schema comparison and decision for
   `lib/ledger_schema.py`
6. **OBPI-0.26.0-06:** Drift-detection comparison and decision for
   `lib/drift_detection.py`
7. **OBPI-0.26.0-07:** ADR-traceability comparison and decision for
   `lib/adr_traceability.py`
8. **OBPI-0.26.0-08:** Validation-receipt comparison and decision for
   `lib/validation_receipt.py`
9. **OBPI-0.26.0-09:** ADR-audit-ledger comparison and decision for
   `lib/adr_audit_ledger.py`
10. **OBPI-0.26.0-10:** CLI-audit comparison and decision for `lib/cli_audit.py`
11. **OBPI-0.26.0-11:** Artifact-management comparison and decision for
    `lib/artifacts.py`
12. **OBPI-0.26.0-12:** Documentation-library comparison and decision for
    `lib/docs.py`

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

gzkit must own all reusable governance library primitives. opsdev's `lib/` package contains ~6,200 lines of domain-agnostic governance implementations covering ADR management (1,588 lines), cross-references and traceability (797 + 277 lines), reconciliation and drift detection (607 + 384 lines), governance policy enforcement (535 lines), ledger schemas (501 lines), validation receipts (274 lines), audit ledger management (249 lines), CLI audit infrastructure (238 lines), artifact management (232 lines), and documentation generation (218 lines). These are focused, single-responsibility library modules — not CLI commands. gzkit has partial coverage for some of these in its monolithic cli.py and ledger.py, but lacks dedicated modules for references, reconciliation, drift detection, traceability, audit ledger, and documentation generation. This ADR governs the item-by-item evaluation and absorption of these 12 modules into gzkit.

## Decision

- Each of the 12 opsdev lib/ modules gets individual OBPI examination
- For each module: read both implementations, compare maturity/completeness/robustness, document decision
- Three possible outcomes per module: **Absorb** (opsdev is better), **Confirm** (gzkit is sufficient), **Exclude** (domain-specific, does not belong in gzkit)
- Absorbed modules must follow gzkit conventions: Pydantic BaseModel, pathlib.Path, UTF-8 encoding, no bare except

### Alternatives Considered

| Alternative | Why rejected |
|-------------|-------------|
| **Single mega-OBPI for all 12 modules** | Too opaque. A monolithic governance-library absorption effort would hide per-module rationale, blur which primitives actually moved upstream, and make partial review or partial completion hard to audit. |
| **Group modules into a few broad domains instead of one module per brief** | Better than one mega-OBPI, but still too coarse. Stronger modules would mask weaker ones, and reviewers could not see exactly which generic governance primitives were accepted, rejected, or confirmed. |
| **Only absorb modules with no gzkit equivalent and skip side-by-side comparisons where gzkit already has partial coverage** | This would bias the program toward gzkit-by-default and violate the ADR's own critical constraint that opsdev wins where it has materially stronger governance depth. |
| **Use file size or broad surface similarity as the sufficiency test** | Length and naming are not proof of maturity, error handling, auditability, or better abstractions. The anti-pattern here is deciding without reading both implementations completely. |

### Checklist Item Necessity Table

| # | OBPI | If removed, what specific capability is lost? |
|---|------|----------------------------------------------|
| 1 | ADR management | No explicit decision on whether gzkit should keep lifecycle management interleaved in `cli.py` or upstream a stronger dedicated ADR-management library. |
| 2 | References | No grounded decision on whether gzkit needs reusable reference-resolution and link-management primitives. |
| 3 | ADR recon | No decision on whether gzkit is missing reconciliation logic that checks ADR metadata, briefs, ledger state, and filesystem state together. |
| 4 | ADR governance | No explicit comparison proving gzkit's current governance-policy enforcement is sufficient or showing why opsdev's dedicated enforcement layer should move upstream. |
| 5 | Ledger schema | No decision on whether gzkit should adopt a dedicated schema/versioning layer for ledger entries. |
| 6 | Drift detection | No grounded decision on governance-drift detection, leaving a likely generic integrity primitive stranded in opsdev. |
| 7 | ADR traceability | No explicit decision on whether gzkit should own reusable ADR-to-artifact traceability chains. |
| 8 | Validation receipt | No explicit comparison proving gzkit validation output already has the receipt structure and audit semantics opsdev provides. |
| 9 | ADR audit ledger | No decision on whether ADR-specific lifecycle audit semantics should remain implicit in the general ledger or become a dedicated upstream capability. |
| 10 | CLI audit | No grounded decision on whether gzkit's CLI audit surface already subsumes opsdev's reusable contract-verification primitives. |
| 11 | Artifacts | No explicit comparison proving gzkit's sync logic already covers artifact discovery, cataloging, and integrity verification. |
| 12 | Docs | No decision on whether governance-document generation and validation should remain ad hoc rather than becoming an explicit upstream library capability. |

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

**Briefs location:** `obpis/OBPI-0.26.0-*.md`

**WBS Completeness Rule:** Every row in this table has a corresponding brief file.

**Execution warning:** `OBPI-0.26.0-01`, `OBPI-0.26.0-02`, and
`OBPI-0.26.0-03` are decision units first, not guaranteed single execution
chunks. If comparison shows that `Absorb` requires substantial implementation
or broad refactoring, split the absorb path into follow-on execution
units/tasks before code changes rather than forcing one brief to carry the full
comparison-plus-implementation load.

**Dependency Graph:**

```text
All 12 OBPIs can begin as comparison units once the tidy-first cross-reference
matrix is assembled.

Comparison tranche (parallelizable):
  01 02 03 04 05 06 07 08 09 10 11 12

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
- Heavy surface changes: `uv run -m behave features/heavy_lane_gate4.feature`
  passes when absorbed governance-library work changes operator-visible CLI or
  generated-surface behavior; otherwise the brief must record `N/A` rationale
- Whole package: `uv run gz lint` and `uv run gz validate --documents`

**Lane definitions:**

- **Heavy** — All OBPIs inherit Heavy scrutiny because every comparison may end
  in absorption into shared runtime or operator-facing surfaces. Gate 4 is
  required when the chosen path changes operator-visible behavior; a brief may
  record BDD as `N/A` only when the final decision is `Confirm` or `Exclude`
  with no external-surface change.

---

## Non-Goals

- No wholesale rewrite of gzkit governance internals beyond the specific module
  selected by an `Absorb` decision.
- No assumption that opsdev always wins because it is older, or that gzkit
  always wins because it already has a command surface.
- No absorption of ops-specific semantics that fail the subtraction test.
- No bundling of multiple module decisions into one undocumented rationale.
- No uncontrolled refactor of unrelated command flows while evaluating one
  governance-library comparison.

### Scope Creep Guardrails

- If a comparison exposes a larger architectural redesign beyond the target
  module, split that redesign into a follow-on ADR or OBPI instead of hiding it
  inside the absorption brief.
- If a module is confirmed as sufficient in gzkit, do not invent refactor work
  just to force an absorption outcome.
- If a module changes operator-visible behavior, attach Gate 4 proof to that
  module's brief instead of deferring behavioral verification to a later
  catch-all step.
- If a no-equivalent module is excluded, the brief must name the exact
  ops-specific semantics that fail the subtraction test rather than relying on
  a generic "does not fit" assertion.

## Rationale

opsdev's `lib/` package represents ~6,200 lines of domain-agnostic governance primitives. gzkit currently has partial equivalents for some of these (ADR management in cli.py, governance enforcement in ledger.py, validation in validate.py, artifact sync in sync.py) but lacks dedicated modules for cross-references, reconciliation, drift detection, traceability, audit ledger, and documentation generation. The subtraction test demands that all reusable governance patterns flow upstream to gzkit. This ADR ensures nothing is missed by examining every module individually. Critically, opsdev's focused library modules (single-responsibility, well-bounded) likely surpass gzkit's monolithic approach where governance logic is interleaved with CLI command handling.

## Consequences

- gzkit's governance library layer becomes comprehensive and self-sufficient
- opsdev can depend on gzkit for all governance primitives, reducing its own library footprint
- New modules in gzkit may require new tests, documentation, and integration work
- gzkit gains dedicated governance library modules instead of mixing governance logic into CLI commands
- Some opsdev modules may have overlap requiring careful merge rather than wholesale absorption

## Long-Term Validity Guards

- The 12-brief matrix is the audit trail for the governance-library subtraction
  test; future companion absorption work should not skip per-module rationale.
- Any future reusable opsdev governance module added without an upstream gzkit
  decision record is doctrinal drift.
- `Confirm` decisions are not permanent exemptions; if opsdev later grows a
  materially stronger generic governance primitive, the comparison should be
  re-opened.
- `Absorb` decisions must leave behind tests and, where relevant, behavioral
  proof so the upstreamed capability remains verifiable after opsdev evolves.

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/test_lib_*.py` — unit tests for each absorbed module
- **BDD (Heavy):** `features/heavy_lane_gate4.feature` when absorbed
  governance-library work changes operator-visible CLI or generated-surface
  behavior; otherwise record `N/A` with rationale in the brief decision
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

- opsdev source: `../airlineops/src/opsdev/lib/`
- gzkit target: `src/gzkit/` — new or enhanced modules

### Tests

- Unit: `tests/test_lib_*.py` (per absorbed module)

### Docs

- Decision rationale: per OBPI brief in `obpis/`
- Governance: this ADR

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|-------------------|----------|-------|
| `src/gzkit/` | M | All absorbed modules integrated | Test output | |
| `tests/` | M | All absorbed modules tested | `uv run gz test` | |
| `obpis/` | P | All 12 OBPIs have decisions documented | Brief review | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes
