---
id: OBPI-0.0.39-02-judge-invocation-schema
parent: ADR-0.0.39-llm-as-judge-doctrine
item: 2
lane: Heavy
status: Draft
allowlist:
- docs/design/adr/foundation/ADR-0.0.39-llm-as-judge-doctrine/**
- src/gzkit/governance/judge_invocation.py
- src/gzkit/schemas/judge_invocation.json
- src/gzkit/arb/validator.py
- tests/governance/test_judge_invocation_schema.py
- tests/arb/test_judge_receipt_validation.py
- features/governance/llm_as_judge_schema.feature
- data/judge_axis_enums.json
reqs:
- REQ-0.0.39-02-01
- REQ-0.0.39-02-02
- REQ-0.0.39-02-03
- REQ-0.0.39-02-04
- REQ-0.0.39-02-05
- REQ-0.0.39-02-06
- REQ-0.0.39-02-07
- REQ-0.0.39-02-08
- REQ-0.0.39-02-09
- REQ-0.0.39-02-10
- REQ-0.0.39-02-11
- REQ-0.0.39-02-12
verification:
- uv run -m unittest tests/governance/test_judge_invocation_schema.py -v
- uv run -m unittest tests/arb/test_judge_receipt_validation.py -v
- uv run -m behave features/governance/llm_as_judge_schema.feature
- uv run python -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); from gzkit.governance.judge_invocation import JudgeInvocation; import json; pydantic_schema = JudgeInvocation.model_json_schema(); committed = json.load(open('src/gzkit/schemas/judge_invocation.json')); assert pydantic_schema == committed, 'schema drift'; print('schema parity ok')"
- uv run gz cli audit
- uv run gz lint
- uv run gz typecheck
- uv run gz validate --documents
- uv run mkdocs build --strict
---

# OBPI-0.0.39-02-judge-invocation-schema: Judge-Invocation Declaration Schema

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.39-llm-as-judge-doctrine/ADR-0.0.39-llm-as-judge-doctrine.md`
- **Checklist Item:** #2 — `judge-invocation-schema` — Define `JudgeInvocation` Pydantic model + JSON Schema mirror; extend ARB receipt validator to require these fields on judge-prefixed receipts.

**Status:** Draft

## Objective

Define the canonical `JudgeInvocation` declaration schema as the mechanical surface for the survey-aligned invariants 5–8 from ADR-0.0.39 § Decision. Author the frozen Pydantic model (`SurfaceAxis`-like enum patterns), the JSON Schema mirror, and the receipt-shape extension so that judge-prefixed receipts (`arb-step-judge-*`) are validated against this schema at emit time. The schema lands the contract; the validators that fire on the contract land in ADR-0.0.40.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.39-llm-as-judge-doctrine/**` — parent ADR package
- `src/gzkit/governance/judge_invocation.py` (new) — Pydantic models (`JudgeInvocation`, `BiasMitigations`, `CandidateProvenance`) + axis enums
- `src/gzkit/schemas/judge_invocation.json` (new) — JSON Schema mirror
- `src/gzkit/arb/validator.py` — extend ARB receipt validator to recognize judge-prefixed receipts and validate against the schema; reserve canonical step prefixes
- `tests/governance/test_judge_invocation_schema.py` (new) — REQ-derived assertions
- `tests/arb/test_judge_receipt_validation.py` (new) — receipt validator integration tests
- `features/governance/llm_as_judge_schema.feature` (new) — BDD scenarios tagged `@REQ-0.0.39-02-NN`
- `data/judge_axis_enums.json` (new) — single source of truth for the three-axis enum values (referenced by the JSON Schema and the Pydantic model via load-and-validate)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `.gzkit/rules/llm-as-judge.md` — rule body authored under OBPI-0.0.39-01; this OBPI may not edit it
- `artifacts/audits/judge-surface-classification-*.md` — produced under OBPI-0.0.39-03
- `gz validate --judge-leakage` / `gz validate --judge-output-discipline` / `judge meta-eval` — these CLI surfaces land under ADR-0.0.40, NOT here. This OBPI may NOT register new validator scopes or new top-level CLI verbs.
- `data/judge_meta_eval_floor.json` — meta-eval floor configuration is ADR-0.0.40's scope
- `data/judge_leakage_waivers.json` — leakage waiver registry is ADR-0.0.40's scope
- New runtime dependencies
- CI files, lockfiles

## Creates These Files

- `src/gzkit/governance/judge_invocation.py` — **CREATE** Pydantic models (`JudgeInvocation`, `BiasMitigations`, `CandidateProvenance`) + axis enums
- `src/gzkit/schemas/judge_invocation.json` — **CREATE** JSON Schema mirror of `JudgeInvocation`
- `data/judge_axis_enums.json` — **CREATE** single-source-of-truth enum/literal vocabulary
- `tests/governance/test_judge_invocation_schema.py` — **CREATE** REQ-derived schema assertions
- `tests/arb/test_judge_receipt_validation.py` — **CREATE** receipt-validator integration tests
- `features/governance/llm_as_judge_schema.feature` — **CREATE** BDD scenarios tagged `@REQ-0.0.39-02-NN`

Existing files modified: `src/gzkit/arb/validator.py` (extend to route judge-prefixed receipts).

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `src/gzkit/governance/judge_invocation.py` defines `JudgeInvocation` as a frozen Pydantic `BaseModel` (`ConfigDict(frozen=True, extra="forbid")`) with the fields enumerated in ADR-0.0.39 § "Judge-invocation declaration schema". Field order in the class definition matches the schema (judge_model, judge_model_family, candidate_provenance, what_axis, how_axis, where_axis, methodology, methodology_rationale, bias_mitigations, explanation_text, verdict, prompt_hash, input_hash, receipt_id, timestamp).
2. REQUIREMENT: `JudgeInvocation` field types are explicit per `.gzkit/rules/models.md`: `str`, `str | None`, frozen sub-model `CandidateProvenance`, frozen sub-model `BiasMitigations`. No `Optional`/`List`; PEP 604 `|` syntax.
3. REQUIREMENT: `WhatAxis`, `HowAxis`, `WhereAxis` are string `Enum` types (or `Literal[...]` unions) with the initial enum values from ADR-0.0.39 § Invariant 5. Adding a value requires foundation-kind ADR amendment per the rule file (OBPI-0.0.39-01).
4. REQUIREMENT: `BiasMitigations` is a frozen Pydantic sub-model with four required fields (position_bias, verbosity_bias, self_preference, preference_leakage), each typed as `Literal["order-randomized", "order-swept", "length-normalized", "length-controlled", "cross-family", "same-family-waived", "n/a"]` or a per-bias `Literal` union of allowed values per ADR-0.0.39 § Invariant 6.
5. REQUIREMENT: `CandidateProvenance` is a frozen Pydantic sub-model with `model: str`, `model_family: str`, `training_relationship: str | None` (Literal: `"same-family" | "ancestor" | "sibling" | "unrelated" | None`).
6. REQUIREMENT: `explanation_text` field has Pydantic constraint `min_length=50` per ADR-0.0.39 § Invariant 8 (default trivial-floor); the constraint is configurable via `data/judge_axis_enums.json` `explanation_min_length` key but defaults to 50.
7. REQUIREMENT: `src/gzkit/schemas/judge_invocation.json` is the JSON Schema mirror of `JudgeInvocation`; `additionalProperties: false`; field order in the schema's `required` array matches the Pydantic class definition; enums in the schema match the Python enums byte-for-byte.
8. REQUIREMENT: `data/judge_axis_enums.json` is the single source of truth for the three-axis enum values plus the bias-mitigations Literal vocabulary plus the `explanation_min_length` configurable. It is loaded by both the Pydantic model (via importable constant) and the JSON Schema (via reference). A test asserts the Python enum and the JSON Schema enum match the JSON file's contents byte-for-byte.
9. REQUIREMENT: `src/gzkit/arb/validator.py` is extended to recognize receipts whose `step_name` starts with `judge-` and validate the receipt's payload against `judge_invocation.json`. Receipts failing schema validation are rejected at emit time per the existing ARB middleware contract — the existing failure path is reused, not a new one. Reserved canonical step prefixes (`arb-step-judge-leakage-*`, `arb-step-judge-output-discipline-*`, `arb-step-judge-meta-eval-*`) are added to `CANONICAL_STEP_COMMANDS` so that ADR-0.0.40's validators have slots; the slots are reserved in this OBPI but the corresponding CLI verbs are NOT added.
10. REQUIREMENT: `tests/governance/test_judge_invocation_schema.py` asserts: (a) compliant invocations validate against both Pydantic and JSON Schema; (b) missing required fields fail with named-field error; (c) off-enum values for what/how/where axes fail; (d) `explanation_text` shorter than 50 chars fails with `min_length` error; (e) the JSON enum file's values exactly match the Pydantic enum.
11. REQUIREMENT: `tests/arb/test_judge_receipt_validation.py` asserts: (a) judge-prefixed receipts are routed to schema validation; (b) compliant receipts pass; (c) non-compliant receipts are rejected with a diagnostic naming the failing field; (d) non-judge receipts (other ARB step prefixes) pass through unchanged.
12. REQUIREMENT: `features/governance/llm_as_judge_schema.feature` defines BDD acceptance scenarios for Gate 4 covering: emitting a compliant judge receipt; rejecting a receipt with empty explanation_text; rejecting a receipt with off-enum what_axis; rejecting a receipt declaring same-family-waived without a corresponding waiver-registry entry (ADR-0.0.40 will add the waiver registry; for this OBPI, the feature scenario asserts the rejection mechanism but the waiver-registry side is fixture-stubbed).
13. REQUIREMENT: `gz cli audit` exits 0 after this OBPI lands — no new top-level verb is added, only the schema validator path inside ARB. The schema landing is invisible at the CLI verb-roster surface.
14. REQUIREMENT: NEVER add `gz validate --judge-leakage`, `gz validate --judge-output-discipline`, `judge meta-eval`, or any other new validator scope or CLI verb in this OBPI. Those land under ADR-0.0.40. Adding them here is a brief-boundary violation per AGENTS.md § Behavior Rules — Never #5.
15. REQUIREMENT: NEVER backfill receipts from existing judge surfaces in this OBPI; the existing-surface retrofit is OBPI-0.0.40-05's scope. Existing red-team receipts emitted before this OBPI lands continue to validate under their pre-schema shape; the new schema applies only to receipts emitted after the schema lands.
16. REQUIREMENT: Pydantic and JSON Schema MUST stay in lockstep — a test asserts `JudgeInvocation.model_json_schema()` matches the committed `judge_invocation.json` byte-for-byte (modulo formatting whitespace per a documented normalization step). Drift is fail-closed.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.39-llm-as-judge-doctrine/ADR-0.0.39-llm-as-judge-doctrine.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.39-llm-as-judge-doctrine/ADR-0.0.39-llm-as-judge-doctrine.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.39-llm-as-judge-doctrine/**`
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
uv run -m unittest tests/governance/test_judge_invocation_schema.py -v
uv run -m unittest tests/arb/test_judge_receipt_validation.py -v

# BDD scenarios (Gate 4)
uv run -m behave features/governance/llm_as_judge_schema.feature

# Lockstep test (Pydantic ↔ JSON Schema parity)
uv run python -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); from gzkit.governance.judge_invocation import JudgeInvocation; import json; pydantic_schema = JudgeInvocation.model_json_schema(); committed = json.load(open('src/gzkit/schemas/judge_invocation.json')); assert pydantic_schema == committed, 'schema drift'; print('schema parity ok')"

# CLI surface unchanged at this OBPI
uv run gz cli audit

# Standard heavy-lane gates
uv run gz lint
uv run gz typecheck
uv run gz validate --documents
uv run mkdocs build --strict

# Confirm canonical artifacts exist
test -f src/gzkit/governance/judge_invocation.py
test -f src/gzkit/schemas/judge_invocation.json
test -f data/judge_axis_enums.json
test -f features/governance/llm_as_judge_schema.feature
grep -q "arb-step-judge-leakage" src/gzkit/arb/validator.py
grep -q "arb-step-judge-output-discipline" src/gzkit/arb/validator.py
grep -q "arb-step-judge-meta-eval" src/gzkit/arb/validator.py
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.39-02-01: Given `from gzkit.governance.judge_invocation import JudgeInvocation`, when imported, then `JudgeInvocation` is a frozen Pydantic BaseModel with `extra="forbid"` and the fields named in ADR-0.0.39 § "Judge-invocation declaration schema" in the documented order.
- [ ] REQ-0.0.39-02-02: Given a compliant invocation dict, when validated against the JSON Schema and the Pydantic model, then both pass and produce the same parsed object.
- [ ] REQ-0.0.39-02-03: Given an invocation missing `explanation_text`, when validated, then validation fails with a named-field error per `min_length` constraint or per `required` constraint.
- [ ] REQ-0.0.39-02-04: Given an invocation with `what_axis` set to a value outside the enum, when validated, then validation fails with an enum-mismatch diagnostic naming the field.
- [ ] REQ-0.0.39-02-05: Given `data/judge_axis_enums.json`, when read by both the Pydantic enum loader and the JSON Schema reference resolver, then the resulting enum values are byte-identical.
- [ ] REQ-0.0.39-02-06: Given an ARB receipt whose step name starts with `judge-`, when emitted, then the receipt validator routes the payload to schema validation against `judge_invocation.json` and rejects on schema failure.
- [ ] REQ-0.0.39-02-07: Given an ARB receipt whose step name does NOT start with `judge-`, when emitted, then the existing receipt validator path applies unchanged (no schema-routing regression).
- [ ] REQ-0.0.39-02-08: Given `CANONICAL_STEP_COMMANDS`, when read, then `arb-step-judge-leakage-*`, `arb-step-judge-output-discipline-*`, and `arb-step-judge-meta-eval-*` slots are reserved (the corresponding CLI verbs do not exist yet — those land under ADR-0.0.40).
- [ ] REQ-0.0.39-02-09: Given the `JudgeInvocation.model_json_schema()` output, when compared to the committed `judge_invocation.json`, then the two are byte-identical (modulo documented normalization).
- [ ] REQ-0.0.39-02-10: Given `gz cli audit`, when run after this OBPI lands, then exit code is 0 and no new top-level verbs appear in the verb roster (the schema landing is invisible at the verb surface).
- [ ] REQ-0.0.39-02-11: Given `features/governance/llm_as_judge_schema.feature`, when run via `uv run -m behave`, then all scenarios pass with `@REQ-0.0.39-02-NN` tags covering the requirement set above.
- [ ] REQ-0.0.39-02-12: Given the Denied Paths boundary, when this OBPI's diff is reviewed, then no `gz validate --judge-leakage`, `--judge-output-discipline`, or `judge meta-eval` CLI verb is registered, no leakage waiver registry is added, no meta-eval floor file is added — those scopes belong to ADR-0.0.40.

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
