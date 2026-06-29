---
id: OBPI-0.30.0-05-progressive-disclosure-path-docs
parent: ADR-0.30.0-okf-documentation-knowledge-structure
item: 5
lane: heavy
status: Completed
req_atomic:
  - REQ-0.30.0-05-01  # Single reachability test walks the bundle link graph — one indivisible test-authoring unit.
  - REQ-0.30.0-05-02  # Three doc-layer edits are one coherent SUPPORT authoring unit (runbook + governance runbook + concept doc describe one path).
  - REQ-0.30.0-05-03  # Single control-surface concept doc names the bundle root — one indivisible authoring unit.
  - REQ-0.30.0-05-04  # Single cli-alignment regression test — one indivisible test-authoring unit.
---

# OBPI-0.30.0-05-progressive-disclosure-path-docs: Wire and document the ONE working progressive-disclosure path — a control surface points an agent into the OKF bundle and the agent reaches the target doc — with three-layer doc updates.

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/ADR-0.30.0-okf-documentation-knowledge-structure.md`
- **Checklist Item:** #5 — "Docs/runbook wiring: show how a control surface points an agent into the OKF bundle (the one working progressive-disclosure path that defines success); three-layer doc updates."

**Status:** Completed

## Objective

Close the tracer bullet by wiring and documenting ONE working progressive-disclosure path: a control surface points an agent into the OKF bundle root, and the agent traverses index → concept links to reach the relevant explanatory doc without a whole-corpus read. Update the three doc layers (operator runbook, governance runbook, command/concept docs) to describe the path. This is the OBPI that defines success for the whole ADR.

## Lane

**Heavy** — This OBPI changes operator-facing documentation contracts (runbooks, concept docs) and wires a control-surface pointer that agents follow.

> Heavy is reserved for command/API/schema/runtime-contract changes; operator-facing doc + control-surface wiring for a shipped capability rides Heavy with its sibling OBPIs.

## Allowed Paths

- `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/ADR-0.30.0-okf-documentation-knowledge-structure.md` — parent ADR for intent and scope
- `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/obpis/OBPI-0.30.0-05-progressive-disclosure-path-docs.md` — this brief
- `docs/user/runbook.md` — operator runbook entry for the progressive-disclosure path
- `docs/governance/governance_runbook.md` — governance-maintainer runbook entry
- `docs/user/concepts/` — new concept doc demonstrating the navigation path (control-surface → bundle root → concept → source)
- `tests/` — REQ-derived unittest case asserting bundle-root → tracer-slice-concept reachability

## Denied Paths

- Paths not listed in Allowed Paths
- `src/gzkit/knowledge/`, `src/gzkit/governance/trust_audits/`, `src/gzkit/commands/`, `src/gzkit/cli/` — the model/generator/validator/CLI are OBPIs 01–04
- The tracer-slice source docs (read-only; referenced, never edited)
- Any wording that would present the OKF bundle as an authority/evidence surface (Boundary Invariant 1) — the docs MUST frame it as orientation only
- New dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: A control surface MUST carry a pointer into the OKF bundle root (e.g. an operator-facing surface that names `.gzkit/governance/knowledge/index.md` as the navigation entry point). *Exact control surface flagged for operator ratification — see Tracked Defects.*
2. REQUIREMENT: The path MUST be reachable — following the bundle root `index.md` and directory `index.md` links MUST reach each tracer-slice concept document (and from there its canonical source doc).
3. REQUIREMENT: All three doc layers (`docs/user/runbook.md`, `docs/governance/governance_runbook.md`, and a `docs/user/concepts/` doc) MUST describe the progressive-disclosure path and MUST frame the OKF bundle as ORIENTATION ONLY, never as evidence/authority (parent ADR Boundary Invariant 1).
4. REQUIREMENT: Every `gz <verb>` reference in the new/updated docs MUST resolve to a registered CLI verb (`gz validate --cli-alignment`).
5. NEVER: No doc may instruct an agent to cite OKF frontmatter/links as proof of a governance claim (parent ADR Boundary Invariant 1).
6. ALWAYS: Tests are derived from the REQs above, not from a run of the implementation.

> SCOPE BOUNDARY: The bundle is produced by OBPIs 02/04; this OBPI consumes the shipped bundle and documents/wires the navigation path. It assumes 01–04 have landed.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the Implementation Summary: "The first implementation is a tracer bullet ... proving one working progressive-disclosure path." Pair it with the success definition from `okf-cms-knowledge-structure-note-2026-06-23.md`: "Success is one working progressive-disclosure path where a control surface can point an agent to the OKF bundle and the agent can find the relevant explanatory document without reading the whole corpus."
- [ ] Parent ADR § Boundary Invariants — invariant 1 (orientation-not-authority) frames how the docs must describe the bundle.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/ADR-0.30.0-okf-documentation-knowledge-structure.md`

> **STOP:** If you cannot quote the parent ADR § Decision item this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `.claude/rules/gate5-runbook-code-covenant.md` — the three-layer documentation model
- [ ] `.claude/rules/governance-core.md` § Operator-doc verb resolution — `gz <verb>` references must resolve
- [ ] `docs/governance/okf-cms-knowledge-structure-note-2026-06-23.md` § Tracer Bullet — the success definition
- [ ] `AGENTS.md` / `CLAUDE.md` — agent operating contract

**Context:**

- [ ] OBPIs 01–04 (the shipped model/generator/validator/CLI this OBPI documents the use of)

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists: the generated `.gzkit/governance/knowledge/` bundle (from OBPI-0.30.0-02 / -04)
- [ ] Required path exists: `docs/user/runbook.md`, `docs/governance/governance_runbook.md`, `docs/user/concepts/`

**Existing Code (understand current state):**

- [ ] Existing concept doc under `docs/user/concepts/` reviewed for the doc shape
- [ ] The existing compact-pointer model reviewed so the OKF pointer COMPLEMENTS rather than competes with it (parent ADR assumption-surfacing)

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Three layers updated; `uv run gz validate --cli-alignment` and `uv run gz validate --documents` pass

### Gate 4: BDD (Heavy only)

- [ ] The reachability path is covered by a direct unit test walking the bundle link graph; no new `.feature` required

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz validate --cli-alignment
uv run gz lint
uv run -m unittest tests.knowledge.test_progressive_disclosure_path -v
uv run mkdocs build --strict
```

## Demo

```bash
# Follow the documented path: control-surface pointer -> bundle root -> concept -> source
cat .gzkit/governance/knowledge/index.md
uv run python -m unittest tests.knowledge.test_progressive_disclosure_path -v
```

## Acceptance Criteria

- [ ] REQ-0.30.0-05-01 [BEHAVIOR]: Given the generated OKF bundle, when the link graph is walked starting at the bundle root `.gzkit/governance/knowledge/index.md` (following directory `index.md` edges), then every tracer-slice concept document is reachable, and each concept links to its canonical source doc.
- [ ] REQ-0.30.0-05-02 [SUPPORT]: All three doc layers (`docs/user/runbook.md`, `docs/governance/governance_runbook.md`, a `docs/user/concepts/` doc) describe the progressive-disclosure path and frame the bundle as orientation-only. Proof channel (SUPPORT, per `.gzkit/rules/tests.md` § REQ Scope Discipline): the three docs are present on disk (path-specific `artifact_edited` authorship, GHI #647) AND their structural shape is admitted by `uv run gz validate --documents` (exit 0). The orientation-only *framing* is a semantic property witnessed by Gate 5 human attestation — `gz validate --documents` admits schema/shape, NOT OKF framing content.
- [ ] REQ-0.30.0-05-03 [BEHAVIOR]: Given the control surface chosen to carry the OKF pointer, when its content is read, then it contains a pointer that names the OKF bundle root (`.gzkit/governance/knowledge/index.md`) as the navigation entry point.
- [ ] REQ-0.30.0-05-04 [BEHAVIOR]: Given the new and updated docs, when `uv run gz validate --cli-alignment` runs, then it exits 0 with no unresolvable `gz <verb>` references in `docs/user/runbook.md`, `docs/governance/governance_runbook.md`, or the new `docs/user/concepts/` doc.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build + cli-alignment output here
```

### Gate 4 (BDD)

```text
# Reachability covered by direct unit test; no behave run required
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

Before this OBPI the model, generator, validator, and CLI exist but no documented path tells an agent how to USE the bundle — the tracer bullet is not yet proven end-to-end. After this OBPI, a control surface points into the bundle root, the index → concept link graph is reachability-tested, and the three doc layers describe the path (framed strictly as orientation, never authority). This is the one working progressive-disclosure path that defines success for the ADR.

### Key Proof


The reachability test walks `.gzkit/governance/knowledge/index.md` → directory indexes → each tracer-slice concept → its source doc, asserting every tracer-slice doc is reachable; the runbooks and a concepts doc describe the path; `gz validate --cli-alignment` and `gz validate --documents` pass.

### Implementation Summary


- Files created/modified: `docs/user/runbook.md`; `docs/governance/governance_runbook.md`; `docs/user/concepts/` (new navigation concept doc + control-surface pointer); `tests/knowledge/` (reachability case).
- Tests added: REQ-0.30.0-05-01 and REQ-0.30.0-05-03 BEHAVIOR cases (`@covers`); REQ-0.30.0-05-04 BEHAVIOR (`gz validate --cli-alignment`); REQ-0.30.0-05-02 SUPPORT (docs + ledger proof).
- Date completed: pending.
- Attestation status: pending (Heavy lane Gate 5).
- Defects noted: control-surface choice for the pointer flagged for operator ratification.

## Tracked Defects

- The exact control surface that carries the bundle pointer (operator runbook vs a `.gzkit/` rule/skill vs a concept doc) is flagged for operator ratification. The brief assumes an operator-facing docs pointer to avoid `.gzkit/` control-surface version-bump + `gz agent sync control-surfaces` churn inside the tracer; the operator may direct the pointer into a canonical control surface instead.

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Heavy-lane Gate 5 for OBPI-0.30.0-05 (progressive-disclosure path docs): operator attested after Stage 4 evidence + independent adversarial validation (REFUTED-WITH-CAVEATS, both caveats resolved). 3/3 REQ-derived tests pass (receipt arb-step-unittest-e4d0008e18fb42969a01c4392af185f7, 6647 total), lint/typecheck/mkdocs clean (arb-ruff-2211bb01004d4af4b4bd240e2853109f, arb-step-typecheck-9f424e20f5b44512a368ea9064fe1b1b, arb-step-mkdocs-548c251a28224c9089b75543b8cd2f32), gz validate --documents + --cli-alignment exit 0. One working progressive-disclosure path proven: control surface docs/user/concepts/okf-navigation.md -> .gzkit/governance/knowledge/index.md -> concept -> canonical source.
- Date: 2026-06-29

---

**Date Completed:** 2026-06-29

**Evidence Hash:** -
