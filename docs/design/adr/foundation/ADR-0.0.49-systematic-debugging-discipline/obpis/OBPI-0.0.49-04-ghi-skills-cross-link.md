---
id: OBPI-0.0.49-04-ghi-skills-cross-link
parent: ADR-0.0.49-systematic-debugging-discipline
item: 4
lane: Heavy
status: Draft
allowlist:
- .gzkit/skills/ghi-author/SKILL.md
- .gzkit/skills/ghi-close/SKILL.md
- docs/design/adr/foundation/ADR-0.0.49-systematic-debugging-discipline/**
- src/gzkit/skills/ghi-author/SKILL.md
- src/gzkit/skills/ghi-close/SKILL.md
- .claude/skills/ghi-author/SKILL.md
- .claude/skills/ghi-close/SKILL.md
- .github/skills/ghi-author/SKILL.md
- .github/skills/ghi-close/SKILL.md
- .gzkit/rules/skill-surface-sync.md
reqs:
- REQ-0.0.49-04-01
- REQ-0.0.49-04-02
- REQ-0.0.49-04-03
- REQ-0.0.49-04-04
- REQ-0.0.49-04-05
verification:
- uv run gz agent sync control-surfaces
- uv run gz validate --documents
- uv run gz arb ruff
- uv run gz arb typecheck
- uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
---

# OBPI-0.0.49-04-ghi-skills-cross-link: Cross-Link GHI Skills to Systematic Debugging

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.49-systematic-debugging-discipline/ADR-0.0.49-systematic-debugging-discipline.md`
- **Checklist Item:** #4 — "Cross-link GHI skills to systematic debugging: edit .gzkit/skills/ghi-author/SKILL.md and .gzkit/skills/ghi-close/SKILL.md to add a Systematic Debugging coupling subsection naming three coupling points (Phase 1 evidence + cross-brief defect → /ghi-author before commit; Phase 4 fix lands → /ghi-close with Phase-1 evidence trail in body; Phase 4.5 architecture pause → /ghi-author for architectural GHI labeled as foundation-ADR candidate)."

**Status:** Draft

## Objective

Triangulate `gz-systematic-debug` with the GHI lifecycle by adding a `## Systematic Debugging coupling` subsection to both `.gzkit/skills/ghi-author/SKILL.md` and `.gzkit/skills/ghi-close/SKILL.md`. The three coupling points operationalize the operator's framing: *"all of these will always require GHIs, so tying the GHI skills into this would triangulate well."* GHIs become the cross-session memory of debugging events, replacing in-context narrative recall (the named anti-pattern in `agent-failure-modes.md`) with ledger-witnessed trackable artifacts.

## Lane

**Heavy** — Modifies two canonical skill surfaces. Per `.gzkit/rules/skill-surface-sync.md`, skill body edits MUST bump `skill-version:` frontmatter; both skills receive minor-version bumps. Foundation-kind parent triggers universal brief-level Gate 5 attestation per ADR-0.0.36.

## Allowed Paths

- `.gzkit/skills/ghi-author/SKILL.md` — coupling subsection added; `skill-version:` minor-bumped
- `.gzkit/skills/ghi-close/SKILL.md` — coupling subsection added; `skill-version:` minor-bumped
- `docs/design/adr/foundation/ADR-0.0.49-systematic-debugging-discipline/**` — parent ADR package scope

**Implementation note:** wheel-shipping (`src/gzkit/skills/ghi-author/SKILL.md`, `src/gzkit/skills/ghi-close/SKILL.md`) and vendor-mirror (`.claude/skills/ghi-author/SKILL.md`, `.claude/skills/ghi-close/SKILL.md`, `.github/skills/ghi-author/SKILL.md`, `.github/skills/ghi-close/SKILL.md`) surfaces MUST be propagated only by `uv run gz agent sync control-surfaces` per `.gzkit/rules/skill-surface-sync.md`. The implementer never hand-edits any derived surface.

## Denied Paths

- `.gzkit/skills/gz-systematic-debug/**`, `.gzkit/personas/investigator.md` — OBPI-01 and OBPI-02 scopes
- `AGENTS.md`, `src/gzkit/templates/AGENTS.md` — OBPI-03 scope
- `.gzkit/rules/systematic-debugging.md`, `docs/governance/advisory-rules-audit.md` — OBPI-05 scope
- Any other skill under `.gzkit/skills/` — only `ghi-author` and `ghi-close` are in scope
- `src/gzkit/skills/**`, `.claude/skills/**`, `.github/skills/**` — derived surfaces; written ONLY by `gz agent sync control-surfaces`
- Any path not listed in Allowed Paths
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `.gzkit/skills/ghi-author/SKILL.md` gains a new top-level `## Systematic Debugging coupling` subsection. The subsection names two coupling points relevant to authoring:
   - **Phase 1 evidence + cross-brief defect → `/ghi-author` before commit**: when Phase-1 root-cause evidence shows the defect crosses brief boundaries (the direct-fix routing thresholds in AGENTS.md § Defect-fix routing fail), the agent files a GHI via `/ghi-author` before committing the fix, citing the `arb-step-root-cause-trace-*` receipt ID in the GHI body.
   - **Phase 4.5 architecture pause → `/ghi-author` for architectural GHI labeled as foundation-ADR candidate**: when the 3+-failed-fixes-architecture-pause rule fires (per AGENTS.md § DO IT RIGHT operative claim #11), the agent files an architectural GHI via `/ghi-author` with the three prior `arb-step-*` receipts cited, labeled as a foundation-ADR candidate.
2. REQUIREMENT: `.gzkit/skills/ghi-close/SKILL.md` gains a new top-level `## Systematic Debugging coupling` subsection. The subsection names one coupling point relevant to closing:
   - **Phase 4 fix lands → `/ghi-close` with Phase-1 evidence trail in body**: when a fix lands and a GHI exists for the defect, the closing comment MUST cite the Phase-1 `arb-step-root-cause-trace-*` receipt ID and the four-phase decision trail (Root Cause / Pattern / Hypothesis / Implementation summary).
3. REQUIREMENT: Both subsections cite `.gzkit/skills/gz-systematic-debug/SKILL.md` as the procedure of record and AGENTS.md § DO IT RIGHT operative claims #10 and #11 as the binding doctrine surface.
4. REQUIREMENT: `.gzkit/skills/ghi-author/SKILL.md` frontmatter `skill-version:` is minor-bumped (e.g. `2.1.0` → `2.2.0`) per `.gzkit/rules/skill-surface-sync.md` version-discipline table (governance rule or procedure change = minor bump).
5. REQUIREMENT: `.gzkit/skills/ghi-close/SKILL.md` frontmatter `skill-version:` is minor-bumped (e.g. `1.4.0` → `1.5.0`) per the same rule.
6. REQUIREMENT: After authoring, `uv run gz agent sync control-surfaces` runs successfully and the updated skills are byte-parity-propagated to all derived surfaces (`src/gzkit/skills/ghi-author/`, `src/gzkit/skills/ghi-close/`, `.claude/skills/ghi-author/`, `.claude/skills/ghi-close/`, `.github/skills/ghi-author/`, `.github/skills/ghi-close/`).
7. REQUIREMENT: NEVER include the operator's personal email in any added prose.
8. REQUIREMENT: Does NOT modify any other skill body content — only the new subsection is additive.
9. REQUIREMENT: Does NOT touch `gz-systematic-debug`, `investigator`, AGENTS.md, or `.gzkit/rules/` — those are sibling OBPI scopes.

> STOP-on-BLOCKERS: if either GHI skill file is absent, or if `gz-systematic-debug` (OBPI-01) does not yet exist, print BLOCKERS and halt. (Sequencing: OBPI-04 depends on OBPI-01.)

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 4 — quote verbatim** into the brief's Implementation Summary.
- [ ] Parent ADR § Consequences § Positive #5 — the "GHI lifecycle becomes the cross-session memory" framing.

**Governance (read once, cache):**

- [ ] `.gzkit/skills/ghi-author/SKILL.md` (current body and frontmatter `skill-version`)
- [ ] `.gzkit/skills/ghi-close/SKILL.md` (current body and frontmatter `skill-version`)
- [ ] `.claude/rules/skill-surface-sync.md` § Version discipline (minor-bump rule for governance/procedure changes)

**Context — coupling targets:**

- [ ] `.gzkit/skills/gz-systematic-debug/SKILL.md` (OBPI-01) — Phase 1 evidence requirements, Phase 4.5 architecture pause rule
- [ ] AGENTS.md § DO IT RIGHT operative claims #10 and #11 (OBPI-03) — the doctrine surface the coupling subsection cites
- [ ] AGENTS.md § Defect-fix routing — the direct-fix vs OBPI-ceremony thresholds the cross-brief coupling key references

**Context — existing cross-link precedent:**

- [ ] How `.gzkit/skills/ghi-author/SKILL.md` already cites other skills (`/ghi-close`, `gz issue file`, etc.) — match the citation style

**Prerequisites (check existence, STOP if missing):**

- [ ] `.gzkit/skills/ghi-author/SKILL.md` present
- [ ] `.gzkit/skills/ghi-close/SKILL.md` present
- [ ] `.gzkit/skills/gz-systematic-debug/SKILL.md` exists (OBPI-01 landed)
- [ ] Parent ADR file present

**Existing Code (understand current state):**

- [ ] Current `skill-version:` values for both GHI skills (record for minor-bump)
- [ ] Current Step 0 prior-art lookup in `.gzkit/skills/ghi-author/SKILL.md` — confirm the new coupling subsection does not duplicate it; it cites alongside it

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item #4 quoted in Implementation Summary

### Gate 2: TDD

- [ ] `uv run gz validate --documents` exits 0
- [ ] `uv run gz agent sync control-surfaces` exits 0 with updates byte-parity-propagated
- [ ] No regression in `uv run -m unittest -q`

### Code Quality

- [ ] Lint clean: `uv run gz arb ruff` (receipt: `arb-ruff-*`)
- [ ] Typecheck clean: `uv run gz arb typecheck` (receipt: `arb-step-typecheck-*`)

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` (receipt: `arb-step-mkdocs-*`)

### Gate 4: BDD (Heavy)

- [ ] No BDD scenario applies — skill body additions are content, not external behavior contract; waiver noted.

### Gate 5: Human (universal per ADR-0.0.36)

- [ ] Foundation-kind brief: explicit human attestation required at completion

## Verification

```bash
grep -q "## Systematic Debugging coupling" .gzkit/skills/ghi-author/SKILL.md
grep -q "## Systematic Debugging coupling" .gzkit/skills/ghi-close/SKILL.md
grep -q "arb-step-root-cause-trace" .gzkit/skills/ghi-author/SKILL.md
grep -q "arb-step-root-cause-trace" .gzkit/skills/ghi-close/SKILL.md
grep -q "architectural GHI labeled as foundation-ADR candidate" .gzkit/skills/ghi-author/SKILL.md
# Confirm skill-version bumped:
grep "skill-version" .gzkit/skills/ghi-author/SKILL.md
grep "skill-version" .gzkit/skills/ghi-close/SKILL.md
uv run gz agent sync control-surfaces
diff .gzkit/skills/ghi-author/SKILL.md src/gzkit/skills/ghi-author/SKILL.md
diff .gzkit/skills/ghi-close/SKILL.md src/gzkit/skills/ghi-close/SKILL.md
uv run gz validate --documents
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Demo

```bash
# After implementation, the coupling subsection is visible in both GHI skills:
grep -A 5 "## Systematic Debugging coupling" .gzkit/skills/ghi-author/SKILL.md
grep -A 5 "## Systematic Debugging coupling" .gzkit/skills/ghi-close/SKILL.md
# The version bumps are observable:
grep -h "skill-version" .gzkit/skills/ghi-author/SKILL.md .gzkit/skills/ghi-close/SKILL.md
```

## Acceptance Criteria

- [ ] REQ-0.0.49-04-01: Given the parent ADR § Decision item 4, when this OBPI completes, then `.gzkit/skills/ghi-author/SKILL.md` contains a `## Systematic Debugging coupling` subsection naming both the cross-brief Phase-1 coupling and the Phase 4.5 architectural-GHI coupling.
- [ ] REQ-0.0.49-04-02: Given the closing coupling requirement (REQ #2), when `.gzkit/skills/ghi-close/SKILL.md` is read, then a `## Systematic Debugging coupling` subsection names the Phase 4 fix-lands coupling with the Phase-1 evidence-trail requirement.
- [ ] REQ-0.0.49-04-03: Given the citation requirement (REQ #3), when both coupling subsections are read, then each cites `.gzkit/skills/gz-systematic-debug/SKILL.md` and AGENTS.md § DO IT RIGHT operative claims #10/#11.
- [ ] REQ-0.0.49-04-04: Given the version-bump requirement (REQs #4/#5), when the frontmatter is parsed for both skills, then `skill-version:` has incremented at the minor digit.
- [ ] REQ-0.0.49-04-05: Given the sync requirement (REQ #6), when `uv run gz agent sync control-surfaces` runs, then both updated skills are byte-parity-propagated to all derived surfaces.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; parent ADR Decision item 4 quoted
- [ ] **Gate 2 (TDD):** `gz validate --documents` clean, sync exits 0, unittest regression-free
- [ ] **Code Quality:** Lint + typecheck + docs build clean with receipts
- [ ] **Value Narrative:** Problem-before (GHI lifecycle was uncoupled from systematic-debug phases; cross-session memory of debugging events lived in in-context narrative recall) vs capability-now (three coupling points operationalize the GHI lifecycle as the structural witness for debugging-event memory)
- [ ] **Key Proof:** `grep -A 5 "## Systematic Debugging coupling"` in both GHI skill files
- [ ] **OBPI Acceptance:** Foundation-kind brief requires explicit human attestation per ADR-0.0.36

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste validate --documents output here
```

### Code Quality

```text
# Paste lint + typecheck + mkdocs output here with ARB receipt IDs
```

### Gate 5 (Human)

```text
# Record attestation text here at completion
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
