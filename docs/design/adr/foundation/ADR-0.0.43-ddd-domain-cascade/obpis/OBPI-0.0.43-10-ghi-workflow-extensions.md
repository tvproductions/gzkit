---
id: OBPI-0.0.43-10-ghi-workflow-extensions
parent: ADR-0.0.43
item: 10
lane: Heavy
status: Draft
---

# OBPI-0.0.43-10-ghi-workflow-extensions: Cascade-aware extensions to ghi-author / ghi-close / ghi-triage

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.43-ddd-domain-cascade/ADR-0.0.43-ddd-domain-cascade.md`
- **Checklist Item:** #10 — "GHI workflow extensions (ghi-author, ghi-close, ghi-triage) — ghi-author requires bounded_context frontmatter + cascade-change flag; ghi-close runs mini-Gate-5 cascade reconciliation; ghi-triage groups by BC + cascade-change priority tier."

**Status:** Draft

## Objective

Extend three GHI-lifecycle skills (`ghi-author`, `ghi-close`, `ghi-triage`) with cascade integration. GHIs are the highest-frequency governance surface; cascade enforcement at GHI close keeps the cascade true between ADR-scale slow-gear turns.

## Lane

**Heavy** — modifies three canonical skill contracts and the underlying GHI parsing surface.

## Allowed Paths

- `.gzkit/skills/ghi-author/SKILL.md` — EXTEND
- `.gzkit/skills/ghi-close/SKILL.md` — EXTEND
- `.gzkit/skills/ghi-triage/SKILL.md` — EXTEND
- `.claude/skills/{ghi-author,ghi-close,ghi-triage}/SKILL.md` — (synced)
- `.agents/skills/{ghi-author,ghi-close,ghi-triage}/SKILL.md` — (synced)
- `.github/skills/{ghi-author,ghi-close,ghi-triage}/SKILL.md` — (synced)
- `src/gzkit/governance/ghi.py` (or wherever GHI parsing lives) — EXTEND to recognize `bounded_context:` and `cascade_change:` frontmatter
- `tests/skills/test_ghi_cascade_extensions.py` — NEW
- `tests/governance/test_ghi_frontmatter_cascade.py` — NEW

## Denied Paths

- ADR-lifecycle skills (`gz-prd`, `gz-design`, `gz-adr-evaluate`, `gz-adr-closeout-ceremony`, `gz-adr-audit`) — OBPI-09
- New domain skills — OBPI-08
- `src/gzkit/governance/domain_models.py` — OBPI-01 / 02
- `src/gzkit/schemas/ghi.json` — OBPI-04 (this OBPI consumes the schema; OBPI-04 defines it)
- `src/gzkit/governance/trust_audits/domain_cascade.py` — OBPI-06
- `src/gzkit/cli/domain.py` — OBPI-03
- `src/gzkit/ledger/**` — OBPI-05 (this OBPI calls emit-helpers)
- Existing GHI body content (closing existing GHIs is operator workflow, not OBPI mutation)
- Runtime dependencies

## Requirements (FAIL-CLOSED)

1. **REQUIREMENT (`ghi-author` — required BC frontmatter).** Skill body adds Step 1 pre-flight: "Which bounded context does this GHI belong to?" Operator answers from PRD § 2.2; new BC → flag for cascade-change; multi-BC → list each. Authored GHI body includes a frontmatter block (when gzkit-managed) or a body trailer `Bounded-Context: <slug>` for GitHub Issue compatibility. **Block-after-backfill**: dialogue refuses to proceed without resolution.
2. **REQUIREMENT (`ghi-author` — cascade-change flag).** Skill asks: "Does resolving this GHI introduce a new BC, glossary term, or context-map entry?" If yes, `cascade_change: true` frontmatter is set and the GHI is labeled `cascade-change` on GitHub.
3. **REQUIREMENT (`ghi-author` — cross-repo provenance).** When invoked under `gz issue file` (cross-repo path), `bounded_context: governance` (or specific BC) is required. Consumer repos filing against gzkit-owned surfaces MUST declare the BC.
4. **REQUIREMENT (`ghi-close` — mini-Gate-5 reconciliation).** Before closing a GHI, the ceremony asks: "Did resolving this GHI introduce or modify any cascade element (new BC, new glossary term, new context-map entry, new DM section)?" Mandatory reconciliation walkthrough:
   - If yes: operator MUST author the cascade addition in the same ceremony OR defer with appropriate event (`bounded_context_pending_ratification`, etc.).
   - If no: operator attests "Cascade is true as of GHI close."
   - Emits `cascade_reconciled` event with `closing_artifact: GHI-<number>` and the diff (empty when nothing introduced).
5. **REQUIREMENT (`ghi-close` — direct-fix path inheritance).** Even `fix(<scope>): … (GHI #N)` direct-fix commits that bypass OBPI ceremony still trip the mini-Gate-5 on close. The mini-Gate-5 is GHI-lifecycle, not OBPI-lifecycle.
6. **REQUIREMENT (`ghi-triage` — BC-grouped rendering).** Triage skill output groups open GHIs by `bounded_context:`. Operator sees "all open issues in experimentation BC" as a coherent slice. Within each BC group, `cascade_change: true` GHIs surface first.
7. **REQUIREMENT (`ghi-triage` — cross-context tier).** GHIs with `crosses_contexts: [a, b]` appear in a dedicated "cross-context blast radius" tier above per-BC groupings.
8. **REQUIREMENT (`ghi-triage` — cascade-change priority).** Triage's rank-ordered deliverable lists `cascade_change: true` GHIs first — they are prerequisites for downstream BC work.
9. **REQUIREMENT (version bumps + sync).** All three SKILL.md files bump `skill-version` per minor-bump policy; `gz agent sync control-surfaces` propagates to four mirrors.
10. **REQUIREMENT (GHI parsing surface).** `src/gzkit/governance/ghi.py` (or equivalent) extends to recognize the new frontmatter keys and surface them in the parsed GHI model.

> STOP-on-BLOCKERS: if GHI parsing in gzkit only reads GitHub Issue API (no body frontmatter parsing), STOP and surface — `bounded_context:` in GHI bodies needs a body-trailer parser similar to `Eval-feedback-source:` commit trailers.

## Discovery Checklist

**Parent ADR:**

- [ ] Parent ADR § Decision item #10 quoted
- [ ] Parent ADR § Intent
- [ ] Parent ADR file

**Governance:**

- [ ] `AGENTS.md` § Skills, § OBPI Acceptance Protocol
- [ ] `.gzkit/rules/skill-surface-sync.md`
- [ ] `.gzkit/rules/gh-cli.md` — GHI conventions
- [ ] `.gzkit/rules/governance-core.md` § Defect-fix routing (direct-fix path inheritance)

**Context:**

- [ ] OBPI-04 (GHI schema cascade keys) landed
- [ ] OBPI-05 (ledger emitters) landed
- [ ] OBPI-06 (cascade validator for `ghi-close` reconciliation) landed
- [ ] Existing `.gzkit/skills/{ghi-author,ghi-close,ghi-triage}/SKILL.md`

**Prerequisites:**

- [ ] OBPI-04 / OBPI-05 / OBPI-06 landed
- [ ] `src/gzkit/governance/ghi.py` (or equivalent) extant

**Existing Code:**

- [ ] Existing GHI parsing surface
- [ ] Existing GitHub Issue API integration

## Quality Gates

### Gate 1: ADR

- [ ] Parent ADR checklist item #10 quoted
- [ ] Intent recorded

### Gate 2: TDD

- [ ] All three SKILL.md files parse against skill schema
- [ ] Version bumps present
- [ ] Sync test: three mirrored to four mirror locations, byte-equal
- [ ] `ghi-author` body output includes `Bounded-Context: <slug>` trailer (or frontmatter when gzkit-managed)
- [ ] `ghi-author` refuses to proceed without BC resolution (post-backfill mode)
- [ ] `ghi-close` mini-Gate-5 ceremony: empty-diff path emits `cascade_reconciled` with `changes=[]`
- [ ] `ghi-close` mini-Gate-5 ceremony: introduced-BC path emits `bounded_context_pending_ratification` event when deferred
- [ ] `ghi-triage` output is grouped by BC
- [ ] `ghi-triage` cross-context tier appears above per-BC tiers
- [ ] `ghi-triage` cascade-change GHIs surface first within each tier
- [ ] Direct-fix path inheritance: `fix(<scope>): ... (GHI #N)` close trips mini-Gate-5
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint / typecheck clean

### Gate 3: Docs (Heavy only)

- [ ] mkdocs build --strict clean

### Gate 4: BDD (Heavy only)

- [ ] Scenario: operator runs `/ghi-author` for a defect → BC pre-flight fires → GHI authored with `bounded_context:` → close triggers mini-Gate-5

### Gate 5: Human (Heavy + Foundation)

- [ ] Attestation recorded

## Verification

```bash
uv run gz validate --documents --surfaces
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

uv run gz agent sync control-surfaces

for skill in ghi-author ghi-close ghi-triage; do
    grep '^skill-version:' .gzkit/skills/$skill/SKILL.md
    diff .gzkit/skills/$skill/SKILL.md .claude/skills/$skill/SKILL.md
done
```

## Demo

```bash
# Open a GHI with cascade frontmatter
gh issue create --title "Demo cascade-aware GHI" --body "
This issue is in the governance BC.

Bounded-Context: governance
Cascade-Change: false
"

# Trigger ghi-triage and see BC grouping
# (Operator demo; interactive output)

# Close the demo GHI through mini-Gate-5
# (Operator demo)
gh issue close $LAST_ISSUE_NUMBER
```

## Acceptance Criteria

- [ ] REQ-0.0.43-10-01: Given each of three SKILL.md files post-edit, when parsed against skill schema, then valid
- [ ] REQ-0.0.43-10-02: Given each SKILL.md, when version-marker compared to pre-edit, then bumped
- [ ] REQ-0.0.43-10-03: Given canonical edits + sync, when four mirrors inspected, then SKILL.md byte-equal for all three skills
- [ ] REQ-0.0.43-10-04: Given `ghi-author` invocation (post-backfill mode), when operator omits BC, then dialogue refuses to proceed past Step 1
- [ ] REQ-0.0.43-10-05: Given `ghi-author` authored GHI body, when inspected, then `Bounded-Context: <slug>` trailer (or frontmatter) present
- [ ] REQ-0.0.43-10-06: Given `ghi-close` invoked on a GHI whose resolution introduced no cascade additions, when ceremony completes, then `cascade_reconciled` event emitted with `changes=[]`
- [ ] REQ-0.0.43-10-07: Given `ghi-close` invoked on a GHI whose resolution introduced a new BC, when ceremony completes, then operator MUST author the BC addition OR `bounded_context_pending_ratification` event is emitted
- [ ] REQ-0.0.43-10-08: Given a direct-fix commit `fix(<scope>): ... (GHI #N)`, when `ghi-close` runs, then mini-Gate-5 reconciliation still fires
- [ ] REQ-0.0.43-10-09: Given `ghi-triage` invoked, when output rendered, then GHIs grouped by `bounded_context:` with cross-context tier first and `cascade_change: true` GHIs prioritized within each group
- [ ] REQ-0.0.43-10-10: Given `gz issue file` cross-repo invocation, when GHI lacks `bounded_context:`, then exit 3 with `Resolve:` line

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** RGR followed
- [ ] **Code Quality:** Clean
- [ ] **Gate 3 (Docs):** mkdocs clean
- [ ] **Gate 4 (BDD):** Scenarios pass
- [ ] **Gate 5 (Human):** Attestation recorded
- [ ] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [ ] Intent recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint output here
```

### Gate 3 (Docs)

```text
# Paste mkdocs output here
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here
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

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
