---
mode: CREATE
adr_id: ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
branch: main
timestamp: "2026-03-11T10:52:50Z"
agent: codex
obpi_id: OBPI-0.11.0-02-obpi-completion-validator-and-git-sync-gate
session_id:
continues_from:
---

## Current State Summary

OBPI-0.11.0-02 is complete through the heavy-lane attestation boundary and sync stage. The brief is marked `Completed`, the parent ADR checklist now shows OBPI-01 and OBPI-02 checked, and an `obpi_receipt_emitted` completion receipt was written to `.gzkit/ledger.jsonl`. Post-attestation runtime verification passed: `uv run gz obpi reconcile OBPI-0.11.0-02-obpi-completion-validator-and-git-sync-gate` reported `PASS`, and `uv run gz adr status ADR-0.11.0-airlineops-obpi-completion-pipeline-parity --json` now reports `obpi_summary.completed = 2`.

## Important Context

The OBPI execution rule is now explicit: use `gz-obpi-pipeline` for all OBPI runs, not freeform implementation. Exact AirlineOps hook-enforcement parity is intentionally not part of OBPI-02; it is tracked in `ADR-pool.obpi-pipeline-enforcement-parity`. A governance defect was reconciled during OBPI-02 completion: the brief had claimed dirty worktrees must fail the validator, but the implemented gzkit validator and the AirlineOps reference both use syncable-state semantics for the pre-completion validator and leave clean-tree enforcement to later receipt/sync behavior. Also note a separate drift defect: `.agents/skills/gz-session-handoff/SKILL.md` references a helper module under `tests/governance/test_session_handoff.py`, but that module does not exist in this repo.

## Decisions Made

- **Decision:** Keep OBPI-0.11.0-02 scoped to the validator/doc/test tranche and do not absorb exact hook-enforcement parity.
  **Rationale:** The approved plan kept AirlineOps-style hook routing and gating in the pool ADR `ADR-pool.obpi-pipeline-enforcement-parity`, avoiding scope collapse across multiple unfinished OBPIs.
  **Alternatives rejected:** Folding plan-audit gating, pipeline-router parity, and pipeline-gate parity into OBPI-02.

- **Decision:** Reconcile the OBPI-02 brief to syncable-state validator semantics instead of changing the implementation to dirty-worktree blocking.
  **Rationale:** `src/gzkit/hooks/obpi.py`, `src/gzkit/git_sync.py`, the command docs, the tests, and the AirlineOps validator all aligned on hard-blocker enforcement rather than dirty-tree blocking.
  **Alternatives rejected:** Rewriting the validator and tests to fail on any dirty worktree despite the reference implementation disagreeing.

- **Decision:** Use the supported runtime receipt surface `uv run gz obpi emit-receipt ... --event completed` for the attested completion event.
  **Rationale:** This repo does not expose a dedicated `gz-obpi-audit` CLI; runtime reconciliation is ledger-driven from receipt events.
  **Alternatives rejected:** Direct ledger edits or inventing an unbacked audit command.

## Immediate Next Steps

1. Implement `OBPI-0.11.0-03` through `gz-obpi-pipeline`, focusing on recorder semantics and structured git-anchored receipt evidence.
2. Implement `OBPI-0.11.0-04` through `gz-obpi-pipeline`, using the new recorder evidence from OBPI-03 to drive drift detection and reconciliation.
3. Promote `ADR-pool.obpi-pipeline-enforcement-parity` or otherwise land the exact AirlineOps hook-enforcement parity so OBPI runs are mechanically routed into the pipeline.
4. Repair the `gz-session-handoff` skill drift by either restoring the referenced helper module or correcting the skill to documented/manual creation behavior.

## Pending Work / Open Loops

ADR-0.11.0 remains incomplete with four OBPIs still open: OBPI-03, OBPI-04, OBPI-05, and OBPI-06. The parent ADR status remains `Pending` and `closeout_ready = false` until those OBPIs carry both file completion and ledger proof. The repository also still contains the pool ADR `ADR-pool.obpi-pipeline-enforcement-parity`, which exists because gzkit currently lacks the same hard hook chain AirlineOps uses to force `gz-obpi-pipeline` entry every time.

## Verification Checklist

- [ ] `uv run gz obpi reconcile OBPI-0.11.0-02-obpi-completion-validator-and-git-sync-gate` returns `PASS`
- [ ] `uv run gz obpi status OBPI-0.11.0-02-obpi-completion-validator-and-git-sync-gate --json` shows `runtime_state` as `attested_completed`
- [ ] `uv run gz adr status ADR-0.11.0-airlineops-obpi-completion-pipeline-parity --json` shows `obpi_summary.completed` as `2`
- [ ] `git status --short` only shows the expected ledger/ADR/brief/handoff changes for this completion transaction

## Evidence / Artifacts

- `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/obpis/OBPI-0.11.0-02-obpi-completion-validator-and-git-sync-gate.md` — attested-complete OBPI brief with value narrative, key proof, evidence, and human attestation
- `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md` — parent ADR checklist with OBPI-01 and OBPI-02 checked
- `.gzkit/ledger.jsonl` — appended `obpi_receipt_emitted` completion evidence for OBPI-0.11.0-02
- `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/handoffs/20260311T105251Z-obpi-02-completed-next-obpis.md` — this handoff for the remaining ADR work
- `docs/design/adr/pool/ADR-pool.obpi-pipeline-enforcement-parity.md` — follow-on governance artifact for exact AirlineOps hook parity

## Environment State

Repository root: `/Users/jeff/Documents/Code/gzkit`. Branch: `main`. The active pipeline marker for OBPI-02 was removed after the completion receipt was emitted. There is no repo CLI for session handoff creation at the moment, so this file was created directly from the handoff template and validated manually against the required sections and referenced paths.
