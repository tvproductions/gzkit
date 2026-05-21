---
id: OBPI-0.0.54-03-agents-md-map-conformance-validator
parent: ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.54-03-agents-md-map-conformance-validator: Ship the `gz validate --agents-md-map-conformance` Validator

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine/ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine.md`
- **Checklist Item:** #3 — "OBPI-0.0.54-03: Ship `gz validate --agents-md-map-conformance` validator + tests + `gz check` integration + manpage"

**Status:** Draft

## Objective

Ship the `gz validate --agents-md-map-conformance` mechanical validator that binds the map-not-encyclopedia shape: it asserts AGENTS.md contains no over-long rationale paragraph, no prohibited subsection title, every `See [...]` link resolves, and the file is within budget. The validator emits a `RemediationPayload` whose `recovery` is `/gz-context-diet`, joins the `gz check` default pipeline, and is covered by REQ-derived tests against each rejection path plus the happy path on the lifted AGENTS.md.

## Lane

**Heavy** — A new `gz validate --agents-md-map-conformance` CLI scope added to the `gz check` default pipeline. Per `.claude/rules/cli.md` a new validator scope is a heavy-lane CLI-contract change. Foundation-kind parent ADR-0.0.54 triggers universal brief-level Gate 5 attestation per ADR-0.0.36.

## Allowed Paths

- `src/gzkit/governance/trust_audits/` — OBPI creates `agents_md_map_conformance.py` (the new validator scope)
- `src/gzkit/commands/validate_cmd.py` — registers the `--agents-md-map-conformance` scope and dispatches the validator
- `src/gzkit/cli/` — OBPI adds the `--agents-md-map-conformance` flag to the `gz validate` parser surface
- `src/gzkit/commands/` — the `gz check` default-pipeline list gains the new scope as a fail-closed step
- `docs/user/manpages/validate.md` — documents the new scope with a real EXAMPLES entry
- `tests/governance/` — OBPI creates `tests/governance/test_agents_md_map_conformance.py`
- `docs/design/adr/foundation/ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine/**` — parent ADR package scope

## Denied Paths

- `AGENTS.md` — the lift is OBPI-02; this OBPI runs the validator against the already-lifted file, never edits it
- `.gzkit/rules/agents-md-map-doctrine.md` — authored in OBPI-01
- `docs/governance/agents-md-doctrine.md` and the OBPI-02 lift targets — not edited here
- `data/instructions_files_budget.json` — the validator reads it; budget changes are OBPI-01/04 scope
- `CLAUDE.md`, `.claude/rules/*.md` — doctrine application to these is OBPI-04 scope
- Any path not listed in Allowed Paths
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `src/gzkit/governance/trust_audits/agents_md_map_conformance.py` defines a validator scope that asserts, against AGENTS.md: (a) every paragraph is ≤ 5 lines OR begins with a binding-bullet marker (`- `, `1.`, `**`); (b) no subsection title is in the prohibited set (`Worked example`, `Anti-patterns`, `Rationale`, `Why this is canon`, `Why X is canon`); (c) every `See [text](path)` link resolves to an existing file with the named anchor; (d) the file size is within the budget declared in `data/instructions_files_budget.json`.
2. REQUIREMENT: `gz validate --agents-md-map-conformance` is a registered scope — the flag resolves against the `gz validate` parser and dispatches the validator.
3. REQUIREMENT: On any conformance failure the validator emits a `RemediationPayload` (per ADR-0.0.53) whose `recovery` field is `/gz-context-diet`. If ADR-0.0.53's `RemediationPayload` port has not yet landed, the validator uses a forward-compatible failure shape that becomes payload-conformant under ADR-0.0.53's migration — the dependency is recorded in the Implementation Summary.
4. REQUIREMENT: `--agents-md-map-conformance` is added to the `gz check` default pipeline as a fail-closed step.
5. REQUIREMENT: Per ADR § Consequences Negative #3 / Negative #7, the per-bullet 3-line heuristic in the binding-rule sections emits a WARNING (not a hard rejection); hard rejection is reserved for the prohibited-subsection-title set. The validator does not block a new binding rule that legitimately exceeds 3 lines.
6. REQUIREMENT: `docs/user/manpages/validate.md` documents the `--agents-md-map-conformance` scope with a real EXAMPLES entry showing observed CLI output.
7. REQUIREMENT: Tests in `tests/governance/test_agents_md_map_conformance.py` assert REQ-derived semantics — each of the four rejection paths (a/b/c/d) flags a deliberately non-conforming fixture; the happy path passes against the lifted AGENTS.md; the per-bullet heuristic warns rather than rejects. Tests assert semantics, not output strings.
8. REQUIREMENT: NEVER edit AGENTS.md, the OBPI-01 rule file, or the OBPI-02 lift targets — this OBPI ships the validator only.
9. REQUIREMENT: NEVER include the operator's personal email in the validator, the manpage, or any test.

> STOP-on-BLOCKERS: if OBPI-02 has not landed (AGENTS.md not lifted; the happy-path test would have no green file to assert against), print BLOCKERS and halt — ADR § Sequencing pins OBPI-03 after OBPI-02.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 3 — quote verbatim** into the brief's Implementation Summary. Decision item 3 is the contract.
- [ ] Parent ADR § Decision — the four assertion criteria (a/b/c/d) and the prohibited-subsection-title set.
- [ ] Parent ADR § Consequences — Negative #3 (heuristic-detection limits), Negative #7 (the 2am-operator / warn-not-reject distinction).
- [ ] Parent ADR § Sequencing — OBPI-03 lands after OBPI-02 (the validator's happy-path test needs the lifted file).

**Governance (read once, cache):**

- [ ] `.gzkit/rules/agents-md-map-doctrine.md` (OBPI-01) — the invariant this validator binds
- [ ] `.gzkit/rules/tests.md` § Tests assert semantics, not strings
- [ ] `docs/governance/trust-doctrine.md` — the promoted-scope catalogue the new scope joins

**Context — the validator surface:**

- [ ] `src/gzkit/governance/trust_audits/` — an existing validator scope (e.g. `instructions_files_budget.py`) for the registration + dispatch convention
- [ ] `src/gzkit/commands/validate_cmd.py` — scope registration; the `gz check` default-pipeline list
- [ ] `gzkit.core.models.RemediationPayload` — the failure shape (ADR-0.0.53 dependency)

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-01 landed: `.gzkit/rules/agents-md-map-doctrine.md` present; budget tightened
- [ ] OBPI-02 landed: AGENTS.md is map-shaped and within budget (the happy-path fixture)

**Existing Code (understand current state):**

- [ ] The `gz check` default-pipeline list — where new scopes register
- [ ] Existing `--instructions-files-budget` scope — the weight-cap sibling this shape check is additive to

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR Decision item 3 quoted in Implementation Summary

### Gate 2: TDD

- [ ] RED tests for each of the four rejection paths, written before implementation
- [ ] Tests pass: `uv run gz arb step --name unittest -- uv run -m unittest -q` (receipt: `arb-step-unittest-*`)
- [ ] No regression in the existing suite

### Code Quality

- [ ] Lint clean: `uv run gz arb ruff` (receipt: `arb-ruff-*`)
- [ ] Typecheck clean: `uv run gz arb typecheck` (receipt: `arb-step-typecheck-*`)

### Gate 3: Docs (Heavy)

- [ ] `docs/user/manpages/validate.md` updated with the new scope and a real EXAMPLES entry
- [ ] Docs build: `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` (receipt: `arb-step-mkdocs-*`)

### Gate 4: BDD (Heavy)

- [ ] BDD scenario covers `gz validate --agents-md-map-conformance` — a prohibited-shape AGENTS.md fixture triggers a fail-closed exit; a conforming file passes

### Gate 5: Human (universal per ADR-0.0.36)

- [ ] Foundation-kind brief: explicit human attestation required at completion

## Verification

```bash
uv run gz validate --agents-md-map-conformance
uv run gz arb step --name unittest -- uv run -m unittest -q tests.governance.test_agents_md_map_conformance
grep -q "agents-md-map-conformance" docs/user/manpages/validate.md
uv run gz check
uv run gz validate --documents --surfaces
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Demo

```bash
# The validator binds the map shape — green against the lifted AGENTS.md:
uv run gz validate --agents-md-map-conformance
# It is part of the default check pipeline:
uv run gz check
```

## Acceptance Criteria

- [ ] REQ-0.0.54-03-01: Given parent ADR § Decision item 3, when `gz validate --agents-md-map-conformance` runs, then it asserts the four criteria (paragraph length, prohibited titles, link resolution, budget) against AGENTS.md.
- [ ] REQ-0.0.54-03-02: Given a deliberately non-conforming AGENTS.md fixture for each of the four rejection paths, when the validator runs, then each path is flagged; given the lifted AGENTS.md, then the validator passes.
- [ ] REQ-0.0.54-03-03: Given a conformance failure, when the validator fails closed, then it emits a `RemediationPayload` (or forward-compatible shape) whose `recovery` field is `/gz-context-diet`.
- [ ] REQ-0.0.54-03-04: Given the `gz check` default pipeline, when `gz check` runs, then `--agents-md-map-conformance` executes as a fail-closed step.
- [ ] REQ-0.0.54-03-05: Given a binding-rule bullet exceeding 3 lines, when the validator runs, then it emits a WARNING, not a hard rejection — hard rejection is reserved for the prohibited-subsection-title set.
- [ ] REQ-0.0.54-03-06: Given the scope boundary, when this OBPI's diff is reviewed, then AGENTS.md, the OBPI-01 rule file, and the OBPI-02 lift targets are unmodified.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; parent ADR Decision item 3 quoted in Implementation Summary
- [ ] **Gate 2 (TDD):** RED-GREEN cycle followed; conformance-validator tests pass; suite regression-free
- [ ] **Code Quality:** Lint + typecheck + docs build clean with receipts
- [ ] **Value Narrative:** Problem-before (map shape unenforced; reactive diet only) vs capability-now (mechanical witness in the `gz check` pipeline)
- [ ] **Key Proof:** `gz validate --agents-md-map-conformance` green; `gz check` runs the new step
- [ ] **OBPI Acceptance:** Foundation-kind brief requires explicit human attestation per ADR-0.0.36

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste unittest output + arb-step-unittest receipt ID here
```

### Code Quality

```text
# Paste lint + typecheck + mkdocs output here with ARB receipt IDs
```

### Gate 4 (BDD)

```text
# Paste behave output here
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
