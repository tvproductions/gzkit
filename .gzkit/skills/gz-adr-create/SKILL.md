---
name: gz-adr-create
description: Create and book a GovZero ADR with its OBPI briefs. Enforces minor-version odometer and five-gate compliance. Portable skill for GovZero-compliant repositories.
category: adr-lifecycle
compatibility: Requires GovZero v6 framework; provides governance rules internally for portable use across repositories
metadata:
  skill-version: "6.0.0"
  govzero-framework-version: "v6"
  version-consistency-rule: "Skill major version tracks GovZero major. Minor increments for governance rule changes. Patch increments for tooling/template improvements."
  govzero-compliance-areas: "charter (gates 1-5), lifecycle (state machine), linkage (ADR/OBPI/GHI), minor-release (odometer discipline)"
  govzero_layer: "Layer 3 - File Sync"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-18
---

# gz-adr-create (v6.0.0)

## Purpose

Create GovZero-compliant ADR files with proper SemVer versioning, OBPI briefs, and registry booking.

**This skill enforces GovZero v6 compliance rules internally and is portable to any GovZero-compliant repository.**

---

## Trust Model

**Layer 3 — File Sync:** This tool creates files without verification.

- **Reads:** User input, templates, existing ADR registry
- **Writes:** ADR files, OBPI brief files, registry entries
- **Does NOT verify:** Evidence, test coverage, or criteria
- **Does NOT touch:** Ledger files

---

## GovZero Compliance Rules (Embedded)

### Versioning (Minor Odometer)

**ADRs propel MINOR versions only (0.y.z where y increments for each ADR).**

- During 0.y.z: Each ADR increments minor (y) → 0.1.0, 0.2.0, 0.3.0
- Patch (z) is for corrections, not sub-minor work
- Format: `ADR-0.{minor}.{patch}` or `ADR-{major}.{minor}.{patch}`
- Agents work under ONE ADR at a time; cannot bump SemVer (human gate required)
- Post-1.0: ADRs still use minor increments for capability additions

### Lifecycle States (Canonical)

| State | Meaning |
|-------|---------|
| Pool | Planned, awaiting prioritization |
| Draft | Being authored, not ready for review |
| Proposed | Submitted for review |
| Accepted | Approved, implementation may begin |
| Completed | Implementation finished, Gate 5 attestation received |
| Superseded | Replaced by newer ADR |
| Abandoned | Work stopped, will not be completed |

**Deprecated terms:** "Deprecated", "Pending", "Retired" — use canonical states above.

### Five Gates

| Gate | Applies | Artifact |
|------|---------|----------|
| Gate 1 (ADR) | All | Intent document with problem/decision/consequences |
| Gate 2 (TDD) | All | Unit tests pass, coverage ≥40% |
| Gate 3 (Docs) | Heavy only | Markdown lint clean, mkdocs build passes |
| Gate 4 (BDD) | Heavy only | Behave scenarios pass (CLI/API/schema contracts) |
| Gate 5 (Attestation) | Heavy only | Human directly observes and attests |

**Lane doctrine:**

- Lite lane (default): Gates 1-2 only (internal changes)
- Heavy lane: Gates 1-5 (external contract changes: CLI, API, schema, errors)

### OBPI Discipline

**One Brief Per Item:** Each ADR checklist item maps to exactly one OBPI brief.

- Format: `OBPI-{version}-{nn}-{slug}.md`
- Briefs live in `obpis/` subfolder (canonical name; `briefs/` is legacy and MUST NOT be used)
- Each OBPI must reference parent ADR and specific checklist item
- OBPI frontmatter MUST use `parent:` (not `parent_adr:`) for the parent ADR field

### OBPI Co-Creation Rule (Mandatory)

**OBPIs are co-created with the ADR, not deferred.**

When creating an ADR:

1. Count the checklist items in the Feature Checklist
2. Create exactly that many OBPI brief files using `gz specify` (preferred) or manually in `obpis/`
3. Verify 1:1 mapping before marking ADR as Proposed

**Prohibited patterns:**

- ❌ ADR table showing "Pending" OBPIs with no actual brief files
- ❌ ADR marked Proposed/Accepted with missing briefs
- ❌ Creating briefs "later" as a separate task

**Rationale:** The WBS is a contract between intent and implementation.
Orphaned checklist items create scope ambiguity. Co-creation locks intent
with execution units at decision time.

**Canonical reference:** `docs/governance/GovZero/adr-lifecycle.md` § OBPI Completeness Requirement

### ADR-Contained Layout (Preferred)

```text
docs/design/adr/adr-X.Y.x/ADR-X.Y.Z-{slug}/
  ADR-X.Y.Z-{slug}.md
  ADR-CLOSEOUT-FORM.md            # optional
  obpis/
    OBPI-X.Y.Z-01-*.md
    OBPI-X.Y.Z-02-*.md
  audit/
    AUDIT-ADR-X.Y.Z-COMPLETED.md
  logs/
    design-outcomes.jsonl         # optional
```

---

## Versioning Covenant

This skill maintains explicit alignment between skill version and GovZero version:

**Format:** `{govzero_major}.{skill_minor}.{skill_patch}`

- **{govzero_major}**: Tracks GovZero major version (e.g., v6 → 6)
- **{skill_minor}**: Increments when GovZero governance rules change
- **{skill_patch}**: Increments for tooling/template improvements, no governance changes

**Examples:**

- `6.0.0` — Initial GovZero v6 implementation
- `6.1.0` — GovZero v6 governance rules updated (charter/lifecycle/gates)
- `6.0.1` — Template or procedure fix, no governance change
- `7.0.0` — GovZero v7 released; major rewrite

**Consistency rule:** The skill version's major component MUST always match the GovZero version it enforces.

---

