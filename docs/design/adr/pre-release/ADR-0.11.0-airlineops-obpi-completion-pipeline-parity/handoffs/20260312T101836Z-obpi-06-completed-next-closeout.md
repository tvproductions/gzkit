---
mode: CREATE
adr_id: ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
branch: main
timestamp: "2026-03-12T10:18:36Z"
agent: codex
obpi_id: OBPI-0.11.0-06-template-closeout-and-migration-alignment
session_id:
continues_from: docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/handoffs/20260312T084121Z-obpi-05-completed-next-obpis.md
---

## Current State Summary

OBPI-0.11.0-06 is complete through the attestation boundary. The brief is
marked `Completed`, the parent ADR checklist now shows OBPI-01 through
OBPI-06 checked, and the doctrine/template/operator surfaces now match the
faithful OBPI completion pipeline that runtime expects.

Post-implementation verification passed for repository quality gates:

- `uv run gz agent sync control-surfaces`
- `uv run gz validate --documents`
- `uv run gz lint`
- `uv run gz typecheck`
- `uv run gz test`
- `uv run mkdocs build --strict`
- `uv run -m behave features/`

## Important Context

This tranche resolved the last guidance-layer contradictions inside ADR-0.11.0:

- Heavy lane is now defined prospectively as command/API/schema/runtime-contract
  change, not generic documentation or process work
- OBPI brief and generated control-surface templates now use gz-native
  verification commands instead of legacy `unittest` placeholders
- workflow/runbook docs now describe the same closeout order the runtime and
  pipeline enforce: verify, attest when required, guarded `git sync`, final
  OBPI completion accounting
- migration notes in ADR-0.7.0 and ADR-0.10.0 redirect operators to the active
  ADR-0.11.0 workflow surfaces

## Decisions Made

- **Decision:** Apply the narrowed Heavy-lane doctrine prospectively and keep
  OBPI-05 as historical record rather than rewriting its closure history.
  **Rationale:** The operator rule is now encoded in canon without retroactive
  record surgery.
  **Alternatives rejected:** retroactive lane relabeling of already-completed
  OBPIs.

- **Decision:** Keep parent-ADR human attestation explicit in the OBPI-06 brief
  even though the child lane is Lite.
  **Rationale:** The parent ADR remains Heavy and the closeout record should
  preserve that inheritance boundary.
  **Alternatives rejected:** silent self-close semantics for the final child.

## Immediate Next Steps

1. Emit the final completed receipt for OBPI-0.11.0-06 from the synced
   repository state.
2. Reconcile OBPI-0.11.0-06 and confirm the parent ADR now reports
   `obpi_summary.completed = 6`.
3. Begin ADR-0.11.0 closeout: `gz adr audit-check`, `gz closeout`,
   `gz attest`, `gz audit`, and `gz adr emit-receipt`.

## Pending Work / Open Loops

ADR-0.11.0 should now be blocked only by ADR-level closeout and attestation
once the final OBPI receipt is written and reconciled.

## Verification Checklist

- [x] `uv run gz agent sync control-surfaces` passes
- [x] `uv run gz validate --documents` passes
- [x] `uv run gz lint` passes
- [x] `uv run gz typecheck` passes
- [x] `uv run gz test` passes
- [x] `uv run mkdocs build --strict` passes
- [x] `uv run -m behave features/` passes

## Evidence / Artifacts

- `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/obpis/OBPI-0.11.0-06-template-closeout-and-migration-alignment.md`
- `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md`
- `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/handoffs/20260312T101836Z-obpi-06-completed-next-closeout.md`
- `.gzkit/ledger.jsonl`
- `docs/governance/GovZero/charter.md`
- `docs/user/concepts/lanes.md`
- `docs/user/concepts/workflow.md`
- `docs/user/runbook.md`
- `src/gzkit/templates/obpi.md`
- `AGENTS.md`
- `tests/test_sync.py`
- `features/heavy_lane_gate4.feature`
