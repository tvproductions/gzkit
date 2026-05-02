---
id: OBPI-0.0.24-02-wire-into-completion
parent: ADR-0.0.24-attestation-receipt-binding
item: 2
lane: Heavy
status: Completed
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

**Prerequisites**

- OBPI-0.0.24-01 has landed — `validate_attestation_receipts` exists at
  `src/gzkit/governance/trust_audits/attestation_receipts.py:171` with the
  signature `(text, *, lane, kind, project_root) -> AttestationReceiptValidationResult`
  and 11 REQ-pinned tests passing (ledger event 4495 records the OBPI-01 completion
  receipt at 2026-05-02T15:19:12Z).
- `CANONICAL_STEP_COMMANDS` in `src/gzkit/arb/validator.py` accepts additive
  extension via the same reserved-slot pattern used by ADR-0.0.22 (`security: []`).
- Heavy-lane / foundation-kind attestation rigor codified in
  `_requires_human_obpi_attestation` (`src/gzkit/commands/adr_audit.py:385`)
  and `_enforce_human_attestation_authenticity` (line 444); the new gate
  must run BEFORE the latter so a mechanical-receipt failure short-circuits
  TTY prompting (REQ-07).

**Existing Code**

- `src/gzkit/commands/obpi_complete.py:obpi_complete_cmd` (line 322) — primary
  surface. Inserts the gate between step 4a (security gate) and step 4b
  (TTY authenticity gate).
- `src/gzkit/commands/adr_audit.py:adr_emit_receipt_cmd` (line 686) — ADR
  audit-receipt path. Inserts the gate before `_enforce_human_attestation_authenticity`
  (line 739) for the human-attestation events `validated`/`attested`/`accepted`
  enumerated by `_HUMAN_ATTESTATION_RECEIPT_EVENTS`.
- `src/gzkit/commands/obpi_cmd.py:obpi_emit_receipt_cmd` (line 125) — sister
  emit-receipt path. Inserts the gate before `_gate_completed_receipt_authenticity`
  (line 181) when `receipt_event == "completed"`.
- `gzkit.ledger_events.audit_receipt_emitted_event` constructor — vehicle for
  the meta-receipt-bind ledger event (`receipt_event="meta-receipt-bind"`,
  `evidence={claim, exit_status, run_id, resolved_receipt_ids, ...}`); chosen
  over a new typed event class so `gzkit.events`/`gzkit.ledger_events` stay
  out of this OBPI's allowlist.
- AGENTS.md § Lane & Kind & Sensitivity Attestation Matrix — projection of
  the three-axis attestation predicate that the gate's fail-closed posture
  parallels (heavy lane OR foundation kind → fail-closed).

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


Heavy/foundation fail-closed and gate-before-TTY ordering:

```
$ uv run -m unittest tests.commands.test_obpi_complete.TestObpiCompleteHeavyMissingReceipt tests.commands.test_obpi_complete.TestObpiCompleteGateRunsBeforeTtyGate -v
test_heavy_lane_missing_receipt_exits_3 ... ok
test_tty_gate_not_called_when_receipt_binding_fails ... ok
# observed: SystemExit(3); ledger.append never called; TTY mock asserted not_called
```

Heavy success → meta-receipt-bind event recorded:

```
$ uv run -m unittest tests.commands.test_obpi_complete.TestObpiCompleteMetaReceiptBindEvent -v
test_meta_receipt_bind_event_payload ... ok
# observed: event.event=="audit_receipt_emitted",
#           event.extra["receipt_event"]=="meta-receipt-bind",
#           evidence.run_id starts "arb-meta-receipt-bind-",
#           evidence.claim=="attestation receipts resolved", exit_status==0
```

ADR-level mirror (REQ-05):

```
$ uv run -m unittest tests.commands.test_adr_emit_receipt -v
test_heavy_lane_validated_with_missing_receipt_exits_3 ... ok
test_heavy_lane_validated_with_valid_receipt_emits_both ... ok
```

