---
id: ADR-0.37.0-govzero-methodology-doc-absorption
status: Proposed
semver: 0.37.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-21
dependencies:
  - ADR-0.26.0
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.37.0: GovZero Methodology Documentation Absorption

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Audit gzkit's `docs/governance/GovZero/` directory to catalog all methodology documents, their content depth, and last-modified dates.
  1. Audit airlineops's `docs/governance/GovZero/` directory to catalog all methodology documents, their content depth, and last-modified dates.
  1. Create a cross-reference matrix mapping each document between the two repos, noting content divergence and which version appears more complete.

**Date Added:** 2026-03-21
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.37.0
**Area:** GovZero Methodology — Companion Absorption (Documentation Authority)

## Agent Context Frame — MANDATORY

**Role:** Absorption evaluator — comparing every GovZero methodology document between airlineops and gzkit, determining which version is more complete and authoritative, and absorbing superior content into gzkit.

**Purpose:** When this ADR is complete, gzkit's `docs/governance/GovZero/` directory is the authoritative source for all GovZero methodology documentation. Every document has been compared between the two repos, superior content has been absorbed, and gzkit-only documents have been verified as complete. The methodology documentation reflects the current state of GovZero governance, not a stale snapshot.

**Goals:**

- Every GovZero methodology document is compared between airlineops and gzkit with documented analysis
- Superior content from either repo is absorbed into gzkit (gzkit is the authority after this ADR)
- gzkit-only documents are verified as complete and current
- No methodology documentation remains more complete in airlineops than in gzkit
- The subtraction test holds: `airlineops GovZero/ - gzkit GovZero/ = nothing` (methodology lives in gzkit)

**Critical Constraint:** gzkit's GovZero docs may have diverged from airlineops's originals. Neither is automatically authoritative — compare content quality and completeness. airlineops may have updated documents that gzkit has not received, or gzkit may have evolved documents beyond the airlineops originals.

**Anti-Pattern Warning:** A failed implementation looks like: assuming gzkit's docs are always the latest version without comparing actual content. Equally bad: blindly overwriting gzkit docs with airlineops versions without checking whether gzkit has evolved them further.

**Integration Points:**

- `docs/governance/GovZero/` — gzkit's methodology documentation directory
- `docs/governance/GovZero/releases/` — release process documentation
- `docs/governance/GovZero/audits/` — governance audit documentation
- `mkdocs.yml` — navigation configuration for methodology docs

---

## Feature Checklist — Appraisal of Completeness

- Scope and surface
  - External contract may change (Heavy lane) — methodology documentation governs all governance behavior
- Tests
  - Documentation structure validation; mkdocs build passes
- Docs
  - Decision rationale documented per OBPI (absorb/confirm with content analysis)
- OBPI mapping
  - Each numbered checklist item maps to one brief; 23 items = 23 briefs

## Intent

gzkit must be the authoritative source for GovZero methodology documentation. Both airlineops and gzkit have `docs/governance/GovZero/` directories containing methodology documents (charter, lifecycle definitions, audit protocols, release processes, schema definitions, etc.). These documents have evolved independently since the initial fork. Some may have diverged significantly — airlineops may have added sections based on operational experience, while gzkit may have refined documents based on tooling evolution. This ADR governs the document-by-document comparison and absorption to ensure gzkit's methodology documentation is complete, current, and authoritative.

## Decision

- Each of the 23 methodology documents or document groups gets individual OBPI examination
- For each document: read both versions completely, compare content quality and completeness, document decision
- Three possible outcomes per document: **Absorb** (airlineops version is more complete), **Confirm** (gzkit version is sufficient or superior), **Merge** (both have unique valuable content that should be combined)
- For gzkit-only documents: verify completeness and currency
- Absorbed or merged content must be editorially consistent with gzkit's documentation style

## Interfaces

- **Documentation surface:** `docs/governance/GovZero/` — served via mkdocs
- **Config keys consumed (read-only):** `mkdocs.yml` — navigation structure
- **Governance pipeline:** Documents referenced by `gz audit`, `gz gates`, `gz closeout`

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.37.0-01 | Compare and absorb `charter.md` — GovZero charter and principles | Heavy | Pending |
| 2 | OBPI-0.37.0-02 | Compare and absorb `gzkit-structure.md` — project structure documentation | Heavy | Pending |
| 3 | OBPI-0.37.0-03 | Compare and absorb `governance-registry-design.md` — registry architecture | Heavy | Pending |
| 4 | OBPI-0.37.0-04 | Compare and absorb `gate5-architecture.md` — Gate 5 attestation architecture | Heavy | Pending |
| 5 | OBPI-0.37.0-05 | Compare and absorb `adr-lifecycle.md` — ADR lifecycle definitions | Heavy | Pending |
| 6 | OBPI-0.37.0-06 | Compare and absorb `adr-status.md` — ADR status definitions and transitions | Heavy | Pending |
| 7 | OBPI-0.37.0-07 | Compare and absorb `adr-obpi-ghi-audit-linkage.md` — governance artifact linkage | Heavy | Pending |
| 8 | OBPI-0.37.0-08 | Compare and absorb `ledger-schema.md` — ledger event schema | Heavy | Pending |
| 9 | OBPI-0.37.0-09 | Compare and absorb `audit-protocol.md` — audit execution protocol | Heavy | Pending |
| 10 | OBPI-0.37.0-10 | Compare and absorb `architectural-enforcement.md` — enforcement patterns | Heavy | Pending |
| 11 | OBPI-0.37.0-11 | Compare and absorb `handoff-validation.md` — session handoff validation | Heavy | Pending |
| 12 | OBPI-0.37.0-12 | Compare and absorb `session-handoff-obligations.md` — handoff obligations | Heavy | Pending |
| 13 | OBPI-0.37.0-13 | Compare and absorb `session-handoff-schema.md` — handoff schema definition | Heavy | Pending |
| 14 | OBPI-0.37.0-14 | Compare and absorb `layered-trust.md` — trust model documentation | Heavy | Pending |
| 15 | OBPI-0.37.0-15 | Compare and absorb `staleness-classification.md` — staleness definitions | Heavy | Pending |
| 16 | OBPI-0.37.0-16 | Compare and absorb `validation-receipts.md` — receipt schema and lifecycle | Heavy | Pending |
| 17 | OBPI-0.37.0-17 | Compare and absorb `agent-era-prompting-summary.md` — prompting methodology | Heavy | Pending |
| 18 | OBPI-0.37.0-18 | Compare and absorb `releases/major-release.md` — major release process | Heavy | Pending |
| 19 | OBPI-0.37.0-19 | Compare and absorb `releases/minor-release.md` — minor release process | Heavy | Pending |
| 20 | OBPI-0.37.0-20 | Compare and absorb `releases/patch-release.md` — patch release process | Heavy | Pending |
| 21 | OBPI-0.37.0-21 | Compare and absorb `audits/` — governance harmonization audits | Heavy | Pending |
| 22 | OBPI-0.37.0-22 | Compare and absorb `handoff-chaining.md` — handoff chain documentation | Heavy | Pending |
| 23 | OBPI-0.37.0-23 | Verify gzkit-only docs (`obpi-runtime-contract.md` + others) for completeness | Heavy | Pending |

**Briefs location:** `obpis/OBPI-0.37.0-*.md`

**WBS Completeness Rule:** Every row in this table has a corresponding brief file.

**Lane definitions:**

- **Heavy** — All OBPIs are Heavy because methodology documentation governs all governance behavior

---

## Rationale

GovZero methodology documentation is the foundation of gzkit's governance model. Both airlineops and gzkit maintain copies of these documents, but they have evolved independently. airlineops may have updated documents based on operational experience (e.g., audit protocol improvements discovered during real audits), while gzkit may have refined documents based on tooling evolution (e.g., new gate architectures). Without systematic comparison, stale or incomplete documentation in gzkit undermines the tooling it governs. This ADR ensures every methodology document is compared and the best content lives in gzkit.

## Consequences

- gzkit becomes the single authoritative source for all GovZero methodology documentation
- airlineops can reference gzkit's docs instead of maintaining its own copies
- Content divergence is resolved — no more wondering which repo has the latest version
- Some documents may require significant merging where both repos evolved the same document differently
- mkdocs navigation may need updates if new documents are added or restructured

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `uv run mkdocs build --strict` — documentation build validation
- **BDD (Heavy):** N/A — methodology docs are reference material, not executable surfaces
- **Docs:** Decision rationale documented per OBPI brief

---

## OBPI Acceptance Note (Human Acknowledgment)

- Each OBPI documents the comparison result and decision (Absorb/Confirm/Merge)
- Human attestation required for all OBPIs (Heavy lane, parent ADR is Heavy)
- Attestation command: `uv run gz gates --adr ADR-0.37.0`

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.37.0`
- **Related:** ADR-0.26.0 (documentation governance)

### Source & Contracts

- airlineops source: `../airlineops/docs/governance/GovZero/`
- gzkit target: `docs/governance/GovZero/` — reconciled methodology documents

### Tests

- Documentation build: `uv run mkdocs build --strict`

### Docs

- Decision rationale: per OBPI brief in `obpis/`
- Governance: this ADR

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|-------------------|----------|-------|
| `docs/governance/GovZero/` | M | All methodology docs reconciled | Content review | |
| `mkdocs.yml` | M | Navigation updated if needed | `uv run mkdocs build --strict` | |
| `obpis/` | P | All 23 OBPIs have decisions documented | Brief review | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes
