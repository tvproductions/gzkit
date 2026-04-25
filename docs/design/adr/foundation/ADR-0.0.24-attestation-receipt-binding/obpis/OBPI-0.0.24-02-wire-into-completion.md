---
id: OBPI-0.0.24-02-wire-into-completion
parent: ADR-0.0.24-attestation-receipt-binding
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.0.24-02-wire-into-completion: Wire gate into obpi complete + adr emit-receipt

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.24-attestation-receipt-binding/ADR-0.0.24-attestation-receipt-binding.md`
- **Checklist Item:** #2 — "Wire the gate into `gz obpi complete` and `gz adr emit-receipt` with lane-conditional fail/warn behavior and a new `arb-meta-receipt-bind-…` self-attesting receipt family"

**Status:** Draft

## Objective

Invoke `validate_attestation_receipts` (from OBPI-01) inside `gz obpi complete` and `gz adr emit-receipt` as a pre-emission gate; behavior is fail-closed on heavy/foundation, warn-only on lite-non-foundation; record a self-attesting `arb-meta-receipt-bind-…` event when the gate fires.

## Lane

**Heavy** — Modifies receipt-emission runtime contract.

## Allowed Paths

- `src/gzkit/commands/obpi.py` — gate invocation in `complete` subcommand
- `src/gzkit/commands/adr_emit_receipt.py` (or equivalent ADR receipt emit module) — gate invocation
- `src/gzkit/arb/validator.py` — extend `CANONICAL_STEP_COMMANDS` with `arb-meta-receipt-bind` family
- `src/gzkit/governance/trust_audits.py` — read access to OBPI-01 validator (no edits)
- `tests/commands/test_obpi_complete.py`, `tests/commands/test_adr_emit_receipt.py` — wiring tests
- `docs/design/adr/foundation/ADR-0.0.24-attestation-receipt-binding/**` — parent ADR package scope

## Denied Paths

- `src/gzkit/governance/trust_audits.py` validator function body — owned by OBPI-01
- `AGENTS.md`, `docs/governance/arb-middleware.md` — doc updates in OBPI-03
- `features/**` — BDD coverage in OBPI-04
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Before emitting a completion receipt, `gz obpi complete --attestation-text <text>` calls `validate_attestation_receipts(text, lane=brief.lane, kind=parent_adr.kind)`.
2. REQUIREMENT: If the parent ADR is `heavy` lane OR `foundation` kind, any non-zero validation result fails the completion (exit 3) and refuses to write the receipt event.
3. REQUIREMENT: If the parent ADR is `lite` lane AND non-`foundation` kind, a non-zero validation result is logged as a warning but the completion proceeds.
4. REQUIREMENT: Same gate logic applied to `gz adr emit-receipt --event closed --attestor … --attestation-text …`.
5. REQUIREMENT: When the gate fires successfully, a self-attesting `arb-meta-receipt-bind-<timestamp>` event is recorded in the ledger with `claim: "attestation receipts resolved"`, `exit_status: 0`, and a payload listing the resolved receipt IDs.
6. REQUIREMENT: `CANONICAL_STEP_COMMANDS` in `src/gzkit/arb/validator.py` extends with the `arb-meta-receipt-bind` slot.
7. REQUIREMENT: The gate respects the existing TTY + `ATTEST` confirmation discipline at `_enforce_human_attestation_authenticity` — the gate runs BEFORE the TTY confirmation, so a mechanical-receipt failure short-circuits human prompting.
8. REQUIREMENT: Test coverage: heavy-lane completion with valid attestation succeeds; heavy-lane with missing receipt fails-closed; lite-non-foundation with missing receipt warns and proceeds; foundation-lite with missing receipt fails-closed (foundation override); meta-receipt event appears in ledger after success.
9. REQUIREMENT: Tests use `tempfile`-backed ledger fixtures and patch the subprocess boundary; NEVER touch the live ledger.
10. REQUIREMENT: Each test decorated with `@covers(REQ-0.0.24-02-NN)`.
11. REQUIREMENT: NEVER include the operator's personal email in code, tests, or fixtures.
12. REQUIREMENT: NEVER bypass the gate via a flag in this OBPI; an emergency-skip path is out of scope (file a follow-up GHI if needed).
13. REQUIREMENT: TDD discipline: Red-Green-Refactor per behavior increment.

> STOP-on-BLOCKERS: if OBPI-01 has not landed (validator function does not exist), STOP.

## Discovery Checklist

- [ ] OBPI-0.0.24-01 evidence — confirm `validate_attestation_receipts` exists and tests pass
- [ ] `src/gzkit/commands/adr_audit.py` — read `_requires_human_obpi_attestation` and `_enforce_human_attestation_authenticity` for ordering
- [ ] AGENTS.md § Lane & Kind Attestation Matrix
- [ ] Existing `obpi complete` flow for receipt emission ordering

## Quality Gates

### Gate 1: ADR

- [ ] Intent recorded
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] RGR per behavior increment
- [ ] `uv run gz test` passes

### Code Quality

- [ ] Lint clean
- [ ] Type check clean

### Gate 3: Docs (Heavy)

- [ ] Manpage updates land in OBPI-03

### Gate 4: BDD (Heavy)

- [ ] BDD scenarios in OBPI-04

### Gate 5: Human (Heavy + Foundation)

- [ ] TTY + `ATTEST` required

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz arb step --name unittest -- uv run -m unittest tests/commands/test_obpi_complete.py tests/commands/test_adr_emit_receipt.py -v
# Smoke test the gate fires on a heavy-lane fixture brief
```

## Acceptance Criteria

- [ ] REQ-0.0.24-02-01: Given a heavy-lane brief with an attestation citing a valid resolved receipt, when `gz obpi complete` runs, then the completion receipt is written and a `arb-meta-receipt-bind-…` event appears in the ledger.
- [ ] REQ-0.0.24-02-02: Given a heavy-lane brief with an attestation citing a missing receipt, when `gz obpi complete` runs, then exit 3 and no completion receipt is written.
- [ ] REQ-0.0.24-02-03: Given a lite-non-foundation brief with a missing receipt, when `gz obpi complete` runs, then a warning is logged and the completion proceeds.
- [ ] REQ-0.0.24-02-04: Given a foundation-kind lite-lane brief with a missing receipt, when `gz obpi complete` runs, then exit 3 (foundation overrides lite).
- [ ] REQ-0.0.24-02-05: Given the same gate logic mirrored to `gz adr emit-receipt --event closed`, when an ADR closeout is attempted with a heavy-lane lineage and missing receipt, then exit 3.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** RGR cycle; tests pass
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Documented
- [ ] **Key Proof:** Successful + failing-gate transcripts
- [ ] **OBPI Acceptance:** Heavy + foundation = TTY + `ATTEST` required

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste RGR observations + final unittest output
```

### Code Quality

```text
# Paste lint/typecheck output
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

- Attestor: `<name>` (heavy + foundation requires human)
- Attestation: substantive attestation text
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
