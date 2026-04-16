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
**Area:** Core Infrastructure — Pattern Harvest (Tier 1 Foundation)

## Agent Context Frame — MANDATORY

**Role:** Pattern harvester — mining airlineops for battle-tested infrastructure patterns worth capturing into gzkit before gzkit replaces airlineops's infrastructure layer and becomes the spec-driven development toolkit for all projects.

**Purpose:** When this ADR is complete, gzkit owns all reusable core infrastructure patterns that currently reside in airlineops. Phase 1 examines `airlineops/src/airlineops/core/` and `common/` (17 modules). Phase 2 examines `airlineops/src/opsdev/` (16 modules) — the governance tooling layer that shares direct functional overlap with gzkit's command and library surface. For each module, gzkit either captured the airlineops pattern (because it earned its way into the platform), confirmed its own implementation already covers the need, or explicitly excluded the module as airline-domain-specific. airlineops development is not being progressed — gzkit is being maximized so it can replace the opsdev layer.

**Goals:**

- Every core/common module in airlineops is examined individually with a documented decision (Phase 1)
- Every opsdev module in airlineops is examined individually with a documented decision (Phase 2)
- gzkit's infrastructure layer is comprehensive enough to serve as the platform foundation for airlineops and future projects
- No reusable pattern remains unexamined in the airlineops codebase
- The subtraction test holds: `airlineops - gzkit = pure airline domain`

**Maturity Context:** This ADR was drafted when airlineops was clearly the more mature codebase. Since then, gzkit has been under exclusive active development and has progressed past airlineops in several areas. The relative maturity of each module is now genuinely case-by-case — some airlineops modules may still have battle-tested patterns worth capturing, while gzkit may already be ahead in others. Do not assume either codebase is uniformly stronger.

**Critical Constraint:** Implementations MUST compare both codebases honestly — if airlineops has a stronger pattern, capture it. If gzkit has already surpassed what airlineops offers, confirm and move on. Do not rubber-stamp either direction. The goal is MAX gzkit — the strongest possible toolkit — not gzkit-by-default and not airlineops-by-nostalgia.

**Anti-Pattern Warning:** A failed implementation looks like: rubber-stamping gzkit's existing code as "sufficient" without actually reading the airlineops version. Equally bad: blindly copying airlineops code into a gzkit module that has already evolved past it.

**Integration Points (Phase 1 — core/common):**

- `src/gzkit/config.py` — configuration loading (compare with `airlineops/config/`)
- `src/gzkit/registry.py` — content type registry (compare with `airlineops/core/registry.py`)
- `src/gzkit/ledger.py` — event ledger (compare with `airlineops/core/ledger.py`)
- `src/gzkit/quality.py` — quality checks (compare with `airlineops/core/qc.py`)
- `src/gzkit/hooks/core.py` — hook infrastructure (compare with `airlineops/core/hooks.py`)
- `src/gzkit/commands/common.py` — console/output patterns (compare with `airlineops/common/console.py`)

**Integration Points (Phase 2 — opsdev):**

- `src/gzkit/commands/adr_*.py`, `src/gzkit/adr_*.py` — ADR lifecycle (compare with `opsdev/lib/adr.py`, `opsdev/lib/adr_governance.py`)
- `src/gzkit/ledger.py`, `src/gzkit/ledger_*.py` — ledger schema and events (compare with `opsdev/lib/ledger_schema.py`)
- `src/gzkit/commands/obpi_*.py` — OBPI reconciliation (compare with `opsdev/lib/adr_recon.py`, `opsdev/lib/adr_audit_ledger.py`)
- `src/gzkit/commands/adr_map.py` — traceability (compare with `opsdev/lib/adr_traceability.py`)
- `src/gzkit/commands/cli_audit.py` — CLI audit (compare with `opsdev/lib/cli_audit.py`)
- `src/gzkit/commands/validate.py` — validation (compare with `opsdev/lib/docs.py`, `opsdev/lib/layout_verify.py`)
- `src/gzkit/arb/` — ARB receipts (compare with `opsdev/arb/`)
- `src/gzkit/drift.py` — drift detection (compare with `opsdev/lib/drift_detection.py`)
- `src/gzkit/hooks/` — policy guards (compare with `opsdev/lib/guards.py`)

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

### Phase 2 — opsdev Governance Tooling (Amendment 2026-04-09)

**Premise correction:** Phase 1 targeted `airlineops/core/` and `common/`, which are primarily airline-domain modules. The actual governance tooling that shares functional overlap with gzkit lives in `airlineops/src/opsdev/`. Phase 2 examines these modules — the ones most likely to yield Absorb or Confirm decisions rather than Exclude.

