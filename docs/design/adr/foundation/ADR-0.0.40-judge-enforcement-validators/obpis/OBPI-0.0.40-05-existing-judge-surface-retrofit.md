---
id: OBPI-0.0.40-05-existing-judge-surface-retrofit
parent: ADR-0.0.40-judge-enforcement-validators
item: 5
lane: Heavy
status: Draft
---

# OBPI-0.0.40-05-existing-judge-surface-retrofit: Existing-Judge-Surface Retrofit (Compliance Close)

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.40-judge-enforcement-validators/ADR-0.0.40-judge-enforcement-validators.md`
- **Checklist Item:** #5 — `existing-judge-surface-retrofit` — Update `gz-adr-evaluate --red-team` to populate JudgeInvocation fields; update `CLAUDE.md` § Advisor Tool with bias profile and named "do not invoke" cases; backfill historical receipts via waiver registry; mark dependent pool ADRs as governed-by-ADR-0.0.40.

**Status:** Draft

## Objective

Close the existing-judge-surface compliance gap. Update `src/gzkit/commands/adr_evaluate.py` red-team path so every emitted ARB receipt populates the full `JudgeInvocation` schema (judge_model, judge_model_family, candidate_provenance, methodology=`red-team-challenge`, what_axis, how_axis, where_axis, bias_mitigations honestly recorded — almost certainly `position_bias: n/a, verbosity_bias: n/a, self_preference: same-family-waived, preference_leakage: same-family-waived` for current red-team behavior, with corresponding waivers added to `data/judge_leakage_waivers.json` for the receipts going forward; the gap is to be closed in a future feature ADR with cross-family judging). Document the runtime `advisor()` tool's bias profile in `CLAUDE.md` § Advisor Tool with explicit "do not invoke" cases (peer review of own prior reasoning; same-family preference-leakage failure-mode tests). Backfill historical receipts via waivers with cited reason `pre-ADR-0.0.40-baseline`. Mark dependent pool ADRs (`attestation-advisory-agent`, `lightweight-pre-implementation-challenger`) as `governed_by: ADR-0.0.40-judge-enforcement-validators` — they remain in pool until later promotion but inherit the validators rather than re-deriving.

This is the **highest-risk OBPI** of ADR-0.0.40 per the parent ADR § Rationale Claim 3. Honest gap-recording is fail-closed; concealing a mitigation gap to ship faster reproduces the doctrine-drift class the survey paper names. Gate 5 walkthrough requires operator confirmation that each gap is recorded honestly.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.40-judge-enforcement-validators/**` — parent ADR package
- `src/gzkit/commands/adr_evaluate.py` — red-team path: populate JudgeInvocation receipt fields on emit
- `src/gzkit/commands/adr_evaluate.py`'s rubric-scoring path — also populate JudgeInvocation receipt fields (same surface)
- `CLAUDE.md` — § Advisor Tool with bias profile + named "do not invoke" cases
- `data/judge_leakage_waivers.json` — backfill historical-receipt waivers with reason `pre-ADR-0.0.40-baseline`
- `docs/design/adr/pool/ADR-pool.attestation-advisory-agent.md` — add `governed_by: ADR-0.0.40-judge-enforcement-validators`
- `docs/design/adr/pool/ADR-pool.lightweight-pre-implementation-challenger.md` — add `governed_by: ADR-0.0.40-judge-enforcement-validators`
- `tests/governance/test_judge_retrofit.py` (new) — REQ-derived assertions on retrofit completeness
- `tests/commands/test_adr_evaluate_judge_invocation.py` (new) — assertions that red-team and rubric-scoring receipts populate JudgeInvocation correctly

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/arb/validator.py`, `src/gzkit/arb/middleware.py` — OBPI-0.0.40-01's
- `src/gzkit/governance/judge_invocation.py`, `src/gzkit/schemas/judge_invocation.json` — OBPI-0.0.39-02's
- `src/gzkit/governance/judge_leakage.py`, `data/judge_model_families.json` — OBPI-0.0.40-02's
- `src/gzkit/governance/judge_output_discipline.py` — OBPI-0.0.40-03's
- `src/gzkit/commands/judge_meta_eval.py`, `data/judge_meta_eval_floor.json` — OBPI-0.0.40-04's
- `.gzkit/rules/llm-as-judge.md` — OBPI-0.0.39-01's
- New runtime dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `src/gzkit/commands/adr_evaluate.py` red-team path is updated so every emitted ARB receipt under `arb-step-judge-*` prefix populates the full `JudgeInvocation` schema (per OBPI-0.0.39-02 contract). Required fields populated: `judge_model`, `judge_model_family`, `candidate_provenance.{model, model_family, training_relationship}`, `methodology=red-team-challenge`, `methodology_rationale`, `what_axis=red-team-challenge`, `how_axis=red-team-challenge`, `where_axis=adr-evaluation`, `bias_mitigations.{position_bias, verbosity_bias, self_preference, preference_leakage}`, `explanation_text`, `verdict`, `prompt_hash`, `input_hash`, `receipt_id`, `timestamp`.
2. REQUIREMENT: The same retrofit applies to `adr_evaluate.py`'s rubric-scoring path. Field values: `methodology=criteria-decomposed`, `methodology_rationale="decomposed across N named criteria with per-criterion verdict per ADR-0.0.39 § Invariant 7"`, `what_axis=adr-rationale` or `obpi-feasibility` depending on which rubric runs, `how_axis=criteria-decomposed`, `where_axis=adr-evaluation`.
3. REQUIREMENT: The retrofit MUST honestly record current bias profile. For today's gz-adr-evaluate red-team and rubric-scoring (which run same-model-family judging without order-randomization or length-normalization): `position_bias: n/a` (single-pass, not pairwise), `verbosity_bias: n/a` (no length-variability), `self_preference: same-family-waived`, `preference_leakage: same-family-waived`. The "waived" status requires corresponding waivers in `data/judge_leakage_waivers.json` with cited reason `current-state-baseline-pending-cross-family-feature-ADR` and `expires_after` set to 6 months out (forcing future ADR work to address the gap).
4. REQUIREMENT: NEVER record a bias mitigation status that does not match observed behavior. If the prompt does not actually elicit explanation before verdict, do NOT record `explanation_text` populated — fix the prompt template instead. The honest-recording requirement is fail-closed at Gate 5.
5. REQUIREMENT: `CLAUDE.md` § Advisor Tool is updated with a new "Bias Profile" subsection declaring: `judge_model_family` (typically claude-opus-4 in operator's session); `candidate_provenance.training_relationship` (typically same-family in operator-self-judging context); applicable biases (preference leakage, self-preference); applicable mitigations (none, today; this is a known gap pending cross-family advisor architecture).
6. REQUIREMENT: `CLAUDE.md` § Advisor Tool is updated with a new "Do Not Invoke" subsection naming explicit anti-cases: (a) peer review of own prior reasoning in the same conversation (the advisor sees the operator's reasoning context and is biased toward agreeing with whatever framing the operator already established); (b) failure-mode testing where the failure under test is preference leakage (invoking advisor to "check" for leakage when advisor itself is the leakage source); (c) any case where the operator has already drafted a conclusion and is seeking validation rather than challenge.
7. REQUIREMENT: Historical receipts emitted under `arb-step-judge-*` prefixes prior to this ADR's close are backfilled with waivers in `data/judge_leakage_waivers.json`. Each waiver covers a `receipt_pattern` (glob matching the historical receipts), `reason: "pre-ADR-0.0.40-baseline; receipts emitted before retrofit lands"`, `cited_authority: "ADR-0.0.40-judge-enforcement-validators"`, `expires_after: null` (permanent waiver — historical receipts are immutable).
8. REQUIREMENT: `ADR-pool.attestation-advisory-agent` frontmatter is updated with `governed_by: ADR-0.0.40-judge-enforcement-validators` (the validator-set governs; the doctrine ADR-0.0.39 also governs but is referenced via the validator-set's enabler).
9. REQUIREMENT: `ADR-pool.lightweight-pre-implementation-challenger` frontmatter is updated with `governed_by: ADR-0.0.40-judge-enforcement-validators` (same as #8).
10. REQUIREMENT: After this OBPI's edits land, `uv run gz validate --judge-leakage` passes (because the waivers cover the same-family pairs); `uv run gz validate --judge-output-discipline` passes (because the receipts now populate all required fields). Both validator runs become CI-stable from this point forward.
11. REQUIREMENT: `tests/governance/test_judge_retrofit.py` asserts: (a) every receipt emitted by adr_evaluate.py red-team/rubric paths populates all JudgeInvocation fields; (b) `data/judge_leakage_waivers.json` contains at least one waiver with reason `pre-ADR-0.0.40-baseline` AND at least one with reason `current-state-baseline-pending-cross-family-feature-ADR`; (c) the two pool ADRs carry `governed_by: ADR-0.0.40-...` frontmatter; (d) `CLAUDE.md` contains a § Advisor Tool subsection with "Bias Profile" and "Do Not Invoke" headings.
12. REQUIREMENT: `tests/commands/test_adr_evaluate_judge_invocation.py` asserts a single end-to-end red-team invocation produces a receipt that validates against `judge_invocation.json` per OBPI-0.0.39-02's emit-time validator (i.e., the receipt would not be rejected at ARB middleware emit).
13. REQUIREMENT: Gate 5 attestation walkthrough is mandatory and includes operator confirmation that: (a) the retrofit's bias-profile recording for red-team is honest (operator quotes the recorded `position_bias`, `verbosity_bias`, `self_preference`, `preference_leakage` values and confirms they match observed behavior); (b) the `expires_after: 6-months-out` waivers genuinely create pressure to land a follow-up cross-family feature ADR; (c) the CLAUDE.md "Do Not Invoke" cases match the operator's intuition about advisor() limitations.
14. REQUIREMENT: NEVER conceal a mitigation gap to ship faster. If observed red-team behavior has no order-randomization, the bias profile records `position_bias: n/a` (because not pairwise) — but if it WERE pairwise without randomization, the recording would be `position_bias: <missing>` and the retrofit would have to fix the prompt template before completing. The retrofit's purpose is honest snapshot + waiver-with-expiration to force follow-up; it is NOT cosmetic compliance.
15. REQUIREMENT: NEVER add or modify validators, schemas, ARB middleware, or any other surface outside this OBPI's allowlist. Five OBPIs in the ADR; each has a strict scope.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.40-judge-enforcement-validators/ADR-0.0.40-judge-enforcement-validators.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.40-judge-enforcement-validators/ADR-0.0.40-judge-enforcement-validators.md`
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/commands/adr_evaluate.py`
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
     outputs into Evidence. -->

```bash
# OBPI-specific tests
uv run -m unittest tests/governance/test_judge_retrofit.py -v
uv run -m unittest tests/commands/test_adr_evaluate_judge_invocation.py -v

