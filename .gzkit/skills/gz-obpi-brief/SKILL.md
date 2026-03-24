---
name: gz-obpi-brief
description: Generate a new OBPI brief file with correct headers, constraints, and evidence stubs. GovZero v6 skill.
category: obpi-pipeline
compatibility: GovZero v6 framework; enforces One Brief Per Item (OBPI) discipline
metadata:
  skill-version: "6.0.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero-spec-references: "docs/governance/GovZero/charter.md, docs/governance/GovZero/adr-obpi-ghi-audit-linkage.md"
  govzero-gates-covered: "Gate 1 (ADR intent), OBPI checklist mapping"
  govzero_layer: "Layer 3 - File Sync"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-18
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

1. **Scaffold from the canonical template first.** Run `gz specify` to generate the brief:

   ```bash
   uv run gz specify --name <kebab-name> --parent <ADR-X.Y.Z> --item <N> --lane <lite|heavy> --title "<title>"
   ```

   This creates the brief with all required sections from `src/gzkit/templates/obpi.md`. **NEVER hand-author a brief from scratch.** The scaffolded file is the starting point.

2. **If lane is Heavy:** Read `assets/HEAVY_LANE_PLAN_TEMPLATE.md` BEFORE authoring. This is mandatory.
3. **Author the scaffolded brief.** Replace all template placeholders with substantive content:

   - Objective — one-sentence concrete outcome
   - Lane — rationale for lane choice
   - Allowed Paths — explicit repo paths
   - Denied Paths — explicit exclusions
   - Requirements (FAIL-CLOSED) — numbered MUST/NEVER rules
   - Discovery Checklist — prerequisites to read before implementation
   - Quality Gates — which gates apply
   - Verification — concrete `uv run ...` commands
   - Acceptance Criteria — deterministic REQ IDs

4. **Validate structural conformance** after authoring:

   ```bash
   uv run gz obpi validate <path-to-brief>
   ```

   This checks required frontmatter fields, required section headings, and template scaffold markers. The brief MUST pass before implementation begins.

5. Ensure the brief is scoped to one checklist item.
6. Ensure Verification uses repo-standard commands (prefer `uv run ...`).

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
