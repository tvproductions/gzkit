---
id: OBPI-0.0.24-04-bdd-coverage
parent: ADR-0.0.24-attestation-receipt-binding
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.24-04-bdd-coverage: BDD scenario coverage for receipt-binding gate

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.24-attestation-receipt-binding/ADR-0.0.24-attestation-receipt-binding.md`
- **Checklist Item:** #4 — "BDD coverage — heavy-lane `@REQ-…`-tagged scenarios in `features/` covering valid receipts, missing receipts, status-mismatched receipts, and lite-lane warn-only"

**Status:** Draft

## Objective

Author behave scenarios that exercise the receipt-binding gate end-to-end against real `gz validate`, `gz obpi complete`, and `gz adr emit-receipt` invocations.

## Lane

**Heavy** — Heavy-lane OBPIs require Gate 4 BDD coverage.

## Allowed Paths

- `features/attestation_receipt_binding.feature` — new feature file
- `features/steps/attestation_receipt_binding_steps.py` (or extend existing step modules) — step implementations
- `data/behave_coverage_waivers.json` — read-only access; no edits expected
- `tests/fixtures/ledger/` (or wherever ledger fixtures live) — fixture ledger files for the scenarios
- `docs/design/adr/foundation/ADR-0.0.24-attestation-receipt-binding/**` — parent ADR package scope

## Denied Paths

- `src/**` — no source changes in this OBPI
- `tests/**` (unit tier) — coverage in OBPI-01 and OBPI-02
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `features/attestation_receipt_binding.feature` exists with at least one scenario per REQ from OBPI-01 (REQ-0.0.24-01-01 through REQ-0.0.24-01-06) and OBPI-02 (REQ-0.0.24-02-01 through REQ-0.0.24-02-05).
2. REQUIREMENT: Each scenario carries an `@REQ-0.0.24-NN-MM` scenario-level tag matching the REQ it covers (per `.claude/rules/tests.md` § Behave scenario tagging, GHI #185).
3. REQUIREMENT: Scenarios run against real `gz validate --attestation-receipts`, real `gz obpi complete`, and real `gz adr emit-receipt` (no subprocess mocking — this is the end-to-end tier).
4. REQUIREMENT: Scenarios use ledger fixtures, not the live `.gzkit/ledger.jsonl`.
5. REQUIREMENT: `uv run gz validate --behave-req-tags` exits 0 — every REQ in OBPI-01/02 is covered by at least one tagged scenario, OR an explicit waiver is registered in `data/behave_coverage_waivers.json` with rationale.
6. REQUIREMENT: `uv run -m behave features/attestation_receipt_binding.feature` exits 0 with all scenarios passing.
7. REQUIREMENT: NEVER spawn real `git` or `uv sync` — those are out of scope; this feature exercises CLI semantics only.
8. REQUIREMENT: NEVER include the operator's personal email in scenario text or fixtures.
9. REQUIREMENT: TTY + `ATTEST` interactive flow is exercised in scenarios that close foundation/heavy briefs. Mock at the subprocess boundary using a `pexpect`-shaped fixture that feeds `ATTEST\n` to the spawned `gz obpi complete` process — DO NOT patch `_enforce_human_attestation_authenticity`'s PTY check internally; the BDD tier is end-to-end and must traverse the real PTY enforcement path. (Unit-tier patching of the PTY check is OBPI-02's surface, not this OBPI's.)

> STOP-on-BLOCKERS: if OBPI-01, OBPI-02, OBPI-03 have not landed, STOP — there is nothing to exercise end-to-end.

## Discovery Checklist

- [ ] OBPI-0.0.24-01, -02, -03 evidence — confirm gate is wired and docs are landed
- [ ] `.claude/rules/tests.md` § Behave scenario tagging
- [ ] `features/` — read existing scenarios for tagging shape and step conventions
- [ ] `data/behave_coverage_waivers.json` — confirm format

## Quality Gates

### Gate 1: ADR

- [ ] Intent recorded
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Scenarios written before implementation? In this OBPI, the implementation is upstream; scenarios are the end-to-end check that the implementation behaves per REQ.
- [ ] `uv run -m behave features/attestation_receipt_binding.feature` exits 0

### Code Quality

- [ ] Lint clean: `uv run gz lint`

### Gate 4: BDD (Heavy)

- [ ] All scenarios pass
- [ ] `gz validate --behave-req-tags` exits 0

### Gate 5: Human (Heavy + Foundation)

- [ ] TTY + `ATTEST` required

## Verification

```bash
uv run gz lint
uv run -m behave features/attestation_receipt_binding.feature
uv run gz validate --behave-req-tags
```

## Acceptance Criteria

- [ ] REQ-0.0.24-04-01: Given the receipt-binding gate landed in OBPI-02, when behave runs the new feature file, then every REQ from OBPI-01 and OBPI-02 has at least one passing tagged scenario.
- [ ] REQ-0.0.24-04-02: Given `gz validate --behave-req-tags`, when run after this OBPI lands, then exit 0 without resorting to a coverage waiver for ADR-0.0.24.
- [ ] REQ-0.0.24-04-03: Given a heavy-lane scenario that closes a brief with a missing receipt, when behave runs, then the scenario asserts exit 3 and verifies no completion event in the fixture ledger.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** behave passes
- [ ] **Code Quality:** Lint clean
- [ ] **Gate 4 (BDD):** All scenarios pass; req-tags validate exits 0
- [ ] **Value Narrative:** Documented
- [ ] **Key Proof:** Behave run output pasted
- [ ] **OBPI Acceptance:** Heavy + foundation = TTY + `ATTEST` required

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Behave run output
```

### Code Quality

```text
# Lint output
```

### Gate 4 (BDD)

```text
# Behave run output (full)
# gz validate --behave-req-tags output
```

### Gate 5 (Human)

```text
# Record attestation text here at completion
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added (BDD scenarios):
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
