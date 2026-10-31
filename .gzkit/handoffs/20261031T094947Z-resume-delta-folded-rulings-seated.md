---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-31T09:49:47Z'
agent: claude-code
session_id: 63a4e8a8-02b8-40ae-be37-ff789c2cc4bc
continues_from:
- .gzkit/handoffs/20261031T091156Z-ghi-1273-mx-signal-repaired-and-closed.md
- .gzkit/handoffs/20261031T093958Z-session-exit-bookmark.md
- .gzkit/handoffs/20261031T094002Z-session-exit-bookmark.md
---

## Current State Summary

Drydock safe mode, RO-0. This session folded the delta left after the last authored handoff and made no repair. The tautological audit's seven findings were cleared by 759d1355e and logged by 31c956d33; this session closed the matching discrepancy line in aa40500ff. CI run 41188802273 on 31c956d33 shows check green on ubuntu and windows and full-strength-report green. Last action: this handoff and the git sync. RO-12's preconditions are next, starting with #1200.

## Important Context

A peer session ended without a handoff at 09:39Z and left the handoff-picture rulings only in uncommitted insights (scope handoff-picture); they are seated here. Its next step was to settle the git-sync staging, then write the handoff skill specification on the operator's word; no commit shows the specification was written. Two sessions were live at once around 09:22Z, which is how the pre-commit-stash defect surfaced. In zsh, a bare ===== word fails, which cost a resume probe here, as the predecessor warned. git add of one path still commits whatever else is staged: the two exit bookmarks landed in aa40500ff. Shift turnover: read the contract's list of discrepancies and passage log and gz obpi lock list; only mx-session is held, no tags are hung because the tag-out log does not exist until RO-12, no finding awaits buy-back, and no work package is commenced. Workflow fronts (docs/governance/build-to-1.0-campaign-2026-09-20.md#workflow-fronts): this session touched the handoff system and the adr/obpi campaign front through the drydock; ghi triage and new R&D were not worked.

## Decisions Made

- [operator-ruled] Clean up first, then go to #1200: close the stale discrepancy line, fold the delta and rulings into a superseding handoff, commit, then bring #1200's first question (verbatim: "a").
- [agent-chose] Seated the peer session's final wording of the three levels, not its two earlier insights, which that wording superseded.
- [agent-chose] Marked the discrepancy line cleared on CI's full-strength-report and the passage log's gz check --full exit 0, keeping the arb red verdict undriven as an open note.

## Immediate Next Steps

1. Continue RO-12's preconditions as direct fixes: put #1200, #1206, #1208 and #1028 to the operator in that order, one question at a time, with the other reused-part defects RO-12's row lists. #1200 first surfaces OBPI-0.35.0-18-dispatch-outcome-recording's claim on the count, then what exits the bound, then whether an escalation at the bound may carry an agent recommendation.
2. File the rebase trap through ghi-author: insight scope mx-1273, the post-commit recorder appending artifact_edited rows during a rebase.
3. Ask the operator to look at the Mermaid drawing that opens at docs/governance/harbor-pilotage-candidate-2026-10-15.md line 83; it was never observed rendering.
4. Ask the operator when to write the handoff skill specification, each level specified by the question it answers with the release horizons as proxies.

## Pending Work / Open Loops

- The pre-commit-stash defect is held only as an insight: a concurrent append during the stash window fails the commit, by a path GHI #1092 [settled] fixed only for the commit-locus recorder.
- gz arb red on 759d1355e returned undriven: one change killed, one surviving as a behavior-preserving extraction, four inconclusive.
- #1272 and #1289 stay open, owned by RO-13's F5; the solo validator scopes go to RO-13's enumerator and R1.
- RO-13's T0 tables are undrafted, owed before the retrofit.
- RO-4 ruling 6 against RO-8 ruling 1 remains open.
- The orientation hook output is over its injected-text budget, measured at 4405 B this session.
- Known limits in docs/governance/harbor-1273-mx-signal-review.md stand.
- The MX session has carried advisory debt past its lease; gz mx renew needs --attestor when the lease lapses.

## Verification Checklist

- git status -sb reads main in step with origin/main.
- gh run view 41188802273 --json jobs shows all three jobs at success.
- uv run gz handoff rulings --search 'scope proxy' returns the seated ruling.
- uv run gz handoff rulings --search 'Per session' returns the seated ruling.
- uv run gz obpi lock list shows the mx-session lease.

## Evidence / Artifacts

- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- `docs/governance/harbor-1273-mx-signal-review.md`
- `.gzkit/insights/agent-insights.jsonl`
- Commits 759d1355e, 31c956d33 and aa40500ff on main.

## Settled Rulings

1894 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
