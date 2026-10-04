---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-04T08:02:46Z'
agent: claude-code
session_id: 7a7dbaad-9721-40d3-9fd3-0c8e6ab30cda
continues_from: .gzkit/handoffs/20261004T074708Z-switch-off-reversed-tune-up-review-booked.md
---

## Current State Summary

The predecessor handoff ended on four questions for the operator, and the operator answered all four in the same session. Nothing was implemented after those answers: the operator directed that they be written to a handoff and synced because the session's context was high. Commit 661d4eb59 (the full reversion and its records) and the predecessor handoff are pushed; origin/main was in sync at 8cd1a62aa before this handoff. CI on 8cd1a62aa was in progress when this was written, and the Code Quality workflow on it had succeeded. No GHI was filed, no OBPI was initiated, and OBPI-0.35.0-10 is unchanged: in progress, not complete, not attested, its lock held by claude-code-a0f543a5 until 2026-10-04T12:35Z.

## Important Context

The operator's reason for stopping is itself the session's finding: a long session re-reads a large context on every call and attends worse, so each unit of work below starts in a fresh session. The ghi-author skill was loaded and its Step 0 prior-art lookup was NOT run, so no defect below has been checked against the open queue yet. Only the operator initiates OBPI work, and the 2026-10-03 (2) amendment has each OBPI initiated on its own through gz-obpi-pipeline; the rulings below settle what is to be done, and the operator still invokes the pipeline for each OBPI. OBPI-0.35.0-10's lock belongs to another session's agent id, so a new session cannot use it as its own before it is reaped after 2026-10-04T12:35Z. The review record at docs/governance/context-phase-review-2026-10-04-evidence/README.md holds the measurements, the nine conversation-only state items and the proposals the design dialogue starts from. Workflow fronts (source: the campaign plan, Workflow fronts section): handoff system was worked; ghi triage was not run; adr/obpi campaign: rulings booked and nothing initiated, with the landed count of ADR-0.35.0 read from gz adr status; new R&D was not touched. The three-pillars hold on GHI #1028 is unchanged.

## Decisions Made

- [operator-ruled] The tune-up is drawn through a gz-design dialogue (verbatim: "1. yes").
- [operator-ruled] The four verified defects and the attestation label go to GHIs for direct repair (verbatim: "2. yes, GHI").
- [operator-ruled] OBPI-0.35.0-10 is repaired by working the pipeline and is completed (verbatim: "3. we repair by working the pipeline - we commit to completing the obpi").
- [operator-ruled] The four repudiated OBPIs are re-completed, done properly (verbatim: "4. yes, we do the work right and thoroughly.").
- [operator-ruled] Write these to a handoff and sync instead of continuing in this session (verbatim: "but make that a handoff and git sync" and "context is high now").
- [agent-chose] Stopped before filing any GHI; the prior-art lookup and the five issues are left for a fresh session.

## Immediate Next Steps

1. In a fresh session, file the five GHIs through ghi-author, running its prior-art lookup first: the unread no-subagents flag of gz obpi pipeline (src/gzkit/cli/parser_obpi.py); the pipeline skill's abort path prescribing a lock release that exits 3; the session orientation's always-empty pipeline section (scripts/session_orientation.py); the pipeline skill citing GHI #196 [settled] where the precomplete issue is GHI #195 [settled]; and gz obpi status printing Attestation State not_required for an uncompleted OBPI (src/gzkit/ledger_semantics.py). Each is recorded in .gzkit/insights/agent-insights.jsonl. Then repair each as a direct fix.
2. The operator opens the gz-design dialogue for the tune-up: phased OBPI runs with runtime-written save points, a marker that advances within a run, lock continuity across a phase boundary, proof staleness scoped to what a proof names, the pipeline skill split by stage, and refusal records for hooks and validators. Ask where it sits relative to ADR-0.35.0.
3. After 2026-10-04T12:35Z, the operator invokes gz-obpi-pipeline for OBPI-0.35.0-10 to repair findings E1 to E5 from docs/governance/obpi-run-cost-2026-10-03-evidence/trial-evaluation.md and complete it. The human-review judgment and the attestation are the operator's words; never author them.
4. The operator invokes gz-obpi-pipeline for each repudiated OBPI in turn: OBPI-0.0.24-04, OBPI-0.0.26-02, OBPI-0.34.0-02 and OBPI-0.35.0-09.
5. Confirm CI on 8cd1a62aa finished green with the full sweep.

## Pending Work / Open Loops

The predecessor handoff names every other open loop in full and none has changed: the unrepaired findings E1 to E6 on OBPI-0.35.0-10 and its unreviewed agent choices; GHI #1154 and GHI #1155 with their owed decisions; GHI #799 waiting on OBPI-0.35.0-10; trackers GHI #611, GHI #921, GHI #978, GHI #1125, GHI #1149 and GHI #1028 under its hold; the unfiled insights; the falling tautological-test debt ceiling; the instruction-file and skill-body budget overruns; the 2026-10-03 amendment's standing items; ghi-triage not run; the stray Codex processes; and the queued Claude Code feedback draft. New here: CI on the switch-off commit b4aedb453 had failed and was not investigated, since that state is reversed. The pipeline-profile idea (fast, standard, max) was withdrawn and is not a pending item.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD: expect 0 0. gh run list --limit 3: expect CI on 8cd1a62aa or later completed with success. uv run gz obpi lock list: expect no OBPI-0.35.0-10 lock after 2026-10-04T12:35Z. uv run gz obpi status OBPI-0.35.0-10-classification-reader-and-ownership: expect Runtime State IN PROGRESS and Completion PENDING until the pipeline completes it. gh issue list --state open --limit 10: expect no issue yet for the five defects. uv run gz handoff rulings --search "commit to completing": expect this handoff's ruling.

## Evidence / Artifacts

Records: `docs/governance/build-to-1.0-campaign-2026-09-20.md`, `docs/governance/context-phase-review-2026-10-04-evidence/README.md`, `docs/governance/obpi-run-cost-2026-10-03-evidence/trial-evaluation.md`, `.gzkit/insights/agent-insights.jsonl`. Predecessor: `.gzkit/handoffs/20261004T074708Z-switch-off-reversed-tune-up-review-booked.md`, whose resume decision is booked proceed under session 7a7dbaad-9721-40d3-9fd3-0c8e6ab30cda with the operator's four answers. Commits: 661d4eb59 and 8cd1a62aa.

## Settled Rulings

1322 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
