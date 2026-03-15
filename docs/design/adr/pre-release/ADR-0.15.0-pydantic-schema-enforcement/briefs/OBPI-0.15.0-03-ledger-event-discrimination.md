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

## QUALITY GATES (Lite)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` — all tests pass
- [ ] Code Quality: `uv run gz lint` + `uv run gz typecheck` clean