## Inputs

- `adr_id`: Example `ADR-0.0.7`.
- `title`: Example `agent-skills-foundation`.
- `series`: Example `adr-0.0.x`.
- `brief_count`: Number of OBPI briefs to create (if requested).

## Assets

- **ADR Template:** `assets/ADR_TEMPLATE_SEMVER.md` (co-located with this skill)
- **OBPI Brief Template:** `src/gzkit/templates/obpi.md` (canonical; `.gzkit/skills/gz-obpi-specify/assets/OBPI_BRIEF-template.md` is the authoring guide)
- **Closeout Form:** Use pattern from existing ADR closeout forms

## Outputs

- ADR markdown file under `docs/design/adr/{series}/ADR-{id}-{slug}/`.
- ADR closeout form: `ADR-CLOSEOUT-FORM.md` in the same folder.
- OBPIs folder: `docs/design/adr/{series}/ADR-{id}-{slug}/obpis/` (canonical).
- Updated registries:
  - `docs/design/adr/adr_index.md`
  - `docs/design/adr/adr_status.md`
  - `docs/governance/GovZero/adr-status.md` (governance copy)
- OBPI briefs under the `obpis/` folder (when requested).

## Procedure

### Step 0: Interview (MANDATORY — NON-NEGOTIABLE)

**No ADR may be authored without first completing a structured interview.**

Run the governance interview before any template work, file creation, or registry updates:

```bash
uv run gz interview adr
```

This command runs a structured Q&A session that captures:

- Problem statement and motivation
- Decision drivers and constraints
- Considered alternatives
- Consequences and trade-offs
- Scope and lane determination

**The interview output is the primary input for populating the ADR template.** Do not
skip this step. Do not substitute freeform conversation for the interview. Do not
create ADR files before the interview is complete.

**Why this is non-negotiable:** Uninterviewed ADRs produce vague intent documents
that drift during implementation. The interview forces structured articulation of
the decision before any artifacts exist, preventing scope ambiguity at the source.

**Prohibited patterns:**

- Creating ADR files first, then "backfilling" interview answers
- Substituting chat conversation for the structured interview
- Skipping the interview because "the intent is already clear"
- Running the interview after OBPI co-creation

---

1. **Read the canonical template** at `assets/ADR_TEMPLATE_SEMVER.md` (co-located with this skill).
2. **Verify GovZero compliance:** ADR ID follows 0.y.z format; status uses canonical lifecycle states.
3. Create the ADR folder: `docs/design/adr/{series}/ADR-{id}-{slug}/`.
4. Create the ADR markdown file using the template structure (all sections required).
5. Create the OBPIs subfolder: `obpis/`.
6. Create `ADR-CLOSEOUT-FORM.md` following existing closeout form patterns.
7. Add the ADR entry to `docs/design/adr/adr_index.md`.
8. Add/refresh the ADR row in `docs/design/adr/adr_status.md`.
9. Add/refresh the ADR row in `docs/governance/GovZero/adr-status.md`.
10. **OBPI Co-Creation (Mandatory):** Create one OBPI brief per checklist item.
    - Count checklist items in Feature Checklist
    - **Preferred:** Run `uv run gz specify <slug> --parent ADR-X.Y.Z --item N --author` for each item
    - After generation, author each brief semantically from the ADR before treating the package as ready
    - **Alternative:** Create files manually in `obpis/` with YAML frontmatter (`id:`, `parent:`, `item:`, `lane:`, `status:`)
    - **Then register:** Run `uv run gz register-adrs ADR-X.Y.Z --all` to ensure `obpi_created` ledger events
    - Verify: `ls obpis/ | wc -l` matches checklist item count
    - Validate authored readiness: `uv run gz obpi validate --adr ADR-X.Y.Z --authored`
    - This is NOT optional — briefs are co-created with the ADR, never deferred
11. **Post-Authoring QC (Mandatory before proposal/defense):**
    Invoke `gz-adr-evaluate ADR-X.Y.Z` to run the ADR and its OBPIs through the
    evaluation framework.
    - Score the ADR on all 8 dimensions
    - Score each OBPI on all 5 dimensions
    - Any ADR dimension scoring 1 or any OBPI dimension scoring 1 must be revised
      before proceeding
    - Optionally use `gz-adr-evaluate ADR-X.Y.Z --red-team` for adversarial review
    - Record the output as `EVALUATION_SCORECARD.md` in the ADR directory
12. Validate:

```bash
uv run -m unittest -q
uv run mkdocs build --strict
```

## Template Sections (Required)

The ADR template includes these sections that must be populated:

- Tidy First Plan
- Feature Checklist — Appraisal of Completeness
- Intent
- Decision
- Interfaces
- Rationale
- Consequences
- Evidence (Four Gates)
- OBPI Acceptance Note
- Evidence Ledger (with subsections)
- Completion Checklist — Post-Ship Tidy
- OBPI Briefs table

## Failure Modes

- ADR created without using the canonical template.
- ADR references files that don't exist.
- Registries drift (ADR exists but isn't indexed or has conflicting status).
- Governance copy not updated (out of sync with main status).

## Acceptance Rules

- ADR uses the canonical template structure.
- No duplicate ADR IDs.
- Registries and ADR content agree on status and series.
- All three registry files are in sync.
- Markdown lint stays clean for `docs/`.

## Related Skills

- `gz-adr-evaluate`: Post-authoring QC evaluation before proposal/defense
- `gz-obpi-specify`: Create and author OBPI briefs from ADR decomposition
- `gz-adr-closeout-ceremony`: Execute closeout ceremony
- `gz-adr-audit`: Verify ADR evidence (includes evidence checks and coverage discovery)
- `gz-adr-sync`: Sync ADR index/status from ADR files (includes registration)
