---
id: OBPI-0.30.0-06-content-boundary-doctrine
parent: ADR-0.30.0-okf-documentation-knowledge-structure
item: 6
lane: heavy
status: Completed
# req_atomic (GHI #590): authoring-only OBPI; each REQ's labor was one
# indivisible unit. REQ-01/02 are a single doctrine-authoring unit (the boundary
# statement and the phased-migration declaration live in the same doc, written
# together); REQ-03 is a negative invariant (no migration performed) proven by a
# verifying test, carrying no production labor; REQ-04 is one runbook-pointer
# authoring unit (two parallel one-line pointer edits). No REQ subdivided into
# seq=02+ steps, so seq=01-only is honest, not coarse-bucketing.
req_atomic:
  - REQ-0.30.0-06-01
  - REQ-0.30.0-06-02
  - REQ-0.30.0-06-03
  - REQ-0.30.0-06-04
---

# OBPI-0.30.0-06-content-boundary-doctrine: Author the `.gzkit/` vs `docs/` content-boundary doctrine doc (homed under `.gzkit/`) declaring the boundary and the PHASED docs/→`.gzkit/` relocation — the migration is NOT performed here.

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/ADR-0.30.0-okf-documentation-knowledge-structure.md`
- **Checklist Item:** #6 — "Content-boundary doctrine: author the `.gzkit/` vs `docs/` content-boundary doctrine doc (homed under `.gzkit/`; gzkit-core canon under `.gzkit/`, `docs/` = adopter space; OKF bundles domain-named) DECLARING the phased docs/→`.gzkit/` relocation as a forced subsequent decision — the migration is NOT performed here; three-layer doc pointers."

**Status:** Completed

## Objective

Establish the `.gzkit/` vs `docs/` content boundary as written doctrine: author a doctrine doc, homed under `.gzkit/` (eating its own dogfood), stating that gzkit-core-function knowledge and the binding canon of documentation live under `.gzkit/` while `docs/` is reserved for adopter-authored project content, and DECLARING the wholesale docs/→`.gzkit/` relocation as a phased, forced subsequent decision that this OBPI does NOT perform. Wire three-layer doc pointers to the doctrine.

## Lane

**Heavy** — This OBPI establishes a binding governance doctrine and changes operator-facing docs (runbooks). It is authoring-only — it performs no code change and no content migration.

> Heavy is reserved for command/API/schema/runtime-contract changes; binding-doctrine + operator-doc authoring for a shipped governance concern rides Heavy with its sibling OBPIs.

## Allowed Paths

- `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/ADR-0.30.0-okf-documentation-knowledge-structure.md` — parent ADR for intent and scope
- `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/obpis/OBPI-0.30.0-06-content-boundary-doctrine.md` — this brief
- `.gzkit/governance/knowledge/content-boundary.md` — the content-boundary doctrine doc, authored INSIDE the governance OKF bundle (`.gzkit/governance/knowledge/`) so it genuinely IS a concept node of the bundle: gzkit-core canon carrying OKF `type: doctrine` frontmatter (operator-ratified placement, 2026-06-28). **CREATE**
- `docs/user/runbook.md` — operator runbook pointer to the doctrine
- `docs/governance/governance_runbook.md` — governance-maintainer runbook pointer to the doctrine
- `tests/` — REQ-derived unittest cases (doctrine present + declares boundary + declares phased migration + asserts NO migration performed)

## Denied Paths

- Paths not listed in Allowed Paths
- ANY relocation, move, or deletion of existing `docs/` core-canon files — the docs/→`.gzkit/` migration is a forced subsequent decision and is explicitly OUT of scope here (parent ADR Boundary Invariant 4; Scope Minimization)
- `src/gzkit/knowledge/`, `src/gzkit/governance/trust_audits/`, `src/gzkit/commands/`, `src/gzkit/cli/` — model/generator/validator/CLI are OBPIs 01–04
- Any `okf/`-named folder (OKF is a property, not a namespace)
- New dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: A content-boundary doctrine doc MUST exist at `.gzkit/governance/knowledge/content-boundary.md` and MUST state the boundary: gzkit-core-function knowledge and the binding canon of documentation live under `.gzkit/`; `docs/` is reserved for adopter-authored project content; OKF bundles are domain-named.
2. REQUIREMENT: The doctrine doc MUST DECLARE the wholesale docs/→`.gzkit/` relocation as a PHASED, forced subsequent decision, and MUST state explicitly that the migration is NOT performed under ADR-0.30.0.
3. REQUIREMENT: This OBPI MUST NOT relocate, move, or delete any existing `docs/` document — no content migration is performed (declaration only).
4. REQUIREMENT: `docs/user/runbook.md` and `docs/governance/governance_runbook.md` MUST point to the content-boundary doctrine; every `gz <verb>` reference added MUST resolve (`gz validate --cli-alignment`).
5. NEVER: The doctrine doc MUST NOT be wired as enforcement evidence in any `gz validate` / gates / closeout surface (parent ADR Boundary Invariant 1); the boundary is audited at ADR closeout (Boundary Invariant 4), not mechanically fail-closed against the current corpus.
6. ALWAYS: Tests are derived from the REQs above, not from a run of the implementation.

> SCOPE BOUNDARY: This OBPI ESTABLISHES the boundary as doctrine. Homing the tracer bundle on the correct side of the boundary is OBPI-0.30.0-02's scope. Performing the corpus migration is future work, not this ADR.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the Implementation Summary: "this ADR establishes the **`.gzkit/` vs `docs/` content boundary** as doctrine ... OBPI-0.30.0-06 authors the content-boundary doctrine doc ... declaring the boundary and the phased relocation plan; the wholesale docs/→`.gzkit/` move is a forced subsequent decision, not this ADR's work."
- [ ] Parent ADR § Boundary Invariants — invariant 4 (the content boundary) is the contract this doctrine doc writes down.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.30.0-okf-documentation-knowledge-structure/ADR-0.30.0-okf-documentation-knowledge-structure.md`

