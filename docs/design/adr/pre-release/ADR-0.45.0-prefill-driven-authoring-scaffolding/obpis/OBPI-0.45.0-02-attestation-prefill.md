---
id: OBPI-0.45.0-02-attestation-prefill
parent: ADR-0.45.0-prefill-driven-authoring-scaffolding
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.45.0-02-attestation-prefill: Attestation text `$EDITOR` prefill

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.45.0-prefill-driven-authoring-scaffolding/ADR-0.45.0-prefill-driven-authoring-scaffolding.md`
- **Checklist Item:** #2 — "Implement attestation text prefill via `$EDITOR` open in `gz obpi complete` and `gz adr emit-receipt`; em-dash separator + receipt-citation slot template"

**Status:** Draft

## Objective

When `gz obpi complete` and `gz adr emit-receipt` are invoked without `--attestation-text`, open `$EDITOR` with a prefilled scaffold containing the user's verbatim invocation token, the canonical em-dash separator, and a receipt-citation slot template.

## Lane

**Heavy** — Modifies attestation authoring CLI surface.

## Allowed Paths

- `src/gzkit/commands/obpi.py` — `complete` subcommand `$EDITOR` integration
- `src/gzkit/commands/adr_emit_receipt.py` — same integration
- `src/gzkit/attestation/prefill.py` (new) — prefill scaffold builder
- `tests/commands/test_obpi_complete_prefill.py`, `tests/commands/test_adr_emit_receipt_prefill.py`
- `tests/attestation/test_prefill_builder.py`
- `docs/design/adr/pre-release/ADR-0.45.0-prefill-driven-authoring-scaffolding/**`

## Denied Paths

- `src/gzkit/skills/**` — brief prefill in OBPI-01
- `src/gzkit/governance/trust_audits.py` — conformance validator in OBPI-03
- `features/**` — BDD coverage in OBPI-03
- Any path not listed

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: When `gz obpi complete <OBPI-ID>` is invoked without `--attestation-text`, the command opens `$EDITOR` (defaulting to `vi` if unset) with a prefilled scaffold.
2. REQUIREMENT: Scaffold contains:
   - Line 1: `<user-token> — ` (the operator's `--attestor` argument, or `attestor` placeholder if running interactively)
   - Empty line for the agent/operator to fill the concrete characterization
   - Final line: `Receipts: lint <ID>; types <ID>; tests <ID>; coverage <ID>.` (slot template)
3. REQUIREMENT: After the editor closes with non-empty content, the captured text is passed through the receipt-binding gate (ADR-0.0.24's `validate_attestation_receipts`).
4. REQUIREMENT: An empty editor save (or `:q!`) aborts the completion with exit 1.
5. REQUIREMENT: Same surface added to `gz adr emit-receipt --event closed` when invoked without `--attestation-text`.
6. REQUIREMENT: Tests cover: editor open with scaffold; non-empty close advances to receipt binding; empty close aborts; `$EDITOR` unset defaults to `vi`; both `obpi complete` and `adr emit-receipt` invocations.
7. REQUIREMENT: Tests mock the `subprocess.run([editor, ...])` call; NEVER spawn a real editor.
8. REQUIREMENT: Each test decorated with `@covers(REQ-0.45.0-02-NN)`.
9. REQUIREMENT: NEVER include the operator's personal email — including in the prefilled scaffold's `<user-token>` field. Use the operator's name only or the GitHub noreply address per AGENTS.md operator-PII rule.
10. REQUIREMENT: TDD discipline.

> STOP-on-BLOCKERS: if ADR-0.0.24 OBPI-01 has not landed (receipt-binding validator does not exist), the gate cannot run; STOP.

## Discovery Checklist

- [ ] Parent ADR § Decision item 2
- [ ] AGENTS.md § Attestation — canonical pattern
- [ ] AGENTS.md operator-PII rule (Local Agent Rules) — for the user-token field
- [ ] `src/gzkit/commands/obpi.py` — existing `complete` subcommand structure

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded
### Gate 2: TDD
- [ ] RGR; tests pass
### Code Quality
- [ ] Lint, type clean
### Gate 3: Docs (Heavy)
- [ ] In OBPI-03
### Gate 4: BDD (Heavy)
- [ ] In OBPI-03
### Gate 5: Human (Heavy)
- [ ] Required

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz arb step --name unittest -- uv run -m unittest tests/commands/test_obpi_complete_prefill.py tests/commands/test_adr_emit_receipt_prefill.py tests/attestation/test_prefill_builder.py -v
```

## Acceptance Criteria

- [ ] REQ-0.45.0-02-01: Given `gz obpi complete <ID>` without `--attestation-text`, when invoked, then `$EDITOR` opens with the canonical scaffold (em-dash separator, receipt-citation slot template).
- [ ] REQ-0.45.0-02-02: Given a non-empty editor save, when the editor closes, then the captured text passes through the receipt-binding gate.
- [ ] REQ-0.45.0-02-03: Given an empty editor save, when the editor closes, then completion aborts with exit 1.
- [ ] REQ-0.45.0-02-04: Given `$EDITOR` unset, when invoked, then `vi` is used as default.
- [ ] REQ-0.45.0-02-05: Given the same surface invoked via `gz adr emit-receipt --event closed`, when invoked, then the prefill scaffold opens identically.

## Completion Checklist

- [ ] **Gate 1:** Intent recorded
- [ ] **Gate 2:** RGR; tests pass
- [ ] **Code Quality:** clean
- [ ] **OBPI Acceptance:** Heavy = TTY + `ATTEST` required

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD)
```text
# RGR + unittest output
```

### Code Quality
```text
# lint/typecheck output
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

- Attestor: `<name>` (heavy lane requires human)
- Attestation: substantive attestation text
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
