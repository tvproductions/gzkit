---
id: OBPI-0.7.0-03-ledger-first-obpi-audit-consumption
parent: ADR-0.7.0-obpi-first-operations
item: 3
lane: Heavy
status: attested_completed
---

# OBPI-0.7.0-03-ledger-first-obpi-audit-consumption: Ledger First Obpi Audit Consumption

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.7.0-obpi-first-operations/ADR-0.7.0-obpi-first-operations.md`
- **Checklist Item:** #3 — "Move audit readiness to ledger-first OBPI consumption."

**Status:** Completed

## Objective

Make OBPI completion/audit checks consume ledger proof as primary evidence instead of relying only on brief text inspection.

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 (Mode C — derived from Objective, Implementation Summary, and Key Proof).
-->

- [x] REQ-0.7.0-03-01: Given the gzkit artifact graph, when constructed, then it includes a `ledger_completed` relation derived from `.gzkit/ledger.jsonl` proof events.
- [x] REQ-0.7.0-03-02: Given an OBPI brief inspection (`_inspect_obpi_brief`), when run, then ledger proof is consulted as primary evidence and brief markdown is consulted only as a fallback context.
- [x] REQ-0.7.0-03-03: Given `gz adr audit-check` is run on an ADR with draft OBPIs lacking ledger proof, when audit checks execute, then the output includes `ledger proof of completion is missing` for those OBPIs.
- [x] REQ-0.7.0-03-04: Given the audit pipeline, when it runs, then the artifact graph is passed through to audit checks so ledger evidence is available end-to-end.

### Implementation Summary

- Files modified: `src/gzkit/ledger.py` (added `ledger_completed` to artifact graph), `src/gzkit/commands/status.py` (updated `_inspect_obpi_brief` to prioritize ledger), `src/gzkit/cli.py` (passed graph to audit checks).
- Date completed: 2026-03-04

### Value Narrative

Before this OBPI, OBPI completion and audit checks relied on parsing brief markdown files as the source of truth. After this OBPI, audit checks consume ledger proof as primary evidence, making completion state deterministic and resistant to brief text drift.

### Key Proof

```bash
# Audit check now explicitly requires ledger proof:
uv run gz adr audit-check ADR-0.7.0-obpi-first-operations
# Output includes: "ledger proof of completion is missing" for drafts.
```

## Human Attestation

- Attestor: human:jeff
- Attestation: "Confirmed status surfaces now prioritize ledger records over file metadata."
- Date: 2026-03-04
