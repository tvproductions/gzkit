---
id: OBPI-0.14.0-03-root-surface-slimming-and-workflow-relocation
parent: ADR-0.14.0
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.14.0-03-root-surface-slimming-and-workflow-relocation: Root Surface Slimming and Workflow Relocation

## ADR Item

- **Source ADR:** `docs\design\adr\pre-release\ADR-0.14.0-multi-agent-instruction-architecture-unification\ADR-0.14.0-multi-agent-instruction-architecture-unification.md`
- **Checklist Item:** #3 - "OBPI-0.14.0-03: Slim generated root control surfaces and move recurring workflows out of always-loaded root files into skills/playbooks."

**Status:** Draft

## Objective

Reduce root instruction surfaces to high-signal durable rules and relocate recurring
workflow guidance into skills/playbooks where it can be loaded on demand.

This OBPI addresses the current giant root-memory pattern where generated root files
inline deep workflow prose and large skill inventories that already exist as canonical
skills under `.gzkit/skills/`.

## Lane

**Heavy** - Changes root control-surface content seen by external agents and operators.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/templates/agents.md` - root shared surface slimming
- `src/gzkit/templates/claude.md` - root adapter slimming
- `src/gzkit/templates/copilot.md` - Copilot adapter slimming
- `.gzkit/skills/**` - receiving recurring workflow content where required
- `.claude/commands/**` and `.claude/agents/**` - thin wrappers or retirement candidates
- `tests/test_templates.py` - root-surface regression coverage
- `docs/user/commands/**` - operator docs for any moved workflow references

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- sync determinism and local-config policy changes belong to OBPI-05
- audit engine changes belong to OBPI-04
- new path-scope semantics belong to OBPI-02
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: Root instruction files MUST contain durable rules, not large catalogs of recurring workflows.
1. REQUIREMENT: Reusable chore/ritual behavior MUST live in skills or playbooks that can be invoked on demand.
1. NEVER: Hide critical governance invariants only inside a task-specific skill.
1. ALWAYS: Preserve discoverability by linking from root surfaces to canonical skill/playbook locations.
1. NEVER: Maintain the same recurring workflow as full prose in root files, Claude
   command docs, and skills at the same time without a declared canonical home.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs\design\adr\pre-release\ADR-0.14.0-multi-agent-instruction-architecture-unification\ADR-0.14.0-multi-agent-instruction-architecture-unification.md`
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required templates exist: `src/gzkit/templates/agents.md`, `src/gzkit/templates/claude.md`, `src/gzkit/templates/copilot.md`
- [ ] Required skills root exists: `.gzkit/skills/`

**Existing Code (understand current state):**

- [ ] Pattern to follow: existing `git-sync` skill and command docs
- [ ] Test patterns: `tests/test_templates.py`

## Target Change

- Remove repeated workflow bodies and oversized skill catalogs from generated root
  surfaces.
- Keep a concise discovery section that points to canonical skills, mirrors, and
  playbook locations.
- Convert `.claude/commands/**` and `.claude/agents/**` surfaces into thin wrappers or
  retire them when a canonical skill already exists.

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run -m unittest discover tests`
- [ ] Coverage maintained: `uv run coverage run -m unittest && uv run coverage report`

### Code Quality

- [ ] Lint clean: `uvx ruff check src tests`
- [ ] Format clean: `uvx ruff format --check .`
- [ ] Type check clean: `uvx ty check src`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uvx mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Human runs these at closeout. -->

```bash
# Gate 2: Tests
uv run -m unittest discover tests

# Specific verification for this OBPI
uv run -m unittest tests.test_templates
uv run gz agent sync control-surfaces --dry-run
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.14.0-03-01: Given generated root control surfaces, when the templates render, then recurring workflow prose is removed from always-loaded root files and replaced by concise references to skills/playbooks.
- [ ] REQ-0.14.0-03-02: Given existing recurring workflows, when gzkit syncs surfaces, then the authoritative workflow content remains accessible through canonical skills or thin wrappers.
- [ ] REQ-0.14.0-03-03: Given the new root surfaces, when they are audited for size and content, then they stay focused on durable repo rules rather than full catalogs and repetitive task guidance.
- [ ] REQ-0.14.0-03-04: Given overlapping wrappers such as `.claude/commands/commit.md` and `.claude/agents/git-sync-repo.md`, when the relocation completes, then the canonical workflow remains the skill definition and wrappers do not become divergent contracts.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:

## Value Narrative

Before this OBPI, root files carried too much procedural detail, increasing context
cost and drift risk. After this OBPI, root surfaces will stay small and durable while
skills become the one place recurring multi-step workflows actually live.

## Key Proof

Rendered root surfaces retain repo invariants and skill discovery, but no longer embed
the full skill catalog or duplicate chore instructions already available in canonical
skills.

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -

