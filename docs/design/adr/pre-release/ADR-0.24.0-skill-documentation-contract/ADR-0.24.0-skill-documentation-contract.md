---
id: ADR-0.24.0-skill-documentation-contract
status: Proposed
semver: 0.24.0
lane: lite
parent: PRD-GZKIT-1.0.0
date: 2026-03-21
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.24.0: Skill Documentation Contract

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Audit the three documentation layers — catalog what currently has manpages (`docs/user/commands/`), what has runbook entries (`docs/user/runbook.md`, `docs/governance/governance_runbook.md`), and what has docstrings. Identify the gap taxonomy.
  1. Audit existing command manpage structure — understand the template pattern, required sections, index format, and mkdocs.yml integration so the same rigor can extend to skills and other artifact types.
  1. Survey SKILL.md files — catalog all 52 skills, their categories, supporting files, and which (if any) already appear in runbooks or other operator documentation.

**Date Added:** 2026-03-21
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.24.0
**Area:** Documentation Architecture — Operator Documentation Taxonomy

## Agent Context Frame — MANDATORY

**Role:** Documentation architect establishing the rationale and contract for what operator artifacts require manpages, runbook entries, and docstrings — and then applying that contract to the undocumented skill surface.

**Purpose:** When this ADR is complete, gzkit has a clear documentation taxonomy that defines which artifacts need manpages, which need runbook entries, and which need docstrings — with rationale for each. The skill surface (52 SKILL.md files with zero operator documentation) is the immediate application, but the contract applies to all operator-facing artifact types.

**Goals:**

- Documentation taxonomy exists defining when manpages, runbooks, and docstrings are required
- Skill manpage template exists with required sections distinct from SKILL.md agent instructions
- `docs/user/skills/` directory exists with index page and mkdocs.yml integration
- Runbooks reference skills at their natural workflow insertion points
- A pilot batch of skill manpages validates the template against real skills

**Critical Constraint:** Implementations MUST distinguish between three documentation audiences: operators reading manpages (what/when/why), agents reading SKILL.md (how to execute), and developers reading docstrings (how code works). Each serves a different reader at a different time. Collapsing these into one artifact fails all three audiences.

**Anti-Pattern Warning:** A failed implementation looks like: a documentation taxonomy that exists on paper but doesn't explain *why* something needs a manpage vs. a runbook entry vs. a docstring. If the rationale is missing, future contributors will skip documentation or create it in the wrong layer. Equally bad: skill manpages that mechanically copy SKILL.md content without adding operator perspective (when to use, what to expect, how it relates to the workflow).

**Integration Points:**

- `docs/user/commands/` — existing command manpage pattern (the model to extend)
- `docs/user/commands/index.md` — existing index pattern to parallel
- `docs/user/runbook.md` — operator runbook where skill invocation points belong
- `docs/governance/governance_runbook.md` — governance runbook for governance skills
- `mkdocs.yml` — site navigation
- `.claude/skills/*/SKILL.md` — agent instruction files (source material, not to be copied verbatim)
- `.claude/rules/gate5-runbook-code-covenant.md` — existing doctrine requiring docs to track behavior

---

## Feature Checklist — Appraisal of Completeness

- Scope and surface
  - External contract unchanged (Lite lane) — documentation surface and taxonomy only; no CLI, API, or schema changes
- Tests
  - No code changes; validation via `mkdocs build --strict` and documentation coverage checks
- Docs
  - Documentation taxonomy with rationale for manpages, runbooks, and docstrings
  - New `docs/user/skills/` surface with index, template, and pilot manpages
  - Runbook entries for skill invocation workflows
- OBPI mapping
  - Each numbered checklist item maps to one brief

## Intent

Neither operators nor agents should have to guess at the intent of anything in gzkit. Everyone should have a solid idea of where to start, what to run, and how workflows are laid out and connect.

gzkit has three documentation layers — manpages, runbooks, and docstrings — but no explicit rationale for when each applies, and no linkage model connecting them. The three layers serve distinct purposes at distinct times:

- **Runbooks** capture end-to-end overarching workflows — the orchestration narrative that tells operators where to start, what sequence to follow, and how workflows connect to each other.
- **Manpages** provide exacting and extensive detail for individual CLI commands and skills — what the tool does, every flag and option, every supporting file, concrete examples.
- **Docstrings** in code link back to manpages and runbooks, reinforcing intent at the implementation level and pointing developers to the broader workflow context.

Today, CLI commands have manpages in `docs/user/commands/` but skills (52 SKILL.md files) have zero operator-facing documentation. Runbooks exist but don't systematically reference skills at their workflow insertion points. Docstrings exist ad hoc with no policy connecting them to the artifacts they document.

This ADR establishes the documentation taxonomy with rationale for each layer, defines the linkage model (docstrings → manpages → runbooks), and applies it immediately to the skill surface — creating `docs/user/skills/` with manpages, integrating skills into runbooks, and establishing the template that future skill authors must follow.

## Decision

- Establish a documentation taxonomy defining when manpages, runbook entries, and docstrings are required:
  - **Manpages:** Required for any operator-invocable artifact (CLI commands, skills). Answer: what, how, when.
  - **Runbook entries:** Required for any artifact that participates in a workflow. Answer: when to use, in what sequence, with what context.
  - **Docstrings:** Required for any artifact with backing code. Answer: how the implementation works, parameters, returns, side effects.
