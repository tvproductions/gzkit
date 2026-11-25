---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-25T07:37:49Z'
agent: claude-code
session_id: ceb51716-bec8-42f2-9f7d-7e2003bbec1e
continues_from: .gzkit/handoffs/20261124T051808Z-deps-ty-rules-landed-t21-open.md
---

## Current State Summary

This session (ceb51716) resumed from 20261124T051808Z-deps-ty-rules-landed-t21-open.md, walked the drydock taxonomy from T21 to T30, paused the walk at W51 on the operator's word, and opened the conceptual-model R&D run, which is in progress. 33 commits since the predecessor's anchor de922cc72, from e68bf2e61 to 75c4664b6, all on main.

Taxonomy walk (docs/governance/drydock-taxonomy.md): W44 (T21, control roles), W45 (T22, position against persona), W46 (T23, construction and work), W47 (T25, who opens the hangar and the floor), W48 (T26, the handback), W49 (T27, the briefing), W50 (T28, the passage log) and W51 (T30, page names and RP-0's page) are ruled; T24 and T29 are marked settled by canon. W51 pauses the walk: T30's sub-ids, T37, W9's cardinality, a FIX's source, the GHI's kind and the construction reading of RP-12's rulings went to the R&D, and W44 to W50 are open to its review.

Conceptual-model R&D (docs/rnd/conceptual-model.md), opened 2026-11-25T00:36Z, diamond 1, not closed. Ruled so far: a discrepancy combines 14 CFR 43.11(b)/91.405 with AC 00-71 3.1 and is measured against declared intent of record; the GHI is the discrepancy's record, one each; a GHI's axes fall in three groups (what it is, where it stands, how it is ended), one name and one home each; class is behavior, process or life-cycle data in one class label; the lifecycle state is derived, never stored; how it surfaced is one of six in one found label; no fixed severity axis, MX reading the hold on return to service; readiness stays triage's per-run reading (settled by ghi-batch-closure Q5); no stored route; per-issue native GitHub features first, class and found staying labels; the secondary labels retire and security sensitivity is read from the diff. The disposition map is empty; the run has not reached review or sign-off.

The MX lease ran out at 1512 of 1440 minutes and was renewed on the operator's word; mx-session is active.

## Important Context

Safe mode is still open under docs/governance/harbor-pilotage-candidate-2026-10-15.md: most guards advisory, slow alarms off, lint and fast static checks, gate5_invariants, the ledger through gz verbs and operator PII still binding.

Method in this run, on the operator's words: favor the operator's input over the agent's framings ("one thing that would help us is when yu favor my input over vibes or multiple choice vibings", then "i didn't say exclusive, i said favor"), and options are welcome ("do not be afraid to offer me options"). Test every proposed field by what reads it before putting it: the operator's question "why are these two dimensions needed, how will they help mx work?" removed a severity axis with no reader. Read both sides of a mapping in full before putting it; twice this session a recommendation missed canon (the closed trailer set; RepairReq being superseded by W6's FIX) and the operator caught it.

The R&D is not the DDD-discipline run: "you found the ddd run and it is related, but we were untangling something different". That run, commissioned 2026-09-27 and ruled pre-1.0, is still unopened and recorded as a defect insight ("leaving that rnd unstarted is not good").

The thirteen conflations the walk surfaced are listed in the R&D record as a sampled hypothesis. The knot being worked is the GHI and what a discrepancy is (operator, verbatim).

Shift turnover, reviewed 2026-11-25: gz wp tag show --all reads "No tag has been issued."; gz wp runs reads "No work package is in flight."; gz obpi lock list shows mx-session as the only lock, renewed; the buy-back record is not built, so no finding awaits buy-back by record.

## Decisions Made

- [operator-ruled] Resume from the predecessor handoff (verbatim: "resume from h/o").
- [operator-ruled] W44, T21: alarm and tripwire keep RP-10 senses; the census role set is the MEL role field with its colliding names renamed interlock and annunciator (verbatim: "A: RP-10 senses (Recommended)").
- [operator-ruled] W45, T22: a position is obligation, authority and responsibility, a persona is disposition (verbatim: "yes on obligation/authority/responsibility (role) vs. disposition"); the crosswalk binds them and the dispatch record names both (verbatim: "A: Crosswalk + record"); one reviewer position with spec and quality sub-roles (verbatim: "A: One reviewer, 2 subs"); the craftsman is a position (verbatim: "A: Craftsman = position").
- [operator-ruled] W46, T23: the side is construction and its package the work package, store kind delivery renamed work (verbatim: "A: Construction / work").
- [operator-ruled] W47, T25: entry, exit and lease renewal on the operator's word, the agent acting through the gz-mx skill (verbatim: "A: Operator rules, agent acts"); the floor and what safe mode never suspends named apart (verbatim: "A: Floor + never-suspended").
- [operator-ruled] W48, T26: gz mx exit's re-run, then the handback, then the flag closes on the return-to-service words (verbatim: "A: Re-run, handback, close"); the subagent's report is the dispatch report (verbatim: "A: \"Dispatch report\"").
- [operator-ruled] W49, T27: the briefing gates no work, the record is validated (verbatim: "A: Different acts").
- [operator-ruled] W50, T28: the passage log closes as a dated record, the maintenance record succeeds it, no backfill (verbatim: "A: Close, no backfill").
- [operator-ruled] W51, T30: pages renamed RP-nnnn-<slug> with harbor allowed in the slug (verbatim: "A. and harbor can be used in thed slug if that helps them stand out"), behind a path-alias map (verbatim: "A: Alias map, then rename"); RP-0 gets its own page (verbatim: "A: Carve its own page"); the walk pauses for an R&D (verbatim: "record the T30 rulings first, then pause for the R&D (this is classic LLM drift: a vibe coded variant of whimsy and copycat convenience)").
- [operator-ruled] Renew the MX lease (verbatim: "reopen mx").
- [operator-ruled] R&D: a discrepancy combines 14 CFR 43.11(b), 91.405 and AC 00-71 3.1 (verbatim: "do not be afraid to offer me options. it is a combination of both of these: 14 CFR § 43.11(b), § 91.405) and AC 00-71 § 3.1"); measured against declared intent of record (verbatim: "A: Declared intent of record").
- [operator-ruled] R&D: the GHI is the discrepancy's record (verbatim: "A: GHI is its record"); three groups of axes (verbatim: "A: Three groups, one home each"); class is behavior, process or life-cycle data (verbatim: "A: Behavior/process/data") in one namespaced label (verbatim: "A: One namespaced label"); lifecycle derived (verbatim: "A: Derived, not stored"); surfacing route six values in one label (verbatim: "A: Six values, one label").
- [operator-ruled] R&D: no fixed severity axis, MX reading the hold on return to service (verbatim: "yes, record that and move to readiness"); no stored route (verbatim: "C: No stored route"); per-issue native GitHub features first (verbatim: "yes, A — record it and move on"); the secondary labels retire (verbatim: "A: Retire all three") and sensitivity is read from the diff (verbatim: "A: Read it from the diff").
- [agent-chose] Recorded readiness as settled by ghi-batch-closure Q5 rather than putting it, since canon rules it.
- [agent-chose] Recorded two stale subagent worktrees under .claude/worktrees as a defect insight rather than removing them; removal waits on the operator.

## Immediate Next Steps

1. Resume the conceptual-model R&D (docs/rnd/conceptual-model.md): recompute the frontier from the subject, the GHI and what a discrepancy is. Next item: family, the last axis of the what-it-is group, tested by what reads it.
2. Then the construction question: RP-12's numbered rulings read as requirements; whether its kit obligations are construction (catalog REQs at civil rule) or FIXes, and what a FIX answers now that one discrepancy is one GHI.
3. Then T37 and the sub-ids, and the review of W44 to W50 against the separated model; then fill the seven-row disposition map, write docs/rnd/conceptual-model/review.md and put sign-off.
4. Ask the operator whether to open the DDD-discipline R&D run, commissioned 2026-09-27 and recorded as an unopened defect this session.
5. Ask the operator whether to remove the two stale subagent worktrees under .claude/worktrees (one holds 214 uncommitted files).

## Pending Work / Open Loops

The taxonomy walk is paused at W51; T31 to T36 and T39 stay unruled, and the walk resumes only after the R&D rules on the paused items. Step 4 of the predecessor (the execution plan for T10's route and the documentation R&D through gz-rnd, W15) waits on the walk. Step 5 of the predecessor (whether the false settled marks in handoff 20261122T051329Z are corrected or kept) was not put this session.

Diamond-2 consequences already recorded in the R&D, executed by nothing: the gh-cli rule's allowed list widened to the per-issue native verbs; ghi-author, ghi-close and ghi-triage carrying the ruled fields; the DSC record and RP-12 rulings 9, 172 and 178 to 181 meeting one-GHI-per-discrepancy; Defect-fix routing's OBPI arm having no GHI destination; the requirements model section 12 still stating the design W6 reversed; the patch release qualifier moving off the runtime label; a diff-read security sensitivity on direct fixes.

Defect insights recorded this session: the unopened DDD-discipline run; the two stale subagent worktrees; and two improvement insights from operator corrections (easy options over conflated concepts; favor, not exclusive). Carried defects from the predecessor still stand: TestGhIssueCreatedAt hexagon-test findings; OBPI-0.39.0-01 and -02 briefs omitting sensitivity; 1049 bare PLC0415 suppressions.

## Verification Checklist

- uv run gz handoff resume, then read docs/rnd/conceptual-model.md whole; its last decision is the secondary labels' retirement.
- git rev-list --left-right --count origin/main...HEAD reads 0 0 after the sync.
- uv run gz obpi lock list shows mx-session as the only lock, inside its 1440-minute lease (renewed 2026-11-25).
- uv run gz wp tag show --all and uv run gz wp runs for the shift-turnover review.
- grep -n "W51" docs/governance/drydock-taxonomy.md shows the walk's pause.

## Evidence / Artifacts

- `docs/rnd/conceptual-model.md` (the R&D record, sources and decisions)
- `docs/governance/drydock-taxonomy.md` (section 8 rows T21 to T30, section 9 rulings W44 to W51)
- `docs/rnd/design-amendment.md` (Q8, the commissioned DDD-discipline run)
- `.gzkit/insights/agent-insights.jsonl` (this session's improvement and defect records)
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md` (the safe-mode contract)
- Commits e68bf2e61 to 75c4664b6 on main.

## Settled Rulings

2533 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
