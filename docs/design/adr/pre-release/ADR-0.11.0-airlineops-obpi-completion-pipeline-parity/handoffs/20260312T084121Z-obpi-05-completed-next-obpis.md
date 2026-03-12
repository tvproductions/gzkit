---
mode: CREATE
adr_id: ADR-0.11.0-airlineops-obpi-completion-pipeline-parity
branch: main
timestamp: "2026-03-12T08:41:21Z"
agent: codex
obpi_id: OBPI-0.11.0-05-gz-obpi-pipeline-skill-and-mirror-surface
session_id:
continues_from: docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/handoffs/20260312T073935Z-obpi-04-completed-next-obpis.md
---

## Current State Summary

OBPI-0.11.0-05 is complete through the attestation boundary. The brief is
marked `Completed`, the parent ADR checklist now shows OBPI-01 through
OBPI-05 checked, and a completed `obpi_receipt_emitted` event was appended to
`.gzkit/ledger.jsonl` through `uv run gz obpi emit-receipt`.

Post-implementation verification passed for repository quality gates:

- `uv run gz validate --documents`
- `uv run gz lint`
- `uv run gz typecheck`
- `uv run gz test`
- `uv run mkdocs build --strict`
- `uv run -m behave features/`

The parent ADR now reports `obpi_summary.completed = 5`.

## Important Context

This tranche turned the OBPI execution pipeline into an explicit closeout
contract instead of a loose operator habit:

- the canonical `gz-obpi-pipeline` skill now defines Stage 5 as sync and
  accounting, with guarded `git sync` before final completion accounting
- mirrored skill surfaces and generated agent contracts carry the same wording
- operator/governance docs now describe the same post-attestation sequence
- tests and Gate 4 coverage lock the wording into generated surfaces

## Decisions Made

- **Decision:** Treat guarded `uv run gz git-sync --apply --lint --test` as the
  canonical Stage 5 sync ritual for gzkit.
  **Rationale:** The surfaced OBPI-03/04 drift defect was a sequencing problem,
  not a missing proof problem.
  **Alternatives rejected:** conditional sync or post-receipt sync.

- **Decision:** Track the lane-definition mismatch raised during closeout as an
  explicit governance defect.
  **Rationale:** Current canon can be read more broadly than the operator rule
  "Heavy only when APIs, commands, or other human/system-used runtime surfaces
  change."
  **Alternatives rejected:** silently accepting the mismatch.

## Immediate Next Steps

1. Implement OBPI-0.11.0-06 to align templates, closeout guidance, and
   migration/doctrine surfaces with the faithful pipeline contract.
2. Reconcile the lane-definition mismatch surfaced during OBPI-05 so canon and
   operator intent agree on what actually triggers Heavy lane.
3. Revisit OBPI-03 and OBPI-04 completion receipts now that the pipeline order
   is explicit, and capture clean replacements if needed.

## Pending Work / Open Loops

ADR-0.11.0 remains incomplete with only OBPI-0.11.0-06 still open.

Open defects carried forward:

- OBPI-03 still reports anchor drift and dirty-worktree receipt evidence.
- OBPI-04 still reports anchor drift and dirty-worktree receipt evidence.
- The lane doctrine may currently over-classify process/documentation surface
  changes as Heavy compared with the operator rule expressed during OBPI-05
  closeout.

## Verification Checklist

- [x] `uv run gz validate --documents` passes
- [x] `uv run gz lint` passes
- [x] `uv run gz typecheck` passes
- [x] `uv run gz test` passes
- [x] `uv run mkdocs build --strict` passes
- [x] `uv run -m behave features/` passes
- [x] `uv run gz adr status ADR-0.11.0-airlineops-obpi-completion-pipeline-parity --json` reports `obpi_summary.completed = 5`

## Evidence / Artifacts

- `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/obpis/OBPI-0.11.0-05-gz-obpi-pipeline-skill-and-mirror-surface.md`
- `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity.md`
- `docs/design/adr/pre-release/ADR-0.11.0-airlineops-obpi-completion-pipeline-parity/handoffs/20260312T084121Z-obpi-05-completed-next-obpis.md`
- `.gzkit/ledger.jsonl`
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md`
- `AGENTS.md`
- `docs/user/commands/git-sync.md`
- `docs/governance/GovZero/obpi-runtime-contract.md`
- `tests/test_sync.py`
- `features/heavy_lane_gate4.feature`