> **STOP:** If you cannot quote the parent ADR § Decision item this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `docs/governance/state-doctrine.md` — the Layer model the boundary complements (and an example of core canon currently mis-homed under `docs/`)
- [ ] `.claude/rules/gate5-runbook-code-covenant.md` — the three-layer documentation model
- [ ] `.claude/rules/governance-core.md` § Operator-doc verb resolution — `gz <verb>` references must resolve
- [ ] `AGENTS.md` / `CLAUDE.md` — agent operating contract

**Context:**

- [ ] OBPI-0.30.0-02 (homes the tracer bundle under `.gzkit/governance/knowledge/`, the boundary in practice)

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists: `.gzkit/governance/` (parent dir; already present — holds `ontology.json`). The bundle sub-root `.gzkit/governance/knowledge/` is created by OBPI-0.30.0-02 / this OBPI (the doctrine doc is authored into it).
- [ ] Required path exists: `docs/user/runbook.md`, `docs/governance/governance_runbook.md`

**Existing Code (understand current state):**

- [ ] Existing governance doctrine doc reviewed for the doctrine-doc shape and tone
- [ ] Confirm no validator mechanically fails-closed on docs/ core canon today (the boundary is doctrine + closeout-audited, not a fail-close against current state)

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
- [ ] Doctrine doc + both runbook pointers authored; `uv run gz validate --documents` and `uv run gz validate --cli-alignment` pass

### Gate 4: BDD (Heavy only)

