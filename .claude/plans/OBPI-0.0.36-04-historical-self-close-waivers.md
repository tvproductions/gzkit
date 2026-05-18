# Plan: OBPI-0.0.36-04-historical-self-close-waivers

## OBPI Reference

- **OBPI ID:** OBPI-0.0.36-04-historical-self-close-waivers
- **Parent ADR:** ADR-0.0.36-universal-obpi-attestation
- **Brief:** docs/design/adr/foundation/ADR-0.0.36-universal-obpi-attestation/obpis/OBPI-0.0.36-04-historical-self-close-waivers.md

## Context

OBPI-03 landed the `gz validate --receipt-shape` validator in
`src/gzkit/governance/trust_audits/receipt_shape.py`. It already loads
`data/historical_self_close_waivers.json` (if present) and cross-checks
pre-cutoff receipt IDs. Two behaviors still need extension for OBPI-04:

1. `added_under` validation: the validator must refuse any waiver entry
   whose `added_under` field is not exactly `OBPI-0.0.36-04-historical-self-close-waivers`.
2. Warn-only for un-waivered pre-cutoff receipts: current code is
   fail-closed; REQ-04 requires warn-only (warning emitted, no fail-closed exit).

48 pre-cutoff deprecated receipts need enumeration across three shape classes:
`attestation_requirement: optional`, `obpi_completion: completed` (unprefixed),
`attestor: agent:*`.

## Allowed Files

- `data/historical_self_close_waivers.json`
- `src/gzkit/models/historical_waiver.py`
- `src/gzkit/governance/trust_audits/receipt_shape.py`
- `tests/models/test_historical_waiver.py`
- `tests/governance/test_historical_waiver_integration.py`
- `docs/governance/historical-self-close-waivers.md`

## Steps

### Step 1: RED — Write Failing Tests

Write `tests/models/test_historical_waiver.py` asserting the Pydantic model
semantics (frozen mutation refused, extra field refused, required-field absence
refused) — tests fail because the model doesn't exist yet.

Write `tests/governance/test_historical_waiver_integration.py` asserting:
- Waivered pre-cutoff receipt passes silently
- Un-waivered pre-cutoff receipt with waiver file present emits warning (no error)
- Un-waivered post-cutoff receipt fails closed (error)
- Waiver entry with bad `added_under` (not `OBPI-0.0.36-04-historical-self-close-waivers`) is rejected

Run `uv run -m unittest tests.models.test_historical_waiver tests.governance.test_historical_waiver_integration -v` — expect RED.

### Step 2: Create Pydantic Model

Create `src/gzkit/models/historical_waiver.py`:
- `HistoricalAttestationWaiver(BaseModel)` with `ConfigDict(frozen=True, extra="forbid")`
  fields: `receipt_id: str`, `obpi_id: str`, `deprecated_shape: str`, `rationale: str`, `added_under: str`
- `HistoricalAttestationWaiverFile(BaseModel)` with `ConfigDict(frozen=True, extra="forbid")`
  field: `waivers: list[HistoricalAttestationWaiver]`

### Step 3: Enumerate Receipts into Waiver File

Create `data/historical_self_close_waivers.json` with all 48 pre-cutoff deprecated
receipts (enumerated above from ledger scan). Each entry:
- `receipt_id`: the ledger event `id` field
- `obpi_id`: the OBPI the receipt belongs to (from event `evidence.obpi_id`)
- `deprecated_shape`: short label (`attestation_requirement:optional`,
  `obpi_completion:completed`, `attestor:agent:*`)
- `rationale`: "Pre-ADR-0.0.36 receipt; doctrine cutoff 2026-04-26. GHI #332 audit."
- `added_under`: `"OBPI-0.0.36-04-historical-self-close-waivers"`

### Step 4: Extend receipt_shape.py

In `src/gzkit/governance/trust_audits/receipt_shape.py`:

a. Update `_load_waiver_ids` to use the Pydantic model for validation and to
   validate each entry's `added_under` field — return `ValidationError` list
   alongside the waiver ID set (or extend the function to expose errors).
   Add a new `_validate_waiver_file` function that:
   - Parses `data/historical_self_close_waivers.json` via `HistoricalAttestationWaiverFile`
   - Emits a `ValidationError` for any entry whose `added_under` is not exactly
     `OBPI-0.0.36-04-historical-self-close-waivers`

b. Fix pre-cutoff un-waivered behavior: when waiver file is present and a
   pre-cutoff receipt is NOT in the waiver list, emit a *warning* (not an
   error). Warnings are logged to stderr; the audit function returns empty
   `list[ValidationError]` for this case (not fail-closed).

c. Wire `_validate_waiver_file` into `audit_receipt_shape` — validate the
   waiver file shape before scanning receipts, return waiver-shape errors if any.

### Step 5: GREEN

Run `uv run -m unittest tests.models.test_historical_waiver tests.governance.test_historical_waiver_integration -v` — expect GREEN.

### Step 6: Documentation

Create `docs/governance/historical-self-close-waivers.md` documenting:
- Purpose: closed waiver list for pre-doctrine receipts
- Cite GHI #332 and ADR-0.0.36
- Explain closed-to-new-entries posture (`added_under` lock)
- Link audit lineage back to GHI #332

Add cross-reference from `docs/governance/state-doctrine.md`.

### Step 7: Quality Gates

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --receipt-shape
```

### Step 8: OBPI Acceptance Ceremony

Present evidence for Gate 5 human attestation.

## Verification

```bash
uv run python -c "
import sys, json, pathlib
sys.stdout.reconfigure(encoding='utf-8')
waiver = json.loads(pathlib.Path('data/historical_self_close_waivers.json').read_text(encoding='utf-8'))
print(f'Waivered receipts: {len(waiver[\"waivers\"])}')
"
uv run -m unittest tests.models.test_historical_waiver tests.governance.test_historical_waiver_integration -v
uv run gz validate --receipt-shape
```
