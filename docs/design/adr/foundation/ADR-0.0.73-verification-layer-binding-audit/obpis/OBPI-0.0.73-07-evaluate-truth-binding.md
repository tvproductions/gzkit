---
id: OBPI-0.0.73-07-evaluate-truth-binding
parent: ADR-0.0.73-verification-layer-binding-audit
item: 7
lane: Heavy
status: Completed
req_atomic:
  - REQ-0.0.73-07-01  # one cohesive substance-grading rewrite of dim-1/dim-2 in adr_eval_scoring.py — indivisible
  - REQ-0.0.73-07-02  # same dim-1/dim-2 rewrite as REQ-01 (keyword-presence-alone non-lift is the inverse face) — no labor below the REQ
  - REQ-0.0.73-07-03  # one advisory self-registration channel (qc_binding.py) + one registration call — indivisible
  - REQ-0.0.73-07-04  # one signature addition (THEATER_SIGNATURES + description + fixture) authored as a single unit — indivisible
  - REQ-0.0.73-07-05  # SUPPORT: adr_eval_scoring.py lands via gz validate --documents; no labor below the REQ
  - REQ-0.0.73-07-06  # STRUCTURAL-FENCE: parent-ADR Boundary Invariant #6; audited at closeout, no labor
  - REQ-0.0.73-07-07  # SUPPORT: manpage lands via gz validate --cli-alignment + cli audit; no labor below the REQ
---

# OBPI-0.0.73-07-evaluate-truth-binding: Evaluate Truth Binding

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md`
- **Checklist Item:** #7 - "Evaluator truth-binding — replace the `gz adr evaluate` dim-1/dim-2 format/keyword heuristics in `src/gzkit/adr_eval_scoring.py` with decision-substance checks (no truth-score satisfiable by keyword/format presence alone); register `gz adr evaluate` as a QC step classified `advisory` (subject to `gz validate --qc-binding`); add a seventh `shape-graded-not-substance` theater signature to the facade regression corpus; manpage + `gz cli audit` green; unit tests"

**Status:** Completed

## Objective

`gz adr evaluate` stops grading prose SHAPE and KEYWORDS and starts grading
decision SUBSTANCE, and it self-registers as a QC step so the verification-layer
mechanism this ADR introduces governs the evaluator itself. Today the dim-1
(Problem Clarity) and dim-2 (Decision Justification) checks score on
`_has_keywords` substring membership and a numbered-list regex — a facade ADR that
stuffs the keywords scores high while a rigorous ADR phrased without them is
floored to 1 (GHI #624). "Done" = no `gz adr evaluate` truth-score is satisfiable
by keyword/format presence alone, rigorous-but-differently-phrased prose is not
floored, `gz adr evaluate` self-registers as an `advisory` QC step that
`gz validate --qc-binding` finds binding-honest, and a seventh
`shape-graded-not-substance` theater fixture (calibrated on GHI #624, distinct
from the six ADR-0.0.37 signatures) is detected by the regression corpus.

Evaluator truth-binding — replace the `gz adr evaluate` dim-1/dim-2 format/keyword heuristics in `src/gzkit/adr_eval_scoring.py` with decision-substance checks (no truth-score satisfiable by keyword/format presence alone); register `gz adr evaluate` as a QC step classified `advisory` (subject to `gz validate --qc-binding`); add a seventh `shape-graded-not-substance` theater signature to the facade regression corpus; manpage + `gz cli audit` green; unit tests.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/traceability.py` — READ-ONLY: the `@covers` decorator imported by this OBPI's tests (not modified). Declared via brief reconcile (attestor g0) because the reconciler's neighborhood heuristic reports it when allowlisted top-level src/gzkit modules share its parent directory.

