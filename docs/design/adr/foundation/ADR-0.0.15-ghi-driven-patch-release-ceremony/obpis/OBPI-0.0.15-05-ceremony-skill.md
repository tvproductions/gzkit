---
id: OBPI-0.0.15-05
parent: ADR-0.0.15-ghi-driven-patch-release-ceremony
item: 5
lane: Heavy
status: Draft
---

# OBPI-0.0.15-05: Patch Release Ceremony Skill

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.15-ghi-driven-patch-release-ceremony/ADR-0.0.15-ghi-driven-patch-release-ceremony.md`
- **Checklist Item:** #6 - "Ceremony skill: narrative drafting, RELEASE_NOTES, GitHub release"

**Status:** Draft

## Objective

A `gz-patch-release` skill orchestrates the ceremony: the agent drafts narrative
release notes from qualifying GHIs, the operator approves, and the skill handles
RELEASE_NOTES.md update, git-sync, and GitHub release creation — mirroring the
closeout ceremony's Steps 9-10 pattern.

## Lane

**Heavy** - Operator-facing ceremony with RELEASE_NOTES and GitHub release
creation. Changes the operator workflow contract.

## Allowed Paths

- `.gzkit/skills/gz-patch-release/SKILL.md` (new)
- `.claude/skills/gz-patch-release/SKILL.md` (mirror)
- `RELEASE_NOTES.md`

## Denied Paths

- `src/gzkit/commands/patch_release.py` — CLI handled in prior OBPIs
- `src/gzkit/commands/closeout.py` — no modifications

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Skill MUST draft narrative release notes from GHI titles and
   descriptions — NEVER use raw GHI titles as release notes
2. REQUIREMENT: Operator MUST approve release notes before any publish action
3. REQUIREMENT: `uv run gz git-sync --apply --lint --test` MUST run immediately
   before `gh release create` — same policy as closeout ceremony
4. REQUIREMENT: Skill MUST apply the Iron Law pattern from gz-obpi-pipeline:
   once the operator approves, the skill flows through all remaining steps
   without pauses or summaries
5. REQUIREMENT: Foundation ADRs (0.0.x) MUST skip GitHub release creation per
   existing policy

> STOP-on-BLOCKERS: if the closeout ceremony skill is being refactored
> concurrently (GHI #65), coordinate to avoid conflicts.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.15-ghi-driven-patch-release-ceremony/ADR-0.0.15-ghi-driven-patch-release-ceremony.md`
- [ ] OBPI-0.0.15-01 through OBPI-0.0.15-04 (prerequisites)
- [ ] Closeout ceremony skill: `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md`
- [ ] OBPI pipeline skill: `.claude/skills/gz-obpi-pipeline/SKILL.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] `gz patch release` CLI command operational (from prior OBPIs)
- [ ] Closeout ceremony skill exists as pattern reference

**Existing Code (understand current state):**

- [ ] Closeout ceremony Steps 9-10: `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md`
- [ ] OBPI pipeline Iron Law: `.claude/skills/gz-obpi-pipeline/SKILL.md`

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Skill documented in runbook

### Gate 4: BDD (Heavy)

- [ ] N/A — skill is agent-orchestrated, not CLI-testable via behave

### Gate 5: Human (Heavy)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

# Specific verification — skill registration and structure
test -f .gzkit/skills/gz-patch-release/SKILL.md && echo "PASS: skill exists"
test -f .claude/skills/gz-patch-release/SKILL.md && echo "PASS: mirror exists"
grep -q "gz-patch-release" .gzkit/manifest.json && echo "PASS: registered in manifest"
uv run gz validate --surfaces
```

## Acceptance Criteria

- [ ] REQ-0.0.15-05-01: Skill drafts narrative release notes from GHI content
- [ ] REQ-0.0.15-05-02: Operator approval gate before publish
- [ ] REQ-0.0.15-05-03: git-sync immediately before GitHub release
- [ ] REQ-0.0.15-05-04: Iron Law pattern applied to post-approval steps
- [ ] REQ-0.0.15-05-05: Foundation ADRs skip GitHub release

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

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

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `n/a`
- Attestation: `n/a`
- Date: `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
