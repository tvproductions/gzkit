---
id: OBPI-0.0.73-06-self-check-facade-regression-corpus
parent: ADR-0.0.73-verification-layer-binding-audit
item: 6
lane: Lite
status: Completed
req_atomic:
  - REQ-0.0.73-06-01  # one self-check test method (audit_qc_binding clean on real project) — indivisible
  - REQ-0.0.73-06-02  # one cohesive corpus deliverable (6 fixtures + detection tests authored as a single unit)
  - REQ-0.0.73-06-03  # one fidelity-gate subprocess test method — indivisible
  - REQ-0.0.73-06-04  # SUPPORT: files land via gz validate --documents; no labor below the REQ
  - REQ-0.0.73-06-05  # STRUCTURAL-FENCE: parent-ADR Boundary Invariant #5; audited at closeout, no labor
  - REQ-0.0.73-06-06  # one green-by-emptiness guard + NC wiring change authored as a single unit
---

# OBPI-0.0.73-06-self-check-facade-regression-corpus: Self Check Facade Regression Corpus

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md`
- **Checklist Item:** #6 - "Self-check + facade regression corpus — this ADR passes its OWN `gz validate --qc-binding`; one regression fixture per theater signature (mtime-where-name-says-content, empty-input, copy-vs-self, fixture-only, skip-if-PASS, prose-graded-by-nothing); gz adr fidelity ADR-0.0.73 green over this ADR's own Fidelity Assertions; unit tests"

**Status:** Accepted (repudiated 2026-06-19 — recovery freeze; self-check is intentionally red until OBPI-02 debt is repaired)

## Objective

This ADR passes its OWN `gz validate --qc-binding`, and a facade regression corpus
ships one fixture per theater signature so the six ADR-0.0.37 signatures stay
caught. "Done" = `gz validate --qc-binding` is green over the ADR-0.0.73 scopes,
the fidelity gate is green over this ADR's own `## Fidelity Assertions`, and the
regression corpus has exactly one detected fixture for each of the six signatures
(mtime-where-name-says-content, empty-input, copy-vs-self, fixture-only,
skip-if-PASS, prose-graded-by-nothing).

**Recovery status (2026-06-19):** this "Done" state is no longer true. The ADR
self-check is intentionally red until OBPI-02's 33 acknowledged negative control
debt entries are replaced with genuine controls and OBPI-08/09 land. The prior
completion is repudiated for the same facade-of-the-facade class this ADR exists
to close.

Self-check + facade regression corpus — this ADR passes its OWN `gz validate --qc-binding`; one regression fixture per theater signature (mtime-where-name-says-content, empty-input, copy-vs-self, fixture-only, skip-if-PASS, prose-graded-by-nothing); the fidelity gate green over this ADR's own Fidelity Assertions; unit tests.

## Lane

