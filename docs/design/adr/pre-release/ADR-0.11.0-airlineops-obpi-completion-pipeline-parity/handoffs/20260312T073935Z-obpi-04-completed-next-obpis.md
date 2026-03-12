---
mode: CREATE
adr_id: ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
branch: main
timestamp: "2026-03-12T07:39:35Z"
agent: codex
obpi_id: OBPI-0.11.0-04-anchor-aware-obpi-drift-and-reconciliation
session_id:
continues_from: docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/handoffs/20260312T070240Z-obpi-03-completed-next-obpis.md
---

## Current State Summary

OBPI-0.11.0-04 is complete through the heavy-lane attestation boundary. The
brief is marked `Completed`, the parent ADR checklist now shows OBPI-01 through
OBPI-04 checked, and a completed `obpi_receipt_emitted` event was appended to
`.gzkit/ledger.jsonl` through `uv run gz obpi emit-receipt`.

Post-attestation verification passed for repository quality gates:

- `uv run gz validate --documents`
- `uv run gz lint`
- `uv run gz typecheck`
- `uv run gz test`
- `uv run mkdocs build --strict`
- `uv run -m behave features/`

The parent ADR now reports `obpi_summary.completed = 4`. The focused runtime
state for OBPI-04 is intentionally not clean yet:

- `uv run gz obpi reconcile OBPI-0.11.0-04-anchor-aware-obpi-drift-and-reconciliation --json`
  returns `passed = false`
- `runtime_state = drift`
- `anchor_state = degraded`
- blocker: `completion receipt was captured from a dirty worktree`

## Important Context

This tranche added anchor-aware OBPI reconciliation without changing the CLI
shape:

- `derive_obpi_semantics()` now returns `anchor_state`, `anchor_commit`,
  `current_head`, `anchor_issues`, and `anchor_drift_files`
- `gz obpi status`, `gz obpi reconcile`, and ADR status rows all surface those
  fields and preserve exact OBPI blocker strings
- completion accounting remains separate from drift signaling, so OBPIs can be
  counted as completed while still failing closeout on anchor blockers

## Decisions Made

- **Decision:** Treat anchor mismatch as blocking only when files changed since
  the anchor overlap the recorded OBPI scope.
  **Rationale:** A simple `anchor != HEAD` rule would make every later commit
  drift every completed OBPI, which is not operationally useful.
  **Alternatives rejected:** unconditional HEAD mismatch drift.

- **Decision:** Keep recorder-time dirty/diverged git evidence as explicit
  reconciliation blockers.
  **Rationale:** The OBPI brief requires explicit blocker reporting for stale or
  degraded anchor evidence.
  **Alternatives rejected:** downgrading recorded dirty/diverged state to an
  informational warning only.

## Immediate Next Steps

1. Implement OBPI-0.11.0-05 so the staged pipeline owns the post-attestation
   sync order instead of leaving receipt emission timing to operator habit.
2. Implement OBPI-0.11.0-06 so templates and closeout guidance reflect the
   anchor-aware runtime states now surfaced by OBPI-04.
3. Revisit OBPI-03 and OBPI-04 receipt timing after pipeline alignment so
   clean completion receipts are captured from a clean worktree rather than
   immediately reconciling as drift.

## Pending Work / Open Loops

ADR-0.11.0 remains incomplete with OBPI-05 and OBPI-06 still open. Closeout is
also blocked by the newly surfaced pipeline defect:

- OBPI-03 now reports `stale` anchor drift because its completion receipt was
  captured before later recorded-scope changes landed.
- OBPI-04 now reports `degraded` anchor drift because its completion receipt was
  captured from a dirty worktree during ceremony sync.

This is a real process defect, not a status rendering glitch. The current
pipeline order allows a heavy-lane OBPI to be attested and synced while still
recording a dirty completion snapshot. That defect should be closed in the
remaining pipeline/template OBPIs rather than ignored.

## Verification Checklist

- [x] `uv run gz validate --documents` passes
- [x] `uv run gz lint` passes
- [x] `uv run gz typecheck` passes
- [x] `uv run gz test` passes
- [x] `uv run mkdocs build --strict` passes
- [x] `uv run -m behave features/` passes
- [x] `uv run gz adr status ADR-0.11.0-airlineops-obpi-completion-pipeline-parity --json` reports `obpi_summary.completed = 4`
- [x] `uv run gz obpi reconcile OBPI-0.11.0-04-anchor-aware-obpi-drift-and-reconciliation --json` reports the dirty-worktree blocker explicitly

## Evidence / Artifacts

- `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/obpis/OBPI-0.11.0-04-anchor-aware-obpi-drift-and-reconciliation.md`
- `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md`
- `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/handoffs/20260312T073935Z-obpi-04-completed-next-obpis.md`
- `.gzkit/ledger.jsonl`
- `src/gzkit/ledger.py`
- `src/gzkit/commands/status.py`
- `src/gzkit/utils.py`
- `src/gzkit/cli.py`
- `tests/test_ledger.py`
- `tests/commands/test_status.py`
- `features/obpi_anchor_drift.feature`
