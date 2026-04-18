---
id: OBPI-0.15.0-03-ledger-event-discrimination
parent: ADR-0.15.0-pydantic-schema-enforcement
item: 3
lane: Lite
status: in_progress
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# OBPI-0.15.0-03 — ledger-event-discrimination

## ADR ITEM (Lite) — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.15.0-pydantic-schema-enforcement/ADR-0.15.0-pydantic-schema-enforcement.md`
- OBPI Entry: `OBPI-0.15.0-03 — "Discriminated unions for typed ledger events; replace manual dispatch"`

## OBJECTIVE (Lite)

Replace the single `LedgerEvent` dataclass with a Pydantic discriminated union over
event types. Each event type (`project_init`, `adr_created`, `obpi_created`,
`attested`, `gate_checked`, `obpi_receipt_emitted`, etc.) gets a specific Pydantic
model with typed `extra` fields. Replace `_validate_ledger_event_fields()` manual
dispatch with Pydantic's discriminator-based parsing. Event factory functions return
typed event models.

## LANE (Lite)

Lite — ADR note + stdlib unittest + smoke (≤60s).

## ALLOWED PATHS (Lite)

- `src/gzkit/ledger.py` (or new `src/gzkit/events.py` if ledger.py gets too large)
- `src/gzkit/validate.py` (remove manual ledger event dispatch)
- `tests/test_ledger.py`
- `tests/test_validate.py`

## DENIED PATHS (Lite)

- `.gzkit/ledger.jsonl` (never edit ledger directly)
- CI files, lockfiles

## REQUIREMENTS (FAIL-CLOSED — Lite)

1. Base `LedgerEvent` model with `event` field as discriminator
1. Specific models for each event type with typed extra fields (e.g., `ObpiReceiptEvent` has typed `evidence` field with `req_proof_inputs`, `scope_audit`, `git_sync_state`)
1. `_validate_ledger_event_fields()` replaced with Pydantic discriminated union parsing
1. `_validate_obpi_receipt_evidence()`, `_validate_req_proof_inputs()`, `_validate_scope_audit()`, `_validate_git_sync_state()` replaced with nested Pydantic models
1. Event factory functions return typed models (not generic dicts)
1. All existing ledger validation tests pass — identical error detection

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.15.0-03-01: Base `LedgerEvent` model with `event` field as discriminator
- [x] REQ-0.15.0-03-02: Specific models for each event type with typed extra fields (e.g., `ObpiReceiptEvent` has typed `evidence` field with `req_proof_inputs`, `scope_audit`, `git_sync_state`)
- [x] REQ-0.15.0-03-03: `_validate_ledger_event_fields()` replaced with Pydantic discriminated union parsing
- [x] REQ-0.15.0-03-04: `_validate_obpi_receipt_evidence()`, `_validate_req_proof_inputs()`, `_validate_scope_audit()`, `_validate_git_sync_state()` replaced with nested Pydantic models
- [x] REQ-0.15.0-03-05: Event factory functions return typed models (not generic dicts)
- [x] REQ-0.15.0-03-06: All existing ledger validation tests pass — identical error detection


## QUALITY GATES (Lite)

- [x] Gate 1 (ADR): Intent recorded in this brief
- [x] Gate 2 (TDD): `uv run gz test` — 571 tests pass
- [x] Code Quality: `uv run gz lint` + `uv run gz typecheck` clean

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
uv run -m unittest tests.test_ledger tests.test_validate -v
Ran 69 tests in 0.013s — OK
events.py coverage: 93.95%
```

### Code Quality

```text
uv run gz lint — All checks passed
uv run gz typecheck — All checks passed
```

### Implementation Summary

Created `src/gzkit/events.py` with:
- Nested evidence models: `ReqProofInput`, `ScopeAudit`, `GitSyncState`, `ObpiReceiptEvidence`
- 12 typed event models with `Literal` discriminators on the `event` field
- `TypedLedgerEvent` discriminated union with `parse_typed_event()` entry point
- Backward-compatible `.extra` property on typed events

Updated `src/gzkit/validate.py`:
- Replaced ~280 lines of manual validation (`_validate_obpi_receipt_evidence` and 6 sub-functions) with 20-line Pydantic model validation
- Error field paths match exactly for backward-compatible error detection

### Key Proof

```bash
uv run -m unittest tests.test_ledger.TestTypedEventModels tests.test_ledger.TestNestedEvidenceModels tests.test_validate.TestValidateLedger -v
# 18/18 pass — typed models parse correctly, existing validation unchanged
```

## Human Attestation

- Attestor: human:Jeff
- Attestation: Completed
- Date: 2026-03-18

---

**Brief Status:** Completed

**Date Completed:** 2026-03-18

**Evidence Hash:** -
