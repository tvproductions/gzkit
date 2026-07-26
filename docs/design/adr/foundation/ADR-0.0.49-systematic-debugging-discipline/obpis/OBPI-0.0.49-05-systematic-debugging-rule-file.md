---
id: OBPI-0.0.49-05-systematic-debugging-rule-file
parent: ADR-0.0.49-systematic-debugging-discipline
item: 5
lane: Heavy
status: Draft
allowlist:
- .gzkit/rules/
- .gzkit/rules/systematic-debugging.md
- docs/governance/advisory-rules-audit.md
- docs/design/adr/foundation/ADR-0.0.49-systematic-debugging-discipline/**
- src/gzkit/rules/systematic-debugging.md
- .claude/rules/systematic-debugging.md
- .github/instructions/systematic_debugging.instructions.md
- .gzkit/rules/skill-surface-sync.md
reqs:
- REQ-0.0.49-05-01
- REQ-0.0.49-05-02
- REQ-0.0.49-05-03
- REQ-0.0.49-05-04
- REQ-0.0.49-05-05
- REQ-0.0.49-05-06
verification:
- grep -q "gz validate --systematic-debug-coupling" .gzkit/rules/systematic-debugging.md
- uv run gz validate --advisory-scorecard
- uv run gz validate --unscoped-rules
- uv run gz agent sync control-surfaces
- uv run gz validate --documents
- uv run gz arb ruff
- uv run gz arb typecheck
- uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
---

# OBPI-0.0.49-05-systematic-debugging-rule-file: Author `systematic-debugging.md` Rule + Scorecard

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.49-systematic-debugging-discipline/ADR-0.0.49-systematic-debugging-discipline.md`
- **Checklist Item:** #5 — "Author .gzkit/rules/systematic-debugging.md rule file with body-version 0.1.0, scoped paths (likely **/*.py and **/*.md), encoding the three coupling points as enforceable doctrine and adding scorecard entry to docs/governance/advisory-rules-audit.md (loading posture: advisory; future GHI promotion target: gz validate --systematic-debug-coupling validator scope)."

**Status:** Draft

## Objective

Author `.gzkit/rules/systematic-debugging.md` as the scoped rule surface that codifies the three coupling points (Phase 1 evidence + cross-brief defect → `/ghi-author` before commit; Phase 4 fix lands → `/ghi-close` with Phase-1 evidence trail; Phase 4.5 architecture pause → `/ghi-author` for architectural GHI labeled as foundation-ADR candidate) and adds the scorecard entry to `docs/governance/advisory-rules-audit.md`. The rule lands as advisory in this ADR; mechanical promotion to a `gz validate --systematic-debug-coupling` validator scope is the named future GHI target.

## Lane

**Heavy** — Adds a new canonical rule under `.gzkit/rules/` with broad `paths:` scope and a new scorecard entry that the scorecard self-test (`gz validate --advisory-scorecard`) verifies. Foundation-kind parent triggers universal brief-level Gate 5 attestation per ADR-0.0.36.

## Allowed Paths

- `.gzkit/rules/` — parent canonical-rules directory; OBPI creates `.gzkit/rules/systematic-debugging.md` here (the new rule file does not yet exist)
- `docs/governance/advisory-rules-audit.md` — scorecard entry added for the new rule (existing scorecard catalog file)
- `docs/design/adr/foundation/ADR-0.0.49-systematic-debugging-discipline/**` — parent ADR package scope

**Implementation note:** wheel-shipping (`src/gzkit/rules/systematic-debugging.md`) and vendor-mirror (`.claude/rules/systematic-debugging.md`, `.github/instructions/systematic_debugging.instructions.md`) surfaces MUST be propagated only by `uv run gz agent sync control-surfaces` per `.gzkit/rules/skill-surface-sync.md`. The implementer never hand-edits any derived surface.

## Denied Paths

- `.gzkit/skills/**`, `.gzkit/personas/**` — OBPIs 01/02/04 scopes
- `AGENTS.md`, `src/gzkit/templates/AGENTS.md` — OBPI-03 scope
- Any other rule file under `.gzkit/rules/` — only the new `systematic-debugging.md` is in scope
- `src/gzkit/rules/**`, `.claude/rules/**`, `.github/instructions/**` — derived surfaces; written ONLY by `gz agent sync control-surfaces`
- Any path not listed in Allowed Paths
- New runtime dependencies, CI files, lockfiles
- Mechanical validator implementation (`src/gzkit/governance/trust_audits.py` `validate_systematic_debug_coupling`) — that is a future GHI target named in this OBPI's loading posture, NOT in scope

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `.gzkit/rules/systematic-debugging.md` exists with valid YAML frontmatter `paths:` array. The `paths:` scope is `["**/*.py", "**/*.md"]` (debug discipline binds across code and authored content) — confirm with the implementer that the scope is appropriate during the brief-level review; the brief-time decision binds. NO `skill-version:` field on rule frontmatter (rejected by `RuleFrontmatter` schema per `.claude/rules/skill-surface-sync.md` § Non-negotiable rule #2).
2. REQUIREMENT: The rule body opens with a body-level `<!-- rule-version: 0.1.0 -->` HTML comment immediately after the frontmatter, and a visible `> **Rule version:** `0.1.0` — initial canonical version; codifies systematic-debugging coupling per ADR-0.0.49.` block quote per `.claude/rules/skill-surface-sync.md` § Non-negotiable rule #2.
3. REQUIREMENT: The rule body codifies the three coupling points as numbered enforceable doctrine:
   1. Phase 1 evidence + cross-brief defect → `/ghi-author` before commit, citing the `arb-step-root-cause-trace-*` receipt ID in the GHI body.
   2. Phase 4 fix lands → `/ghi-close` with the Phase-1 receipt ID and four-phase decision trail in the closing comment.
   3. Phase 4.5 architecture pause (3+ failed fix attempts) → `/ghi-author` for an architectural GHI labeled as a foundation-ADR candidate, citing the three prior `arb-step-*` receipts.
4. REQUIREMENT: The rule body contains a `## Loading posture` section naming the rule's posture as advisory (no mechanical gate in this ADR) and the future GHI promotion target: `gz validate --systematic-debug-coupling` validator scope that checks (a) every commit with `fix(<scope>):` subject for an `arb-step-root-cause-trace-*` receipt trailer when the touched files span >1 brief allowlist, and (b) every architectural GHI labeled foundation-ADR-candidate for the three-prior-receipts-cited pattern.
5. REQUIREMENT: The rule body contains a `## Related` section linking to (a) `.gzkit/skills/gz-systematic-debug/SKILL.md`, (b) `.gzkit/personas/investigator.md`, (c) AGENTS.md § DO IT RIGHT operative claims #10/#11 + § Behavior Rules Always #14, (d) `.gzkit/skills/ghi-author/SKILL.md` § Systematic Debugging coupling + `.gzkit/skills/ghi-close/SKILL.md` § Systematic Debugging coupling, and (e) `.gzkit/rules/agent-failure-modes.md` § Skipped cheap verification row (the upstream binding the rule defends against).
6. REQUIREMENT: `docs/governance/advisory-rules-audit.md` gains a new scorecard entry for `systematic-debugging.md` classifying the rule on the four-class spectrum (`Mechanical / Promotable / Judgment / Ambiguous`) per the scorecard catalog convention. Initial classification: `Promotable` (advisory now, mechanical promotion target named in OBPI body).
7. REQUIREMENT: `uv run gz validate --advisory-scorecard` exits 0 after both edits — every new rule file under `.gzkit/rules/` MUST have a corresponding scorecard entry (per `AGENTS.md` § Governance doctrine surfaces — the scorecard is self-testing).
8. REQUIREMENT: After authoring, `uv run gz agent sync control-surfaces` runs successfully and the rule is byte-parity-propagated to `src/gzkit/rules/systematic-debugging.md` (wheel-shipping copy) and `.claude/rules/systematic-debugging.md`, `.github/instructions/systematic_debugging.instructions.md` (vendor mirrors).
9. REQUIREMENT: NEVER include the operator's personal email in the rule body, scorecard entry, or any example.
10. REQUIREMENT: Does NOT implement the `gz validate --systematic-debug-coupling` validator scope — that is a future GHI target, not in this OBPI's scope.
11. REQUIREMENT: Does NOT modify any other rule file, skill, persona, or AGENTS.md — those are sibling OBPI scopes.

> STOP-on-BLOCKERS: if `.gzkit/rules/` is absent, if AGENTS.md does not contain the operative claims OBPI-03 was supposed to add, or if the parent ADR file is absent, print BLOCKERS and halt. (Sequencing: OBPI-05 depends on OBPI-03 and OBPI-04.)

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 5 — quote verbatim** into the brief's Implementation Summary.
- [ ] Parent ADR § Alternatives Considered #6 and #10 — the rationale for why the rule file is required (not redundant with the skill).

**Governance (read once, cache):**

- [ ] `.claude/rules/skill-surface-sync.md` § Non-negotiable rules + § Version discipline (rule version marker shape)
- [ ] `.claude/rules/agent-failure-modes.md` — the upstream taxonomy this rule defends against (`Skipped cheap verification`)
- [ ] `docs/governance/advisory-rules-audit.md` — the scorecard catalog the new entry joins (read existing entries for shape/tone)
- [ ] AGENTS.md § Governance doctrine surfaces — names the self-testing scorecard invariant

**Context — coupling targets:**

- [ ] `.gzkit/skills/gz-systematic-debug/SKILL.md` (OBPI-01) — Phase names cited in coupling points
- [ ] `.gzkit/personas/investigator.md` (OBPI-02) — persona cited in § Related
- [ ] AGENTS.md operative claims #10/#11 + Behavior Rule #14 (OBPI-03) — doctrine surfaces cited in § Related
- [ ] `.gzkit/skills/ghi-author/SKILL.md` + `.gzkit/skills/ghi-close/SKILL.md` § Systematic Debugging coupling (OBPI-04) — operational surfaces cited in § Related

**Context — existing rule files for shape match:**

- [ ] `.gzkit/rules/agent-failure-modes.md` — similar advisory-rule shape, body-version marker, paths scope, § Loading posture section
- [ ] `.gzkit/rules/security-sensitivity.md` — heavy-doctrine rule with explicit validator-pointer pattern in `## Mechanical check`
- [ ] `.gzkit/rules/tool-skill-runbook-alignment.md` — three-invariant codification pattern (matches the three-coupling-point shape of this rule)

**Prerequisites (check existence, STOP if missing):**

- [ ] `.gzkit/rules/` directory present
- [ ] `docs/governance/advisory-rules-audit.md` present
- [ ] `.gzkit/skills/gz-systematic-debug/SKILL.md` exists (OBPI-01 landed)
- [ ] `.gzkit/personas/investigator.md` exists (OBPI-02 landed)
- [ ] AGENTS.md operative claims #10/#11 + Behavior Rule #14 present (OBPI-03 landed)
- [ ] `.gzkit/skills/ghi-author/SKILL.md` + `.gzkit/skills/ghi-close/SKILL.md` § Systematic Debugging coupling present (OBPI-04 landed)
- [ ] Parent ADR file present

**Existing Code (understand current state):**

- [ ] No existing `.gzkit/rules/systematic-debugging.md` file (the OBPI is creating it)
- [ ] Current scorecard catalog rows — read shape, classification spectrum, entry conventions

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item #5 quoted in Implementation Summary

### Gate 2: TDD

- [ ] `uv run gz validate --documents` exits 0
- [ ] `uv run gz validate --advisory-scorecard` exits 0 (the new rule has a scorecard entry)
- [ ] `uv run gz validate --unscoped-rules` exits 0 (the rule's `paths:` scope is named and not `**`-only without rationale; both `**/*.py` and `**/*.md` are bounded)
- [ ] `uv run gz agent sync control-surfaces` exits 0 with rule propagated to all derived surfaces
- [ ] No regression in `uv run -m unittest -q`

### Code Quality

- [ ] Lint clean: `uv run gz arb ruff` (receipt: `arb-ruff-*`)
- [ ] Typecheck clean: `uv run gz arb typecheck` (receipt: `arb-step-typecheck-*`)

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` (receipt: `arb-step-mkdocs-*`)

### Gate 4: BDD (Heavy)

- [ ] No BDD scenario applies — rule is advisory content, not mechanical surface; waiver noted. Future GHI promotion to `gz validate --systematic-debug-coupling` will land BDD scenarios.

### Gate 5: Human (universal per ADR-0.0.36)

- [ ] Foundation-kind brief: explicit human attestation required at completion. Operator confirms `paths:` scope, scorecard classification, three-coupling-point codification matches the parent ADR's binding doctrine.

## Verification

```bash
test -f .gzkit/rules/systematic-debugging.md
grep -q "rule-version: 0.1.0" .gzkit/rules/systematic-debugging.md
grep -q "^paths:" .gzkit/rules/systematic-debugging.md
grep -q "Phase 4.5 architecture pause" .gzkit/rules/systematic-debugging.md
grep -q "## Loading posture" .gzkit/rules/systematic-debugging.md
grep -q "gz validate --systematic-debug-coupling" .gzkit/rules/systematic-debugging.md
grep -q "systematic-debugging.md" docs/governance/advisory-rules-audit.md
uv run gz validate --advisory-scorecard
uv run gz validate --unscoped-rules
uv run gz agent sync control-surfaces
test -f src/gzkit/rules/systematic-debugging.md
test -f .claude/rules/systematic-debugging.md
uv run gz validate --documents
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Demo

```bash
# After implementation, the new canonical rule file exists with version markers:
head -10 .gzkit/rules/systematic-debugging.md
# The scorecard entry is visible:
grep -B 1 -A 3 "systematic-debugging" docs/governance/advisory-rules-audit.md
# The rule is reachable across all surface mirrors (sync-managed):
ls -1 .gzkit/rules/systematic-debugging.md .claude/rules/systematic-debugging.md .github/instructions/systematic_debugging.instructions.md
# The self-test passes — the new rule has a matching scorecard entry:
uv run gz validate --advisory-scorecard
```

## Acceptance Criteria

- [ ] REQ-0.0.49-05-01: Given the parent ADR § Decision item 5, when this OBPI completes, then `.gzkit/rules/systematic-debugging.md` exists with `paths:` scope, body-version `0.1.0` marker (HTML comment + visible block quote), and the three coupling points codified as numbered enforceable doctrine.
- [ ] REQ-0.0.49-05-02: Given the loading-posture requirement (REQ #4), when the rule body is read, then a `## Loading posture` section names the rule as advisory and the future GHI promotion target as `gz validate --systematic-debug-coupling` with both check criteria spelled out.
- [ ] REQ-0.0.49-05-03: Given the § Related requirement (REQ #5), when the rule body is read, then all five named coupling surfaces (skill, persona, AGENTS.md sections, GHI skills coupling subsections, agent-failure-modes upstream) are linked.
- [ ] REQ-0.0.49-05-04: Given the scorecard requirement (REQ #6), when `docs/governance/advisory-rules-audit.md` is read, then a new entry for `systematic-debugging.md` classifies it `Promotable` and names the mechanical promotion target.
- [ ] REQ-0.0.49-05-05: Given the scorecard self-test (REQ #7), when `uv run gz validate --advisory-scorecard` runs, then it exits 0 — the new rule file has a matching scorecard entry.
- [ ] REQ-0.0.49-05-06: Given the sync requirement (REQ #8), when `uv run gz agent sync control-surfaces` runs, then the rule is byte-parity-propagated to the wheel-shipping copy and both vendor mirrors.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; parent ADR Decision item 5 quoted
- [ ] **Gate 2 (TDD):** `gz validate --documents` clean, `--advisory-scorecard` clean, `--unscoped-rules` clean, sync exits 0, unittest regression-free
- [ ] **Code Quality:** Lint + typecheck + docs build clean with receipts
- [ ] **Value Narrative:** Problem-before (the three coupling points existed only in the ADR's Decision body — no scoped doctrine surface for future agents to consult) vs capability-now (canonical rule file with paths scope, scorecard entry, and named mechanical promotion target)
- [ ] **Key Proof:** `uv run gz validate --advisory-scorecard` exits 0; canonical rule + scorecard entry both present on disk
- [ ] **OBPI Acceptance:** Foundation-kind brief requires explicit human attestation per ADR-0.0.36

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste validate --documents, --advisory-scorecard, --unscoped-rules output here
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
