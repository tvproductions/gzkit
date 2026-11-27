---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-27T09:24:54Z'
agent: claude-code
session_id: 0cce0fdc-f063-4df2-a674-b3dfa432e382
continues_from: .gzkit/handoffs/20261127T080353Z-m25-m29-ty-rp4-r9-rnd-resumed.md
---

## Current State Summary

Resumed the conceptual-model R&D on the operator's ruling 'renew the lease, then proceed' (booked through gz handoff decide). The MX lease was renewed through gz-mx. The construction question was ruled: RP-12's kit obligations are construction (catalog REQs), built legitimately in the drydock, which repairs, refits, rearms and upgrades; the REQs need not wait for civil rule; RP-12 may hold FIXes beside them (4c9ed55c0). W9 stands as ruled; the agent wrongly re-put it, and the record now sets the method: a paused ruling is checked against later rulings, never put again (a1a0480ab). The agent then called the prompt audit's M30 to M51 untracked; the operator asked for a tracking GHI, #1398 was filed, then withdrawn on the operator's word, since those rows are carried by the landed audit map and the ruled walk (8d7e634a0). Five insights recorded the session's corrections. Last action: this handoff, then git-sync on the operator's words.

## Important Context

Safe mode is still open (docs/governance/harbor-pilotage-candidate-2026-10-15.md). Every act is one commit with a Task: trailer.
Shift turnover, reviewed 2026-11-27:
- gz wp tag show --all: No tag has been issued.
- gz wp runs: No work package is in flight.
- gz obpi lock list: mx-session ACTIVE, renewed this session.
- The buy-back record is not built.
Communication, operator ruling of this session: in a CLI session, lead every reply with the vital facts and the direct answers, short; the operator cannot always read long replies.
The three-level brief: the ruling 'The picture is a tactical, operational and strategic brief known at every major state change' binds, and the session's two edges are the handoff's bookends. No surface builds it (the contract's list of discrepancies holds the line open). Give it by hand at resume and at handoff until it is built.
Method for the R&D's paused rulings (W44 to W50, W9 done): check each against the later rulings; record it standing where nothing contradicts it; put only a contradiction to the operator, both rulings quoted. T37 and the sub-ids were never ruled, so they are real questions, put only after canon is checked.
Doctrine carried: the drydock moves forward to the new structure (insight prompt-audit:drydock-forward-not-doctor); last_reviewed records a review, never an edit; skill-surface-sync.md rule 6 still says otherwise and waits for diamond 2.

## Decisions Made

- [operator-ruled] Renew the MX lease, then proceed with the advised steps (verbatim: "renew the lease, then proceed").
- [operator-ruled] RP-12's kit obligations are construction, catalog REQs, built legitimately in the drydock without waiting for civil rule (verbatim: "A, but we don't need to wait for civil rule - classic dry dock is for repair, refit, rearm, or even upgrade - most of RP-12 is to reshape older gzkit structures with new, so even if these are REQs, the dry dock is purposeful and legitimate.").
- [operator-ruled] RP-12 may hold FIXes beside its REQs (verbatim: "and, it could well be that there are a mix of FIX and REQ in RP-12").
- [operator-ruled] A prior ruling is not re-adjudicated; W9 stands (verbatim: "A (and why have me reevaluate and reajudicate prior rulings? that is how drift happens. Why are you reopening a past ruling?)").
- [operator-ruled] Withdraw the tracking GHI #1398 (verbatim: "the belay the ghi request").
- [operator-ruled] Write a fresh handoff and git-sync (verbatim: "fresh handoff and git sync").
- [agent-chose] Closed #1398 as withdrawn citing cbad48c18 and 8f2ffdd67, the landed audit map and the walk's ruling, so the withdrawal names where the work is carried.

## Immediate Next Steps

1. Give the operator the strategic, operational and tactical brief at resume, short, vital facts first.
2. Resume the prompt-audit walk at M30 (docs/rnd/conceptual-model/sources/prompt-audit-2026-11-25.md, Revised mechanism map), on the operator's go: screen each row against the repair order that retires its subject, then file it through ghi-author as its own GHI, repair, have a reviewer subagent confirm, and close through ghi-close. M30 to M51 remain.
3. After the walk, the R&D's T37 and the sub-ids: check canon first, then put each as its own question.
4. Then check W44 to W50 against the separated model (record each standing or put a contradiction), the open frontier from the construction ruling (how a drydock package carries REQs beside FIXes; the release reading of drydock construction), the disposition map, docs/rnd/conceptual-model/review.md and sign-off.

## Pending Work / Open Loops

- Prompt audit M30 to M51 unwalked; #1357 (M1) still open.
- #1388 awaits the operator's ruling on the gz chores run exit code.
- OBPI-0.35.0-16 row 12 records the runtime printing --apply --lint --test; amending it is the operator's act.
- The three-level brief is not built (the drydock contract's list of discrepancies).
- Insight (defect): .pre-commit-config.yaml:15 vs gzkit/mx/alarms.py:35 on when alarm hooks skip.
- Insight (defect) gz-adr-audit:code-inside-audit is an input for the order that retires the ADR audit.
- skill-surface-sync.md rule 6 and scorecard row 33c contradict the review-only-date ruling; diamond-2 work.
- #1332: unsound-assignment and unsound-return still growing while off.
- The MX hangar's advisory debt is past 990 hours.

## Verification Checklist

- git rev-list --left-right --count origin/main...HEAD: 0 0 after the sync.
- gh run list --branch main --limit 1: the CI run on the synced head passes check (ubuntu-latest) and check (windows-latest); full-strength-report stays red on #1262.
- gh issue view 1398 --json state,stateReason: CLOSED NOT_PLANNED.
- grep -n 'construction, built legitimately' docs/rnd/conceptual-model.md: the ruling's entry.
- uv run gz handoff resume: names this handoff and step 1, the brief.

## Evidence / Artifacts

- `docs/rnd/conceptual-model.md` (two decisions: the construction ruling; W9 stands)
- `.gzkit/insights/agent-insights.jsonl` (five records of this session)
- `docs/rnd/conceptual-model/sources/prompt-audit-2026-11-25.md` (the audit map, unchanged)
- GHI #1398 (filed and withdrawn)
- Commits 4c9ed55c0, a1a0480ab, a38794482, 732ee640c, 8d7e634a0

## Settled Rulings

2622 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
