---
id: ADR-0.38.0-templates-scaffolds-agent-contract-absorption
status: Proposed
semver: 0.38.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-21
dependencies:
  - ADR-0.36.0
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.38.0: Templates, Scaffolds and Agent Contract Absorption

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Catalog all template files in both gzkit and airlineops (ADR templates, OBPI templates, closeout forms, audit templates, PRD templates, constitution templates, AGENTS.md, skill templates).
  1. Catalog the generic (non-domain-specific) sections of `copilot-instructions.md` and `AGENTS.md` in both repos.
  1. Create a cross-reference matrix mapping each template pair for side-by-side comparison.

**Date Added:** 2026-03-21
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.38.0
**Area:** Templates & Agent Contracts — Companion Absorption (Tier 3 Governance Surfaces)

## Agent Context Frame — MANDATORY

**Role:** Template quality evaluator — comparing template pairs between airlineops and gzkit for completeness, section coverage, guidance quality, and structural consistency.

**Purpose:** When this ADR is complete, every governance template used in both repos has been compared pair-by-pair. For each pair, the superior version is identified and absorbed into gzkit as the canonical template. The generic sections of agent contracts (copilot-instructions.md, AGENTS.md) are also compared and the best guidance absorbed. Additionally, the structural enforcement modules (guards.py, layout_verify.py) are compared to ensure gzkit's enforcement is at least as strong as airlineops's.

**Goals:**

- Every template type used in both repos is compared with a documented decision
- gzkit owns the canonical version of every governance template
- Template sections, guidance quality, and completeness are evaluated — not just file existence
- Agent contract generic sections are compared and the best guidance absorbed
- Structural enforcement code is compared for completeness

**Critical Constraint:** Templates shape every artifact created in the system. Template quality directly impacts governance artifact quality. Compare carefully. Two templates that produce the same file type may differ significantly in the sections they require, the guidance they provide, and the quality they enforce.

**Anti-Pattern Warning:** A failed implementation looks like: assuming templates are equivalent because they produce the same file types. The actual content, sections, and guidance within templates may differ significantly. Equally bad: comparing only file names and line counts without reading the actual template content.

**Integration Points:**

- `.gzkit/templates/` — gzkit template storage
- `AGENTS.md` — agent contract (generic sections)
- `copilot-instructions.md` — copilot instructions (generic sections)
- Skill templates — `.claude/skills/` or `.github/skills/`
- `guards.py` / `layout_verify.py` — structural enforcement modules

---

## Feature Checklist — Appraisal of Completeness

- Scope and surface
  - External contract may change (Heavy lane) — template improvements affect every future artifact created in the system
- Tests
  - Template validation tests; coverage >= 40%
- Docs
  - Comparison rationale documented per OBPI
- OBPI mapping
  - Each numbered checklist item maps to one brief; 10 items = 10 briefs

## Intent

Templates and scaffolds are the DNA of governance artifacts. Every ADR, OBPI, closeout form, audit, PRD, and constitution created in gzkit or airlineops begins as a template instantiation. If gzkit's templates are weaker than airlineops's, then every artifact gzkit produces is weaker. This ADR governs the pair-by-pair comparison of every template type, plus the generic sections of agent contracts (copilot-instructions.md, AGENTS.md) and the structural enforcement code (guards.py, layout_verify.py). The goal is to ensure gzkit owns the best version of every template.

## Decision

- Each of the 10 template/contract pairs gets individual OBPI examination
- For each pair: read both implementations, compare sections, guidance quality, completeness, and structural enforcement
- Three possible outcomes per pair: **Absorb** (airlineops template is better), **Confirm** (gzkit template is sufficient), **Merge** (both have strengths, combine into a superior version)
- Absorbed templates must follow gzkit conventions

## Interfaces

