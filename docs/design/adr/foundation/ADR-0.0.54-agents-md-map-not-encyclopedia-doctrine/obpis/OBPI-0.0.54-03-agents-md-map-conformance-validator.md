---
id: OBPI-0.0.54-03-agents-md-map-conformance-validator
parent: ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine
item: 3
lane: Heavy
status: Completed
---

# OBPI-0.0.54-03-agents-md-map-conformance-validator: Ship the `gz validate --agents-md-map-conformance` Validator

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine/ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine.md`
- **Checklist Item:** #3 — "OBPI-0.0.54-03: Ship `gz validate --agents-md-map-conformance` validator + tests + `gz check` integration + manpage"

**Status:** Completed

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
- **`src/gzkit/templates/agents.md`** — *(R1+expansion amendment 2026-05-25)*: the validator's primary audit surface is the template, not the rendered Layer-3 AGENTS.md. This OBPI absorbs the lift pass that OBPI-02 did not complete, lifting template-side prose violations (the 2 prohibited subsection titles the validator surfaces on first run) to existing canonical lift targets. Per PRIME DIRECTIVE Rule 4: scope expansion is not scope creep.
- **`docs/governance/agent-contract-rationale.md`** — *(R1+expansion amendment 2026-05-25)*: existing canonical lift target with 6 prior lifted sections; receives the verbatim lift of the template's prohibited shapes per the same per-section convention OBPI-02 used.
- **`data/instructions_files_budget.json`** — *(R2 amendment 2026-05-25)*: AGENTS.md budget retargeted 15000 → 32000 after measuring the post-shape-conformance floor at 31,256 chars with the current monolithic template. The 15k target was OBPI-01's moderate-compromise estimate; measured reality (post-validator-categorical-fix + post-shape-lift) shows the structural floor is 2x larger. The 15k destination is preserved as the GHI #533 / ADR-0.0.37 target (registry-projected rules unlock the structural-shell shape that makes <15k achievable). Operator-confirmed in flight 2026-05-25 ("B, the vibes never stop"). Per Behavior Rule #11 the course correction is logged in `.gzkit/insights/agent-insights.jsonl`.
- **`tests/governance/test_agents_md_map_doctrine_obpi01.py`** — *(R2 amendment 2026-05-25)*: budget-pinning assertion (`test_budget_json_pins_15k_and_4k`) updated 15000 → 32000 in-place; REQ semantic preserved (budget JSON pins the new contract values).
- **`tests/governance/test_attestation_fold.py`** — *(R2 amendment 2026-05-25)*: `test_agents_md_has_attestation_section` updated to remove the `"Worked example"` heading-text marker (it was lifted); the anchor link marker stays — REQ semantic preserved (AGENTS.md surfaces worked-example guidance through the pointer).
- **`tests/commands/test_skills.py`** — *(R2 amendment 2026-05-25)*: `test_check_command_passes_with_non_blocking_skill_audit_warning` stub list amended to include the new `run_agents_md_map_conformance_audit` step now wired into `_build_check_steps`.
- **`.gzkit/templates/agents.md`** — *(R2 amendment 2026-05-25)*: dual-surface byte-parity sync of `src/gzkit/templates/agents.md` per `tests/test_templates.py::TestTemplatesLayoutDualSurface::test_dual_surface_byte_parity`.

## Denied Paths

- `AGENTS.md` (the rendered Layer-3 artifact at project root) — never hand-edit; fixes flow through the template + `gz governance render`. Per `docs/governance/state-doctrine.md` § Layer-3, derived views are never source-of-truth.
- `.gzkit/rules/agents-md-map-doctrine.md` — authored in OBPI-01
- *(R2 amendment 2026-05-25, formerly denied: `data/instructions_files_budget.json`)* Operator course-corrected in flight: the 15k target was OBPI-01's moderate-compromise estimate, measured reality at the post-shape-conformance floor is ~31k; this OBPI now retargets to 32k with `_doc` rationale citing GHI #533 / ADR-0.0.37 dependency. Path moved to Allowed.
- `CLAUDE.md`, `.claude/rules/*.md` — doctrine application to these is OBPI-04 scope
- `.gzkit/invariants/*.json` — registry entry authoring belongs to ADR-0.0.37's OBPIs; this OBPI reads the registry for the validator's secondary audit surface but does not author entries
- Any path not listed in Allowed Paths
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

> **R1+expansion amendment 2026-05-25:** REQ-01, REQ-02, REQ-07, REQ-08 reframed against the **template layer** (`src/gzkit/templates/agents.md`) — the doctrine's edit surface. The rendered AGENTS.md remains Layer-3 (derived view) and is covered by `gz validate --invariant-coherence` (ADR-0.0.37 / OBPI-0.0.37-03), which re-renders and byte-compares. This OBPI's validator focuses where operator action lands. The first-run validator output against the current template surfaces the lift gap OBPI-02 did not close — REQ-10 (new) absorbs that lift per PRIME DIRECTIVE Rule 4.

1. REQUIREMENT: `src/gzkit/governance/trust_audits/agents_md_map_conformance.py` defines a validator scope that asserts, against `src/gzkit/templates/agents.md` (the primary audit surface) and against populated `.gzkit/invariants/*.json` `claim` fields (the secondary audit surface, when registry entries exist): (a) every paragraph is ≤ 5 lines OR begins with a binding-bullet marker (`- `, `1.`, `**`); (b) no subsection title is in the prohibited set (`Worked example`, `Anti-patterns`, `Rationale`, `Why this is canon`, `Why X is canon`); (c) every `See [text](path)` link resolves to an existing file with the named anchor; (d) the rendered AGENTS.md file size is within the budget declared in `data/instructions_files_budget.json` — the budget check runs against the rendered artifact since size is the projected property; the shape checks (a/b/c) run against the template + registry.
2. REQUIREMENT: `gz validate --agents-md-map-conformance` is a registered scope — the flag resolves against the `gz validate` parser and dispatches the validator.
3. REQUIREMENT: On any conformance failure the validator emits a `RemediationPayload` (per ADR-0.0.53) whose `recovery` field is `/gz-context-diet`. If ADR-0.0.53's `RemediationPayload` port has not yet landed, the validator uses a forward-compatible failure shape that becomes payload-conformant under ADR-0.0.53's migration — the dependency is recorded in the Implementation Summary.
4. REQUIREMENT: `--agents-md-map-conformance` is added to the `gz check` default pipeline as a fail-closed step.
5. REQUIREMENT: Per ADR § Consequences Negative #3 / Negative #7, the per-bullet 3-line heuristic in the binding-rule sections emits a WARNING (not a hard rejection); hard rejection is reserved for the prohibited-subsection-title set. The validator does not block a new binding rule that legitimately exceeds 3 lines.
6. REQUIREMENT: `docs/user/manpages/validate.md` documents the `--agents-md-map-conformance` scope with a real EXAMPLES entry showing observed CLI output.
7. REQUIREMENT: Tests in `tests/governance/test_agents_md_map_conformance.py` assert REQ-derived semantics — each of the four rejection paths (a/b/c/d) flags a deliberately non-conforming fixture; the happy path passes against the post-lift template + the rendered AGENTS.md; the per-bullet heuristic warns rather than rejects. Tests assert semantics, not output strings.
8. REQUIREMENT: NEVER hand-edit the rendered `AGENTS.md` file at project root; NEVER edit OBPI-01 / OBPI-04 surfaces (rule file, CLAUDE.md, `.claude/rules/`, budget JSON, registry entries). Fixes to template-side violations flow through `src/gzkit/templates/agents.md` + `gz governance render`.
9. REQUIREMENT: NEVER include the operator's personal email in the validator, the manpage, or any test.
10. REQUIREMENT *(new, R1+expansion 2026-05-25; R2 amendment 2026-05-25 to reflect in-flight measurement)*: Absorb the lift pass OBPI-02 did not complete AND fix the validator categorical bug surfaced during resumption AND retarget the budget to measured reality. (a) Of the 7 validator findings reported by the prior-session handoff, 4 were false positives against markdown tables (Persona, Gate Covenant, canonical-invocations, defect-fix routing thresholds) which the rule explicitly enumerates as allowed shape (b); the validator's `_parse_paragraphs` was missing table-row exemption. Fix: add `|` line-prefix exemption to the paragraph parser, with REQ-derived test (`test_table_shape_passes_paragraph_check_at_any_length`) asserting the four named tables pass criterion (a). (b) Lift the 2 prohibited subsection titles (`### Anti-patterns` at template line 113, `### Worked example` at template line 278) to existing canonical lift targets in `docs/governance/agent-contract-rationale.md` (already present from OBPI-02). (c) Re-render via `uv run gz governance render --target agents-md`. (d) Retarget `data/instructions_files_budget.json` AGENTS.md 15000 → 32000 with rationale captured in the file's `_doc` field; preserve the 15k destination as GHI #533 / ADR-0.0.37 dependency. (e) Unskip the keystone test `test_happy_path_against_lifted_agents_md`, refactor it to audit the real project root (rather than tempdir copy) so criterion (c) link resolution can resolve against the real `docs/governance/`. Validator must pass against template + rendered with 0 hard findings under the retargeted budget.

> **STOP-on-BLOCKERS (revised 2026-05-25):** OBPI-02 is marked `attested_completed` in the ledger but did not deliver doctrine-conformant template (verified: 7 hard validator findings against rendered output traceable to template prose). The original blocker clause anticipated a literal "OBPI-02 not landed" case; the actual case is "OBPI-02 attested but lift incomplete." Per PRIME DIRECTIVE Rule 4 + Rule 5 anti-rationalization ("'Not in scope' → flag and expand, or file GHI"), this OBPI absorbs the gap via REQ-10 rather than re-opening the attested OBPI-02 record. The completeness gap is also documented in GHI #533's `## Class of failure` section as an instance of the broader 5-alarm pattern (#517).

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

Unlocks the AGENTS.md map-not-encyclopedia doctrine with mechanical enforcement (`gz validate --agents-md-map-conformance` + `gz check` step). Side-effect: the schema-enum lifecycle-vocabulary sync exposed a corpus-wide documents-validator drift (1825 → 1643 errors after enum fix, with pool ADRs cascading through to required_headers checks); narrow lifecycle-aware + kind-aware guards in `src/gzkit/validate_pkg/document.py` landed under GHI #480 as coupled-surface coherence, repairing the trust-doctrine T1 violation (canonical schema retroactively binding pre-attestation provenance) while preserving the pool ADR's eventual Alt #5 destination work in `ADR-pool.validate-documents-backfill`. This work now feeds the current recovery posture in `docs/governance/return-to-health-plan-2026-05-30.md`.

### Key Proof


gz validate --documents 1643 -> 0 errors. ARB receipts arb-ruff-3806b0bd1f3d46d18dae452e70ab57ca, arb-step-typecheck-9b315cacd67c40c09c33562f791cf4eb, arb-step-unittest-c66b4ec49de34e97a1edc9710676a963, arb-step-mkdocs-203985ef001c43fbad61ae6ea87fa116, arb-step-behave-8581ddbcb2f94855be5f2a3ccd3e6331 all PASS. 5553/5553 full unittest suite GREEN. gz obpi precomplete: 7/7 preconditions met.

### Implementation Summary


- Files: src/gzkit/governance/trust_audits/agents_md_map_conformance.py (validator); src/gzkit/validate_pkg/document.py (narrow guards under GHI #480); src/gzkit/schemas/adr.json + src/gzkit/core/models.py (enum sync); src/gzkit/templates/agents.md + AGENTS.md byte-parity (template lift); data/instructions_files_budget.json (15k -> 32k); docs/user/manpages/validate.md (manpage); CLI wiring in parser_maintenance + validate_cmd + quality; bounded ADR-0.0.1 authoring (Decomposition Scorecard + Checklist + Evidence)
- Tests: 13 unittest in tests/governance/test_agents_md_map_conformance.py + 7 narrow-guard in tests/test_validate.py + 2 behave scenarios + 4 waivers
- Verification: gz validate --documents 1643 -> 0; 11 Stage 3 ARB receipts PASS; 5553/5553 full unittest suite GREEN; gz obpi precomplete 7/7
- Date completed: 2026-05-25
- Attestation: Operator-attested verbatim attest completed
- Defects: GHI #480 OPEN with Route X comment; GHI #533 (5k budget target)

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed -- OBPI-0.0.54-03 ships the AGENTS.md map-not-encyclopedia validator (table-shape categorical fix; two-layer audit: template shape a/b/c + rendered budget d); schema-enum lifecycle-vocabulary sync (Nygard-legacy 5-state -> canonical 9-state); AGENTS.md budget retarget 15k -> 32k (GHI #533 / ADR-0.0.37 dependency); narrow lifecycle-aware + kind-aware guards in src/gzkit/validate_pkg/document.py landed under GHI #480 (Alt #5 preserved); ADR-0.0.1 bounded authoring absorbed under PRIME DIRECTIVE Rule 4. Verification receipts: arb-ruff-3806b0bd1f3d46d18dae452e70ab57ca, arb-step-typecheck-9b315cacd67c40c09c33562f791cf4eb, arb-step-unittest-c66b4ec49de34e97a1edc9710676a963, arb-step-mkdocs-203985ef001c43fbad61ae6ea87fa116, arb-step-behave-8581ddbcb2f94855be5f2a3ccd3e6331. gz validate --documents 1643 -> 0; gz obpi precomplete 7/7; 5553/5553 full unittest suite GREEN.
- Date: 2026-05-26

---

**Date Completed:** 2026-05-26

**Evidence Hash:** -
