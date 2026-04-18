---
id: ADR-0.39.0-instruction-plugin-registry
status: Pending
semver: 0.39.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-21
dependencies:
  - ADR-0.36.0
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.39.0: Instruction Plugin Registry

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Audit gzkit's current instruction files (`.claude/rules/`, `.github/instructions/`) to catalog every canonical instruction and its scope.
  1. Identify which instructions are gzkit-canonical (shipped with the framework) vs. project-local (specific to gzkit-the-repo).
  1. Survey extension patterns in existing plugin/registry systems (Python entry_points, VS Code extensions, Terraform providers) for design inspiration.

**Date Added:** 2026-03-21
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.39.0
**Area:** Instruction Management — Greenfield Plugin Architecture

## Agent Context Frame — MANDATORY

**Role:** Greenfield architect — designing a new instruction plugin registry that balances framework strictness with project extensibility, and includes conformance checking to prevent contradictions.

**Purpose:** When this ADR is complete, gzkit has a working instruction plugin registry. The framework ships canonical instruction templates (cross-platform rules, testing policy, model conventions, CLI doctrine, etc.). Projects that use gzkit can extend or specialize these instructions through a registered plugin mechanism. `gz validate instructions` checks that local overrides conform to canonical rules and do not contradict them. No ad-hoc instruction overrides are permitted.

**Goals:**

- A schema-validated plugin manifest format for registering instruction extensions
- gzkit's current canonical instructions extracted into shippable template form
- A clear mechanism for projects to register domain-specific specializations
- `gz validate instructions` command that checks conformance and detects contradictions
- Migration tooling to move from flat-file instructions to the registry

**Critical Constraint:** This is net-new architecture. There is no prior art in either codebase. The design must balance strictness (gzkit's framework rules prevail on conflict) with extensibility (projects can specialize for their domain). The registry is not a simple file-copy mechanism — its value is in conformance checking and contradiction detection.

**Anti-Pattern Warning:** A failed implementation looks like: a registry that just copies template files into projects without any validation. The entire point is conformance checking — ensuring local instructions don't contradict canonical ones. Equally bad: a registry so strict that projects cannot specialize at all, making it useless for domain-specific needs.

**Integration Points:**

- `.claude/rules/` — current instruction file location
- `.github/instructions/` — mirror location for GitHub Copilot
- `src/gzkit/commands/validate.py` — `gz validate` command family
- `.gzkit/manifest.json` — project manifest (registry metadata)
- `config/` — configuration schemas

---

## Feature Checklist — Appraisal of Completeness

- Scope and surface
  - External contract will change (Heavy lane) — new `gz validate instructions` command, new manifest format, new plugin mechanism
- Tests
  - Registry schema validation tests, conformance check tests, contradiction detection tests; coverage >= 40%
- Docs
  - Plugin authoring guide, migration guide, command documentation
- OBPI mapping
  - Each numbered checklist item maps to one brief; 6 items = 6 briefs

## Intent

gzkit ships canonical instruction files that govern agent behavior: cross-platform rules, testing policy, Pydantic model conventions, CLI doctrine, and more. Currently, these are flat files in `.claude/rules/` with no mechanism for projects to extend, specialize, or override them in a controlled way. Projects either use gzkit's instructions as-is or make ad-hoc modifications that may contradict canonical rules. This ADR introduces a plugin registry that formalizes the extension mechanism: projects register instruction plugins through a manifest, gzkit validates conformance, and contradictions are detected before they cause governance drift.

## Decision

- Design a schema-validated plugin manifest format for instruction registration
- Extract gzkit's current canonical instructions into a shippable template set
- Implement a project extension mechanism with explicit registration
- Build `gz validate instructions` for conformance checking
- Implement contradiction detection between local and canonical instructions
- Provide migration tooling for existing flat-file instruction setups

## Interfaces

- **CLI (external contract):** `uv run gz validate instructions` — conformance validation command
- **Config keys consumed (read-only):** `.gzkit/manifest.json` — plugin registry entries
- **New config:** `instruction-plugins.json` or equivalent manifest section — plugin registration
- **Internal APIs:** `src/gzkit/instructions/` — registry, validation, and contradiction detection modules

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.39.0-01 | Registry schema design — define the plugin manifest format with JSON Schema validation | Heavy | Pending |
| 2 | OBPI-0.39.0-02 | Canonical template set — extract gzkit's current rules into shippable, versioned templates | Heavy | Pending |
| 3 | OBPI-0.39.0-03 | Project extension mechanism — how projects register domain-specific specializations | Heavy | Pending |
| 4 | OBPI-0.39.0-04 | Conformance validation — `gz validate instructions` checks overrides against canonical set | Heavy | Pending |
| 5 | OBPI-0.39.0-05 | Contradiction detection — detect when local instructions contradict canonical rules | Heavy | Pending |
| 6 | OBPI-0.39.0-06 | Migration tooling — migrate existing flat-file instruction setups to the registry | Heavy | Pending |

**Briefs location:** `obpis/OBPI-0.39.0-*.md`

**WBS Completeness Rule:** Every row in this table has a corresponding brief file.

**Lane definitions:**

- **Heavy** — All OBPIs are Heavy because this introduces new CLI commands, new config schemas, and new validation behavior

---

## Rationale

Instruction files are the mechanism through which gzkit governs agent behavior across projects. Without a registry, there is no way to distinguish canonical instructions from project-local modifications, no way to detect when a project's instructions contradict gzkit's rules, and no way to distribute instruction updates to downstream projects. The plugin registry solves all three problems: it establishes canonical vs. extension boundaries, provides conformance checking, and enables controlled distribution of instruction updates.

## Consequences

- Projects gain a formal mechanism to extend gzkit's instructions for domain-specific needs
- Contradiction detection prevents governance drift before it causes problems
- gzkit can ship instruction updates and projects can validate conformance
- The registry adds a new configuration surface (manifest) that projects must maintain
- Migration from flat files to the registry requires tooling and documentation
- The conformance checking algorithm must be carefully designed to avoid false positives

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/test_instruction_registry*.py` — schema, conformance, and contradiction tests
- **BDD (Heavy):** `features/instruction_registry.feature` — `gz validate instructions` end-to-end
- **Docs:** Plugin authoring guide, migration guide, command docs for `gz validate instructions`

---

## OBPI Acceptance Note (Human Acknowledgment)

- Each OBPI documents the design decision and implementation approach
- Human attestation required for all OBPIs (Heavy lane, parent ADR is Heavy)
- Attestation command: `uv run gz gates --adr ADR-0.39.0`

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.39.0`
- **Dependencies:** ADR-0.36.0

### Source & Contracts

- Greenfield — no prior art in either codebase
- Current instructions: `.claude/rules/`, `.github/instructions/`
- Target: `src/gzkit/instructions/` — new module package

### Tests

- Unit: `tests/test_instruction_registry*.py` (schema, conformance, contradiction)

### Docs

- Plugin authoring guide: `docs/user/instruction-plugins.md`
- Migration guide: `docs/user/instruction-migration.md`
- Command docs: `docs/user/commands/validate-instructions.md`
- Governance: this ADR

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|-------------------|----------|-------|
| `src/gzkit/instructions/` | M | Registry, validation, contradiction detection | Test output | |
| `tests/` | M | All registry tests pass | `uv run gz test` | |
| `data/schemas/` | M | Plugin manifest schema validates | Schema tests | |
| `docs/user/` | P | Plugin guide, migration guide, command docs | Doc review | |
| `obpis/` | P | All 6 OBPIs have designs documented | Brief review | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes
