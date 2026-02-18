---
name: gz-obpi-brief
description: Generate a new OBPI brief file with correct headers, constraints, and evidence stubs. GovZero v6 skill.
compatibility: GovZero v6 framework; enforces One Brief Per Item (OBPI) discipline
metadata:
  skill-version: "6.0.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero-spec-references: "docs/governance/GovZero/charter.md, docs/governance/GovZero/adr-obpi-ghi-audit-linkage.md"
  govzero-gates-covered: "Gate 1 (ADR intent), OBPI checklist mapping"
  govzero_layer: "Layer 3 — File Sync"
---

# gz-obpi-brief

## Purpose

Create a compliant OBPI markdown brief that maps to exactly one ADR checklist item.

---

## Trust Model

**Layer 3 — File Sync:** This tool creates files without verification.

- **Reads:** User input, templates, ADR checklist items
- **Writes:** OBPI brief markdown files
- **Does NOT verify:** Evidence, test coverage, or criteria
- **Does NOT touch:** Ledger files

---

## Inputs

- `adr_id`: ADR identifier (example: `ADR-0.0.7`).
- `obpi_id`: OBPI identifier (example: `OBPI-0.0.7-002`).
- `title`: Brief title (short, action-oriented).
- `adr_item`: ADR checklist area (example: "Tests").
- `checklist_item`: Single checklist item text.
- `lane`: `Lite` or `Heavy`.
- `allowed_paths`: List of repo paths allowed to change.
- `denied_paths`: List of repo paths disallowed to change.

## Outputs

- A new markdown file at:
  - `docs/design/briefs/{series}/{adr-slug}/{obpi_id}-{kebab-title}.md`

## Assets

- Template: `assets/OBPI_BRIEF-template.md`
- **Heavy Lane Plan Template: `assets/HEAVY_LANE_PLAN_TEMPLATE.md` (MANDATORY for Heavy lane)**

## Procedure

1. **If lane is Heavy:** Read `assets/HEAVY_LANE_PLAN_TEMPLATE.md` FIRST. This is mandatory.
1. Set the OBPI H1 to `{obpi_id}: {title}`.
1. Include the standard header fields:

   - **ADR Item**
   - **Source ADR**
   - **Checklist Item**
   - **Status**

1. Write these sections (in order):

   - Objective
   - Lane
   - Allowed Paths
   - Denied Paths
   - Requirements (FAIL-CLOSED)
   - Verification
   - Acceptance Criteria (This Brief)
   - Evidence

1. Ensure the brief is scoped to one checklist item.
1. Ensure Verification uses repo-standard commands (prefer `uv run ...`).

## Failure Modes

- Missing or ambiguous checklist mapping (more than one checklist item).
- Non-deterministic steps (network required without an explicit brief).
- Paths outside Allowed Paths are modified.
- **Heavy lane: Marking OBPI closed before human attestation.**
- **Heavy lane: Skipping Gate 5 attestation step.**
- **Heavy lane: Not presenting CLI commands for human verification.**

## Acceptance Rules

- Brief is short, deterministic, and auditable.
- No bare URLs.
- Markdown lint clean.
- **Heavy lane: Gate 5 attestation received and recorded before OBPI closure.**
- **Heavy lane: Human executed CLI commands and provided explicit attestation response.**