18. **OBPI-0.25.0-18:** ADR lifecycle comparison and decision for
    `opsdev/lib/adr.py` (1603 lines) — ADR index generation, status tables, title normalization
19. **OBPI-0.25.0-19:** ADR audit ledger comparison and decision for
    `opsdev/lib/adr_audit_ledger.py` (249 lines) — OBPI audit ledger consumption for Gate 5
20. **OBPI-0.25.0-20:** ADR governance comparison and decision for
    `opsdev/lib/adr_governance.py` (535 lines) — evidence audit and autolink management
21. **OBPI-0.25.0-21:** ADR reconciliation comparison and decision for
    `opsdev/lib/adr_recon.py` (607 lines) — OBPI table sync with ledger proof
22. **OBPI-0.25.0-22:** ADR traceability comparison and decision for
    `opsdev/lib/adr_traceability.py` (277 lines) — ADR-to-artifact relationship inference
23. **OBPI-0.25.0-23:** Artifact management comparison and decision for
    `opsdev/lib/artifacts.py` (232 lines) — artifact scanning and registry cleanup
24. **OBPI-0.25.0-24:** CLI audit comparison and decision for
    `opsdev/lib/cli_audit.py` (238 lines) — CLI structure and consistency audit
25. **OBPI-0.25.0-25:** Documentation validation comparison and decision for
    `opsdev/lib/docs.py` (218 lines) — documentation structure validation
26. **OBPI-0.25.0-26:** Drift detection comparison and decision for
    `opsdev/lib/drift_detection.py` (384 lines) — validation receipt temporal anchoring
27. **OBPI-0.25.0-27:** Policy guards comparison and decision for
    `opsdev/lib/guards.py` (145 lines) — policy enforcement scanning
28. **OBPI-0.25.0-28:** Layout verification comparison and decision for
    `opsdev/lib/layout_verify.py` (143 lines) — tree layout validation against config
29. **OBPI-0.25.0-29:** Ledger schema comparison and decision for
    `opsdev/lib/ledger_schema.py` (501 lines) — unified Pydantic schema for JSONL ledger entries
30. **OBPI-0.25.0-30:** References comparison and decision for
    `opsdev/lib/references.py` (797 lines) — bibliography index and citation generation
31. **OBPI-0.25.0-31:** Validation receipts comparison and decision for
    `opsdev/lib/validation_receipt.py` (274 lines) — validation anchoring schema
32. **OBPI-0.25.0-32:** Handoff validation comparison and decision for
    `opsdev/governance/handoff_validation.py` (312 lines) — session handoff governance
33. **OBPI-0.25.0-33:** ARB analysis comparison and decision for
    `opsdev/arb/` (603 lines total) — receipt advise, validate, and pattern extraction

Support obligations for the checklists above:

- Parent ADR is Heavy because the program explicitly permits absorption into
  shared runtime and operator-facing surfaces
- Each numbered checklist item maps 1:1 to one brief and one module-comparison
  record
- `Absorb` outcomes require tests and, when operator-visible behavior changes,
  Gate 4 behavioral proof
- `Confirm` and `Exclude` outcomes still require comparison-based rationale
  grounded in both codebases

## Intent

gzkit is the forward platform — it will serve as the governance and infrastructure foundation for airlineops and future projects. To fulfil that role, gzkit must own all reusable core infrastructure patterns. This ADR governs a one-time harvest across two phases:

**Phase 1** examines airlineops's `core/` and `common/` packages (17 modules) — attestation, progress tracking, cryptographic signing, world-state hashing, registry patterns, error hierarchies, admission control, cross-platform file operations, and console output.

**Phase 2** (amendment 2026-04-09) examines airlineops's `opsdev/` package (16 modules) — ADR lifecycle management, audit ledgers, reconciliation, traceability, drift detection, CLI audit, policy guards, ledger schemas, validation receipts, handoff governance, and ARB analysis. These are the governance tooling modules that share direct functional overlap with gzkit's command and library surface. Phase 1 established that most `core/` modules are airline-domain-specific; Phase 2 targets the modules most likely to yield meaningful Absorb or Confirm decisions.

After absorption, the subtraction test holds: the only thing left in airlineops that isn't from gzkit is pure airline domain code.

## Decision

- Each of the 33 airlineops modules (17 core/common + 16 opsdev) gets individual OBPI examination
- For each module: read both implementations, compare maturity/completeness/robustness, document decision
- Three possible outcomes per module: **Absorb** (airlineops has a pattern worth capturing), **Confirm** (gzkit already covers this), **Exclude** (domain-specific, does not belong in gzkit)
- Absorbed modules must follow gzkit conventions: Pydantic BaseModel, pathlib.Path, UTF-8 encoding, no bare except

### Alternatives Considered

| Alternative | Why rejected |
|-------------|-------------|
| **Single mega-OBPI for all 17 modules** | Too opaque. A monolithic absorption effort would hide per-module rationale, make partial progress hard to review, and break the subtraction-test audit trail. |
| **Group modules into a few broad domains instead of per-module decisions** | Better than one mega-OBPI, but still too coarse. Stronger modules would mask weaker ones, and reviewers could not see exactly which reusable patterns did or did not move upstream. |
| **Only absorb modules missing from gzkit and skip side-by-side comparisons where gzkit already has an implementation** | This would bias the program toward gzkit-by-default and miss battle-tested patterns worth capturing. The whole point of the harvest is honest comparison. |
| **Use file size or rough surface similarity as the sufficiency test** | Length is not proof of maturity, edge-case handling, or better abstractions. The anti-pattern here is deciding without reading both implementations completely. |

### Checklist Item Necessity Table

| # | OBPI | If removed, what specific capability is lost? |
|---|------|----------------------------------------------|
| 1 | Attestation | No explicit decision on whether gzkit is missing reusable attestation infrastructure. |
| 2 | Progress | No grounded decision on whether gzkit needs a unified progress facade. |
| 3 | Signature | No decision on cryptographic hashing/fingerprinting absorption, leaving a likely generic primitive uncaptured. |
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
| 18 | ADR lifecycle | No comparison of ADR index/status table generation between opsdev and gzkit. |
| 19 | ADR audit ledger | No comparison of OBPI audit ledger consumption patterns. |
| 20 | ADR governance | No comparison of evidence audit and autolink management approaches. |
| 21 | ADR reconciliation | No comparison of OBPI table reconciliation strategies. |
| 22 | ADR traceability | No comparison of ADR-to-artifact traceability inference. |
| 23 | Artifacts | No comparison of artifact scanning and registry management. |
| 24 | CLI audit | No comparison of CLI structure audit approaches. |
| 25 | Docs validation | No comparison of documentation validation strategies. |
| 26 | Drift detection | No comparison of validation receipt temporal anchoring. |
| 27 | Policy guards | No comparison of policy enforcement scanning approaches. |
| 28 | Layout verify | No comparison of tree layout validation against config. |
| 29 | Ledger schema | No comparison of unified JSONL ledger Pydantic schemas. |
| 30 | References | No decision on whether bibliography/citation management belongs in gzkit. |
| 31 | Validation receipts | No comparison of validation anchoring schema approaches. |
| 32 | Handoff validation | No comparison of session handoff governance validation. |
| 33 | ARB analysis | No comparison of ARB receipt analysis, validation, and pattern extraction. |

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

### Phase 2 — opsdev Governance Tooling (Amendment 2026-04-09)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 18 | OBPI-0.25.0-18 | Evaluate and absorb `opsdev/lib/adr.py` (1603 lines) — ADR index generation, status tables, title normalization | Heavy | Pending |
| 19 | OBPI-0.25.0-19 | Evaluate and absorb `opsdev/lib/adr_audit_ledger.py` (249 lines) — OBPI audit ledger consumption for Gate 5 | Heavy | Pending |
| 20 | OBPI-0.25.0-20 | Evaluate and absorb `opsdev/lib/adr_governance.py` (535 lines) — evidence audit and autolink management | Heavy | Pending |
| 21 | OBPI-0.25.0-21 | Evaluate and absorb `opsdev/lib/adr_recon.py` (607 lines) — OBPI table sync with ledger proof | Heavy | Pending |
| 22 | OBPI-0.25.0-22 | Evaluate and absorb `opsdev/lib/adr_traceability.py` (277 lines) — ADR-to-artifact relationship inference | Heavy | Pending |
| 23 | OBPI-0.25.0-23 | Evaluate and absorb `opsdev/lib/artifacts.py` (232 lines) — artifact scanning and registry cleanup | Heavy | Pending |
| 24 | OBPI-0.25.0-24 | Evaluate and absorb `opsdev/lib/cli_audit.py` (238 lines) — CLI structure and consistency audit | Heavy | Pending |
| 25 | OBPI-0.25.0-25 | Evaluate and absorb `opsdev/lib/docs.py` (218 lines) — documentation structure validation | Heavy | Pending |
| 26 | OBPI-0.25.0-26 | Evaluate and absorb `opsdev/lib/drift_detection.py` (384 lines) — validation receipt temporal anchoring | Heavy | Pending |
| 27 | OBPI-0.25.0-27 | Evaluate and absorb `opsdev/lib/guards.py` (145 lines) — policy enforcement scanning | Heavy | Pending |
| 28 | OBPI-0.25.0-28 | Evaluate and absorb `opsdev/lib/layout_verify.py` (143 lines) — tree layout validation against config | Heavy | Pending |
| 29 | OBPI-0.25.0-29 | Evaluate and absorb `opsdev/lib/ledger_schema.py` (501 lines) — unified Pydantic schema for JSONL ledger entries | Heavy | Pending |
| 30 | OBPI-0.25.0-30 | Evaluate and absorb `opsdev/lib/references.py` (797 lines) — bibliography index and citation generation | Heavy | Pending |
| 31 | OBPI-0.25.0-31 | Evaluate and absorb `opsdev/lib/validation_receipt.py` (274 lines) — validation anchoring schema | Heavy | Pending |
| 32 | OBPI-0.25.0-32 | Evaluate and absorb `opsdev/governance/handoff_validation.py` (312 lines) — session handoff governance | Heavy | Pending |
| 33 | OBPI-0.25.0-33 | Evaluate and absorb `opsdev/arb/` (603 lines total) — receipt advise, validate, and pattern extraction | Heavy | Pending |

**Briefs location:** `obpis/OBPI-0.25.0-*.md`

**WBS Completeness Rule:** Every row in this table has a corresponding brief file.

**Dependency Graph:**

```text
Phase 1 (core/common — parallelizable):
  01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17

Phase 2 (opsdev — parallelizable, independent of Phase 1):
  18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33

Implementation / proof consequence:
  Any OBPI with an Absorb decision
    └──► module adaptation + tests
           └──► docs / Gate 4 proof when operator-visible behavior changes
```

**Critical path:** complete the slowest comparison tranche in each phase,
then execute any absorb-path implementation and behavioral verification
required by the winning modules. Phase 2 can begin independently of Phase 1.

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
- No assumption that airlineops patterns are automatically better because
  they are older, or that gzkit is automatically sufficient because it is larger.
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

gzkit is becoming a spec-driven development toolkit that will replace most of opsdev in airlineops and serve as the foundation for future projects. This ADR addresses two layers of that transition: Phase 1 harvests from airlineops's `core/` and `common/` packages (1,700+ lines), and Phase 2 (amendment 2026-04-09) harvests from the `opsdev/` package (8,100+ lines of governance tooling). Phase 1 established that most `core/` modules are airline-domain-specific. Phase 2 targets the governance tooling that shares direct functional overlap with gzkit — ADR lifecycle, audit ledgers, reconciliation, traceability, drift detection, and ARB analysis. Full replacement of opsdev also requires governance authority migration (ADR-pool.airlineops-direct-governance-migration, not yet promoted) and additional work beyond this ADR's scope. This ADR ensures the infrastructure foundation is solid by examining every module individually.

## Consequences

- gzkit's infrastructure foundation becomes solid enough to begin replacing opsdev in airlineops — this ADR is a necessary predecessor, not the complete replacement
- Combined with governance migration (future ADR), most of airlineops's opsdev layer becomes redundant
- Future projects start on gzkit directly, inheriting the harvested patterns without repeating the exercise
- New modules in gzkit may require new tests, documentation, and integration work
- Some airlineops modules may be excluded as domain-specific (e.g., dataset_version.py may have airline-specific semantics)

## Long-Term Validity Guards

- The 33-brief matrix (17 core/common + 16 opsdev) is the audit trail for the
  subtraction test; future companion absorption work should not skip per-module
  rationale.
- Any future reusable airlineops module added without an upstream gzkit decision
  record is doctrinal drift.
- This is a one-time harvest. After absorption completes, innovation flows
  from gzkit outward — airlineops and future projects adopt gzkit patterns,
  not the reverse.
- `Absorb` decisions must leave behind tests and, where relevant, behavioral
  proof so the captured pattern remains verifiable as gzkit evolves.

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

- airlineops source (Phase 1): `../airlineops/src/airlineops/core/`, `../airlineops/src/airlineops/common/`
- airlineops source (Phase 2): `../airlineops/src/opsdev/lib/`, `../airlineops/src/opsdev/governance/`, `../airlineops/src/opsdev/arb/`
- gzkit target: `src/gzkit/` — new or enhanced modules

### Tests

- Unit: `tests/test_core_*.py` (per absorbed module)

### Docs

- Decision rationale: per OBPI brief in `obpis/`
- Governance: this ADR

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|-------------------|----------|-------|
| `src/gzkit/` | M | All absorbed modules integrated | Test output | |
| `tests/` | M | All absorbed modules tested | `uv run gz test` | |
| `obpis/` | P | All 33 OBPIs have decisions documented | Brief review | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.25.0 | Completed | Jeffry | 2026-04-15 | completed |