**Lite** - This OBPI remains internal to the promoted ADR implementation scope.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md` — parent ADR (self-check subject; carries the `## Fidelity Assertions` block)
- `tests/governance/test_qc_binding_self_check.py` **CREATE** — asserts this ADR's scopes pass `--qc-binding`; honest-accounting (no green-by-emptiness)
- `tests/governance/test_facade_regression_corpus.py` **CREATE** — one detected fixture per theater signature + behavioral-catch proof
- `tests/governance/fixtures/facade_corpus/` **CREATE** — the six calibration fixtures (one per signature)
- `src/gzkit/governance/trust_audits/qc_binding.py` — **ALLOWLIST AMENDMENT (operator-attested, 2026-06-18)**: green-by-emptiness guard + acknowledged `_NEGATIVE_CONTROL_DEBT` + genuine negative control for the `qc-binding` step this ADR owns. Coupled OBPI-02 correction surface — its checklist promised "each step ships a fixture it must fail on"; the wiring was unbuilt.
- `tests/governance/test_qc_binding_scope.py` — **ALLOWLIST AMENDMENT (operator-attested, 2026-06-18)**: coupled-surface coherence (rule 1a) — the OBPI-02 contract test for `audit_qc_binding` encodes the old green-by-emptiness contract and must move to the new one in the same change.
- `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/obpis/OBPI-0.0.73-06-self-check-facade-regression-corpus.md` — this brief (evidence recording)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: This ADR MUST pass its own `gz validate --qc-binding` — exit 0, no theater detected in this ADR's QC scopes (maps to REQ-0.0.73-06-01).
1. REQUIREMENT: The facade regression corpus MUST contain one fixture per theater signature; the scope MUST detect every signature — none silently passes (maps to REQ-0.0.73-06-02).
1. REQUIREMENT: `gz adr fidelity ADR-0.0.73-verification-layer-binding-audit` MUST be green — all Fidelity Assertions pass (maps to REQ-0.0.73-06-03).
1. REQUIREMENT: The facade corpus and self-check artifacts MUST land as committed files — `gz validate --documents` exits 0 (maps to REQ-0.0.73-06-04).
1. REQUIREMENT: This ADR MUST pass both checks — no facade-of-the-facade — satisfying Boundary Invariant #5 (maps to REQ-0.0.73-06-05).
1. REQUIREMENT: `gz validate --qc-binding` MUST NOT pass green-by-emptiness — an unwired `bound` step is a finding unless it is in the acknowledged `_NEGATIVE_CONTROL_DEBT` set; the `qc-binding` step MUST be genuinely wired (maps to REQ-0.0.73-06-06).
1. NEVER: Mark the OBPI accepted while scaffold defaults remain in the brief
1. ALWAYS: Reconcile the brief with the parent ADR before implementation begins

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/**`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

<!-- Which gates apply and how to verify them. -->

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

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. These are CONSTRUCTION HOUSEKEEPING (lint, type,
     test, mkdocs) — they prove the codebase is healthy, not what the OBPI
     yielded. The yielded product belongs in the `## Demo` section below.

     AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects. The
     OBPI-pipeline verify stage executes commands via shlex.split + shell=False
     (GHI #415); compound commands are blocked at authoring time by
     gz validate --brief-command-shape and rejected at the verify stage.
     Write multi-step verification as separate uv run ... lines. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
test -f tests/governance/test_qc_binding_self_check.py
test -f tests/governance/test_facade_regression_corpus.py
uv run gz validate --qc-binding
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. The fidelity-gate command is
     unregistered until OBPI-03 lands; the skip marker suppresses the
     command-shape check on the fenced block below (GHI #432). -->

<!-- gz-validate-skip: command-shape -->
``bash
# This ADR passes its own check — no facade-of-the-facade.
uv run gz validate --qc-binding
uv run gz adr fidelity ADR-0.0.73-verification-layer-binding-audit
``

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.73-06-01 [BEHAVIOR]: Given the QC scopes ADR-0.0.73 introduces, when `gz validate --qc-binding` runs over them, then it exits 0 — this ADR passes its own check. (@covers test in `tests/governance/test_qc_binding_self_check.py`)
- [ ] REQ-0.0.73-06-02 [BEHAVIOR]: Given one regression fixture per theater signature (mtime-where-name-says-content, empty-input, copy-vs-self, fixture-only, skip-if-PASS, prose-graded-by-nothing), when the scope runs over the corpus, then every signature is detected (none silently passes). (@covers test in `tests/governance/test_facade_regression_corpus.py`)
- [ ] REQ-0.0.73-06-03 [BEHAVIOR]: Given this ADR's `## Fidelity Assertions` block, when the fidelity gate runs it, then every assertion passes (observed exit equals expected exit). (@covers test in `tests/governance/test_qc_binding_self_check.py`)
- [ ] REQ-0.0.73-06-04 [SUPPORT]: The facade regression corpus and self-check land. Proof: `gz validate --documents` exit 0 + `artifact_edited` ledger event for `tests/governance/test_facade_regression_corpus.py`.
- [ ] REQ-0.0.73-06-05 [STRUCTURAL-FENCE]: This ADR passes its own `gz validate --qc-binding` and its own fidelity gate — no facade-of-the-facade (parent ADR § Boundary Invariants #5).
- [ ] REQ-0.0.73-06-06 [BEHAVIOR]: Given a `bound` QC step with no registered negative control, when `audit_qc_binding` runs and the step is not in the acknowledged `_NEGATIVE_CONTROL_DEBT` set, then it emits a green-by-emptiness finding (no silent skip); and the `qc-binding` step is genuinely wired (its NC fails on planted theater). (@covers test in `tests/governance/test_qc_binding_self_check.py`)

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

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
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof


`uv run gz adr fidelity ADR-0.0.73-verification-layer-binding-audit` -> 5 pass, 0 fail. `uv run gz validate --qc-binding` -> exit 0, "No QC theater detected". `uv run gz validate --documents` -> exit 0. Full suite 6265/6265 pass (receipt arb-step-unittest-d7ef711909cd469d8d87e9231356cafc).

**SUPERSEDED 2026-06-19:** this evidence packet is no longer completion proof.
`uv run gz validate --qc-binding` now exits 3 with 33 named negative-control
debt findings, and `uv run gz adr fidelity ADR-0.0.73-verification-layer-binding-audit`
fails while the recovery rows remain red.

### Implementation Summary


- Fidelity Assertions table: removed backtick wrapping from all command cells (was causing FileNotFoundError -> observed -1), fixed row 3 circular self-reference to --check form, removed duplicate row 4 — table parses, 5 assertions all PASS
- Facade corpus: created 6 JSON fixtures in tests/governance/fixtures/facade_corpus/, one per theater signature (mtime-where-name-says-content, empty-input, copy-vs-self, fixture-only, skip-if-PASS, prose-graded-by-nothing)
- Self-check + corpus tests: created test_facade_regression_corpus.py (8 tests) and test_qc_binding_self_check.py (6 tests)
- Green-by-emptiness guard: src/gzkit/governance/trust_audits/qc_binding.py gained _NEGATIVE_CONTROL_DEBT (33 acknowledged steps), genuine qc-binding NC, and the guard that fails any unwired/unacknowledged bound step
- Coupled-surface coherence (rule 1a): migrated test_qc_binding_scope.py contract test to the wired-or-acknowledged contract
- Scorecard fix: Baseline Selected 6->7 to reconcile the Final Target formula with the operator-directed OBPI-08 addition

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

- **OBPI-02 correction — negative-control coverage debt.** OBPI-0.0.73-02's checklist promised "each step ships a fixture it must fail on; the scope runs it", but its implementation shipped the NC infrastructure with an empty registry and deferred real wiring to OBPI-06. This OBPI wires the `qc-binding` step it owns and installs a green-by-emptiness guard so the gate can no longer pass on zero coverage; the remaining 33 `bound` steps are enumerated in the acknowledged `_NEGATIVE_CONTROL_DEBT` constant (`src/gzkit/governance/trust_audits/qc_binding.py`). That constant IS the tracking surface — the self-check fails if a step leaves it without being wired. Authoring honest negative controls for those 33 steps is tracked OBPI-02 correction work (operator-directed routing, 2026-06-18; see `.gzkit/insights/agent-insights.jsonl`).

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.73-06 self-check + facade regression corpus verified: gz adr fidelity ADR-0.0.73 green (5/5 pass), gz validate --qc-binding exit 0 (no theater), gz validate --documents exit 0, 6265/6265 unittests pass (receipt arb-step-unittest-d7ef711909cd469d8d87e9231356cafc); six theater-signature fixtures detected, green-by-emptiness guard wired with genuine qc-binding negative control.
- Date: 2026-06-18
- **REPUDIATED:** 2026-06-19 (attestor: g0; cause: recovery-freeze) — self-check completion was invalid because it accepted acknowledged `_NEGATIVE_CONTROL_DEBT` as green. The runtime now fails closed on that debt; this OBPI requires re-work after OBPI-02 repairs the missing controls.

---

**Date Completed:** 2026-06-18

**Evidence Hash:** -
