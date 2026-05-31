---
id: OBPI-0.0.40-03-judge-output-discipline-validator
parent: ADR-0.0.40-judge-enforcement-validators
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.40-03-judge-output-discipline-validator: Judge Output-Discipline Validator

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.40-judge-enforcement-validators/ADR-0.0.40-judge-enforcement-validators.md`
- **Checklist Item:** #3 — `judge-output-discipline-validator` — Implement `gz validate --judge-output-discipline` (Authoritative axis): verify explanation precedes verdict, methodology + three-axis + bias_mitigations declared, integrate into default `gz check`.

**Status:** Draft

## Objective

Implement `gz validate --judge-output-discipline` as an Authoritative-axis validator scope that enumerates every judge-invocation receipt and verifies output-discipline compliance: (a) `explanation_text` populated and meets the configured `min_length` floor (default 50 chars per ADR-0.0.39 § Invariant 8); (b) `verdict` populated; (c) the receipt's prompt-hash structure shows explanation was elicited before verdict (the validator reads the canonical prompt template, not the raw model response — verdict-precedes-explanation in prompt is the failure shape); (d) `methodology` declared from the canonical enum (ADR-0.0.39 § Invariant 7); (e) all three axes (what/how/where) populated from canonical enums (ADR-0.0.39 § Invariant 5); (f) `bias_mitigations` populated for every roster entry (ADR-0.0.39 § Invariant 6) — `n/a` is acceptable but explicit. Fail-close (exit 3) on any missing or out-of-order field. Integrate into the default `gz check` scope set.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.40-judge-enforcement-validators/**` — parent ADR package
- `src/gzkit/governance/trust_audits.py` — add `audit_judge_output_discipline`
- `src/gzkit/governance/judge_output_discipline.py` (new) — output-discipline checker helper module
- `src/gzkit/cli/parser_validate.py` — register `--judge-output-discipline` flag
- `src/gzkit/commands/validate.py` — wire scope into validate dispatcher; add to default `gz check` scope set
- `tests/governance/test_judge_output_discipline_validator.py` (new) — REQ-derived assertions
- `features/governance/judge_output_discipline.feature` (new) — BDD scenarios tagged `@REQ-0.0.40-03-NN`
- `docs/user/manpages/gz-validate.md` — document `--judge-output-discipline` scope
- `docs/user/runbook.md` — operator workflow entry
- `docs/governance/governance_runbook.md` — governance-maintainer workflow entry

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/arb/validator.py`, `src/gzkit/arb/middleware.py` — ARB middleware extension is OBPI-0.0.40-01's scope
- `src/gzkit/governance/judge_invocation.py`, `src/gzkit/schemas/judge_invocation.json` — schema is OBPI-0.0.39-02's
- `src/gzkit/governance/judge_leakage.py`, `data/judge_leakage_waivers.json`, `data/judge_model_families.json` — OBPI-0.0.40-02's scope
- `gz judge meta-eval` registration — OBPI-0.0.40-04's scope
- `src/gzkit/commands/adr_evaluate.py` — retrofit is OBPI-0.0.40-05's scope
- `CLAUDE.md` § Advisor Tool — bias profile docs are OBPI-0.0.40-05's scope
- New runtime dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `gz validate --judge-output-discipline` is registered at `src/gzkit/cli/parser_validate.py` with `axis: authoritative` per ADR-0.0.38. The scope is added to `gz check`'s default scope set (no opt-out).
2. REQUIREMENT: `audit_judge_output_discipline` enumerates every judge-invocation receipt (per the canonical inventory from OBPI-0.0.40-01) and verifies for each:
   (a) `explanation_text` is non-empty AND meets the `min_length` floor (default 50, configurable via `data/judge_axis_enums.json` `explanation_min_length` from OBPI-0.0.39-02);
   (b) `verdict` is non-empty;
   (c) the receipt declares its prompt structure such that explanation precedes verdict — the validator reads the canonical prompt template (referenced from `methodology_rationale` field) and asserts the prompt elicited explanation before verdict;
   (d) `methodology` is declared from the ADR-0.0.39 § Invariant 7 enum (single-grading, pairwise, list-wise, reference-based, criteria-decomposed, ensemble, red-team-challenge);
   (e) all three axes (what_axis, how_axis, where_axis) populated from the ADR-0.0.39 § Invariant 5 enums;
   (f) `bias_mitigations` populated for all four roster entries (position_bias, verbosity_bias, self_preference, preference_leakage) — `n/a` is acceptable but MUST be explicit, not absent.
3. REQUIREMENT: For each failure class (a)–(f), the validator emits exit 3 with a diagnostic naming the receipt_id, the failing field, the expected value or shape, and a citation to the relevant ADR-0.0.39 invariant.
4. REQUIREMENT: Diagnostic output (default + `--json`) groups failures by failure class so an operator can see "3 receipts failed verdict-precedes-explanation, 2 failed methodology-declaration, 1 failed bias-mitigations-completeness" rather than a flat list.
5. REQUIREMENT: `judge_output_discipline.py` defines `check_explanation_precedes_verdict(receipt: JudgeInvocation, prompt_template_registry: PromptTemplateRegistry) -> bool`, `check_methodology_declared(receipt) -> bool`, etc. Each checker is pure-function with deterministic output.
6. REQUIREMENT: The validator integrates with the OBPI-0.0.40-01 receipt-emit floor — receipts emitted with output-discipline failures are *also* rejected at emit time by the schema validator. The corpus-scan validator here catches receipts that may have been waived through emit-time validation OR receipts created before the emit-time floor landed.
7. REQUIREMENT: `tests/governance/test_judge_output_discipline_validator.py` asserts each of the six failure classes (a)–(f) is detected, each diagnostic names the relevant field and ADR-0.0.39 invariant, and clean fixtures pass.
8. REQUIREMENT: `features/governance/judge_output_discipline.feature` covers: clean corpus pass, each named drift case fails-closed, JSON output shape matches documented schema. Tags `@REQ-0.0.40-03-NN`.
9. REQUIREMENT: `docs/user/manpages/gz-validate.md` documents `--judge-output-discipline` with EXAMPLES section showing real CLI output. Runbook entries added per gate5-runbook-code-covenant.
10. REQUIREMENT: The validator emits `arb-step-judge-output-discipline-*` receipts per the canonical-step slot reserved in OBPI-0.0.40-01.
11. REQUIREMENT: `gz cli audit` and `gz validate --cli-alignment` exit 0 with the new scope appearing in manpage + command doc index + SKILL coverage roster.
12. REQUIREMENT: Pythonic size limits per `.gzkit/rules/pythonic.md` — `audit_judge_output_discipline` and each per-failure-class checker fit within ≤50 lines.
13. REQUIREMENT: NEVER allow a `--ignore-violations` or `--warn-only` flag. Fail-closed semantics are non-negotiable.
14. REQUIREMENT: NEVER add a `--judge-leakage` scope (OBPI-02's), `gz judge meta-eval` verb (OBPI-04's), `adr_evaluate.py` retrofit (OBPI-05's), or any other surface outside this OBPI's scope.

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
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.40-judge-enforcement-validators/**`
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
uv run -m unittest tests/governance/test_judge_output_discipline_validator.py -v