- **CLI (external contract):** `uv run gz scaffold {type}` — template instantiation commands
- **Config keys consumed (read-only):** `.gzkit/manifest.json` — template paths, scaffold configuration
- **Internal APIs:** Template rendering and validation in `src/gzkit/`

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.38.0-01 | Compare ADR templates between airlineops and gzkit — sections, guidance, frontmatter | Heavy | Pending |
| 2 | OBPI-0.38.0-02 | Compare OBPI brief templates — objective, requirements, quality gates sections | Heavy | Pending |
| 3 | OBPI-0.38.0-03 | Compare closeout form templates — checklist items, evidence paths, attestation sections | Heavy | Pending |
| 4 | OBPI-0.38.0-04 | Compare audit templates — audit sequence, evidence gathering, receipt emission | Heavy | Pending |
| 5 | OBPI-0.38.0-05 | Compare PRD templates — structure, scope definition, deliverable enumeration | Heavy | Pending |
| 6 | OBPI-0.38.0-06 | Compare constitution templates — governance principles, rule structure, enforcement | Heavy | Pending |
| 7 | OBPI-0.38.0-07 | Compare AGENTS.md templates/contracts — generic governance sections, agent role definitions | Heavy | Pending |
| 8 | OBPI-0.38.0-08 | Compare skill templates — skill definition format, metadata, invocation contracts | Heavy | Pending |
| 9 | OBPI-0.38.0-09 | Compare copilot-instructions.md generic sections — non-domain-specific guidance and rules | Heavy | Pending |
| 10 | OBPI-0.38.0-10 | Compare guards.py / layout_verify.py — structural enforcement, validation rules, layout checks | Heavy | Pending |

**Briefs location:** `obpis/OBPI-0.38.0-*.md`

**WBS Completeness Rule:** Every row in this table has a corresponding brief file.

**Lane definitions:**

- **Heavy** — All OBPIs are Heavy because template changes affect every future artifact's quality and structure

---

## Rationale

Templates are the most leveraged artifacts in a governance system. A single improvement to an ADR template improves every future ADR. A missing section in an OBPI template means every future OBPI lacks that section. airlineops and gzkit have evolved their templates independently, and each may have developed strengths the other lacks. This ADR ensures the best of both ends up in gzkit as the canonical template set. The agent contract comparison (AGENTS.md, copilot-instructions.md) ensures gzkit's agent guidance is comprehensive. The guards/layout comparison ensures structural enforcement is robust.

## Consequences

- gzkit owns the canonical, highest-quality version of every governance template
- Future artifacts created from these templates will be more complete and consistent
- airlineops can adopt gzkit's templates, reducing template drift
- Template changes require careful migration of existing artifacts (not in scope for this ADR)
- Agent contract improvements may change agent behavior for the better

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/test_templates*.py` — template validation tests
- **BDD (Heavy):** `features/templates.feature` — if scaffold CLI surfaces change
- **Docs:** Comparison rationale documented per OBPI brief

---

## OBPI Acceptance Note (Human Acknowledgment)

- Each OBPI documents the comparison result and decision (Absorb/Confirm/Merge)
- Human attestation required for all OBPIs (Heavy lane, parent ADR is Heavy)
- Attestation command: `uv run gz gates --adr ADR-0.38.0`

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.38.0`
- **Dependencies:** ADR-0.36.0

### Source & Contracts

- airlineops source: template files, `AGENTS.md`, `copilot-instructions.md`, `guards.py`, `layout_verify.py`
- gzkit target: `.gzkit/templates/`, `AGENTS.md`, agent contract surfaces

### Tests

- Unit: `tests/test_templates*.py` (template validation)

### Docs

- Decision rationale: per OBPI brief in `obpis/`
- Governance: this ADR

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|-------------------|----------|-------|
| `.gzkit/templates/` | M | All templates reflect best-of-both comparison | Brief review | |
| `tests/` | M | Template validation tests pass | `uv run gz test` | |
| `obpis/` | P | All 10 OBPIs have decisions documented | Brief review | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes
