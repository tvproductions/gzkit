---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-05T19:59:12Z'
agent: claude-code
session_id: 2b7106c8-4b2f-45ab-ad2b-3d217ab14989
continues_from: .gzkit/handoffs/20261005T194803Z-tune-up-questions-ruled-law-landed-ci-red.md
---

## Current State Summary

This handoff supersedes the 19:48Z handoff of 2026-10-05 by one ruling and changes nothing else. After that handoff was committed, the operator ruled how CI goes green: by working item 10, not by the cleanup that would archive its FAIL plan-audit receipt. The operator then asked for a handoff and a sync before clearing context. No file other than this handoff and the session records changed between the two documents. CI is still red at the Preflight step on the two stale markers of the parked OBPI-0.35.0-10 run, and stays red until item 10's pipeline launch rewrites them. OBPI-0.35.0-10 is unchanged in the ledger: in progress, not complete, not attested, with no lock since the reap at 18:15Z on 2026-10-05 and a plan-audit receipt whose verdict is FAIL. Everything else the predecessor reports still holds: the in-flight ADR revision law is landed, every Open Design Question in briefs 15 to 20 of ADR-0.35.0 is ruled and recorded, six issues are closed, and the working order inside ADR-0.35.0 is item 10, then items 15 to 20, then items 11 to 13. The per-change gz check passed and main was level with origin before this handoff was written.

## Important Context

Read the predecessor's Important Context whole before acting; it is not restated here. Three points from it decide the next move. First, CI is red and the per-change gz check cannot see it, because Preflight runs only under gz check --full in CI; read gh run list --workflow CI --limit 3 before trusting a sync. Second, starting item 10 is not one command: the pipeline launch refuses while the plan-audit receipt for OBPI-0.35.0-10 reads FAIL, and the lock must be claimed again, so the plan audit has to reach a pass first. Third, every one of those acts is the operator's: an agent never claims a lock, clears or writes a pipeline marker, or initiates OBPI work on its own. Do not run gz preflight --apply; the operator ruled against the cleanup, and this session restored the markers after trying it. Do not use gz content land for AGENTS.md until its reordering is settled.

The operator puts decisions one at a time as short bounded choices and answers with a single letter. Before recommending on a routing or doctrine question, read every carrier of the clause; this session had to withdraw a recommendation that contradicted lane is not route.

Workflow fronts (source: docs/governance/build-to-1.0-campaign-2026-09-20.md, Workflow fronts section). Handoff system: worked (this successor seats one late ruling; the 19:48Z handoff is superseded here). GHI triage: not run. ADR and OBPI campaign: ADR-0.35.0 reads 9 of 20 by the ADR status command; item 10 is next and nothing is initiated. New R&D: not touched. The three-pillars hold on GHI #1028 is unchanged.

## Decisions Made

- [operator-ruled] CI goes green by working item 10: re-run its plan audit to a pass, claim its lock and invoke the pipeline, which rewrites the stale markers (verbatim: "A, but we need to clear context and hit a h/o and git sync"). Rejected alternative offered: rule the cleanup, which clears the markers and archives the FAIL plan-audit receipt with its finding unresolved.
- [operator-ruled] Write a handoff and sync before the context is cleared (verbatim: "we need to clear context and hit a h/o and git sync").
- [agent-chose] Wrote a short successor that seats the late ruling and points at the predecessor, in place of restating the predecessor's sections.

## Immediate Next Steps

1. The operator works item 10, which is also what turns CI green. In order: re-run the plan audit for OBPI-0.35.0-10 until its receipt reads PASS (the current receipt reads FAIL with one gap); claim the OBPI-0.35.0-10 lock; invoke gz-obpi-pipeline for it. Then read gh run list --workflow CI --limit 3 and confirm the Preflight step passes. The disposition of the earlier independent review's FAIL verdict on item 10 is also the operator's.
2. After item 10, the operator initiates the tune-up items in the ruled order: 15, 16, 17 and 20, with 18 and 19 anywhere among them, then items 11 to 13. The four repudiated OBPIs carried from earlier handoffs (OBPI-0.0.24-04, OBPI-0.0.26-02, OBPI-0.34.0-02, OBPI-0.35.0-09) still await the operator; the human-review judgment and the attestation are the operator's words, never authored.
3. The operator rules whether red CI being invisible to the local gate and to session orientation gets a work order, and whether OBPI-0.35.0-13 owns the gz content land reorder or land must refuse a reordering candidate until that brief lands. Both are recorded as insights only.
4. Before brief 19 is planned, draft Sub-Invariant 8 of .gzkit/rules/token-block-discipline.md for the operator and replace the brief's Demo block; before briefs 16, 18 and 19 are planned, settle each new flag's name in the plan. Brief 17 cannot be planned until briefs 15 and 16 are completed in the ledger.
5. Amend ADR-pool.skill-runtime-authority-inversion, which overlaps briefs 17 and 20, and find the Windows unit test that failed once on 7a920a590 with a resource-deadlock error.

## Pending Work / Open Loops

The predecessor's Pending Work is unchanged and is not restated here; read it there. One item moved: how CI goes green was open in the predecessor and is ruled here, so only the operator's execution of it remains. CI will keep failing at Preflight on every push until item 10's launch rewrites the markers; that includes the push of this handoff. Nothing new was discovered between the two documents.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD: expect 0 0 after the sync. gh run list --workflow CI --limit 3: expect failure on each completed run until item 10 is launched. uv run gz preflight: expect exit 1 naming two stale markers for OBPI-0.35.0-10 and nothing else. uv run gz obpi lock list: expect no active lock for OBPI-0.35.0-10. uv run gz obpi status OBPI-0.35.0-10-classification-reader-and-ownership: expect Runtime State IN PROGRESS and Completion PENDING. The verdict field of the plan-audit receipt for OBPI-0.35.0-10 under .claude/plans: expect FAIL until the operator re-runs the audit. uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing: expect 9 of 20. uv run gz handoff rulings --search 'CI goes green by working item 10': expect this handoff's ruling. Every other check is in the predecessor's Verification Checklist and still applies.

## Evidence / Artifacts

Predecessor, which this document supersedes and whose sections it relies on: `.gzkit/handoffs/20261005T194803Z-tune-up-questions-ruled-law-landed-ci-red.md`, landed at f755b1695. Its own predecessor: `.gzkit/handoffs/20261004T181932Z-four-first-questions-ruled-item-17-split.md`.

The surfaces the ruling concerns, none changed since the predecessor: `.claude/plans/.pipeline-active.json`, `.claude/plans/.pipeline-active-OBPI-0.35.0-10-classification-reader-and-ownership.json`, `.claude/plans/.plan-audit-receipt-OBPI-0.35.0-10-classification-reader-and-ownership.json`, `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-10-classification-reader-and-ownership.md`.

Records: `.gzkit/insights/agent-insights.jsonl` (the ci-preflight rows of 2026-10-05 describe the red CI and the stalled cleanup), `docs/governance/build-to-1.0-campaign-2026-09-20.md` (amendment 2026-10-05 carries the working order). No issue was filed, commented or closed after the predecessor was written.

## Settled Rulings

1396 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
