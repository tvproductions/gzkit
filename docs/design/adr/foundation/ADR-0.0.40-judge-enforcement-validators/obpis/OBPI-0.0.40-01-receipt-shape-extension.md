---
id: OBPI-0.0.40-01-receipt-shape-extension
parent: ADR-0.0.40-judge-enforcement-validators
item: 1
lane: Heavy
status: Draft
allowlist:
- docs/design/adr/foundation/ADR-0.0.40-judge-enforcement-validators/**
- src/gzkit/arb/validator.py
- src/gzkit/arb/middleware.py
- .gzkit/schemas/ledger_events.json
- tests/arb/test_judge_receipt_routing.py
- tests/governance/test_judge_invocation_validated_event.py
- features/governance/judge_receipt_validation.feature
reqs:
- REQ-0.0.40-01-01
- REQ-0.0.40-01-02
- REQ-0.0.40-01-03
- REQ-0.0.40-01-04
- REQ-0.0.40-01-05
- REQ-0.0.40-01-06
- REQ-0.0.40-01-07
- REQ-0.0.40-01-08
- REQ-0.0.40-01-09
- REQ-0.0.40-01-10
- REQ-0.0.40-01-11
verification:
- uv run -m unittest tests/arb/test_judge_receipt_routing.py -v
- uv run -m unittest tests/governance/test_judge_invocation_validated_event.py -v
- uv run -m behave features/governance/judge_receipt_validation.feature
- uv run gz cli audit
- uv run gz lint
- uv run gz typecheck
- uv run gz validate --documents
- uv run mkdocs build --strict
---

# OBPI-0.0.40-01-receipt-shape-extension: ARB Receipt-Shape Extension for Judge Invocations

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.40-judge-enforcement-validators/ADR-0.0.40-judge-enforcement-validators.md`
- **Checklist Item:** #1 — `receipt-shape-extension` — Extend ARB middleware to validate judge-invocation receipts at emit time; canonical step slots reserved; ledger event family added.

**Status:** Draft

## Objective

Extend the ARB receipt validator's middleware path so that any receipt whose step name starts with `judge-` is routed to schema validation against the `judge_invocation.json` schema authored under OBPI-0.0.39-02. Reserve `CANONICAL_STEP_COMMANDS` slots for the three downstream judge step prefixes (`arb-step-judge-leakage-*`, `arb-step-judge-output-discipline-*`, `arb-step-judge-meta-eval-*`) so OBPI-0.0.40-02/03/04 can cite them. Add a `judge_invocation_validated` ledger event family that records every emit-time validation pass with metadata (receipt_id, step name, validation outcome). The middleware change is the receipt-side enforcement floor; OBPI-0.0.40-02/03 are the corpus-side enforcement floors.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.40-judge-enforcement-validators/**` — parent ADR package
- `src/gzkit/arb/validator.py` — extend `CANONICAL_STEP_COMMANDS`; route judge-prefixed receipts to schema validation
- `src/gzkit/arb/middleware.py` (or equivalent active path) — receipt-emit hook routing
- `.gzkit/schemas/ledger_events.json` — register `judge_invocation_validated` event family
- `tests/arb/test_judge_receipt_routing.py` (new) — REQ-derived assertions on routing path
- `tests/governance/test_judge_invocation_validated_event.py` (new) — REQ-derived assertions on ledger event shape
- `features/governance/judge_receipt_validation.feature` (new) — BDD scenarios tagged `@REQ-0.0.40-01-NN`

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/governance/judge_invocation.py` — schema landed under OBPI-0.0.39-02; this OBPI may NOT modify the Pydantic model or the JSON Schema
- `src/gzkit/schemas/judge_invocation.json` — landed under OBPI-0.0.39-02
- `src/gzkit/cli/parser_validate.py` — `--judge-leakage` and `--judge-output-discipline` registration is OBPI-0.0.40-02/03's scope
- `src/gzkit/cli/parser_*.py` for `gz judge` verb — OBPI-0.0.40-04's scope
- `src/gzkit/commands/adr_evaluate.py` — retrofit is OBPI-0.0.40-05's scope
- `data/judge_leakage_waivers.json`, `data/judge_model_families.json`, `data/judge_meta_eval_floor.json` — these data files belong to -02 and -04
- `CLAUDE.md` § Advisor Tool — bias profile docs are -05's scope
- New runtime dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `CANONICAL_STEP_COMMANDS` in `src/gzkit/arb/validator.py` is extended with three new entries: `arb-step-judge-leakage-*`, `arb-step-judge-output-discipline-*`, `arb-step-judge-meta-eval-*`. Each entry maps to its canonical command-line invocation per AGENTS.md § Attestation. The slots are reserved here; the validator scopes / CLI verb that emit receipts under these prefixes land in OBPI-0.0.40-02/03/04 respectively.
2. REQUIREMENT: ARB middleware is extended so that any receipt whose `step_name` starts with the literal prefix `judge-` is routed to schema validation against `src/gzkit/schemas/judge_invocation.json`. The routing predicate is **prefix-match-only**, not substring or regex — false-positive on near-miss prefixes (e.g. a hypothetical `judgement-*` step) is rejected by the test suite.
3. REQUIREMENT: A receipt routed to schema validation that fails validation is rejected at emit time per the existing ARB middleware contract — the existing failure path is reused, NOT a new one. The diagnostic names the failing field and cites `judge_invocation.json`.
4. REQUIREMENT: A receipt that passes schema validation results in a `judge_invocation_validated` ledger event being appended via the canonical event-emit helper. Event payload: `{receipt_id, step_name, source_commit, timestamp, schema_version}`.
5. REQUIREMENT: `.gzkit/schemas/ledger_events.json` is updated to register `judge_invocation_validated` as a new event family with the documented payload shape. The schema validates incoming events at write time.
6. REQUIREMENT: A receipt whose `step_name` does NOT start with `judge-` is unaffected by this change — existing ARB behavior for non-judge receipts is preserved byte-for-byte. Regression test asserts non-judge receipts still pass through their pre-extension code path.
7. REQUIREMENT: `tests/arb/test_judge_receipt_routing.py` asserts: (a) judge-prefixed receipts route to schema validation; (b) compliant judge receipts pass and emit `judge_invocation_validated`; (c) non-compliant judge receipts fail with named-field diagnostic; (d) near-miss-prefix receipts (e.g. `judgement-foo`, `pre-judge-bar`) do NOT route to validation; (e) non-judge receipts are unaffected.
8. REQUIREMENT: `tests/governance/test_judge_invocation_validated_event.py` asserts: (a) the event family is registered in `ledger_events.json`; (b) emitting an event with the documented payload validates against the schema; (c) emitting with missing required fields fails validation.
9. REQUIREMENT: `features/governance/judge_receipt_validation.feature` defines BDD acceptance scenarios for Gate 4 covering: emit-time validation pass case; emit-time validation fail case; non-judge receipt pass-through case; near-miss-prefix non-routing case. Tags use `@REQ-0.0.40-01-NN`.
10. REQUIREMENT: `gz cli audit` exits 0 after this OBPI lands — no new top-level CLI verb is added. The middleware extension is invisible at the verb-roster surface.
11. REQUIREMENT: Pythonic size limits per `.gzkit/rules/pythonic.md` — the routing predicate function and the event-emit helper each fit within ≤50 lines.
12. REQUIREMENT: NEVER add a `gz validate --judge-*` scope or a `gz judge` verb in this OBPI; those are OBPI-02/03/04's scope. NEVER edit `judge_invocation.py` or `judge_invocation.json`; those are -02's scope. NEVER edit `gz-adr-evaluate --red-team` or `CLAUDE.md`; those are -05's scope.
13. REQUIREMENT: NEVER reduce the routing predicate's strictness — a judge-prefixed receipt MUST always route to validation. Adding an `--ignore-validation` flag or a "warn-only" mode is a doctrine violation per AGENTS.md § Anti-Vibing Mantra.

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
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/arb/validator.py`
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
uv run -m unittest tests/arb/test_judge_receipt_routing.py -v
uv run -m unittest tests/governance/test_judge_invocation_validated_event.py -v

# BDD scenarios (Gate 4)
uv run -m behave features/governance/judge_receipt_validation.feature

# CLI surface unchanged
uv run gz cli audit

# Standard heavy-lane gates
uv run gz lint
uv run gz typecheck
uv run gz validate --documents
uv run mkdocs build --strict

# Confirm canonical artifacts
grep -q "arb-step-judge-leakage" src/gzkit/arb/validator.py
grep -q "arb-step-judge-output-discipline" src/gzkit/arb/validator.py
grep -q "arb-step-judge-meta-eval" src/gzkit/arb/validator.py
grep -q "judge_invocation_validated" .gzkit/schemas/ledger_events.json
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.40-01-01: Given `CANONICAL_STEP_COMMANDS` after this OBPI, when read, then it includes `arb-step-judge-leakage-*`, `arb-step-judge-output-discipline-*`, `arb-step-judge-meta-eval-*` slots.
- [ ] REQ-0.0.40-01-02: Given a receipt with `step_name` starting with literal `judge-`, when emitted, then the ARB middleware routes the payload to schema validation against `judge_invocation.json`.
- [ ] REQ-0.0.40-01-03: Given a compliant judge receipt, when emitted, then validation passes and a `judge_invocation_validated` ledger event is recorded with the documented payload.
- [ ] REQ-0.0.40-01-04: Given a non-compliant judge receipt (missing required field), when emitted, then validation fails with a diagnostic naming the failing field and citing `judge_invocation.json`.
- [ ] REQ-0.0.40-01-05: Given `.gzkit/schemas/ledger_events.json` after this OBPI, when read, then `judge_invocation_validated` is a registered event family with payload schema covering `receipt_id, step_name, source_commit, timestamp, schema_version`.
- [ ] REQ-0.0.40-01-06: Given a receipt with `step_name` NOT starting with `judge-` (e.g. `arb-step-ruff-*`, `arb-step-unittest-*`), when emitted, then the routing predicate does NOT route to schema validation and the existing ARB pass-through behavior is preserved.
- [ ] REQ-0.0.40-01-07: Given a near-miss prefix (e.g. `judgement-foo`, `pre-judge-bar`), when matched against the routing predicate, then the predicate returns False and routing does not fire.
- [ ] REQ-0.0.40-01-08: Given `features/governance/judge_receipt_validation.feature`, when `uv run -m behave` runs, then all scenarios pass with `@REQ-0.0.40-01-NN` tags covering the requirement set.
- [ ] REQ-0.0.40-01-09: Given the Pythonic size-limit rule (≤50 lines/function), when `uv run gz lint` runs, then the routing predicate function and event-emit helper each fit within the limit.
- [ ] REQ-0.0.40-01-10: Given the Denied Paths boundary, when this OBPI's diff is reviewed, then no new CLI verb or validator scope is registered, no edits to `judge_invocation.py` or `judge_invocation.json`, no edits to `adr_evaluate.py` or `CLAUDE.md`.
- [ ] REQ-0.0.40-01-11: Given the validator's MUST-NOT-degrade requirement, when the routing-predicate source is read, then no `--ignore-validation`, `--warn-only`, or equivalent escape flag exists.

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