- `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md` — parent ADR for intent and scope
- `src/gzkit/adr_eval_scoring.py` — replace the dim-1/dim-2 (and any sibling) format/keyword heuristics with decision-substance checks
- `src/gzkit/adr_eval.py` — adjust the `_has_keywords` helper usage / dimension wiring as the substance checks require
- `src/gzkit/qc_binding.py` — SHARED surface created by OBPI-01 (already landed); extended here with a `register_advisory_qc_step()` self-registration channel so `gz adr evaluate` registers as an `advisory` QC step (the bound-step registry stays derived from `_build_check_steps()`)
- `src/gzkit/governance/trust_audits/qc_binding.py` — add the seventh `shape-graded-not-substance` entry to `THEATER_SIGNATURES` + its description so `_check_theater_signatures` detects the new fixture (allowlist amendment, plan-audit 2026-06-18: REQ-07-04 cannot fire without this coupled surface)
- `tests/governance/test_adr_eval_truth_binding.py` **CREATE** — unit tests for substance scoring, evaluator registration, and corpus detection
- `tests/governance/fixtures/facade_corpus/shape_graded_not_substance.json` **CREATE** — the seventh theater-signature fixture (the `facade_corpus/` dir is created by OBPI-06; `.json` matches the six existing fixtures)
- `tests/governance/test_facade_regression_corpus.py` — extend the corpus regression suite for the seventh signature (the existing `test_all_six_signatures_have_fixtures` count assertion breaks otherwise; allowlist amendment, plan-audit 2026-06-18)
- `docs/user/manpages/adr-evaluate.md` — document substance-grading and QC-step registration (Heavy-lane docs gate)
- `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/obpis/OBPI-0.0.73-07-evaluate-truth-binding.md` — this brief (evidence recording)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: A rigorous ADR phrased WITHOUT the hardcoded dim-1/dim-2 keywords (no literal "before"/"after"/"because", parts not a markdown numbered list) MUST NOT be floored to 1 — dim-1/dim-2 grade decision SUBSTANCE, not keyword/format presence (maps to REQ-0.0.73-07-01).
1. REQUIREMENT: Keyword/format presence ALONE MUST NOT lift the dim-1/dim-2 score — an otherwise-hollow ADR that stuffs the keywords does not score high; no truth-score is satisfiable by keyword presence alone (maps to REQ-0.0.73-07-02).
1. REQUIREMENT: `gz adr evaluate` MUST self-register as a QC step classified `advisory`, and `gz validate --qc-binding` MUST report no binding-mismatch for it (maps to REQ-0.0.73-07-03).
1. REQUIREMENT: The seventh `shape-graded-not-substance` theater-signature fixture MUST be detected by the facade regression corpus — it does not silently pass (maps to REQ-0.0.73-07-04).
1. REQUIREMENT: The evaluator rescore and QC-step registration MUST land as committed surfaces — `gz validate --documents` exits 0 with an `artifact_edited` event for `src/gzkit/adr_eval_scoring.py` (maps to REQ-0.0.73-07-05).
1. REQUIREMENT: No `gz adr evaluate` truth-score MUST be satisfiable by keyword/format presence alone, and `gz adr evaluate` MUST be a registered QC step subject to `gz validate --qc-binding` (Boundary Invariant #6; maps to REQ-0.0.73-07-06).
1. REQUIREMENT: The substance-grading change MUST be documented in the manpage and `gz cli audit` MUST be green — `gz validate --cli-alignment` exits 0 with an `artifact_edited` event for `docs/user/manpages/adr-evaluate.md` (maps to REQ-0.0.73-07-07).
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

- [ ] Related OBPIs in same ADR (OBPI-01 registry, OBPI-02 `--qc-binding` scope, OBPI-06 facade corpus)
- [ ] GHI #624 — the defect this OBPI homes

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md`
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/adr_eval_scoring.py`
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
test -f tests/governance/test_adr_eval_truth_binding.py
test -f tests/governance/fixtures/facade_corpus/shape_graded_not_substance.py
uv run gz adr evaluate ADR-0.0.73-verification-layer-binding-audit
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. The qc-binding scope is unregistered
     until OBPI-02 lands; the skip marker suppresses the command-shape check on
     the fenced block below (GHI #432). -->

<!-- gz-validate-skip: command-shape -->
``bash
# Keyword stuffing no longer lifts a truth-score; rigorous prose is not floored.
uv run gz adr evaluate ADR-0.0.73-verification-layer-binding-audit
# The evaluator is now a registered QC step, binding-honest under qc-binding.
uv run gz validate --qc-binding
``

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.73-07-01 [BEHAVIOR]: Given an ADR whose Decision is rigorous (alternatives weighed, consequences honest, rationale present) but phrased without the hardcoded keywords (no literal "before"/"after"/"because", parts bold-numbered rather than a markdown numbered list), when `gz adr evaluate` scores dim-1 and dim-2, then the scores reflect decision substance and are NOT floored to 1 by keyword/format absence. (@covers test in `tests/governance/test_adr_eval_truth_binding.py`)
- [ ] REQ-0.0.73-07-02 [BEHAVIOR]: Given an otherwise-hollow ADR that stuffs the dim-1/dim-2 keywords (and a markdown numbered list) into its prose, when `gz adr evaluate` scores it, then keyword/format presence ALONE does not lift the dim-1/dim-2 score — no truth-score is satisfiable by keyword presence alone. (@covers test in `tests/governance/test_adr_eval_truth_binding.py`)
- [ ] REQ-0.0.73-07-03 [BEHAVIOR]: Given the QC-step registry, when it is derived from what the evaluation surface runs, then `gz adr evaluate` self-registers as a QC step classified `advisory`, and `gz validate --qc-binding` reports no binding-mismatch for it (it no longer presents shape-graded scores as authoritative truth). (@covers test in `tests/governance/test_adr_eval_truth_binding.py`)
- [ ] REQ-0.0.73-07-04 [BEHAVIOR]: Given the seventh `shape-graded-not-substance` theater-signature fixture added to the facade regression corpus, when `gz validate --qc-binding` runs over the corpus, then the signature is detected (it does not silently pass). (@covers test in `tests/governance/test_adr_eval_truth_binding.py`)
- [ ] REQ-0.0.73-07-05 [SUPPORT]: The evaluator rescore and QC-step registration land. Proof: `gz validate --documents` exit 0 + `artifact_edited` ledger event for `src/gzkit/adr_eval_scoring.py`.
- [ ] REQ-0.0.73-07-06 [STRUCTURAL-FENCE]: No `gz adr evaluate` truth-score is satisfiable by keyword/format presence alone, and `gz adr evaluate` is a registered QC step subject to `gz validate --qc-binding` (parent ADR § Boundary Invariants #6).
- [ ] REQ-0.0.73-07-07 [SUPPORT]: The substance-grading change is documented in the manpage and `gz cli audit` is green. Proof: `gz validate --cli-alignment` exit 0 + `artifact_edited` ledger event for `docs/user/manpages/adr-evaluate.md`.

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


uv run gz adr evaluate ADR-0.0.73-verification-layer-binding-audit --json shows Problem Clarity=4 and Decision Justification=4 (verdict GO) for the rigorous keyword-free ADR — the test fixture proves the old keyword scorer floored identical prose to 1; the hollow keyword-stuffed fixture scores <3 on both dims (TestSubstanceNotShape). gz validate --qc-binding exits 0 with the evaluator self-registered advisory. Receipts: arb-step-unittest-c58e18da75d940bea65ce3d478ae1d2f (6275 pass), arb-ruff-e18e7eeff1a74d35b8beb546c43c0146, arb-step-typecheck-5c4aca73c85b4de189091490f7d07b4a, arb-step-mkdocs-0936d789b32b4e258888f702bff263cc.

### Implementation Summary


- Decision item: Evaluator truth-binding — replaced gz adr evaluate dim-1/dim-2 format/keyword heuristics in src/gzkit/adr_eval_scoring.py with decision-substance checks; registered gz adr evaluate as an advisory QC step; added a seventh shape-graded-not-substance theater signature; manpage + gz cli audit green; unit tests.
- dim-1 (Problem Clarity): replaced the two _has_keywords(before/after) checks with concrete-grounding (_references_concrete_artifacts) and multi-sentence problem-outcome contrast (_substantive_sentence_count); depth threshold raised to 120 words.
- dim-2 (Decision Justification): replaced the numbered-list regex and _has_keywords(because) check with weighed-and-rejected-alternatives (_weighs_rejected_alternatives) and honest-negative-consequences (_acknowledges_negative_consequences); depth threshold 100 words.
- Self-registration: register_advisory_qc_step() + _SELF_REGISTERED_ADVISORY_STEPS in qc_binding.py; build_qc_registry() triggers registration via the safe gzkit.adr_eval import and extends the derived bound registry with the advisory channel.
- Seventh theater signature shape-graded-not-substance added to THEATER_SIGNATURES + description in governance/trust_audits/qc_binding.py, with corpus fixture shape_graded_not_substance.json.
- Coupled-surface coherence: refined 4 OBPI-01/02 registry/signature tests (bound-scope preserved); updated validate.md + adr-evaluate.md manpages.
- Files created: tests/governance/test_adr_eval_truth_binding.py (9 tests), tests/governance/fixtures/facade_corpus/shape_graded_not_substance.json.
- Tests added: 9 truth-binding tests + 1 corpus test; all 6275 unittests pass.
- Date completed: 2026-06-18. Attestation: operator-attested.
- Defects noted: sibling OBPI-05 brief fails gz validate --sensitivity (exit 3) — pre-existing on clean HEAD, out of OBPI-07 scope, recorded in insights.

## Tracked Defects

- REQ-count drift: 3 declared vs 7 acceptance criteria (brief reconcile, attestor g0)

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

- GHI #624 — `gz adr evaluate` dim-1/dim-2 score prose shape & keywords, not decision truth; homed into this OBPI as the first caught instance of the verification-layer binding-mismatch class.

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Heavy-lane foundation OBPI-0.0.73-07 verified: gz adr evaluate dim-1/dim-2 now grade decision substance not keyword/format presence (GHI #624), evaluator self-registers as advisory QC step, seventh shape-graded-not-substance theater signature detected. 6275/6275 unittests pass (receipt arb-step-unittest-c58e18da75d940bea65ce3d478ae1d2f), ruff/typecheck/mkdocs clean, gz validate --qc-binding/--documents/--cli-alignment exit 0, behavior_uncovered_reqs=0.
- Date: 2026-06-18

---

**Date Completed:** 2026-06-18

**Evidence Hash:** -
</content>
</invoke>
