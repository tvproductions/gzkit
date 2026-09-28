---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-09-28T09:22:44Z'
agent: claude-code
session_id: f56ac20c-69a6-4172-9cce-26bfa359fc7c
continues_from: .gzkit/handoffs/20260928T091343Z-obpi-07-completed.md
---

## Current State Summary

Session f56ac20c ended with a clean tree in sync with origin/main (HEAD ad10c0814) and no OBPI locks held. Delivered this session: the git-sync type-check repair (2cb130920); GHI #1143 closed fixed (d3e97d2a7, 4723e2d20); GHI #1144 filed (investigation, open); OBPI-0.35.0-07-content-land-orchestrator taken from its paused Step 4b to ATTESTED COMPLETED (d7ea6e55b, 71af9ed3e). ADR-0.35.0 now stands at 9/14 OBPIs, and its closeout is blocked on OBPI-0.35.0-08, -10, -11, -12 and -13.

## Important Context

ADR-0.35.0 is the lowest feature ADR with unlanded OBPIs and the campaign's TOPMOST item; only the operator initiates its next OBPI (gz-obpi-pipeline). Lessons from OBPI-07 that apply to the next heavy OBPI: any edit to a brief's contract (REQs, Threat Model) stales every proof and review, so settle the Threat Model before Step 4b round 1. Compose any prompt containing backticks with a quoted heredoc. Re-run gz obpi brief-drift after acceptance proofs, because they bump source mtimes. Author the brief's '### Step 4b — Independent Adversarial Validation' section before the first push after gz obpi complete. Codex tier 1 on this Mac: plugin 1.0.6, task --write, ready true.

## Decisions Made

- [agent-chose] Wrote a session-end handoff chained to the OBPI-07 completion handoff, rather than editing that record.

## Immediate Next Steps

1. Present ADR-0.35.0's remaining OBPIs (read live from uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing) so the operator can initiate the next one through gz-obpi-pipeline.
2. On the operator's go, run ghi-triage over the open queue, which now includes GHI #1144.
3. On the operator's go, route the four gz-obpi-pipeline and brief-drift insights recorded 2026-09-28 (skill drift on lock release, the missing Step 4b authoring step, the mtime-keyed drift receipt, gz test --obpi without a timeout) through gz-skill-review or ghi-author.

## Pending Work / Open Loops

- GHI #1144: unittest-parallel worker deadlock root cause, plus instrumentation that names the stalled test.
- Insights from 2026-09-28 not yet routed: (a) gz-obpi-pipeline Stage 5 lock-release step disagrees with gz obpi complete; (b) Stage 5 lacks the Step 4b section authoring step; (c) the brief-reconcile receipt is mtime-keyed; (d) gz test --obpi has no hang bound; (e) the unquoted-heredoc near-miss.
- Carried from earlier handoffs, still operator-gated: the ruling-docket session; the design-amendment disposition-2 GHIs; OBPI-0.37.0-04 line 64 reconciliation when ADR-0.37.0 is drawn.

## Verification Checklist

git status -sb (expect main in sync, clean); uv run gz obpi status OBPI-0.35.0-07-content-land-orchestrator (expect ATTESTED COMPLETED); uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing, which reports the landed OBPI count; uv run gz obpi lock list (expect no active locks); gh issue view 1144 (expect OPEN).

## Evidence / Artifacts

- `.gzkit/handoffs/20260928T091343Z-obpi-07-completed.md` (OBPI-07 completion handoff)
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-07-content-land-orchestrator.md` (Change Log, Step 4b section)
- `.gzkit/evidence/OBPI-0.35.0-07-content-land-orchestrator.stage4a.md`
- `.gzkit/insights/agent-insights.jsonl` (the 2026-09-28 insights)

## Settled Rulings

1162 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
