---
id: OBPI-0.0.40-02-judge-leakage-validator
parent: ADR-0.0.40-judge-enforcement-validators
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.0.40-02-judge-leakage-validator: Judge Leakage Validator (Preference-Leakage Detection)

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.40-judge-enforcement-validators/ADR-0.0.40-judge-enforcement-validators.md`
- **Checklist Item:** #2 — `judge-leakage-validator` — Implement `gz validate --judge-leakage` (Authoritative axis): same-family judge⇄candidate detection across the receipt corpus, with `data/judge_leakage_waivers.json` waiver registry and `data/judge_model_families.json` family-equivalence registry.

**Status:** Draft

## Objective

Implement `gz validate --judge-leakage` as an Authoritative-axis validator scope that enumerates every judge-invocation receipt (under `artifacts/receipts/judge-*.json` and the historical ledger), consults `data/judge_model_families.json` for model-family equivalence, flags same-family `judge_model_family` ⇄ `candidate_provenance.model_family` pairs, and fail-closes (exit 3) on any unwaived violation. The waiver registry at `data/judge_leakage_waivers.json` honors named exceptions with cited rationale and `expires_after` discipline (precedent: `data/security_surfaces.json`, `_UTF8_PIPE_WAIVERS`). The validator's diagnostic explicitly cites the survey paper's preference-leakage class so future operators reading a flagged receipt understand the structural concern. BDD acceptance scenarios cover the leakage-detected, waiver-honored, and family-registry-edge cases.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.40-judge-enforcement-validators/**` — parent ADR package
- `src/gzkit/governance/trust_audits.py` — add `audit_judge_leakage` audit function
- `src/gzkit/governance/judge_leakage.py` (new) — leakage detector helper module
- `src/gzkit/cli/parser_validate.py` — register `--judge-leakage` flag
- `src/gzkit/commands/validate.py` — wire scope into validate dispatcher
- `data/judge_leakage_waivers.json` (new) — frozen Pydantic-validated waiver registry
- `data/judge_model_families.json` (new) — frozen Pydantic-validated model-family equivalence registry
- `tests/governance/test_judge_leakage_validator.py` (new) — REQ-derived assertions
- `tests/governance/test_judge_model_families.py` (new) — registry shape assertions
- `features/governance/judge_leakage.feature` (new) — BDD scenarios tagged `@REQ-0.0.40-02-NN`
- `docs/user/manpages/gz-validate.md` — document `--judge-leakage` scope
- `docs/user/runbook.md` — operator workflow entry
- `docs/governance/governance_runbook.md` — governance-maintainer workflow entry

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/arb/validator.py`, `src/gzkit/arb/middleware.py`, `.gzkit/schemas/ledger_events.json` — ARB middleware extension is OBPI-0.0.40-01's scope
- `src/gzkit/governance/judge_invocation.py`, `src/gzkit/schemas/judge_invocation.json` — schema landed under OBPI-0.0.39-02; this OBPI may NOT modify
- `gz validate --judge-output-discipline` registration — OBPI-0.0.40-03's scope
- `gz judge meta-eval` registration — OBPI-0.0.40-04's scope
- `src/gzkit/commands/adr_evaluate.py` — retrofit is OBPI-0.0.40-05's scope
- `CLAUDE.md` § Advisor Tool — bias profile docs are OBPI-0.0.40-05's scope
- `data/judge_meta_eval_floor.json` — meta-eval config is OBPI-0.0.40-04's scope
- New runtime dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `gz validate --judge-leakage` is a registered scope at `src/gzkit/cli/parser_validate.py` and dispatches to `src/gzkit/commands/validate.py`. The scope is included in `gz check` default scope set under heavy lane, and is gated by axis declaration `axis: authoritative` per ADR-0.0.38.
2. REQUIREMENT: `audit_judge_leakage` in `src/gzkit/governance/trust_audits.py` enumerates every judge-invocation receipt: (a) all `arb-step-judge-*` receipts under `artifacts/receipts/`; (b) all `judge_invocation_validated` ledger events. For each receipt, it reads `judge_model_family` and `candidate_provenance.model_family` per the OBPI-0.0.39-02 schema.
3. REQUIREMENT: `data/judge_model_families.json` is a frozen Pydantic-validated registry mapping model strings to family names. Schema (Pydantic): `ModelFamilyEntry(model_string: str, family: str, training_relationship_to_family: str | None)`. Initial registry seeds (subject to operator confirmation at Gate 5): `claude-opus-4-7` → family `claude-opus-4`, `claude-opus-4-6` → family `claude-opus-4`, `claude-sonnet-4-6` → family `claude-sonnet-4`, `claude-haiku-4-5-20251001` → family `claude-haiku-4`, `gpt-5.5` → family `gpt-5`, etc. Editing the registry requires explicit operator authorization in the editing brief's frontmatter.
4. REQUIREMENT: `judge_leakage.py` defines `detect_leakage(judge_family: str, candidate_family: str, registry: ModelFamilyRegistry) -> bool` returning True when the two families are equal OR when the registry declares them as ancestor/sibling related. The detector is pure function (no side effects); a test asserts deterministic behavior across registry inputs.
5. REQUIREMENT: `data/judge_leakage_waivers.json` is a frozen Pydantic-validated waiver registry. Schema: `JudgeLeakageWaiver(receipt_pattern: str, reason: str, cited_authority: str, expires_after: str | None, declared_by: str, declared_at: str)`. The `receipt_pattern` is a glob or exact-match string against `receipt_id`. Waivers with expired `expires_after` are NOT honored; the validator names the expired waiver in its diagnostic. Adding a waiver requires the editing brief to declare a `cited_authority` (foundation ADR or operator decision-record reference).
6. REQUIREMENT: The validator's exit semantics: exit 0 when no leakage detected OR all detected leakage is covered by unexpired waivers; exit 3 when any unwaived leakage is detected (heavy-lane fail-closed); exit 3 when the waiver registry itself is malformed.
7. REQUIREMENT: Diagnostic output (default + `--json`) for each detected leakage names: receipt_id, judge_model + family, candidate_model + family, training_relationship, applied_waiver (if any), survey-paper citation (verbatim quote of `arxiv 2411.15594` § Preference Leakage warning).
8. REQUIREMENT: `tests/governance/test_judge_leakage_validator.py` asserts: (a) leakage-free corpus passes; (b) same-family pair without waiver fails-closed; (c) same-family pair with valid waiver passes; (d) same-family pair with expired waiver fails-closed naming the expired waiver; (e) malformed waiver registry fails-closed with diagnostic; (f) `--json` output schema matches documented shape.
9. REQUIREMENT: `tests/governance/test_judge_model_families.py` asserts: (a) registry validates against Pydantic schema; (b) registry edits require explicit cited authority; (c) `detect_leakage` returns expected values for each registered family pair.
10. REQUIREMENT: `features/governance/judge_leakage.feature` covers: clean corpus pass; leakage detected; waiver applied; expired waiver flagged; unknown model family handled gracefully (warns, does not crash). Tags `@REQ-0.0.40-02-NN`.
11. REQUIREMENT: `docs/user/manpages/gz-validate.md` documents `--judge-leakage` with EXAMPLES section showing real CLI output (per `.gzkit/rules/cli.md`). Runbook entries added per gate5-runbook-code-covenant.
12. REQUIREMENT: The validator emits `arb-step-judge-leakage-*` receipts per the canonical-step slot reserved in OBPI-0.0.40-01.
13. REQUIREMENT: `gz cli audit` and `gz validate --cli-alignment` exit 0 with the new scope appearing in manpage + command doc index + SKILL coverage roster.
14. REQUIREMENT: Pythonic size limits per `.gzkit/rules/pythonic.md` — `audit_judge_leakage` and `detect_leakage` each fit within ≤50 lines.
15. REQUIREMENT: NEVER allow a `--ignore-violations` or `--warn-only` flag. Waivers are the sole escape, and waivers require cited authority. NEVER add a `--judge-output-discipline` scope, a `gz judge meta-eval` verb, or any other surface from OBPI-0.0.40-03/04/05.

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
- [ ] Required path exists or is intentionally created in this OBPI: `data/judge_leakage_waivers.json`
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
uv run -m unittest tests/governance/test_judge_leakage_validator.py -v
uv run -m unittest tests/governance/test_judge_model_families.py -v

# BDD scenarios (Gate 4)
uv run -m behave features/governance/judge_leakage.feature

# CLI alignment + manpage coverage
uv run gz cli audit
uv run gz validate --cli-alignment

# The validator runs against itself
uv run gz validate --judge-leakage
uv run gz validate --judge-leakage --json

# Standard heavy-lane gates
uv run gz lint
uv run gz typecheck
uv run gz validate --documents
uv run mkdocs build --strict

# ARB-wrapped receipt for attestation
uv run gz arb step --name judge-leakage -- uv run gz validate --judge-leakage

# Confirm canonical artifacts
test -f data/judge_leakage_waivers.json
test -f data/judge_model_families.json
test -f src/gzkit/governance/judge_leakage.py
test -f features/governance/judge_leakage.feature
grep -q "preference leakage" docs/user/manpages/gz-validate.md
grep -q "judge-leakage" docs/user/runbook.md
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

- [ ] REQ-0.0.40-02-01: Given a clean repo with no judge receipts, when `uv run gz validate --judge-leakage` runs, then exit code is 0 and stdout names "no leakage detected".
- [ ] REQ-0.0.40-02-02: Given a fixture corpus with a same-family judge⇄candidate receipt and no waiver, when the validator runs, then exit code is 3 and the diagnostic names the receipt_id, both model families, and the survey-paper citation.
- [ ] REQ-0.0.40-02-03: Given a fixture corpus with a same-family judge⇄candidate receipt AND a valid waiver in `data/judge_leakage_waivers.json` covering it, when the validator runs, then exit code is 0 and the waiver is named in the report's "waived" section.
- [ ] REQ-0.0.40-02-04: Given a waiver with expired `expires_after`, when the validator runs against a same-family receipt the waiver originally covered, then exit code is 3 and the diagnostic names the expired waiver.
- [ ] REQ-0.0.40-02-05: Given a malformed `data/judge_leakage_waivers.json`, when the validator runs, then exit code is 3 with a schema-validation diagnostic.
- [ ] REQ-0.0.40-02-06: Given `data/judge_model_families.json`, when read by the registry loader, then it validates against `ModelFamilyEntry` and `detect_leakage(family_a, family_b)` returns expected results for each registered pair.
- [ ] REQ-0.0.40-02-07: Given `--json` flag, when the validator runs, then stdout is JSON-parseable with shape `{scope: "judge-leakage", passed: bool, violations: [...], waivers_applied: [...], survey_citation: str}`.
- [ ] REQ-0.0.40-02-08: Given `gz cli audit` and `gz validate --cli-alignment`, when run after the new scope lands, then both exit 0 with `--judge-leakage` appearing in manpage + command doc index + SKILL coverage roster.
- [ ] REQ-0.0.40-02-09: Given `features/governance/judge_leakage.feature`, when run via `uv run -m behave`, then all scenarios pass with `@REQ-0.0.40-02-NN` tags.
- [ ] REQ-0.0.40-02-10: Given the diagnostic output, when read for a flagged receipt, then it includes a verbatim citation of arxiv 2411.15594 § Preference Leakage so future operators understand the structural concern.
- [ ] REQ-0.0.40-02-11: Given the Pythonic size-limit rule (≤50 lines/function), when `uv run gz lint` runs, then `audit_judge_leakage` and `detect_leakage` each fit within the limit.
- [ ] REQ-0.0.40-02-12: Given the Denied Paths boundary, when this OBPI's diff is reviewed, then no edits to ARB middleware (-01's scope), no `--judge-output-discipline` scope (-03's), no `gz judge meta-eval` verb (-04's), no `adr_evaluate.py` retrofit (-05's).
- [ ] REQ-0.0.40-02-13: Given the validator's MUST-NOT-degrade requirement, when source is read, then no `--ignore-violations` or `--warn-only` flag exists.

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
