---
id: OBPI-0.0.53-03-extend-payload-arb-receipts
parent: ADR-0.0.53-validator-remediation-payload-invariant
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.53-03-extend-payload-arb-receipts: Extend the Payload Contract to ARB Step + Receipt Failures

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.53-validator-remediation-payload-invariant/ADR-0.0.53-validator-remediation-payload-invariant.md`
- **Checklist Item:** #3 — "OBPI-0.0.53-03: Extend payload contract to ARB step / receipt validation failures + extend meta-validator scope"

**Status:** Draft

## Objective

Extend the `RemediationPayload` contract to the ARB surface: every `gz arb step` that exits non-zero emits the structured payload to stderr; every receipt `failure` block carries the three fields; every `gz arb validate` rejection (receipt-shape, fabricated-receipt, missing-receipt) speaks the payload; `CANONICAL_STEP_COMMANDS` enforcement emits a payload whose `recovery` is the canonical invocation string. Extend the `gz validate --remediation-payload-binding` meta-validator's scope to cover `src/gzkit/arb/**/*.py` and drain the ARB entries from the baseline allowlist.

## Lane

**Heavy** — Behavior change across every ARB step / receipt-validation failure path, an extension of the `gz validate --remediation-payload-binding` meta-validator scope, and a change to `CANONICAL_STEP_COMMANDS` rejection output. Per `.claude/rules/cli.md` the ARB step exit semantics are an external CLI contract. Foundation-kind parent ADR-0.0.53 triggers universal brief-level Gate 5 attestation per ADR-0.0.36.

## Allowed Paths

- `src/gzkit/arb/` — every ARB step / receipt-validation failure path migrates to emit a `RemediationPayload`; `CANONICAL_STEP_COMMANDS` rejection output gains the payload shape
- `src/gzkit/governance/trust_audits/` — the `remediation-payload-binding` meta-validator's scope is extended to cover `src/gzkit/arb/**/*.py` (the scope grows monotonically per ADR § Sequencing)
- `data/` — ARB-surface entries are drained from the baseline allowlist `data/validator_remediation_baseline.json` (created by OBPI-02; edited here)
- `tests/arb/` — OBPI creates `tests/arb/test_remediation_payload.py`
- `docs/user/manpages/` — ARB-step manpage EXAMPLES updated where the failure-output shape changed
- `docs/design/adr/foundation/ADR-0.0.53-validator-remediation-payload-invariant/**` — parent ADR package scope

## Denied Paths

- `src/gzkit/core/models.py`, `src/gzkit/core/exceptions.py`, `src/gzkit/__main__.py` — the port is OBPI-01 scope
- `.gzkit/rules/validator-remediation.md` — authored in OBPI-01
- `src/gzkit/hooks/**` — hook migration is OBPI-04 scope
- Validator-scope migration under `trust_audits/` beyond the meta-validator scope extension — OBPI-02 owns the validator bodies; this OBPI only widens the meta-validator's `arb/` coverage
- Any path not listed in Allowed Paths
- New runtime dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Every `gz arb step` invocation whose wrapped command exits non-zero emits a `RemediationPayload` to stderr — the JSON-line rendering first, the human rendering after — via `RemediationFailure`, never an ad-hoc string.
2. REQUIREMENT: When an ARB receipt records a failure, the receipt body's `failure` block carries the three canonical fields `rule_citation`, `diagnosis`, `recovery` — populated from the same `RemediationPayload` the stderr rendering used, never hand-formatted separately.
3. REQUIREMENT: Every `gz arb validate` rejection — receipt-shape rejection, fabricated-receipt detection, missing-receipt detection — emits a `RemediationPayload`. When `gz arb validate` rejects a non-canonical step, the `rule_citation` points at `AGENTS.md` § Attestation and the `recovery` field is the canonical invocation string from `CANONICAL_STEP_COMMANDS`.
4. REQUIREMENT: The `gz validate --remediation-payload-binding` meta-validator's scope is extended to import and assert against `src/gzkit/arb/**/*.py` — every ARB fail-closed path raises `RemediationFailure`; every emitted payload validates the model.
5. REQUIREMENT: Every ARB-surface entry present in `data/validator_remediation_baseline.json` at this OBPI's start is removed from the allowlist; the allowlist shrinks monotonically and carries zero ARB entries at this OBPI's completion.
6. REQUIREMENT: Tests in `tests/arb/test_remediation_payload.py` assert REQ-derived semantics — a failing `gz arb step` emits a valid payload; a receipt `failure` block carries the three fields; `gz arb validate` rejections speak the payload; a non-canonical-step rejection's `recovery` equals the `CANONICAL_STEP_COMMANDS` invocation. Tests assert semantics, not output strings.
7. REQUIREMENT: NEVER edit OBPI-01's port files and NEVER touch `src/gzkit/hooks/` — hook migration is OBPI-04.
8. REQUIREMENT: NEVER include the operator's personal email in any ARB code, the baseline file, the manpage updates, or any test.

> STOP-on-BLOCKERS: if OBPI-01's port or OBPI-02's meta-validator is absent (`gz validate --remediation-payload-binding` is not a registered scope), print BLOCKERS and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item 3 — quote verbatim** into the brief's Implementation Summary. Decision item 3 is the contract.
- [ ] Parent ADR § Decision — the canonical `RemediationPayload` invariant statement.
- [ ] Parent ADR § Sequencing — OBPI-03 lands after OBPI-02; the meta-validator scope grows monotonically.
- [ ] Parent ADR § Scope boundary — "Does NOT canonize recovery commands as receipts" (the `recovery` field is the manual-recovery command, not a step-receipt invocation).

**Governance (read once, cache):**

- [ ] `AGENTS.md` § Attestation — the canonical-invocations table; `CANONICAL_STEP_COMMANDS` is the locked source
- [ ] `.gzkit/rules/validator-remediation.md` — the invariant this OBPI extends to ARB
- [ ] `docs/governance/arb-middleware.md` — the ARB receipt model and `failure`-block shape

**Context — the ARB surface:**

- [ ] `src/gzkit/arb/` — enumerate the step/receipt/validate failure paths
- [ ] `src/gzkit/arb/validator.py`, `step_reporter.py` — the receipt-emission and step-wrapping code
- [ ] `src/gzkit/governance/trust_audits/` — the OBPI-02 meta-validator file whose scope this OBPI widens

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-01 landed: `RemediationPayload` / `RemediationFailure` importable
- [ ] OBPI-02 landed: `gz validate --remediation-payload-binding` is a registered scope

**Existing Code (understand current state):**

- [ ] `CANONICAL_STEP_COMMANDS` definition and its current rejection-output shape
- [ ] Existing ARB receipt `failure`-block schema

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR Decision item 3 quoted in Implementation Summary

### Gate 2: TDD

- [ ] RED test asserting a failing `gz arb step` emits a valid payload, written before implementation
- [ ] Tests pass: `uv run gz arb step --name unittest -- uv run -m unittest -q` (receipt: `arb-step-unittest-*`)
- [ ] No regression in the existing suite

### Code Quality

- [ ] Lint clean: `uv run gz arb ruff` (receipt: `arb-ruff-*`)
- [ ] Typecheck clean: `uv run gz arb typecheck` (receipt: `arb-step-typecheck-*`)

### Gate 3: Docs (Heavy)

- [ ] ARB-step manpage EXAMPLES updated where the failure-output shape changed
- [ ] Docs build: `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` (receipt: `arb-step-mkdocs-*`)

### Gate 4: BDD (Heavy)

- [ ] BDD scenario covers a failing `gz arb step` emitting the structured payload to stderr

### Gate 5: Human (universal per ADR-0.0.36)

- [ ] Foundation-kind brief: explicit human attestation required at completion

## Verification

```bash
uv run gz validate --remediation-payload-binding
uv run gz arb step --name unittest -- uv run -m unittest -q tests.arb.test_remediation_payload
uv run python -c "import json; b = json.load(open('data/validator_remediation_baseline.json')); assert not any('arb' in str(e) for e in b), 'ARB entries still in baseline'; print('baseline drained of ARB entries')"
uv run gz validate --documents --surfaces
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Demo