# BDD scenarios (Gate 4)
uv run -m behave features/governance/judge_output_discipline.feature

# CLI alignment + manpage coverage
uv run gz cli audit
uv run gz validate --cli-alignment

# The validator runs against itself
uv run gz validate --judge-output-discipline
uv run gz validate --judge-output-discipline --json

# Confirm scope is in default gz check
uv run gz check --list-scopes

# Standard heavy-lane gates
uv run gz lint
uv run gz typecheck
uv run gz validate --documents
uv run mkdocs build --strict

# ARB-wrapped receipt for attestation
uv run gz arb step --name judge-output-discipline -- uv run gz validate --judge-output-discipline

# Confirm canonical artifacts
test -f src/gzkit/governance/judge_output_discipline.py
test -f features/governance/judge_output_discipline.feature
grep -q "judge-output-discipline" docs/user/runbook.md
grep -q "judge-output-discipline" docs/user/manpages/gz-validate.md
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

- [ ] REQ-0.0.40-03-01: Given a clean fixture corpus with all judge receipts compliant, when `uv run gz validate --judge-output-discipline` runs, then exit code is 0 and stdout names "all receipts pass output discipline".
- [ ] REQ-0.0.40-03-02: Given a fixture receipt with empty `explanation_text`, when the validator runs, then exit code is 3 and the diagnostic names the receipt_id, the explanation_text field, and cites ADR-0.0.39 § Invariant 8.
- [ ] REQ-0.0.40-03-03: Given a fixture receipt with `explanation_text` shorter than the configured min_length, when the validator runs, then exit code is 3 with a min_length-floor diagnostic.
- [ ] REQ-0.0.40-03-04: Given a fixture receipt whose prompt template shows verdict requested before explanation, when the validator runs, then exit code is 3 and the diagnostic names the prompt-order violation.
- [ ] REQ-0.0.40-03-05: Given a fixture receipt with `methodology` outside the canonical enum, when the validator runs, then exit code is 3 and the diagnostic cites ADR-0.0.39 § Invariant 7.
- [ ] REQ-0.0.40-03-06: Given a fixture receipt with any of the three axes (what/how/where) outside the canonical enum, when the validator runs, then exit code is 3 and the diagnostic cites ADR-0.0.39 § Invariant 5.
- [ ] REQ-0.0.40-03-07: Given a fixture receipt with `bias_mitigations` missing one of the four required entries (position_bias, verbosity_bias, self_preference, preference_leakage), when the validator runs, then exit code is 3 and the diagnostic cites ADR-0.0.39 § Invariant 6 and names the missing entry.
- [ ] REQ-0.0.40-03-08: Given diagnostic output, when read for a corpus with mixed failures, then failures are grouped by failure class (verdict-precedes-explanation, missing-methodology, off-enum-axis, incomplete-bias-mitigations) so the operator can see counts per class.
- [ ] REQ-0.0.40-03-09: Given `--json` flag, when the validator runs, then stdout is JSON-parseable with shape `{scope: "judge-output-discipline", passed: bool, violations_by_class: {...}}`.
- [ ] REQ-0.0.40-03-10: Given `gz check --list-scopes`, when run after this OBPI lands, then `judge-output-discipline` is in the default scope set (no opt-out).
- [ ] REQ-0.0.40-03-11: Given `gz cli audit` and `gz validate --cli-alignment`, when run, then both exit 0 with the new scope in manpage + command doc index + SKILL coverage.
- [ ] REQ-0.0.40-03-12: Given the Pythonic size-limit rule (≤50 lines/function), when `uv run gz lint` runs, then `audit_judge_output_discipline` and each per-failure-class checker fit within the limit.
- [ ] REQ-0.0.40-03-13: Given the Denied Paths boundary, when this OBPI's diff is reviewed, then no edits to ARB middleware (-01's), no `--judge-leakage` scope (-02's), no `gz judge meta-eval` verb (-04's), no `adr_evaluate.py` retrofit (-05's).
- [ ] REQ-0.0.40-03-14: Given the validator's MUST-NOT-degrade requirement, when source is read, then no `--ignore-violations` or `--warn-only` flag exists.

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
