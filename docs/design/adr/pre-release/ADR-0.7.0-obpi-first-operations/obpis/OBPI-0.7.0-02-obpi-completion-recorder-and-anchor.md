---
id: OBPI-0.7.0-02-obpi-completion-recorder-and-anchor
parent: ADR-0.7.0-obpi-first-operations
item: 2
lane: Heavy
status: attested_completed
---

# OBPI-0.7.0-02-obpi-completion-recorder-and-anchor: Obpi Completion Recorder And Anchor

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.7.0-obpi-first-operations/ADR-0.7.0-obpi-first-operations.md`
- **Checklist Item:** #2 — "Implement OBPI completion recorder and anchor parity."

**Status:** Completed

## Objective

Record OBPI completion transitions as first-class runtime events with optional git anchor capture for temporal provenance.

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 (Mode C — derived from Objective, Implementation Summary, and Key Proof).
-->

- [x] REQ-0.7.0-02-01: Given an OBPI completion transition, when the recorder hook runs, then a first-class `obpi_receipt_emitted` event is appended to `.gzkit/ledger.jsonl`.
- [x] REQ-0.7.0-02-02: Given the recorder is enabled, when a completion event fires, then the emitted event includes an `anchor` object capturing the current git commit hash.
- [x] REQ-0.7.0-02-03: Given the recorder is enabled, when a completion event fires, then the emitted event includes the OBPI's parent ADR semver in the anchor metadata.
- [x] REQ-0.7.0-02-04: Given the recorder integrates with the hook system, when an OBPI brief transitions to Completed, then the recorder runs automatically (no manual CLI invocation required).

### Implementation Summary

- Files created: `src/gzkit/utils.py` (Git/Exec utilities)
- Files modified: `src/gzkit/ledger.py` (updated event schema), `src/gzkit/hooks/core.py` (automated recorder integration), `src/gzkit/cli.py` (command-level anchor capture)
- Tests added: `test_recorder_appends_receipt_to_ledger` in `tests/test_obpi_validator.py`
- Date completed: 2026-03-04

### Value Narrative

Before this OBPI, OBPI completion transitions were fire-and-forget — no runtime event was recorded and there was no git anchor to prove when the work was done. After this OBPI, every completion transition emits a first-class ledger event with an optional git anchor commit, establishing temporal provenance for the OBPI lifecycle.

### Key Proof

```bash
# Verify ledger event with anchor:
tail -n 1 .gzkit/ledger.jsonl
# Output: {"event":"obpi_receipt_emitted", ..., "anchor":{"commit":"19f5230","semver":"0.7.0"}}
```

## Human Attestation

- Attestor: human:jeff
- Attestation: "Confirmed automated recorder hook correctly captures git state."
- Date: 2026-03-04
