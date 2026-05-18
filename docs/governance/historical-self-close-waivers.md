<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Historical Self-Close Waivers

> Closed waiver list of pre-doctrine OBPI receipts that pre-date the universal-attestation cutoff (ADR-0.0.36, 2026-04-26).

## Purpose

This document explains `data/historical_self_close_waivers.json`, the closed enumeration of every receipt in `.gzkit/ledger.jsonl` that:

1. Pre-dates the ADR-0.0.36 cutoff (2026-04-26), AND
2. Carries one of the deprecated self-close shapes:
   - `attestation_requirement: optional`
   - `obpi_completion: completed` (missing the `attested_` prefix)
   - `attestor: agent:*` (machine attestation instead of human attestation)

The waiver list resolves the tension between ledger immutability (Behavior Rules — Never #2: never edit the ledger directly) and the new fail-closed validator scope `gz validate --receipt-shape` (introduced under OBPI-0.0.36-03). Without the waiver list, the validator would refuse historical receipts the doctrine cannot retroactively re-attest. With the waiver list, pre-cutoff drift is preserved as documented historical fact (auditable, dated, bounded) while the doctrine binds going forward.

## Schema

The file conforms to `HistoricalAttestationWaiverFile` Pydantic model in `src/gzkit/models/historical_waiver.py`. Each waiver entry has five fields:

| Field | Type | Meaning |
|-------|------|---------|
| `receipt_id` | str | Ledger event ID of the waivered receipt |
| `obpi_id` | str | OBPI that generated the receipt (legacy slug form) |
| `deprecated_shape` | str | Comma-separated labels of the deprecated shapes present |
| `rationale` | str | Why this receipt is waivered |
| `added_under` | str | Exact value: `OBPI-0.0.36-04-historical-self-close-waivers` |

The Pydantic model is configured with `ConfigDict(frozen=True, extra="forbid")` — extra fields are refused and post-construction mutation raises `ValidationError`.

## Closed-to-New-Entries Posture

The waiver list is **closed**. Any future attempt to add a waiver entry will be refused by the validator unless its `added_under` field is exactly `"OBPI-0.0.36-04-historical-self-close-waivers"` — and since this OBPI is the only one that may legitimately stamp that value, the list is effectively frozen.

If a future doctrine genuinely needs to extend the waiver mechanism (which it should not), it requires its own ADR ceremony to author a new sanctioned `added_under` value. This is by design — the waiver mechanism exists to document historical drift, not to provide an open escape hatch for future drift.

See ADR-0.0.36 § Decision item #4 for the binding doctrine:
> "The waiver list is closed to new entries — adding a waiver after this ADR's authoring is itself a doctrine breach."

## Audit Lineage

The waiver list was authored in response to GHI #332 (audit of ADR-0.16.0 closeout drift), which surfaced the deprecated-shape pattern across multiple historical OBPIs. The audit findings drove ADR-0.0.36 (Universal OBPI Attestation), under which:

- OBPI-0.0.36-01 collapsed the Lane & Kind Attestation Matrix in `AGENTS.md`
- OBPI-0.0.36-02 collapsed the runtime gate `_requires_human_obpi_attestation`
- OBPI-0.0.36-03 added the `gz validate --receipt-shape` fail-closed scope
- **OBPI-0.0.36-04 (this work)** enumerated the historical waiver list
- OBPI-0.0.36-05 swept skill and rule prose

The waiver list is the documented bridge between pre-doctrine ledger state and post-doctrine validator enforcement. It records drift, never rewrites it.

## Validator Behavior

`gz validate --receipt-shape` consults this file with the following semantics:

| Receipt date | Waiver file present | Receipt in waiver list | Behavior |
|-------------|--------------------|------------------------|----------|
| Pre-cutoff | absent | n/a | Warn-only (no errors) |
| Pre-cutoff | present | yes | Silent pass |
| Pre-cutoff | present | no | Warning emitted (no fail-closed exit) |
| Post-cutoff | n/a | n/a | Fail-closed on any deprecated shape |

The implementation lives in `src/gzkit/governance/trust_audits/receipt_shape.py::audit_receipt_shape`.

## References

- [ADR-0.0.36 — Universal OBPI Attestation](../design/adr/foundation/ADR-0.0.36-universal-obpi-attestation/ADR-0.0.36-universal-obpi-attestation.md)
- [GHI #332 — Audit of ADR-0.16.0 closeout drift](https://github.com/gzkit/gzkit/issues/332)
- [GHI #342 — Universal-attestation destination ADR](https://github.com/gzkit/gzkit/issues/342)
- `AGENTS.md` § OBPI Acceptance Protocol — universal attestation doctrine
- `src/gzkit/models/historical_waiver.py` — Pydantic schema
- `data/historical_self_close_waivers.json` — the waiver list itself
