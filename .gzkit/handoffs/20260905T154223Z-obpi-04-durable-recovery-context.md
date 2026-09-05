---
mode: CHECKPOINT
adr_id: ADR-0.35.0
branch: main
timestamp: '2026-09-05T15:42:23Z'
agent: codex-01a07001
obpi_id: OBPI-0.35.0-04-section-ownership-and-ratchet
session_id: 01a07001-c6d4-7261-86e7-027170714777
continues_from: 20260905T125247Z-obpi-0-35-0-04-execution-paused-by-operator.md
---

## Current State Summary

Preserved 131 historical assessment and evidence files under the owning ADR, with SHA-256 inventory and a current-status index linked from OBPI-04. Implementation remains in progress; this checkpoint makes no completion claim.

## Important Context

The operator has repeatedly directed Codex to own and finish this OBPI. Conversation compaction lost the established execution plan; the archive restores it. Existing execution, commit and push authorization persists. Read the archive index before using historical reports; retain the existing scope, ledger exceptions and threat boundary.

## Decisions Made

- [operator-ruled] "these clearly need to be saved with the ADR/OBPI since your context window is not large and you clearly are not the AGI that Sam Altman says you are."
- [agent-chose] Preserve original report bytes and hashes, and distinguish dated findings from current progress in a separate index.

## Immediate Next Steps

1. Read the linked archive index and reconcile its remaining work with the live brief and source.
2. Finish native Windows implementation review and real Windows integration verification.
3. Refresh final-revision mutation and acceptance evidence, then complete the existing governed review and attestation sequence.

## Pending Work / Open Loops

Production Windows integration verification, final source-bound mutation sweep, independent acceptance review and human attestation remain unfinished. This archive does not change the standing refuted verdict.

## Verification Checklist

Archive preservation verified all 131 original SHA-256 hashes. Check live git status and source hashes against the archive manifest before reusing evidence. Historical test results do not certify subsequent source changes.

## Evidence / Artifacts

- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/appendices/obpi-04-recovery-2026-09-05/README.md`
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/appendices/obpi-04-recovery-2026-09-05/archive-manifest.json`
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/appendices/obpi-04-recovery-2026-09-05/EXECUTION.md`
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/appendices/obpi-04-recovery-2026-09-05/contract-assessment.md`

## Settled Rulings

724 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
