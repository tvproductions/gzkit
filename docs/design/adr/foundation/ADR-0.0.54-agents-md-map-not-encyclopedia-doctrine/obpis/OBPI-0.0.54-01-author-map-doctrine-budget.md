---
id: OBPI-0.0.54-01-author-map-doctrine-budget
parent: ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine
item: 1
lane: Heavy
status: Completed
---

# OBPI-0.0.54-01-author-map-doctrine-budget: Author the Map-Not-Encyclopedia Doctrine + Budget Tightening Port

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine/ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine.md`
- **Checklist Item:** #1 — "OBPI-0.0.54-01: Author map-not-encyclopedia doctrine + budget tightening + rule + scorecard + canonical doctrine doc"

**Status:** Completed

## Objective

Author the map-not-encyclopedia port: the `.gzkit/rules/agents-md-map-doctrine.md` rule file (version `0.1.0`) naming the invariant and the five prohibited shapes, the `docs/governance/agents-md-doctrine.md` canonical expansion the AGENTS.md link will point to, the `data/instructions_files_budget.json` tightening (AGENTS.md `40000 → 15000`, CLAUDE.md `40000 → 4000`), and the `advisory-rules-audit.md` scorecard entry. This OBPI ships the contract and the budget; the lift (OBPI-02) and the validator (OBPI-03) consume them.

## Lane

**Heavy** — Adds a new canonical rule surface (`.gzkit/rules/agents-md-map-doctrine.md`), a new governance doctrine doc, and a budget change in `data/instructions_files_budget.json` that retunes the per-turn context contract every agent reads. Per `.gzkit/rules/skill-surface-sync.md` a new canonical rule file is a heavy-lane surface change. Foundation-kind parent ADR-0.0.54 triggers universal brief-level Gate 5 attestation per ADR-0.0.36.

## Allowed Paths

- `.gzkit/rules/` — OBPI creates `.gzkit/rules/agents-md-map-doctrine.md` (new rule file, version `0.1.0`, the invariant + five prohibited shapes)
- `docs/governance/` — OBPI creates `docs/governance/agents-md-doctrine.md` (the canonical expansion)
- `data/instructions_files_budget.json` — AGENTS.md budget `40000 → 15000`; CLAUDE.md budget `40000 → 4000`
- `docs/governance/advisory-rules-audit.md` — scorecard entry classifying the new rule
- `docs/design/adr/foundation/ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine/**` — parent ADR package scope

## Denied Paths

- `AGENTS.md` — the section lift is OBPI-02 scope; this OBPI does NOT move any content out of AGENTS.md
- `docs/governance/agent-contract-rationale.md`, `docs/governance/prime-directive.md`, `docs/governance/behavior-rules.md`, `docs/governance/skills-catalog.md`, `docs/governance/obpi-attestation.md` — lift targets, written in OBPI-02
- `src/gzkit/governance/trust_audits/` — the `--agents-md-map-conformance` validator is OBPI-03 scope
- `CLAUDE.md`, `.claude/rules/*.md` — doctrine application to these is OBPI-04 scope (the budget *value* for CLAUDE.md changes here; the CLAUDE.md *file* is not edited)
- Any path not listed in Allowed Paths
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `.gzkit/rules/agents-md-map-doctrine.md` exists with rule body version `0.1.0`, `paths:` frontmatter scoping `AGENTS.md`, `CLAUDE.md`, and `.claude/rules/*.md`, and a body declaring the invariant verbatim from the parent ADR § Decision canonical statement plus the five prohibited shapes: (i) multi-paragraph rationale prose, (ii) worked examples / anti-pattern catalogs, (iii) "Why this is canon" coda blockquotes, (iv) narrative pedagogical sections, (v) operative-claims expansions whose binding-bullet form already states the rule.
2. REQUIREMENT: `docs/governance/agents-md-doctrine.md` exists as the canonical doctrine expansion — the encyclopedia entry the AGENTS.md `Why this contract is not minimal` link will eventually resolve to.
3. REQUIREMENT: `data/instructions_files_budget.json` is updated — the AGENTS.md budget changes from `40000` to `15000` and the CLAUDE.md budget from `40000` to `4000`. The per-rule-file `16000` budget is left unchanged (parallel `.claude/rules/*.md` tightening is deferred per ADR § Decision item 1).
4. REQUIREMENT: `docs/governance/advisory-rules-audit.md` gains a scorecard entry for `.gzkit/rules/agents-md-map-doctrine.md` classifying it **Mechanical** for shape, with the entry text noting the per-section size targets remain **Judgment** and live in the ADR § Intent TOC table.
5. REQUIREMENT: This OBPI moves ZERO content out of AGENTS.md — the lift is OBPI-02. The budget tightening is the precondition for the lift per ADR § Sequencing; the transitional window where AGENTS.md exceeds the new `15000` budget is closed by OBPI-02 and is documented in the Implementation Summary.
6. REQUIREMENT: No content is compressed by summarization — the doctrine doc is authored fresh; it does not paraphrase or lossily restate any AGENTS.md section (verbatim-preservation applies to the OBPI-02 lift, not this authoring pass).
7. REQUIREMENT: NEVER include the operator's personal email in the rule file, the doctrine doc, the budget file, or the scorecard entry.

> STOP-on-BLOCKERS: if `data/instructions_files_budget.json` or `docs/governance/advisory-rules-audit.md` is absent, print BLOCKERS and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 1 — quote verbatim** into the brief's Implementation Summary. Decision item 1 is the contract.
- [ ] Parent ADR § Decision — the canonical map-not-encyclopedia invariant statement and the five prohibited shapes.
- [ ] Parent ADR § Intent — the OpenAI four-failure-mode framing and the target-TOC table.
- [ ] Parent ADR § Sequencing — OBPI-01 is the precondition for the lift; the budget change lands first.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/` — existing rule-file frontmatter (`paths:`, version) and body conventions
- [ ] `docs/governance/advisory-rules-audit.md` — existing scorecard-entry shape (Mechanical / Promotable / Judgment / Ambiguous)
- [ ] `data/instructions_files_budget.json` — the current budget structure and key names

**Context — the existing mechanisms this doctrine composes with:**

- [ ] `gz validate --instructions-files-budget` — the weight cap this doctrine's shape check is additive to
- [ ] `.gzkit/skills/gz-context-diet/SKILL.md` — the reactive operator-facing remedy this doctrine makes the mechanical default
- [ ] `docs/governance/agent-contract-rationale.md` — the existing lift target with six prior lifted sections

**Prerequisites (check existence, STOP if missing):**

- [ ] `data/instructions_files_budget.json` present
- [ ] `docs/governance/advisory-rules-audit.md` present
- [ ] `.gzkit/rules/` directory present

**Existing Code (understand current state):**

- [ ] Current AGENTS.md size (~30,900 chars) versus the new `15000` budget — the transitional over-budget window
- [ ] Current CLAUDE.md size (~1,378 chars) versus the new `4000` budget — headroom

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR Decision item 1 quoted in Implementation Summary

### Gate 2: TDD

- [ ] Doctrine doc + rule file are content; `gz validate --documents --advisory-scorecard` clean run is the structural floor
- [ ] Tests pass: `uv run gz arb step --name unittest -- uv run -m unittest -q` (receipt: `arb-step-unittest-*`)
- [ ] No regression in the existing suite

### Code Quality

- [ ] Lint clean: `uv run gz arb ruff` (receipt: `arb-ruff-*`)
- [ ] Typecheck clean: `uv run gz arb typecheck` (receipt: `arb-step-typecheck-*`)

### Gate 3: Docs (Heavy)

- [ ] `docs/governance/agents-md-doctrine.md` and the scorecard entry render cleanly
- [ ] Docs build: `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` (receipt: `arb-step-mkdocs-*`)

### Gate 4: BDD (Heavy)

- [ ] No BDD scenario applies — this OBPI ships a rule file + doctrine doc + budget value, not an operator-facing CLI behavior. The behavior-bearing surface (the conformance validator) lands in OBPI-03. Waiver noted.

### Gate 5: Human (universal per ADR-0.0.36)

- [ ] Foundation-kind brief: explicit human attestation required at completion

## Verification

```bash
test -f .gzkit/rules/agents-md-map-doctrine.md
grep -q "0.1.0" .gzkit/rules/agents-md-map-doctrine.md
test -f docs/governance/agents-md-doctrine.md
uv run python -c "import json; b = json.load(open('data/instructions_files_budget.json')); print('AGENTS.md budget:', b)"
grep -q "agents-md-map-doctrine" docs/governance/advisory-rules-audit.md
uv run gz validate --documents --advisory-scorecard
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Demo

```bash
# The new budget contract — AGENTS.md halved, CLAUDE.md tightened:
uv run python -c "import json; b = json.load(open('data/instructions_files_budget.json')); print(json.dumps(b, indent=2))"
# The doctrine doc is the encyclopedia entry the future AGENTS.md link resolves to:
head -20 docs/governance/agents-md-doctrine.md
```

## Acceptance Criteria

- [ ] REQ-0.0.54-01-01: Given parent ADR § Decision item 1, when this OBPI completes, then `.gzkit/rules/agents-md-map-doctrine.md` exists at body version `0.1.0` with `paths:` scoping `AGENTS.md`, `CLAUDE.md`, and `.claude/rules/*.md`, and a body naming the invariant and the five prohibited shapes.
- [ ] REQ-0.0.54-01-02: Given the doctrine-expansion requirement, when the repo is inspected, then `docs/governance/agents-md-doctrine.md` exists as the canonical encyclopedia entry.
- [ ] REQ-0.0.54-01-03: Given `data/instructions_files_budget.json`, when it is read, then the AGENTS.md budget is `15000`, the CLAUDE.md budget is `4000`, and the per-rule-file budget remains `16000`.
- [ ] REQ-0.0.54-01-04: Given the scorecard requirement, when `docs/governance/advisory-rules-audit.md` is inspected, then it carries a Mechanical-classified entry for the new rule noting that per-section size targets remain Judgment-class.
- [ ] REQ-0.0.54-01-05: Given the scope boundary, when this OBPI's diff is reviewed, then zero content is moved out of `AGENTS.md` and no lift-target governance doc is written — those are OBPI-02.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; parent ADR Decision item 1 quoted in Implementation Summary
- [ ] **Gate 2 (TDD):** Scorecard + documents validation clean; suite regression-free
- [ ] **Code Quality:** Lint + typecheck + docs build clean with receipts
- [ ] **Value Narrative:** Problem-before (encyclopedia-style accretion; reactive diet) vs capability-now (declared map-not-encyclopedia doctrine + tightened budget contract)
- [ ] **Key Proof:** The tightened budget JSON; the doctrine doc as the encyclopedia entry
- [ ] **OBPI Acceptance:** Foundation-kind brief requires explicit human attestation per ADR-0.0.36

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste validate --documents --advisory-scorecard output + arb-step-unittest receipt ID here
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


The tightened budget contract is now mechanically enforced:

```
$ uv run python -c "import json; b = json.load(open('data/instructions_files_budget.json')); print(json.dumps(b['files'], indent=2))"
{
  "AGENTS.md": 15000,
  "CLAUDE.md": 4000
}
```

Doctrine + scorecard + rule file present and consumed by validators:

```
$ test -f .gzkit/rules/agents-md-map-doctrine.md && grep -q "0.1.0" $_ && echo rule-ok
rule-ok
$ test -f docs/governance/agents-md-doctrine.md && echo doctrine-ok
doctrine-ok
$ grep -q "agents-md-map-doctrine" docs/governance/advisory-rules-audit.md && echo scorecard-ok
scorecard-ok
$ uv run gz validate --advisory-scorecard
✓ All validations passed (1 scopes).
```

ARB receipts (canonical-invocation per AGENTS.md § Attestation):
- `arb-step-unittest-6007458fe7174922888ab2d7b93b2367` (5528/5528 pass)
- `arb-ruff-67c400ad2c6844328a6aaffebf1e74a3` (lint clean)
- `arb-step-typecheck-2980d7808c074c9599f4354dca933f77` (typecheck clean)
- `arb-step-mkdocs-d40b4110bacc42598fb19e5074130130` (mkdocs --strict clean)

REQ coverage 5/5 via `tests/governance/test_agents_md_map_doctrine_obpi01.py` (`gz covers OBPI-0.0.54-01-author-map-doctrine-budget --json` → covered_reqs=5, uncovered_reqs=0). Test layer flagged anti-pattern per GHI #531 categorical defect; bookmarked for Move 6 decommissioning sweep.

### Implementation Summary

<!-- gz-validate-skip: brief-cross-references -->
- Files created (4 in-scope + 1 in-flight scope-expansion test): `.gzkit/rules/agents-md-map-doctrine.md` (rule file v0.1.0 with invariant + 5 prohibited shapes + paths scoping AGENTS.md/CLAUDE.md/.claude/rules/*.md); `docs/governance/agents-md-doctrine.md` (canonical doctrine expansion authored fresh per REQ-06 no-summarization); `tests/governance/test_agents_md_map_doctrine_obpi01.py` (operator-approved in-flight scope expansion to satisfy Stage 3 Phase 1b REQ→@covers parity gate; subsequently identified as anti-pattern exemplar per GHI #531 categorical defect — queued for Move 6 / ADR-0.0.59 bulk decommissioning sweep)
- Files modified (4 in-scope + 1 derived-surface metadata): `data/instructions_files_budget.json` (AGENTS.md 40000→15000, CLAUDE.md 40000→4000, per-rule 16000 unchanged); `docs/governance/advisory-rules-audit.md` (new section "Map-Not-Encyclopedia Doctrine" with row 58 classifying rule Mechanical-for-shape with Judgment note for per-section sizes; Summary count Mechanical 41→42; narrative updated); `data/behave_coverage_waivers.json` (added `adr-0.0.54-content-only` rationale + waiver entry for this OBPI per brief Gate 4 intent); `.gzkit/insights/agent-insights.jsonl` (3 improvement records per Behavior Rule #11); `AGENTS.md` (auto-sync metadata stamp only — derived surface; zero content lift per REQ-05 negative-scope verified)
- Tests added: 5 REQ-derived (anti-pattern flagged for Move 6 sweep)
- Date completed: 2026-05-25
- Attestation status: attested (operator verbatim "attest completed" 2026-05-25; foundation-kind Gate 5 universal per ADR-0.0.36)
<!-- gz-validate-skip: brief-cross-references -->
- Defects noted: GHI #530 (brief Allowed-Paths gap; closed superseded against ADR-pool.brief-authoring-evidence-checks); GHI #531 (categorical test-shape category error surfaced by GHI #530's workaround; routed to foundation ADR-0.0.59 per operator directive; recovery plan amended with Move 6 between Move 3 and Move 4; GHI #517 5-alarm cross-linked); transitional AGENTS.md budget overrun by design per ADR § Sequencing

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
<!-- gz-validate-skip: brief-cross-references -->
- Attestation: attest completed — OBPI-0.0.54-01 ships the map-not-encyclopedia port: `.gzkit/rules/agents-md-map-doctrine.md` v0.1.0 (invariant + 5 prohibited shapes; paths frontmatter scopes AGENTS.md, CLAUDE.md, .claude/rules/*.md), `docs/governance/agents-md-doctrine.md` (canonical doctrine expansion, fresh authoring per REQ-06 no-summarization), `data/instructions_files_budget.json` tightened (AGENTS.md 40000→15000, CLAUDE.md 40000→4000, per-rule 16000 unchanged), and `docs/governance/advisory-rules-audit.md` row 58 classifying the rule Mechanical-for-shape with Judgment note for per-section sizes. ARB receipts: arb-step-unittest-6007458fe7174922888ab2d7b93b2367 (5528/5528 pass), arb-ruff-67c400ad2c6844328a6aaffebf1e74a3 (lint clean), arb-step-typecheck-2980d7808c074c9599f4354dca933f77 (typecheck clean), arb-step-mkdocs-d40b4110bacc42598fb19e5074130130 (mkdocs --strict clean). REQ coverage 5/5 via tests/governance/test_agents_md_map_doctrine_obpi01.py — operator-noted anti-pattern exemplar per GHI #531, queued for Move 6 (ADR-0.0.59) bulk decommissioning sweep. Transitional AGENTS.md budget overrun (31387>15000) is by design per ADR § Sequencing, closed by OBPI-02 lift. Zero content moved from AGENTS.md per REQ-05 negative-scope verified. Foundation-kind Gate 5 attestation per ADR-0.0.36. Two in-flight defects routed: GHI #530 (brief Allowed-Paths gap → superseded against ADR-pool.brief-authoring-evidence-checks), GHI #531 (categorical test-shape category error → routed to ADR-0.0.59 foundation ADR, recovery plan amended with Move 6, GHI #517 5-alarm cross-linked).
- Date: 2026-05-25

---

**Date Completed:** 2026-05-25

**Evidence Hash:** -