- [ ] Authoring-only doctrine surface covered by direct unit tests; no new `.feature` required

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz validate --cli-alignment
uv run gz lint
uv run -m unittest tests.knowledge.test_content_boundary_doctrine -v
uv run mkdocs build --strict
```

## Demo

```bash
# The doctrine is written down and homed under .gzkit/ (core canon side of the boundary)
cat .gzkit/governance/knowledge/content-boundary.md
# No docs/ canon was relocated — the migration is declared, not performed
uv run -m unittest tests.knowledge.test_content_boundary_doctrine -v
```

## Acceptance Criteria

- [ ] REQ-0.30.0-06-01 [BEHAVIOR]: Given the repository, when `.gzkit/governance/knowledge/content-boundary.md` is read, then it exists and states the boundary (gzkit-core canon under `.gzkit/`; `docs/` = adopter space; OKF bundles domain-named).
- [ ] REQ-0.30.0-06-02 [BEHAVIOR]: Given the doctrine doc, when its content is read, then it declares the docs/→`.gzkit/` relocation as a phased subsequent decision AND states the migration is NOT performed under ADR-0.30.0.
- [ ] REQ-0.30.0-06-03 [BEHAVIOR]: Given this OBPI's change set, when the existing `docs/` core-canon files are checked, then none has been relocated, moved, or deleted (the migration is declared, not performed).
- [ ] REQ-0.30.0-06-04 [SUPPORT]: `docs/user/runbook.md` and `docs/governance/governance_runbook.md` point to the content-boundary doctrine — proven by `uv run gz validate --documents` and `uv run gz validate --cli-alignment` passing AND `artifact_edited` ledger events citing the two runbooks emitted at OBPI completion.

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
# Authoring-only doctrine covered by direct unit tests; no behave run required
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

Before this OBPI the `.gzkit/` vs `docs/` content boundary lives only in the operator's head and this ADR's prose — there is no homed, citable doctrine, and gzkit-core canon is scattered under `docs/` (adopter space). After this OBPI the boundary is written doctrine, homed under `.gzkit/` (practicing what it preaches), declaring the phased docs/→`.gzkit/` relocation as future work while performing none of it. The delicate migration gets a tracked home without a risky mass move inside a tracer bullet.

### Key Proof


`cat .gzkit/governance/knowledge/content-boundary.md` shows the boundary stated (.gzkit/ = gzkit-core canon, docs/ = adopter space, OKF bundles domain-named) and the migration declared-not-performed under ADR-0.30.0. `uv run -m unittest tests.knowledge.test_content_boundary_doctrine -v` → 9/9 pass. `uv run gz covers OBPI-0.30.0-06-content-boundary-doctrine --json` → 4/4 covered, 0 uncovered. Receipt arb-step-unittest-befc65b4514b462bb24b596089fe2457 records exit_status=0.

### Implementation Summary


- Files created: .gzkit/governance/knowledge/content-boundary.md (content-boundary doctrine doc, OKF `type: doctrine`); tests/knowledge/test_content_boundary_doctrine.py (9 REQ-derived tests).
- Files modified: docs/user/runbook.md, docs/governance/governance_runbook.md (content-boundary doctrine pointers).
- Tests: REQ-0.30.0-06-01/02/03 BEHAVIOR (semantic co-occurrence assertions binding boundary direction, phased-not-performed, no-relocation invariant); REQ-0.30.0-06-04 SUPPORT (both runbooks name the full doctrine path). Parity 4/4 via `gz covers`.
- Adversarial validation (Step 4b): Codex REFUTED-WITH-CAVEATS flagged 7 hollow substring tests; rewrote to semantic assertions and verified via negative control they fail on an inverted doctrine.
- Date completed: 2026-06-29. Attestation: operator "attest completed" (Heavy lane Gate 5).
- Tracked: the wholesale docs/→.gzkit/ migration is declared by the doctrine and NOT performed here — a forced subsequent decision (likely its own ADR phase).

## Tracked Defects

- The wholesale docs/→`.gzkit/` relocation of gzkit's existing core canon is a delicate, phased subsequent decision declared by this doctrine doc and NOT performed here; it is a candidate for its own future ADR phase (flagged for operator sequencing).

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Heavy-lane content-boundary doctrine OBPI-0.30.0-06: doctrine doc authored at .gzkit/governance/knowledge/content-boundary.md stating the .gzkit/ vs docs/ boundary and declaring the phased migration as NOT performed; 9/9 REQ-derived tests green (receipt arb-step-unittest-befc65b4514b462bb24b596089fe2457, exit_status=0); ruff/typecheck/mkdocs clean; REQ parity 4/4 via gz covers; Step 4b Codex adversarial validation returned REFUTED-WITH-CAVEATS and the hollow-test gap was fixed (7 substring checks rewritten to semantic co-occurrence assertions, negative-control verified to discriminate an inverted doctrine).
- Date: 2026-06-29

---

**Date Completed:** 2026-06-29

**Evidence Hash:** -