- Create `docs/user/skills/` as the canonical skill manpage surface, parallel to `docs/user/commands/`
- Define a skill manpage template with required sections (Purpose, When to Use, What to Expect, Supporting Files, Related Skills/Commands)
- Integrate skill documentation into mkdocs.yml navigation
- Add skill invocation entries to operator and governance runbooks at workflow insertion points
- Validate the contract with a pilot batch of skill manpages

## Interfaces

- **Documentation surface:** `docs/user/skills/{skill-name}.md` — one manpage per skill
- **Index:** `docs/user/skills/index.md` — categorized skill listing with one-line descriptions
- **Taxonomy:** Documentation taxonomy in governance docs defining manpage/runbook/docstring requirements
- **Navigation:** `mkdocs.yml` nav entry under User Guide section
- **Runbooks:** `docs/user/runbook.md` and `docs/governance/governance_runbook.md` — skill references at workflow insertion points

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.24.0-01 | Define documentation taxonomy — rationale for when manpages, runbook entries, and docstrings are required | Lite | Pending |
| 2 | OBPI-0.24.0-02 | Define skill manpage template with required sections distinct from SKILL.md | Lite | Pending |
| 3 | OBPI-0.24.0-03 | Create docs/user/skills/ surface with index page and mkdocs.yml integration | Lite | Pending |
| 4 | OBPI-0.24.0-04 | Add skill invocation entries to operator and governance runbooks | Lite | Pending |
| 5 | OBPI-0.24.0-05 | Write pilot batch of skill manpages to validate template | Lite | Pending |

**Briefs location:** `briefs/OBPI-0.24.0-*.md` (each brief is a **Level 2 WBS** element)

**WBS Completeness Rule:** Every row in this table MUST have a corresponding brief file.
The brief elaborates the "how" while this table defines the "what."

**Lane definitions:**

- **Lite** — Internal change only; Gates 1-2 required (ADR + TDD)
- **Heavy** — External contract changed; Gates 1-4 required (ADR + TDD + Docs + BDD)

---

## Rationale

The Gate 5 Runbook-Code Covenant (`.claude/rules/gate5-runbook-code-covenant.md`) establishes that documentation is a first-class deliverable. But it doesn't define *which documentation types* apply to *which artifact types*. This gap means:

- CLI commands have manpages by convention, but no doctrine says why or what sections are required
- Skills have SKILL.md files for agents but nothing for operators who invoke them directly
- Runbook entries exist for some workflows but not others, with no systematic coverage rule
- Docstrings exist where developers remembered to add them, with no policy connecting them to the artifacts they document

The documentation taxonomy closes this gap by making the rationale explicit:

1. **Manpages** exist because operators need to know what a tool does, when to use it, and what to expect — without reading source code or agent instructions.
2. **Runbook entries** exist because operators need workflow context — a tool in isolation isn't useful; operators need to know the sequence and the decision points.
3. **Docstrings** exist because developers maintaining code need to understand implementation decisions without re-reading the ADR or SKILL.md.

Skills are the most acute gap: 52 SKILL.md files exist but are agent-facing instructions. Operators who invoke skills directly (for determinism) have no documentation surface. This ADR fixes that immediately while establishing the taxonomy that prevents future gaps.

## Consequences

- `docs/user/skills/` becomes the canonical location for skill operator documentation
- SKILL.md remains the agent-facing instruction file; manpages are the operator-facing complement
- Documentation taxonomy becomes a governance artifact that defines documentation requirements per artifact type
- New skills created after this ADR must include a manpage (enforcement via coverage audit)
- Runbook coverage becomes a systematic requirement for workflow-participating artifacts
- The three-layer documentation model (manpage/runbook/docstring) extends to future artifact types beyond skills

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** Validation via `uv run mkdocs build --strict` — docs build with skill pages included
- **BDD (not required — Lite lane):** N/A
- **Docs:** `docs/user/skills/` surface with index, template, and pilot manpages; documentation taxonomy

---

## OBPI Acceptance Note (Human Acknowledgment)

- Each ADR checklist item maps to one brief (OBPI). Record a one-line acceptance note in the brief once gates are green.

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.24.0`
- **Related issues:** None

### Source & Contracts

- Documentation only — no source code changes

### Docs

- Taxonomy: documentation taxonomy governance artifact (location TBD during OBPI-01)
- Template: `docs/user/skills/_TEMPLATE.md`
- Index: `docs/user/skills/index.md`
- Pilot manpages: `docs/user/skills/gz-adr-map.md` and others
- Runbook updates: `docs/user/runbook.md`, `docs/governance/governance_runbook.md`
- Navigation: `mkdocs.yml`

### Summary Deltas (git window)

- Added: TBD
- Modified: TBD
- Removed: 0
- Notes: Documentation-only ADR; no code changes expected

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors (observable, reproducible) | Evidence (link/snippet/hash) | Notes |
|---|---|---|---|---|
| docs/user/skills/index.md | P | Skills index renders in mkdocs | `uv run mkdocs build --strict` | |
| docs/user/skills/_TEMPLATE.md | P | Template has all required sections | Manual review | |
| docs/user/runbook.md | M | Skill invocation points documented | Manual review | |
| mkdocs.yml | M | Skills nav entry present | `uv run mkdocs build --strict` | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes

If "Request Changes," required fixes:

1. …

1. …
