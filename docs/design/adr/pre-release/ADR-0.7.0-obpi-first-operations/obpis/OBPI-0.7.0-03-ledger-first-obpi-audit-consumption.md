---
id: OBPI-0.7.0-03-ledger-first-obpi-audit-consumption
parent: ADR-0.7.0-obpi-first-operations
item: 3
lane: Heavy
status: Completed
---

# OBPI-0.7.0-03-ledger-first-obpi-audit-consumption: Ledger First Obpi Audit Consumption

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.7.0-obpi-first-operations/ADR-0.7.0-obpi-first-operations.md`
- **Checklist Item:** #3 — "Move audit readiness to ledger-first OBPI consumption."

**Status:** Completed

## Objective

Make OBPI completion/audit checks consume ledger proof as primary evidence instead of relying only on brief text inspection.

### Implementation Summary

- Files modified: `src/gzkit/ledger.py` (added `ledger_completed` to artifact graph), `src/gzkit/commands/status.py` (updated `_inspect_obpi_brief` to prioritize ledger), `src/gzkit/cli.py` (passed graph to audit checks).
- Date completed: 2026-03-04

## Key Proof

```bash
# Audit check now explicitly requires ledger proof:
uv run gz adr audit-check ADR-0.7.0-obpi-first-operations
# Output includes: "ledger proof of completion is missing" for drafts.
```

## Human Attestation

- Attestor: human:jeff
- Attestation: "Confirmed status surfaces now prioritize ledger records over file metadata."
- Date: 2026-03-04
