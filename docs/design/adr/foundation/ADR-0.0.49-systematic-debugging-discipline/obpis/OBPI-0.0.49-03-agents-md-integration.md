---
id: OBPI-0.0.49-03-agents-md-integration
parent: ADR-0.0.49-systematic-debugging-discipline
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.49-03-agents-md-integration: AGENTS.md Integration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.49-systematic-debugging-discipline/ADR-0.0.49-systematic-debugging-discipline.md`
- **Checklist Item:** #3 — "AGENTS.md integration (single OBPI for coupled edits): DO IT RIGHT operative claim #10 (Iron Law precondition form citing gz-systematic-debug), DO IT RIGHT operative claim #11 (3+-failed-fixes-architecture-pause routing to /ghi-author), PRIME DIRECTIVE item #5 one-line cross-reference, Behavior Rule Always #14 (spawn investigator subagent with gz-systematic-debug; Phase 1 evidence captured as ARB step receipt before fix proposal), update Persona table (add investigator as seventh persona), update Skills catalog (add gz-systematic-debug under Code Quality)."

**Status:** Draft

## Objective

Wire systematic debugging into AGENTS.md as a foundation-attested invariant: add two new DO IT RIGHT operative claims (Iron Law precondition + 3+-failed-fixes-architecture-pause), a one-line PRIME DIRECTIVE cross-reference, a new Behavior Rule Always #14 binding the skill to the persona at the trigger surface, the new persona row in the § Persona table, and the new skill row under the § Skills catalog Code Quality cluster. All edits land in one OBPI because they are coupled — the operative claims cite the skill which cites the persona which is dispatched by the behavior rule; splitting them produces incoherent intermediate states.

## Lane

**Heavy** — AGENTS.md is the universal agent contract; operative-claim additions are constitutional invariants. Foundation-kind parent triggers universal brief-level Gate 5 attestation per ADR-0.0.36.

## Allowed Paths

- `AGENTS.md` — the universal agent contract (the primary scoped artifact for coupled edits)
- `src/gzkit/templates/AGENTS.md` — template surface, edited in lockstep with AGENTS.md so `gz init` adopters receive the same contract
- `CLAUDE.md` — only if AGENTS.md import or cross-link requires updating; otherwise denied
- `docs/governance/agent-contract-rationale.md` — rationale doc, may receive worked-example or pedagogy additions for the two new operative claims (per the diet doctrine: terse-binding-bullets in AGENTS.md, rich pedagogy in the rationale doc)
- `docs/design/adr/foundation/ADR-0.0.49-systematic-debugging-discipline/**` — parent ADR package scope

## Denied Paths

- `.gzkit/skills/**`, `.gzkit/personas/**`, `.gzkit/rules/**` — OBPIs 01/02/04/05 scopes
- `docs/governance/advisory-rules-audit.md` — OBPI-05 scope
- Any path not listed in Allowed Paths
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: AGENTS.md § DO IT RIGHT § Operative claims (binding) gains a new claim #10 — the precondition-form Iron Law verbatim: `NO FIX MAY BE PROPOSED UNTIL ROOT-CAUSE EVIDENCE IS CAPTURED AS AN ARB STEP RECEIPT.` The claim cites `.gzkit/skills/gz-systematic-debug/SKILL.md` as the procedure of record; the bullet body is at most two sentences (per the diet doctrine — pedagogy lifts to `docs/governance/agent-contract-rationale.md`).
2. REQUIREMENT: AGENTS.md § DO IT RIGHT § Operative claims (binding) gains a new claim #11 — the 3+-failed-fixes-architecture-pause rule: *"After three failed fix attempts on the same defect, the failure class is wrong architecture, not the next patch — STOP and route to `/ghi-author` for an architectural GHI labeled as a foundation-ADR candidate, citing the three prior `arb-step-*` receipts in the GHI body."* At most two sentences.
3. REQUIREMENT: AGENTS.md § PRIME DIRECTIVE gains a one-line cross-reference under item #5 (FLAG DEFECTS, NEVER EXCUSE THEM): *"Defect surfaced in flight → invoke `gz-systematic-debug` before proposing fix; capture Phase-1 evidence as an ARB step receipt."* Added as a sub-bullet, not a new numbered item (preserves the existing 6-item enumeration).
4. REQUIREMENT: AGENTS.md § Behavior Rules § Always gains a new rule #14: *"On bug / test failure / unexpected behavior: spawn `investigator` subagent with `gz-systematic-debug`; capture Phase 1 root-cause evidence as an ARB step receipt before proposing any fix. After 3+ failed fix attempts, route to `/ghi-author` per DO IT RIGHT operative claim #11."* Maintains the existing rule-#11/#12/#13 numbering posture; #14 is additive.
5. REQUIREMENT: AGENTS.md § Persona table gains a new row for `investigator` (positioned alphabetically between `implementer` and `main-session`): role = "Systematic-debug investigation subagent", traits = "evidence-first, hypothesis-discipline, fix-impulse-suspending, architecture-questioning".
6. REQUIREMENT: AGENTS.md § Skills § Available Skills § Code Quality cluster gains `gz-systematic-debug` (alphabetically positioned). The Code Quality cluster currently lists: `complexity-advisor`, `complexity-guide`, `gz-check`, `gz-chore-runner`, `gz-cli-audit`, `gz-complexity-distill`, `gz-context-diet`, `gz-deps-upgrade`, `gz-pythonic-pattern-apply`, `gz-pythonic-pattern-detect`, `gz-tech-debt-review`. Insert `gz-systematic-debug` alphabetically.
7. REQUIREMENT: `src/gzkit/templates/AGENTS.md` receives the SAME edits in lockstep — `gz init` adopters MUST receive the same contract on first init. The template uses `{placeholder}` tokens for project-specific values (e.g. `{skills_catalog}`); the new claims/rules/table-rows are template-constant and apply to every adopter.
8. REQUIREMENT: `uv run gz validate --instructions-files-budget` exits 0 after the edits — the per-file character budget for AGENTS.md (default 40k chars per `data/instructions_files_budget.json`) is not exceeded. If the additions push AGENTS.md over budget, the operator MUST be notified and the edits MUST lift pedagogy to `docs/governance/agent-contract-rationale.md` per the diet doctrine.
9. REQUIREMENT: `uv run gz validate --documents` exits 0 — the AGENTS.md and CLAUDE.md schema checks pass, no broken anchors/cross-links to the new skill / persona / rule introduced in sibling OBPIs.
10. REQUIREMENT: NEVER include the operator's personal email in any added prose.
11. REQUIREMENT: Does NOT add new operative claims to MAKE LLM STOCHASTIC VIBES INERT, STDLIB-FIRST, or OPERATOR ECONOMY sections — the two new claims are scoped to DO IT RIGHT only.
12. REQUIREMENT: Does NOT modify the existing Defect-fix routing thresholds — those remain authoritative; the new operative claims sit upstream as the precondition that produces evidence the routing decision consumes (per ADR § Scope boundary).

> STOP-on-BLOCKERS: if AGENTS.md is absent, or if the skill/persona referenced (OBPIs 01/02) does not yet exist on disk, print BLOCKERS and halt. (Sequencing: OBPI-03 depends on OBPI-01 and OBPI-02 landing first.)

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 3 — quote verbatim** into the brief's Implementation Summary.
- [ ] Parent ADR § Intent — the AGENTS.md operative-claim doctrine framing.
- [ ] Parent ADR § Consequences § Negative #1 — the "DO IT RIGHT grows from 9 → 11 operative claims" cost framing the diet check defends against.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § DO IT RIGHT (current 9 operative claims plus references to agent-failure-modes) — the surface receiving the new claims
- [ ] `AGENTS.md` § PRIME DIRECTIVE (current 6 items, item #5 receiving the sub-bullet)
- [ ] `AGENTS.md` § Behavior Rules § Always (current 13 rules) — the surface receiving rule #14
- [ ] `AGENTS.md` § Persona (current 6-row table)
- [ ] `AGENTS.md` § Skills § Code Quality (current 11-skill cluster)
- [ ] `docs/governance/agent-contract-rationale.md` — where pedagogy lives (diet doctrine target)
- [ ] `.claude/rules/skill-surface-sync.md` § Bootstrap semantics — explains why `src/gzkit/templates/AGENTS.md` edits track AGENTS.md in lockstep

**Context — diet doctrine:**

- [ ] `data/instructions_files_budget.json` — current per-file char budgets; the 40k AGENTS.md budget governs whether the additions need pedagogy lifted
- [ ] `gz-context-diet` skill SKILL.md — the trim-then-lift pattern if the additions exceed budget

**Prerequisites (check existence, STOP if missing):**

- [ ] `AGENTS.md` present and parseable (no current schema errors per `gz validate --documents`)
- [ ] `.gzkit/skills/gz-systematic-debug/SKILL.md` exists (OBPI-01 landed)
- [ ] `.gzkit/personas/investigator.md` exists (OBPI-02 landed)
- [ ] Parent ADR file present
- [ ] `src/gzkit/templates/AGENTS.md` present

**Existing Code (understand current state):**

- [ ] Current AGENTS.md char count — establish baseline for diet check
- [ ] How existing DO IT RIGHT operative claims cite skills (look at claims that cite `gz-systematic-debug`-shape rules already)
- [ ] How existing Behavior Rules Always #11/#12/#13 cite skills and external surfaces — match that citation style for #14

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item #3 quoted in Implementation Summary

### Gate 2: TDD

- [ ] `uv run gz validate --documents` exits 0
- [ ] `uv run gz validate --instructions-files-budget` exits 0 (AGENTS.md still under 40k)
- [ ] `uv run gz validate --advisory-scorecard` does not regress (scorecard entry added in OBPI-05)
- [ ] No regression in `uv run -m unittest -q`

### Code Quality

- [ ] Lint clean: `uv run gz arb ruff` (receipt: `arb-ruff-*`)
- [ ] Typecheck clean: `uv run gz arb typecheck` (receipt: `arb-step-typecheck-*`)

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` (receipt: `arb-step-mkdocs-*`)

### Gate 4: BDD (Heavy)

- [ ] No BDD scenario applies — AGENTS.md is doctrine content, not external behavior contract; waiver noted. Future GHI promotion to `gz validate --systematic-debug-coupling` (OBPI-05 forward reference) will land BDD scenarios.

### Gate 5: Human (universal per ADR-0.0.36)

- [ ] Foundation-kind brief: explicit human attestation required at completion. Operator confirms operative-claim wording, PRIME DIRECTIVE sub-bullet phrasing, Behavior Rule #14 phrasing, persona-table position, skill-catalog position.

## Verification

```bash
grep -q "NO FIX MAY BE PROPOSED UNTIL ROOT-CAUSE EVIDENCE IS CAPTURED AS AN ARB STEP RECEIPT" AGENTS.md
grep -q "3+ failed fix attempts" AGENTS.md
grep -q "investigator" AGENTS.md
grep -q "gz-systematic-debug" AGENTS.md
# expect >= 2 (Persona table + Behavior Rule)
grep -c "investigator" AGENTS.md
# AGENTS.md operative-claim block must match the template lockstep:
grep -A 2 "operative claim" AGENTS.md
grep -A 2 "operative claim" src/gzkit/templates/AGENTS.md
# (the two outputs above must be identical — fix lockstep if they drift)
uv run gz validate --documents
uv run gz validate --instructions-files-budget
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Demo

```bash
# After implementation, the new operative claims are visible at the AGENTS.md surface:
grep -nC 1 "NO FIX MAY BE PROPOSED" AGENTS.md
# The new Behavior Rule binds skill to persona at the trigger surface:
grep -A 1 "spawn .investigator. subagent" AGENTS.md
# The investigator persona is the seventh row in the Persona table:
grep -A 8 "^| Persona" AGENTS.md | head -10
```

## Acceptance Criteria

- [ ] REQ-0.0.49-03-01: Given the parent ADR § Decision item 3, when this OBPI completes, then AGENTS.md § DO IT RIGHT contains exactly 11 operative claims with #10 carrying the precondition-form Iron Law verbatim and #11 carrying the 3+-failed-fixes-architecture-pause rule.
- [ ] REQ-0.0.49-03-02: Given the PRIME DIRECTIVE cross-reference (REQ #3), when AGENTS.md § PRIME DIRECTIVE is read, then item #5 carries a one-line sub-bullet referencing `gz-systematic-debug` while preserving the existing 6-item numbered enumeration.
- [ ] REQ-0.0.49-03-03: Given the Behavior Rules Always #14 requirement (REQ #4), when AGENTS.md § Behavior Rules § Always is read, then rule #14 binds the `investigator` persona to the `gz-systematic-debug` skill at the trigger surface (bug / test failure / unexpected behavior) and cites the ARB step receipt as the structural precondition.
- [ ] REQ-0.0.49-03-04: Given the persona-table and skill-catalog requirements (REQs #5/#6), when AGENTS.md is read, then the `investigator` row appears in the § Persona table and `gz-systematic-debug` appears in the § Skills § Code Quality cluster, both alphabetically positioned.
- [ ] REQ-0.0.49-03-05: Given the template-lockstep requirement (REQ #7), when `src/gzkit/templates/AGENTS.md` is diffed against AGENTS.md for the affected sections, then the additions match (apart from template `{placeholder}` tokens).
- [ ] REQ-0.0.49-03-06: Given the diet requirement (REQ #8), when `uv run gz validate --instructions-files-budget` runs, then it exits 0 — AGENTS.md remains under the 40k per-file budget.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; parent ADR Decision item 3 quoted
- [ ] **Gate 2 (TDD):** `gz validate --documents` clean, `--instructions-files-budget` clean, unittest regression-free
- [ ] **Code Quality:** Lint + typecheck + docs build clean with receipts
- [ ] **Value Narrative:** Problem-before (systematic debugging was an unnamed principle inside DO IT RIGHT) vs capability-now (two operative claims plus PRIME DIRECTIVE cross-ref plus Behavior Rule #14 wire the skill+persona to the trigger surface)
- [ ] **Key Proof:** `grep -c "investigator" AGENTS.md` ≥ 2 (Persona table + Behavior Rule)
- [ ] **OBPI Acceptance:** Foundation-kind brief requires explicit human attestation per ADR-0.0.36; operator confirms verbatim wording

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste validate --documents and validate --instructions-files-budget output here
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
