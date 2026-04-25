---
id: OBPI-0.0.24-01-validator-scope
parent: ADR-0.0.24-attestation-receipt-binding
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.24-01-validator-scope: `gz validate --attestation-receipts` scope

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.24-attestation-receipt-binding/ADR-0.0.24-attestation-receipt-binding.md`
- **Checklist Item:** #1 — "Implement `gz validate --attestation-receipts` scope (parse, ledger lookup, claim/category match) with table-driven unit tests"

**Status:** Draft

## Objective

Implement a new `gz validate --attestation-receipts` scope that, given an attestation string, parses inline `arb-…` receipt IDs, looks each up in `.gzkit/ledger.jsonl`, and asserts existence + `exit_status == 0` + claim-category match.

## Lane

**Heavy** — Adds a new validate scope; runtime contract change.

## Allowed Paths

- `src/gzkit/governance/trust_audits.py` — new validator function `validate_attestation_receipts`
- `src/gzkit/cli/parser_artifacts.py` (or wherever `gz validate` flags are registered) — add `--attestation-receipts` flag
- `src/gzkit/arb/validator.py` — read access to `CANONICAL_STEP_COMMANDS` for claim-category mapping (no edits)
- `tests/governance/test_attestation_receipt_validator.py` — new test module
- `docs/design/adr/foundation/ADR-0.0.24-attestation-receipt-binding/**` — parent ADR package scope

## Denied Paths

- `src/gzkit/commands/obpi.py`, `src/gzkit/commands/adr_emit_receipt.py` — gate wiring lands in OBPI-02
- `AGENTS.md`, `docs/governance/arb-middleware.md` — doc updates in OBPI-03
- `features/**` — BDD coverage in OBPI-04
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: New function `validate_attestation_receipts(attestation_text: str, lane: str, kind: str) -> ValidationResult` in `src/gzkit/governance/trust_audits.py`.
2. REQUIREMENT: The function parses the attestation string for receipt IDs matching the regex `arb-[a-z]+(-[a-z0-9]+)*-\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}` (canonical ARB receipt ID shape).
3. REQUIREMENT: For each parsed ID, the function reads `.gzkit/ledger.jsonl`, finds the matching `arb-receipt` event, and asserts: (a) the event exists; (b) `exit_status == 0`; (c) the receipt's claim category matches the category named adjacent to the citation in the attestation text (lint, types, tests, coverage, mkdocs, etc., per AGENTS.md § Canonical invocations).
4. REQUIREMENT: The function returns a structured `ValidationResult` with per-receipt status (`resolved` / `missing` / `status_mismatch` / `claim_mismatch`).
5. REQUIREMENT: `gz validate --attestation-receipts <attestation-string-or-file>` invokes the function and prints results in the standard `gz validate` output shape.
6. REQUIREMENT: Exit code: 0 on all-resolved, 3 on any failure (consistent with other validate scopes per `.claude/rules/cli.md`).
7. REQUIREMENT: Table-driven unit tests cover: all-valid attestation, missing receipt, exit-status-1 receipt, claim-category-mismatch receipt, malformed receipt-ID, attestation with zero receipts (warn-only signal returned).
8. REQUIREMENT: Tests use `tempfile`-backed ledger fixtures; NEVER read the live `.gzkit/ledger.jsonl` in tests.
9. REQUIREMENT: Each test decorated with `@covers(REQ-0.0.24-01-NN)` per the REQ-derivation rule.
10. REQUIREMENT: Lane behavior is parameter-driven in this OBPI but NOT yet wired into `obpi complete` / `adr emit-receipt` (that lands in OBPI-02).
11. REQUIREMENT: NEVER include the operator's personal email in any code, test fixture, or docstring.
12. REQUIREMENT: NEVER mock `pathlib.Path` away; use `tempfile.TemporaryDirectory()`.
13. REQUIREMENT: TDD discipline: Red-Green-Refactor per behavior increment, observed RED before GREEN.

> STOP-on-BLOCKERS: if `.gzkit/ledger.jsonl` schema or the `CANONICAL_STEP_COMMANDS` shape has changed since this OBPI was authored, STOP and reconcile before implementing.

## Discovery Checklist

- [ ] AGENTS.md § Attestation, § Canonical invocations
- [ ] `src/gzkit/arb/validator.py` — read `CANONICAL_STEP_COMMANDS`
- [ ] `src/gzkit/governance/trust_audits.py` — existing validator shape (e.g. `validate_utf8_prefix`)
- [ ] `.gzkit/ledger.jsonl` — sample existing `arb-receipt` event shape
- [ ] `tests/governance/test_type_ignore_syntax.py` — example of a fail-closed governance test

## Quality Gates

### Gate 1: ADR

- [ ] Intent recorded
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Red-Green-Refactor cycle observed for each REQ
- [ ] `uv run gz test` passes
- [ ] Coverage does not regress below 40%

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] `gz validate --help` and the new `--attestation-receipts` flag appear in the manpage; manpage authored under OBPI-03

### Gate 4: BDD (Heavy)

- [ ] BDD scenarios authored in OBPI-04

### Gate 5: Human (Heavy + Foundation)

- [ ] Human attestation required at completion (heavy + foundation = mandatory)

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz arb step --name unittest -- uv run -m unittest tests/governance/test_attestation_receipt_validator.py -v
# Smoke test:
uv run gz validate --attestation-receipts "lint clean (lint: receipt arb-2026-04-25T12-00-00-ruff)"
```

## Acceptance Criteria

- [ ] REQ-0.0.24-01-01: Given a valid attestation citing a resolved receipt with `exit_status=0` and matching claim category, when `gz validate --attestation-receipts` runs, then exit 0.
- [ ] REQ-0.0.24-01-02: Given an attestation citing a receipt that does not exist in the ledger, when the validator runs, then exit 3 with a `missing` status for that receipt.
- [ ] REQ-0.0.24-01-03: Given an attestation citing a receipt with `exit_status=1`, when the validator runs, then exit 3 with a `status_mismatch` status.
- [ ] REQ-0.0.24-01-04: Given an attestation citing a receipt whose claim category does not match the category named adjacent to the citation, when the validator runs, then exit 3 with a `claim_mismatch` status.
- [ ] REQ-0.0.24-01-05: Given a malformed receipt ID in the attestation, when the validator runs, then the result is reported (not silently skipped).
- [ ] REQ-0.0.24-01-06: Given an attestation with zero receipts, when the validator runs in lite-non-foundation mode, then exit 0 with a warn-only signal; in heavy or foundation mode, exit 3.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** RGR cycle observed; tests pass
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Documented
- [ ] **Key Proof:** Smoke test included
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