# Standard heavy-lane gates
uv run gz lint
uv run gz typecheck
uv run gz validate --documents
uv run mkdocs build --strict
uv run -m behave features/

# After retrofit, the validators from -02 and -03 must pass
uv run gz validate --judge-leakage
uv run gz validate --judge-output-discipline

# End-to-end emit test: one red-team run produces a compliant receipt
uv run gz adr evaluate ADR-0.0.40 --red-team
ls artifacts/receipts/arb-step-judge-*

# Confirm pool ADR frontmatter updates
grep -q "governed_by: ADR-0.0.40" docs/design/adr/pool/ADR-pool.attestation-advisory-agent.md
grep -q "governed_by: ADR-0.0.40" docs/design/adr/pool/ADR-pool.lightweight-pre-implementation-challenger.md

# Confirm CLAUDE.md updates
grep -q "Bias Profile" CLAUDE.md
grep -q "Do Not Invoke" CLAUDE.md

# Confirm waivers exist with the correct reasons
grep -q "pre-ADR-0.0.40-baseline" data/judge_leakage_waivers.json
grep -q "current-state-baseline-pending-cross-family-feature-ADR" data/judge_leakage_waivers.json

# ARB receipt for retrofit attestation
uv run gz arb step --name judge-retrofit-baseline -- echo "retrofit baseline complete"
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers. The closeout
     ceremony walkthrough harvests this section (parser-validated;
     unregistered verbs are dropped). Prefer real paths and arguments
     over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Replace with concrete product demonstrations for this OBPI.
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.40-05-01: Given a single end-to-end `gz adr evaluate <ADR-ID> --red-team` invocation, when run after this OBPI, then the emitted ARB receipt populates all `JudgeInvocation` fields and validates against `judge_invocation.json` at emit time.
- [ ] REQ-0.0.40-05-02: Given a single `gz adr evaluate <ADR-ID>` rubric-scoring invocation, when run, then the emitted receipt populates all `JudgeInvocation` fields with `methodology=criteria-decomposed` and `where_axis=adr-evaluation`.
- [ ] REQ-0.0.40-05-03: Given the bias-profile recording in emitted receipts, when reviewed, then values honestly match observed red-team and rubric behavior — `self_preference: same-family-waived` and `preference_leakage: same-family-waived` are recorded with corresponding waivers in the registry, NOT recorded as `cross-family` (which would be a false claim).
- [ ] REQ-0.0.40-05-04: Given `data/judge_leakage_waivers.json`, when read, then it contains: (a) at least one waiver with reason `pre-ADR-0.0.40-baseline` and `expires_after: null` covering historical receipts; (b) at least one waiver with reason `current-state-baseline-pending-cross-family-feature-ADR` and `expires_after` 6 months out covering current red-team / rubric receipts.
- [ ] REQ-0.0.40-05-05: Given `CLAUDE.md` after this OBPI, when read, then § Advisor Tool contains a "Bias Profile" subsection naming applicable biases and a "Do Not Invoke" subsection naming at least three explicit anti-cases (peer review of own reasoning; failure-mode tests where the failure is leakage; confirmation-seeking).
- [ ] REQ-0.0.40-05-06: Given `ADR-pool.attestation-advisory-agent.md` and `ADR-pool.lightweight-pre-implementation-challenger.md`, when frontmatter is parsed, then both carry `governed_by: ADR-0.0.40-judge-enforcement-validators`.
- [ ] REQ-0.0.40-05-07: Given `uv run gz validate --judge-leakage` after this OBPI's edits land, when run, then exit code is 0 (the retrofit's recorded same-family waivers cover all current receipts).
- [ ] REQ-0.0.40-05-08: Given `uv run gz validate --judge-output-discipline` after this OBPI, when run, then exit code is 0 (all receipts populate required fields).
- [ ] REQ-0.0.40-05-09: Given the Gate 5 walkthrough, when the operator attests, then the attestation text confirms (a) honest bias-profile recording for red-team and rubric paths; (b) `expires_after` 6-months-out genuinely creates follow-up pressure; (c) "Do Not Invoke" cases match operator intuition.
- [ ] REQ-0.0.40-05-10: Given the attestation text, when validated, then it cites at least one `arb-step-judge-retrofit-baseline-*` receipt OR an `arb-step-surface-axis-baseline-*` receipt for the retrofit's snapshot.
- [ ] REQ-0.0.40-05-11: Given the Denied Paths boundary, when this OBPI's diff is reviewed, then no edits to ARB middleware (-01's), no edits to leakage validator or model-families registry (-02's), no edits to output-discipline validator (-03's), no edits to meta-eval CLI or floor (-04's), no edits to `judge_invocation.py` or `llm-as-judge.md`.
- [ ] REQ-0.0.40-05-12: Given the honest-recording fail-closed requirement, when source is reviewed, then no recorded bias-mitigation status conceals a gap. If observed behavior diverges from recorded status, the OBPI is incomplete (Gate 5 attestation refuses to write).
- [ ] REQ-0.0.40-05-13: Given the cross-family-pending-feature-ADR waiver pressure, when the waiver `expires_after` lands, then a follow-up GHI is filed (or already exists) tracking the cross-family advisor architecture work that closes the gap permanently.

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

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