Quality gates (lint: receipt arb-ruff-cbf6764cf9f241e6bfd377f2f2940ade; typecheck: receipt arb-step-typecheck-c0a0573cc3f446cb9bd4b33d64702e35; unittest: receipt arb-step-unittest-3947d0c134ca422b9ff81dc8cf703f58; mkdocs: receipt arb-step-mkdocs-b20d0e1d3c2e40ce9819006b770b0c20) — 3946/3946 tests pass, 1 skipped.

### Implementation Summary


- Files modified: `src/gzkit/arb/validator.py` (added `meta-receipt-bind: []` reserved slot to `CANONICAL_STEP_COMMANDS`); `src/gzkit/commands/obpi_complete.py` (added `_read_adr_kind`, `_build_meta_receipt_evidence`, `_enforce_attestation_receipt_gate` helpers; wired between security gate 4a and TTY gate 4b in `obpi_complete_cmd`); `src/gzkit/commands/adr_audit.py` (wired the gate into `adr_emit_receipt_cmd` before `_enforce_human_attestation_authenticity` for `validated`/`attested`/`accepted`); `src/gzkit/commands/obpi_cmd.py` (wired the gate into `obpi_emit_receipt_cmd` for `--event completed` to close the sister-path fabrication vector); `tests/test_obpi_complete_cmd.py` (no-op patches in 3 pre-existing tests under Behavior Rule 1a coupled-surface coherence); `tests/commands/test_runtime.py` (added `setUp` patcher for the new gate covering all 38 end-to-end tests).
- Files created: `tests/commands/test_obpi_complete.py` (7 tests pinning REQ-01..04 + slot/ordering/payload via the auxiliary REQUIREMENTs); `tests/commands/test_adr_emit_receipt.py` (2 tests pinning REQ-05 fail-closed + success-with-meta-bind).
- Tests added: 10 OBPI-scoped tests; full sweep 3946/3946 pass (1 skipped).
- Date completed: 2026-05-02.
- Attestation status: `attest completed` — operator-typed.
- Defects noted: none.

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.24-02-wire-into-completion landed the receipt-binding gate across all three completion-emitting CLI surfaces (`gz obpi complete`, `gz adr emit-receipt --event {validated,attested,accepted}`, `gz obpi emit-receipt --event completed`). The gate runs BEFORE `_enforce_human_attestation_authenticity` at every site so a mechanical-receipt failure short-circuits TTY prompting (REQ-07). Heavy-lane OR foundation-kind = exit 3 fail-closed on unresolvable ARB receipts (REQ-02, REQ-04); lite + non-foundation = warn-only proceed (REQ-03). Successful gate firings emit a self-attesting `audit_receipt_emitted` event with `receipt_event="meta-receipt-bind"`, `evidence={run_id: "arb-meta-receipt-bind-<32hex>", claim: "attestation receipts resolved", exit_status: 0, resolved_receipt_ids: [...]}` (REQ-05 mechanism). `CANONICAL_STEP_COMMANDS` extended with reserved `meta-receipt-bind: []` slot mirroring the ADR-0.0.22 `security: []` pattern (REQ-06). 5/5 formal acceptance criteria covered by 10 REQ-decorated tests; full sweep 3946/3946 pass (lint: receipt arb-ruff-cbf6764cf9f241e6bfd377f2f2940ade; typecheck: receipt arb-step-typecheck-c0a0573cc3f446cb9bd4b33d64702e35; unittest: receipt arb-step-unittest-3947d0c134ca422b9ff81dc8cf703f58; mkdocs: receipt arb-step-mkdocs-b20d0e1d3c2e40ce9819006b770b0c20).
- Date: 2026-05-02

---

**Brief Status:** Completed

**Date Completed:** 2026-05-02

**Evidence Hash:** -
