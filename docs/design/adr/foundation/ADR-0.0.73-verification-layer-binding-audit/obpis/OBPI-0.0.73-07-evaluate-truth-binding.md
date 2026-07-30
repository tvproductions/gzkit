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

`gz adr evaluate` stops PRESENTING prose SHAPE as authoritative SUBSTANCE — the
defect GHI #624 named and the prior completion of this OBPI faked (repudiated
2026-06-19: docstrings claimed substance grading while the bodies graded keyword
regex / word-count). The honest contract, in three composing parts:

- **A — demote-and-decouple.** The deterministic evaluator (dim-1 Problem Clarity,
  dim-2 Decision Justification, and the rest) grades STRUCTURAL COMPLETENESS only —
  section presence, depth, references — and is labelled as such. No deterministic
  score (keyword, word-count, or regex) is presented as a substance/quality verdict;
  the scorecard and CLI declare structural-completeness scope and carry a
  do-not-composite disclaimer.
- **B — genuine substance channel.** Decision substance is graded ONLY by a recorded,
  disciplined judge verdict (the record-and-validate judge flow,
  `gzkit.adr_eval_substance`; no live LLM call). Absent a verdict, substance is
  reported `UNGRADED` — never derived from shape. The two channels carry distinct
  labels and are never composited.
- **C — self-binding.** `gz adr evaluate` self-registers as an `advisory` QC step that
  `gz validate --qc-binding` finds binding-honest; the seventh
  `shape-graded-not-substance` theater signature is detected (not silently passed); a
  regression guard pins that the evaluator output never re-asserts shape as
  authoritative substance.

"Done" = the live evaluator renders structural-completeness + an UNGRADED substance
channel (no authoritative quality GO from shape), `gz validate --qc-binding` is green,
and the structural scorers carry no substance claim.

Forced downstream (named, NOT this OBPI): the full judge governance (leakage /
output-discipline / meta-eval validators, JudgeInvocation model — ADR-pool.judge-enforcement-validators) needed
to POPULATE the substance channel; until it lands, substance is honestly UNGRADED.

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
- `docs/user/manpages/adr-evaluate.md` — document the structural-completeness vs substance channels (Heavy-lane docs gate)
- `src/gzkit/adr_eval_substance.py` **CREATE** — the judge-graded substance read-seam (Part B); UNGRADED default, never derived from shape (post-repudiation amendment 2026-06-19, attestor g0)
- `src/gzkit/commands/adr_promote.py` — reframe the `gz adr evaluate` CLI output to structural-completeness + substance channel (coupled CLI surface; post-repudiation amendment 2026-06-19, attestor g0)
- `src/gzkit/eval/scorer.py` — second shape-as-substance surface (`score_adr_eval`); docstring scopes its dims as structural-completeness, not substance (post-repudiation amendment 2026-06-19, attestor g0)
- `tests/test_adr_eval_substance.py` **CREATE** — substance-channel tests: shape can never produce a substance grade (post-repudiation amendment 2026-06-19, attestor g0)
- `tests/test_adr_eval.py` — renderer assertion updated to structural-completeness framing (coupled test surface; post-repudiation amendment 2026-06-19, attestor g0)
- `.gzkit/ledger.jsonl` — command-authored governance events (repudiation, lock, brief reconcile) emitted during the OBPI-07 repair ceremony
- `.claude/plans/OBPI-0.0.73-07-evaluate-truth-binding.md` — the comprehensive A+B+C plan authored for this repair
- `.claude/plans/.plan-audit-receipt-OBPI-0.0.73-07-evaluate-truth-binding.json` — the PASS plan-audit receipt for this repair
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

