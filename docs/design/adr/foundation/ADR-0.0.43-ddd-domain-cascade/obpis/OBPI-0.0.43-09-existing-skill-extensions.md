---
id: OBPI-0.0.43-09-existing-skill-extensions
parent: ADR-0.0.43-ddd-domain-cascade
item: 9
lane: Heavy
status: Draft
---

# OBPI-0.0.43-09-existing-skill-extensions: Cascade-aware extensions to gz-prd / gz-design / gz-adr-evaluate / gz-adr-closeout-ceremony / gz-adr-audit

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.43-ddd-domain-cascade/ADR-0.0.43-ddd-domain-cascade.md`
- **Checklist Item:** #9 — "Existing-skill extensions (gz-prd, gz-design, gz-adr-evaluate, gz-adr-closeout-ceremony, gz-adr-audit) — gz-prd scaffolds three new PRD sections; gz-design adds pre-flight BC question + new-BC / multi-BC sub-dialogues; gz-adr-evaluate adds cascade-compliance scoring dimension; gz-adr-closeout-ceremony adds mini-Gate-5 cascade reconciliation; gz-adr-audit adds cascade integrity audit section."

**Status:** Draft

## Objective

Extend five existing ADR-lifecycle skills with cascade-aware behavior so every fast-gear ADR workflow references and enforces the cascade. Each skill gets a version bump and sync propagation; no new skill files (those are OBPI-08).

## Lane

**Heavy** — modifies five canonical skill contracts that operators and agents already use.

## Allowed Paths

- `.gzkit/skills/gz-prd/SKILL.md` — EXTEND
- `.gzkit/skills/gz-design/SKILL.md` — EXTEND
- `.gzkit/skills/gz-adr-evaluate/SKILL.md` — EXTEND
- `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md` — EXTEND
- `.gzkit/skills/gz-adr-audit/SKILL.md` — EXTEND
- `.claude/skills/gz-prd/SKILL.md` — (synced)
- `.claude/skills/gz-design/SKILL.md` — (synced)
- `.claude/skills/gz-adr-evaluate/SKILL.md` — (synced)
- `.claude/skills/gz-adr-closeout-ceremony/SKILL.md` — (synced)
- `.claude/skills/gz-adr-audit/SKILL.md` — (synced)
- `.agents/skills/<same five>/SKILL.md` — (synced)
- `.github/skills/<same five>/SKILL.md` — (synced)
- `tests/skills/test_skill_cascade_extensions.py` — NEW
- `src/gzkit/governance/adr_evaluate.py` (or equivalent) — EXTEND with cascade-compliance scoring dimension

## Denied Paths

- New skills (`gz-domain-enumerate`, `gz-domain-model`) — OBPI-08
- GHI skills (`ghi-author`, `ghi-close`, `ghi-triage`) — OBPI-10
- `src/gzkit/governance/domain_models.py` — OBPI-01 / 02
- Other schemas — other scopes
- `src/gzkit/governance/trust_audits/domain_cascade.py` — OBPI-06
- `src/gzkit/cli/domain.py` — OBPI-03
- `src/gzkit/ledger/**` — OBPI-05
- Runtime dependencies

## Requirements (FAIL-CLOSED)

1. **REQUIREMENT (`gz-prd` extension).** Skill body adds a Step 0 pre-flight: "If this PRD will declare BCs (typically yes), invoke `gz-domain-enumerate` after scaffolding § 2.1 / 2.2 / 2.3 sections." Skill description triggers updated to include "domain modeling" language. Version bump to next minor.
2. **REQUIREMENT (`gz-design` extension — pre-flight BC question).** Skill Step 2 (Clarify) gains a binding first question: "Which bounded context does this ADR belong to?" Operator answers from PRD § 2.2 list; new BC → invoke `gz-domain-enumerate` sub-dialogue; multi-BC → list each. **Block-after-backfill** is enforced: once legacy migration is complete, the dialogue refuses to proceed past Step 2 without a resolved BC. Skill version bump.
3. **REQUIREMENT (`gz-design` extension — new-BC sub-dialogue).** When operator answers "new BC," skill invokes `gz-domain-enumerate` to add the BC to PRD § 2.2 in the same conversation. After ratification, returns to ADR design with the resolved BC.
4. **REQUIREMENT (`gz-design` extension — multi-BC sub-dialogue).** When operator names ≥2 BCs, skill requires confirmation of the context-map entry (per pair). Drafts the entry; operator approves; entry appended to PRD § 2.3 in the same conversation.
5. **REQUIREMENT (`gz-adr-evaluate` cascade-compliance dimension).** New 9th scoring dimension: "Cascade Compliance" with weight 5% (subtracting from existing dimensions proportionally, or operator-confirmed weight rebalancing). Score 4: BC resolves, all glossary markers resolve, context-map entries present for multi-BC ADRs. Score 3: minor issues (e.g., one unresolved marker). Score 2: BC unresolved. Score 1: cascade-unaware (no `bounded_context:` frontmatter on a non-pool ADR after backfill). Score-1 blocks promotion.
6. **REQUIREMENT (`gz-adr-closeout-ceremony` mini-Gate-5 cascade reconciliation).** New ceremony step before final attestation: "Cascade reconciliation — did this ADR's implementation introduce new BCs, glossary terms, or context-map entries?" If yes, operator must (a) author the additions in the same ceremony, OR (b) defer with `bounded_context_pending_ratification` event (and the GHI tracking the deferral). If no, operator attests "Cascade is true as of completion." Emits `cascade_reconciled` event with the diff (empty list if "nothing introduced").
7. **REQUIREMENT (`gz-adr-audit` cascade integrity section).** New audit section in the audit template: "Cascade Integrity — verify (a) `bounded_context:` resolves (b) all glossary markers in ADR/OBPI prose resolve (c) context-map entries cover declared cross-context impact (d) DM `## Implementation Surface` aligns with OBPI Allowed Paths". Section runs `gz validate --domain-cascade --target <adr-id>` and pastes the output as evidence.
8. **REQUIREMENT (version bumps).** All five SKILL.md files MUST bump their `skill-version` per `.gzkit/rules/skill-surface-sync.md` minor-bump policy (governance rule change).
9. **REQUIREMENT (sync propagation).** `uv run gz agent sync control-surfaces` after every edit propagates to four mirrors; mirrors MUST be byte-equal to canonical post-sync.

> STOP-on-BLOCKERS: if `gz-adr-evaluate` cannot accommodate a 9th scoring dimension without breaking existing scorecard JSON consumers (downstream tooling reading scorecard JSON), halt and surface — schema versioning of the scorecard may be required.

## Discovery Checklist

**Parent ADR:**

- [ ] Parent ADR § Decision item #9 quoted
- [ ] Parent ADR § Intent
- [ ] Parent ADR file

**Governance:**

- [ ] `AGENTS.md` § Skills, § OBPI Acceptance Protocol, § Attestation
- [ ] `.gzkit/rules/skill-surface-sync.md`
- [ ] `.gzkit/rules/model-selection.md`
- [ ] `docs/governance/state-doctrine.md`

**Context:**

- [ ] OBPI-04 (frontmatter schemas) landed
- [ ] OBPI-06 (cascade validator) landed
- [ ] OBPI-05 (ledger event emitters) landed
- [ ] Existing `.gzkit/skills/{gz-prd,gz-design,gz-adr-evaluate,gz-adr-closeout-ceremony,gz-adr-audit}/SKILL.md`

**Prerequisites:**

- [ ] OBPI-04 / OBPI-05 / OBPI-06 landed (extensions invoke these surfaces)
- [ ] OBPI-08 landed (new skills referenced by `gz-design` sub-dialogue)

**Existing Code:**

- [ ] `src/gzkit/governance/adr_evaluate.py` for scorecard implementation
- [ ] Existing scorecard JSON consumers

## Quality Gates

### Gate 1: ADR

- [ ] Parent ADR checklist item #9 quoted
- [ ] Intent recorded

### Gate 2: TDD

- [ ] All five canonical SKILL.md files parse against skill schema post-edit
- [ ] Version bumps present in all five frontmatters
- [ ] Sync test: all five mirrored to four mirror locations, byte-equal
- [ ] `gz-adr-evaluate` cascade-compliance dimension test: ADR with resolved cascade scores 4; ADR with unresolved BC scores 2; ADR without `bounded_context:` (post-backfill) scores 1
- [ ] `gz-adr-closeout-ceremony` test: ceremony step prompts for reconciliation; empty diff emits `cascade_reconciled` with `changes=[]`
- [ ] `gz-adr-audit` test: cascade integrity section runs `gz validate --domain-cascade --target <id>` and pastes output
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint / markdownlint clean

### Gate 3: Docs (Heavy only)

- [ ] mkdocs build --strict clean
- [ ] Skill descriptions visible in `gz skill list` reflect new behavior

### Gate 4: BDD (Heavy only)

- [ ] BDD scenario: operator runs `/gz-design` → pre-flight BC question fires → operator answers → ADR scaffolded with `bounded_context:`

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

# Confirm version bumps
for skill in gz-prd gz-design gz-adr-evaluate gz-adr-closeout-ceremony gz-adr-audit; do
    grep '^skill-version:' .gzkit/skills/$skill/SKILL.md
done

# Confirm mirror parity
for skill in gz-prd gz-design gz-adr-evaluate gz-adr-closeout-ceremony gz-adr-audit; do
    diff .gzkit/skills/$skill/SKILL.md .claude/skills/$skill/SKILL.md
done
```

## Demo

```bash
# Trigger gz-design and verify pre-flight BC question
# (Operator demo — invocation is conversational; cannot script the full dialogue here)

# Run gz-adr-evaluate on a cascade-compliant ADR
uv run gz adr evaluate ADR-0.0.43 --json --output /tmp/adr-eval.json
# then: jq '.dimensions[] | select(.name == "Cascade Compliance")' /tmp/adr-eval.json

# Demo closeout ceremony cascade reconciliation step
# (Operator demo — interactive)
```

## Acceptance Criteria

- [ ] REQ-0.0.43-09-01: Given each of five SKILL.md files post-edit, when parsed against skill schema, then valid
- [ ] REQ-0.0.43-09-02: Given each of five SKILL.md files, when version-marker compared to pre-edit, then bumped
- [ ] REQ-0.0.43-09-03: Given canonical edits and sync invoked, when four mirror surfaces inspected, then SKILL.md byte-equal to canonical for all five skills
- [ ] REQ-0.0.43-09-04: Given a cascade-compliant ADR, when `gz adr evaluate` runs, then Cascade Compliance dimension scores 4
- [ ] REQ-0.0.43-09-05: Given an ADR with unresolved BC, when `gz adr evaluate` runs, then Cascade Compliance dimension scores 2
- [ ] REQ-0.0.43-09-06: Given an ADR without `bounded_context:` frontmatter (and post-backfill mode), when `gz adr evaluate` runs, then Cascade Compliance dimension scores 1; ADR is blocked from promotion
- [ ] REQ-0.0.43-09-07: Given `gz-adr-closeout-ceremony` invoked on an ADR whose OBPIs introduced no new cascade entries, when ceremony completes, then `cascade_reconciled` event emitted with `changes=[]`
- [ ] REQ-0.0.43-09-08: Given `gz-adr-closeout-ceremony` invoked on an ADR whose OBPIs introduced a new BC, when ceremony completes, then operator MUST author the BC addition OR defer with `bounded_context_pending_ratification` event
- [ ] REQ-0.0.43-09-09: Given `gz-adr-audit` invoked on a cascade-compliant ADR, when audit completes, then cascade integrity section shows `gz validate --domain-cascade --target <id>` exit 0 output
- [ ] REQ-0.0.43-09-10: Given `/gz-design` invoked, when Step 2 starts, then the first question is "Which bounded context does this ADR belong to?"

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
