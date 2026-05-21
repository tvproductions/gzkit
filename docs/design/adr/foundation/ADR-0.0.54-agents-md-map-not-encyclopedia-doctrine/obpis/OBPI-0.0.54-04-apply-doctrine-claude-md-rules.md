---
id: OBPI-0.0.54-04-apply-doctrine-claude-md-rules
parent: ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.54-04-apply-doctrine-claude-md-rules: Apply the Doctrine to CLAUDE.md and `.claude/rules/*.md`

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine/ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine.md`
- **Checklist Item:** #4 — "OBPI-0.0.54-04: Apply doctrine to CLAUDE.md and `.claude/rules/*.md` + final budget amendments + runbook updates"

**Status:** Draft

## Objective

Apply the map-not-encyclopedia doctrine to CLAUDE.md and every `.claude/rules/*.md` file: audit each against the shape rules, lift any prohibited shape to a per-rule expansion doc, finalize `data/instructions_files_budget.json`, update both runbooks with the canonical drift→`/gz-context-diet` recovery path, and cross-link the `gz validate --agents-md-map-conformance` validator from the trust-doctrine page. This OBPI closes the doctrine: every instruction file in the named scope is map-shaped.

## Lane

**Heavy** — Doctrine application to CLAUDE.md (the model-specific harness file every Claude run reads) and the `.claude/rules/*.md` files, a final budget amendment, and updates to both runbooks. Per `.gzkit/rules/skill-surface-sync.md` and the universality of the instruction files under change. Foundation-kind parent ADR-0.0.54 triggers universal brief-level Gate 5 attestation per ADR-0.0.36.

## Allowed Paths

- `CLAUDE.md` — audited against the shape rules; any prohibited shape lifted
- `.gzkit/rules/` — each canonical rule file audited (the ADR § Decision item 4 names `.claude/rules/*.md`; those are generated vendor mirrors per `src/gzkit/hooks/obpi.py` — the canonical edit surface is `.gzkit/rules/*.md`); prohibited shapes lifted to expansion docs
- `docs/governance/` — OBPI creates per-rule expansion docs as the audit identifies lift targets; cross-links the new validator from `docs/governance/trust-doctrine.md`
- `data/instructions_files_budget.json` — finalized to its final values (per-rule-file tightening if the audit identifies headroom; an AGENTS.md budget amendment if OBPI-02 overran)
- `docs/user/runbook.md` — § Recovery flows gains the "AGENTS.md drift → /gz-context-diet" path
- `docs/governance/governance_runbook.md` — § Instruction files names the map-not-encyclopedia doctrine as the resting state
- `docs/design/adr/foundation/ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine/**` — parent ADR package scope

**Implementation note (canonical-vs-mirror):** ADR § Decision item 4 names `.claude/rules/*.md` as the audit target. Those files are generated vendor mirrors — the `gz obpi validate` engine and `src/gzkit/hooks/obpi.py` reject `.claude/rules/` as an edit surface and route to the canonical `.gzkit/rules/*.md`. This OBPI audits and lifts on the canonical `.gzkit/rules/*.md` files; the `.claude/rules/*.md` mirrors are re-propagated by `uv run gz agent sync control-surfaces` and are NEVER hand-edited. The ADR's `.claude/rules/*.md` phrasing is read as "the project rule files" — the doctrine binds them through their canonical home.

## Denied Paths

- `AGENTS.md` — lifted in OBPI-02; not re-edited here (a budget amendment for AGENTS.md, if needed, touches only `data/instructions_files_budget.json`)
- `.gzkit/rules/agents-md-map-doctrine.md` — authored in OBPI-01
- `src/gzkit/governance/trust_audits/agents_md_map_conformance.py` — the validator is OBPI-03 scope; this OBPI cross-links it, never edits it
- The OBPI-02 lift targets (`prime-directive.md`, `behavior-rules.md`, etc.) — not re-edited here
- Any path not listed in Allowed Paths
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: CLAUDE.md is audited against the five prohibited shapes from `.gzkit/rules/agents-md-map-doctrine.md`. Any prohibited shape is lifted to a per-rule/per-topic expansion doc under `docs/governance/`. If the audit surfaces zero prohibited shapes (CLAUDE.md is currently ~1,378 chars and tight), the OBPI's deliverable is the audit receipt itself, recorded in the Implementation Summary.
2. REQUIREMENT: Every canonical rule file under `.gzkit/rules/*.md` is audited against the same shape rules; prohibited shapes are lifted to per-rule expansion docs under `docs/governance/`, with the canonical rule file retaining the binding bullets plus a one-line `See [...]` link. The `.claude/rules/*.md` vendor mirrors are re-propagated by `uv run gz agent sync control-surfaces` — never hand-edited.
3. REQUIREMENT: `data/instructions_files_budget.json` is finalized — per-`.claude/rules/*.md`-file budget tightened if the audit identifies headroom; an AGENTS.md budget amendment recorded here (with rationale) only if OBPI-02 reported an overrun against the `15000` target.
4. REQUIREMENT: `docs/user/runbook.md` § Recovery flows documents the canonical "AGENTS.md (or instruction-file) shape drift → `/gz-context-diet`" recovery path; `docs/governance/governance_runbook.md` § Instruction files names the map-not-encyclopedia doctrine as the resting state. Both updates land in the same patch set as the doctrine application per `.claude/rules/gate5-runbook-code-covenant.md`.
5. REQUIREMENT: `docs/governance/trust-doctrine.md` cross-links the `gz validate --agents-md-map-conformance` scope (the promoted-scope catalogue gains the new entry).
6. REQUIREMENT: No content is compressed by summarization — every lifted `.gzkit/rules` or CLAUDE.md prose block survives verbatim at its expansion-doc home (ADR § Scope boundary).
7. REQUIREMENT: After any `.gzkit/rules/*.md` edit, `uv run gz agent sync control-surfaces` runs successfully so the `.claude/rules/*.md` mirrors stay byte-consistent with canonical; the implementer never hand-edits a mirror.
8. REQUIREMENT: NEVER re-edit AGENTS.md, the OBPI-01 rule file, the OBPI-02 lift targets, or the OBPI-03 validator.
9. REQUIREMENT: NEVER include the operator's personal email in CLAUDE.md, any `.gzkit/rules` or `.claude/rules` file, any expansion doc, the budget file, or the runbooks.

> STOP-on-BLOCKERS: if OBPI-03 has not landed (`gz validate --agents-md-map-conformance` is not a registered scope), print BLOCKERS and halt — this OBPI cross-links and relies on the validator.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 4 — quote verbatim** into the brief's Implementation Summary. Decision item 4 is the contract.
- [ ] Parent ADR § Decision — the CLAUDE.md / `.claude/rules/*.md` shape-inheritance statement.
- [ ] Parent ADR § Consequences — Negative #5 (CLAUDE.md 4000 floor pre-mortem), Negative #2 (15k overrun → amendment path).
- [ ] Parent ADR § Alternatives — Alt 5 (why CLAUDE.md / `.claude/rules` are in scope, not skipped).

**Governance (read once, cache):**

- [ ] `.gzkit/rules/agents-md-map-doctrine.md` (OBPI-01) — the five prohibited shapes the audit applies
- [ ] `.claude/rules/gate5-runbook-code-covenant.md` — runbook updates land in the same patch as the change
- [ ] `docs/governance/trust-doctrine.md` — the promoted-scope catalogue to cross-link into

**Context — the audit surface:**

- [ ] `CLAUDE.md` — current shape (~1,378 chars); audit for prohibited shapes
- [ ] `.gzkit/rules/` — every canonical `*.md` file; audit each (current max ~15k chars per file); `.claude/rules/*.md` are the generated mirrors
- [ ] `data/instructions_files_budget.json` — current per-rule-file `16000` budget

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-01/02/03 landed: rule file present; AGENTS.md lifted; `gz validate --agents-md-map-conformance` registered
- [ ] `docs/user/runbook.md` and `docs/governance/governance_runbook.md` present

**Existing Code (understand current state):**

- [ ] Each `.claude/rules/*.md` file's current shape and char count
- [ ] The runbook sections (§ Recovery flows, § Instruction files) to update

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR Decision item 4 quoted in Implementation Summary

### Gate 2: TDD

- [ ] Audit + lift is content; `gz validate --documents --instructions-files-budget --agents-md-map-conformance` clean run is the structural floor
- [ ] Tests pass: `uv run gz arb step --name unittest -- uv run -m unittest -q` (receipt: `arb-step-unittest-*`)
- [ ] No regression in the existing suite

### Code Quality

- [ ] Lint clean: `uv run gz arb ruff` (receipt: `arb-ruff-*`)
- [ ] Typecheck clean: `uv run gz arb typecheck` (receipt: `arb-step-typecheck-*`)

### Gate 3: Docs (Heavy)

- [ ] Both runbooks and the trust-doctrine cross-link updated; expansion docs render cleanly
- [ ] Docs build: `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` (receipt: `arb-step-mkdocs-*`)

### Gate 4: BDD (Heavy)

- [ ] No BDD scenario applies — this OBPI is an audit + content lift + runbook update; the behavior-bearing surface (the validator) landed in OBPI-03. Waiver noted.

### Gate 5: Human (universal per ADR-0.0.36)

- [ ] Foundation-kind brief: explicit human attestation required at completion
- [ ] Attestation confirms CLAUDE.md and every `.claude/rules/*.md` file conform to the doctrine

## Verification

```bash
uv run gz validate --agents-md-map-conformance
uv run python -c "from pathlib import Path; print('CLAUDE.md chars:', len(Path('CLAUDE.md').read_text(encoding='utf-8')))"
grep -q "gz-context-diet" docs/user/runbook.md
grep -q "Instruction files" docs/governance/governance_runbook.md
grep -q "agents-md-map-conformance" docs/governance/trust-doctrine.md
uv run gz validate --documents --instructions-files-budget --surfaces
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Demo

```bash
# Every instruction file in scope is now map-shaped:
uv run gz validate --agents-md-map-conformance
# The recovery path is documented in the operator runbook:
grep -A2 "gz-context-diet" docs/user/runbook.md
```

## Acceptance Criteria

- [ ] REQ-0.0.54-04-01: Given parent ADR § Decision item 4, when CLAUDE.md is audited against the five prohibited shapes, then any prohibited shape is lifted to a `docs/governance/` expansion doc, or — if the audit is clean — the audit receipt is recorded in the Implementation Summary.
- [ ] REQ-0.0.54-04-02: Given each canonical `.gzkit/rules/*.md` file, when audited, then prohibited shapes are lifted to per-rule expansion docs, the canonical rule file retains binding bullets plus a `See [...]` link, and `.claude/rules/*.md` mirrors are re-propagated by `gz agent sync control-surfaces` (never hand-edited).
- [ ] REQ-0.0.54-04-03: Given `data/instructions_files_budget.json`, when this OBPI completes, then it holds its final values, with any AGENTS.md budget amendment carrying a recorded rationale tied to an OBPI-02 overrun.
- [ ] REQ-0.0.54-04-04: Given `.claude/rules/gate5-runbook-code-covenant.md`, when the patch set is reviewed, then `docs/user/runbook.md` § Recovery flows and `docs/governance/governance_runbook.md` § Instruction files are updated in the same commit window.
- [ ] REQ-0.0.54-04-05: Given `docs/governance/trust-doctrine.md`, when it is read, then it cross-links the `gz validate --agents-md-map-conformance` scope in the promoted-scope catalogue.
- [ ] REQ-0.0.54-04-06: Given the doctrine application, when `gz validate --agents-md-map-conformance` runs across the full named scope, then CLAUDE.md and every `.claude/rules/*.md` file conform.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; parent ADR Decision item 4 quoted in Implementation Summary
- [ ] **Gate 2 (TDD):** Documents + budget + conformance validation clean; suite regression-free
- [ ] **Code Quality:** Lint + typecheck + docs build clean with receipts
- [ ] **Value Narrative:** Problem-before (only AGENTS.md map-shaped) vs capability-now (every instruction file in scope map-shaped; doctrine fully landed)
- [ ] **Key Proof:** `gz validate --agents-md-map-conformance` green across the full scope; runbook recovery path documented
- [ ] **OBPI Acceptance:** Foundation-kind brief requires explicit human attestation per ADR-0.0.36

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste validate --documents --instructions-files-budget --agents-md-map-conformance output here
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