- [ ] REQ-0.0.73-07-01 [BEHAVIOR]: Given any ADR (rigorous or hollow), when `gz adr evaluate` runs, then decision SUBSTANCE is reported `UNGRADED` unless a recorded, disciplined judge verdict exists — substance is never derived from the deterministic prose analysis. (@covers test in `tests/test_adr_eval_substance.py`)
- [ ] REQ-0.0.73-07-02 [BEHAVIOR]: Given a recorded judge substance verdict (explanation-first rationale >= 50 chars + an `arb-step-judge-*` receipt), when `gz adr evaluate` reads it, then it surfaces that graded verdict; given only an undisciplined or absent record, then the dimension stays `UNGRADED` — a grade requires a disciplined judge verdict, never keyword/format presence. (@covers test in `tests/test_adr_eval_substance.py`)
- [ ] REQ-0.0.73-07-03 [BEHAVIOR]: Given the deterministic dimensions, when `gz adr evaluate` scores them, then they grade STRUCTURAL COMPLETENESS only (section presence/depth) and the rendered scorecard + CLI declare structural-completeness scope with a do-not-composite disclaimer — never an authoritative quality/substance GO. (@covers tests in `tests/governance/test_adr_eval_truth_binding.py` and `tests/test_adr_eval.py`)
- [ ] REQ-0.0.73-07-04 [BEHAVIOR]: Given the QC-step registry, then `gz adr evaluate` self-registers as `advisory` and `gz validate --qc-binding` reports no binding-mismatch for it; and the seventh `shape-graded-not-substance` theater signature is detected on a flagged step (it does not silently pass). (@covers test in `tests/governance/test_adr_eval_truth_binding.py`)
- [ ] REQ-0.0.73-07-05 [SUPPORT]: The demote-and-decouple rescore + the substance channel land. Proof: `gz validate --documents` exit 0 + `artifact_edited` ledger event for `src/gzkit/adr_eval_scoring.py` and `src/gzkit/adr_eval_substance.py`.
- [ ] REQ-0.0.73-07-06 [STRUCTURAL-FENCE]: `gz adr evaluate` never presents shape as authoritative substance — substance is judge-graded or `UNGRADED`, the channels are distinct and never composited, and the evaluator is a registered QC step subject to `gz validate --qc-binding` (parent ADR § Boundary Invariants #6, reworded 2026-06-19).
- [ ] REQ-0.0.73-07-07 [SUPPORT]: The structural-completeness vs substance-channel contract is documented in the manpage and `gz cli audit` is green. Proof: `gz validate --cli-alignment` exit 0 + `artifact_edited` ledger event for `docs/user/manpages/adr-evaluate.md`.

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



`uv run gz adr evaluate ADR-0.0.73-verification-layer-binding-audit` now renders "ADR structural completeness: ... STRUCTURALLY COMPLETE / Structural-completeness score: 3.55/4.0 / Substance: 0 graded, 2 UNGRADED (substance is judge-graded, never derived from the above)" — the same 3.55 that was the distrusted false GO, now honestly structural with substance UNGRADED. `uv run gz validate --qc-binding` exits 0 (evaluator binding-honest, no theater). Receipts: arb-step-unittest-e87b1fd709874362ba24ddc4699e52b9 (6297 pass), arb-ruff-b64753ca47064e68b91323e8183389b9, arb-step-typecheck-773838b5d89c487a8742ddce06288222.

### Implementation Summary



- Defect eradicated: gz adr evaluate no longer presents keyword/word-count shape as authoritative substance (GHI #624); the false "3.55/GO" is now an honest "3.55 STRUCTURALLY COMPLETE / Substance UNGRADED"
- Part A (demote-and-decouple): adr_eval_scoring.py dim-1/dim-2 substance-claiming docstrings stripped to honest structural-completeness; adr_eval.py renderer + adr_promote.py CLI reframed with a do-not-composite disclaimer; second scorer eval/scorer.py scoped honest
- Part B (substance channel): src/gzkit/adr_eval_substance.py CREATE — judge-graded read-seam, UNGRADED default, never derived from shape
- Part C (self-binding): seventh theater signature + regression guard test pinning the eradication against revert
- Governance: ADR-0.0.73 Boundary Invariant #6 reworded to the honest contract; OBPI-07 brief Objective/REQs repointed to A+B+C; manpage rewritten
- Prior cosmetic completion repudiated 2026-06-19 (verification-invalid, attestor g0)
- Files created: adr_eval_substance.py, tests/test_adr_eval_substance.py; modified: adr_eval.py, adr_eval_scoring.py, adr_promote.py, eval/scorer.py, test_adr_eval_truth_binding.py, test_adr_eval.py, ADR-0.0.73, manpage
- Tests: 6297 unittests green; 7 substance-channel tests; full repo green (ruff, typecheck, documents, cli-alignment, qc-binding, mkdocs --strict)
- Date completed: 2026-06-19
- Attestation status: operator-attested (g0)
- Forced downstream (named): full judge governance (leakage/output-discipline/meta-eval, JudgeInvocation model — ADR-pool.judge-enforcement-validators) to POPULATE the substance channel

## Tracked Defects

- REQ-count drift: 3 declared vs 7 acceptance criteria (brief reconcile, attestor g0)

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

- GHI #624 — `gz adr evaluate` dim-1/dim-2 score prose shape & keywords, not decision truth; homed into this OBPI as the first caught instance of the verification-layer binding-mismatch class.

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.73-07 eradicates the shape-as-substance defect in gz adr evaluate (GHI #624). The deterministic evaluator is demoted to an honest structural-completeness lint (no substance-claiming docstrings; scorecard + CLI carry a do-not-composite disclaimer); decision substance is a separate judge-graded channel (src/gzkit/adr_eval_substance.py), UNGRADED absent a disciplined judge verdict and never derived from shape; the two channels are decoupled and never composited; the evaluator self-registers advisory and passes gz validate --qc-binding. Verified green across the full repo: 6297 unittests (arb-step-unittest-e87b1fd709874362ba24ddc4699e52b9), ruff (arb-ruff-b64753ca47064e68b91323e8183389b9), typecheck (arb-step-typecheck-773838b5d89c487a8742ddce06288222), gz validate --documents, --cli-alignment, --qc-binding, mkdocs --strict exit 0. Boundary Invariant #6 reworded to the honest contract; the prior cosmetic completion was repudiated 2026-06-19 (verification-invalid, g0).
- Date: 2026-06-19

---

**Date Completed:** 2026-06-19

**Evidence Hash:** -
</content>
</invoke>