```bash
# A failing ARB step now emits the structured payload — JSON line first:
uv run gz arb step --name demo-fail -- python -c "import sys; sys.exit(1)" 2>&1 | head -4
# The meta-validator now covers the ARB surface:
uv run gz validate --remediation-payload-binding
```

## Acceptance Criteria

- [ ] REQ-0.0.53-03-01: Given parent ADR § Decision item 3, when a `gz arb step` wrapped command exits non-zero, then a `RemediationPayload` is emitted to stderr with the JSON-line rendering first.
- [ ] REQ-0.0.53-03-02: Given an ARB receipt recording a failure, when the receipt body is read, then its `failure` block carries `rule_citation`, `diagnosis`, and `recovery` from the same payload the stderr rendering used.
- [ ] REQ-0.0.53-03-03: Given a `gz arb validate` rejection, when it fails closed, then the rejection emits a `RemediationPayload`; for a non-canonical-step rejection the `recovery` field equals the `CANONICAL_STEP_COMMANDS` canonical invocation and `rule_citation` points at `AGENTS.md` § Attestation.
- [ ] REQ-0.0.53-03-04: Given the meta-validator scope extension, when `gz validate --remediation-payload-binding` runs, then it imports and asserts against `src/gzkit/arb/**/*.py` and passes for every migrated ARB path.
- [ ] REQ-0.0.53-03-05: Given the baseline allowlist, when this OBPI completes, then `data/validator_remediation_baseline.json` carries zero ARB-surface entries (monotonic drain).

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; parent ADR Decision item 3 quoted in Implementation Summary
- [ ] **Gate 2 (TDD):** RED-GREEN cycle followed; ARB payload tests pass; suite regression-free
- [ ] **Code Quality:** Lint + typecheck + docs build clean with receipts
- [ ] **Value Narrative:** Problem-before (ARB failures in ad-hoc shapes) vs capability-now (every ARB refusal is a structured prompt; meta-validator covers the surface)
- [ ] **Key Proof:** A failing `gz arb step` emitting the structured payload; the meta-validator green over `arb/`
- [ ] **OBPI Acceptance:** Foundation-kind brief requires explicit human attestation per ADR-0.0.36

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste unittest output + arb-step-unittest receipt ID here
```

### Code Quality

```text
# Paste lint + typecheck + mkdocs output here with ARB receipt IDs
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here at completion
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
