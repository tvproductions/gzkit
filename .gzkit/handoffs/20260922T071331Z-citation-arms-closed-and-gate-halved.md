---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-22T07:13:31Z'
agent: claude-code
session_id: 5da590f6-38fc-46ed-b180-087497abdc20
continues_from:
- .gzkit/handoffs/20260921T111028Z-gate-cost-instrumented-and-four-fences-landed.md
- .gzkit/handoffs/20260922T063506Z-session-exit-bookmark.md
---

## Current State Summary

HEAD is b100117a4, clean except one untracked PDF, and origin/main is level (0 0). The gate is green at real exit 0 and the whole sweep now runs in 70.87s wall, 62 steps, sum 177.45s -- down from the 167.63s wall the last authored handoff recorded on 2026-09-21.

THIS DOCUMENT IS A RECONSTRUCTION, NOT A MEMORY. The session that did the work (db0f0fa4) ended on a /clear and left only the mechanical exit bookmark at `.gzkit/handoffs/20260922T063506Z-session-exit-bookmark.md`, which enumerates nothing. Everything below was rebuilt in this session from Layer-2 and GitHub evidence -- five commits, three GHI bodies with their close comments, the insight tail, and live `gz` state. Claims sourced that way are marked where it matters; what this document cannot recover is what the working session considered and rejected without writing down.

What landed since the last authored handoff: three GHIs closed. #1078 gave ADR citations a verdict, discharging the deferral #1076 left documented in code. #1079 found that both ledger arms were unreachable -- they looked citations up as exact artifact-graph keys while real handoffs cite prefixes -- and made them answer the prose as written. #1080 opened the step #1077 had measured and refused to touch, and cut `Validate default scopes` from 65.29s to 2.80s by caching three derived streams over an already-cached row list. Steps 1 and 2 of the previous handoff's advised list are therefore discharged; steps 3, 4 and 5 are carried below unchanged in substance.

One decision was taken in this session rather than reconstructed: the two design-reference PDFs under `docs/design/requirements/` were surfaced with their routing facts and ruled the same session -- both are intended repository-tracked references, both ship in the sync that commits this document. That closes the only open loop this session opened.

## Important Context

READ THE PROVENANCE BEFORE YOU TRUST A SENTENCE. Nothing here comes from the working session's own account of itself. The reconstruction inputs were: `git log 5552696af..HEAD`, the bodies and final comments of GHI #1078, #1079 and #1080, the last six rows of `.gzkit/insights/agent-insights.jsonl`, and live reads of `gz status`, `gz obpi lock list`, `gz adr status`, `gz handoff resume` and `gz check`. Where this document states a number, it is either quoted from one of those or observed in this session; it is never carried from prose.

THE #1079 CLASS IS THE MOST TRANSFERABLE THING IN THE INTERVAL. #1076 shipped the OBPI citation arm, verified it against hand-written full-slug ids, and closed. The arm was correct and answered nothing: zero of the 867 OBPI citations in the real handoff corpus are exact graph ids, because the extractor takes the identifier as the AUTHOR typed it and the graph is keyed by full slug. The arm passed its tests, passed its close review, and was unreachable in production for a day. The generalization its close comment states: verify a resolver against the inputs its own upstream extractor emits, not against inputs you construct.

THE #1079 CEILING IS DELIBERATE AND SHOULD NOT BE READ AS SHORTFALL. After the fix, ADR citations answer 1651/1854 (89.1%) and OBPI 397/867 (45.8%). The 466 unanswered OBPI citations are ambiguous prefixes, refused on purpose: GHI #826 forbids resolving an id to a nearest sibling, and the hazard is live in this graph -- OBPI-0.35.0-08 extends to both -forbid-pytest and -remember-post-append-advisory. A future session that "improves" the hit rate by guessing is reversing a ruling.

#1080 INVERTED ITS OWN ISSUE'S PREMISE, AND THE INVERSION IS THE FINDING. The issue argued the risk was cache freshness on the full-ledger read. The close comment records that the file read was never the cost: reads were already cached and already invalidated on every mutation. The 20.35ms per call was netting over an already-parsed list -- 19.94ms in the live-event fold, 0.61ms in the rename fold -- times 2691 resolve calls from the frontmatter validator. So the change reads the file no more often than before and joins an invalidation discipline that already existed.

A GATE WITNESS WAS REPAIRED AT THE SURFACE RATHER THAN LOOSENED. A test in `tests/test_ontology_corpus.py` carries @covers REQ-0.32.0-02-04 and counts full-ledger read CALLS. Routing the rename map through that read added a second, cache-cheap, redundant call and turned it red. The recorded repair passes the caller's already-read stream into the fold; the test is untouched. This is the attested-REQ discipline working as written -- the witness was not spent on convenience.

CITATION RESOLUTION IS NOW OBSERVABLE, AND IT CHANGES WHAT `gz handoff resume` SHOWS. Verified live this session against the previous handoff: step 4's references render OBPI-0.35.0-08 unknown (ambiguous prefix, correctly refused) and ADR-0.35.0 live, where both read unknown before. A reader comparing today's resume output against a quoted older one should expect this difference and not treat it as drift.

## Decisions Made

- [operator-ruled] Commit both PDFs under `docs/design/requirements/` as intended repository-tracked design references, ruled 2026-09-22 against the routing facts in this session, choosing commit-both over ignoring-and-untracking them and over ignoring only the new one. The accidental coupling of the 3.8 MB PDF into GHI #1079's fix commit stands disclosed rather than remedied; the only remedy is a history rewrite policy forbids.
- [agent-chose] Authored this as an explicit reconstruction from Layer-2 and GitHub evidence, and said so in the first two sections, rather than writing a confident narrative of a session this agent did not witness.
- [agent-chose] Chained from `.gzkit/handoffs/20260921T111028Z-gate-cost-instrumented-and-four-fences-landed.md` rather than from the newer mechanical bookmark, so the 1022-entry ruling lineage carries; the bookmark is recorded as the second continues_from so the exit beat is not lost.
- [agent-chose] Seated the interval's three operator rulings through the late-ruling flag instead of writing them as this document's own operator-ruled entries, because this traversal did not receive them -- they arrived in session db0f0fa4, which wrote no handoff to book them.
- [agent-chose] Recorded those three rulings' substance with the GHI or insight as authority and did NOT manufacture quoted operator wording, since the verbatim words were not recoverable from any surface this session could read.
- [agent-chose] Re-authored this document after the PDF ruling landed rather than shipping the first draft, whose advised step 2 the ruling had already voided; a handoff whose step is dead before it is committed is the decay the citation machinery exists to prevent.
- [agent-chose] Ran the full gate on the tree as found rather than staging everything first, so an undecided 1.0 MB PDF was not staged to buy a recorded-verified flag; the pass is real and observed, and the gate itself printed that it was not recorded as verified.

## Immediate Next Steps

1. Author the feature ADR that gate instrumentation Arm 2 needs. The 2026-09-21 ruling to build Arm 2 as specified stands -- a duration field on QualityResult feeding `gz check --json`, plus duration and timestamp in the check-verified cache -- and the blocker is that no live parent ADR owns the subject. Recorded as a discovery insight under scope gzkit.check at 2026-09-21T11:59:35Z with its evidence: ADR-0.2.0-gate-verification is Validated and COMPLETED, the four Pending feature ADRs own other subjects, and Architectural Boundary 2 forbids a pool ADR on the runtime track. Route named in that insight: gz-design then gz-plan, after which Arm 2 becomes a Feature Checklist item with its own OBPI. Operator-only work.

2. Measure whether pool ADRs are absent from the artifact graph by design or by omission. 203 ADR citations still resolve UNKNOWN after #1079 [settled], most of them pool ADRs. This was named as an open uncertainty when #1079 [settled] was filed and its close comment records that it was not resolved by it. Measurement first, route second.

3. ADR-0.35.0 remains campaign TOPMOST with closeout BLOCKED. Verified live this session: lifecycle Pending, pre_closeout, Closeout Readiness BLOCKED, every enumerated blocker reading "ledger proof of completion is missing". Read the OBPI count from `uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` rather than from any figure in prose. OBPI-0.35.0-08 reads in_progress from a one-way pipeline_launched latch and its lock was released 2026-08-23. GHI #930 owns that finding and carries the mechanical evidence. Only the operator can move it.

4. Decide whether the gz-obpi-pipeline skill's Stage 4 extracts to a references directory. Carried unchanged from the previous handoff: 605 lines of a 1710-line body at its ceiling, mechanically available, the pattern already ships. The judgment recorded against it is that Stage 4 is the human-gate ceremony an agent would then fetch rather than read by default.

5. Decide whether the extractor's OBPI truncation pattern is a defect. It produces 4 citations of shape OBPI-0.51.0-0 that no author wrote; the segment-boundary rule from #1079 [settled] makes them refuse safely rather than resolve wrongly, so nothing is currently wrong -- but the pattern emitting ids that cannot exist is untested either way.

## Pending Work / Open Loops

DISCHARGED IN THE INTERVAL, VERIFIED CLOSED THIS SESSION. GHI #1078 [settled] (closed 2026-09-21T11:47:44Z), #1079 [settled] (closed 2026-09-22T00:49:21Z), #1080 [settled] (closed 2026-09-22T00:41:56Z). Each close comment carries a closure contract, mutation controls that failed then restored green, and a cause-to-test table. The previous handoff's advised steps 1 and 2 are discharged by these and should not be re-relayed as open.

OPEN, RULED, BLOCKED ON AN ARTIFACT THAT DOES NOT EXIST. Arm 2 of gate instrumentation. The operator ruled it should be built; it cannot be initiated because no live parent ADR owns quality-gate instrumentation. This is the only item in this document whose blocker is an absence rather than a decision.

OPEN, MEASURED, UNROUTED. The 203 remaining UNKNOWN ADR citations (pool ADRs, graph membership unmeasured). The 4 OBPI citation truncations of shape OBPI-0.51.0-0, produced by the extractor's own pattern rather than by any author -- the segment-boundary rule makes them refuse safely, but whether the pattern itself is defective is untested. Whether flag-scoped `gz check` steps carry the same repeated-resolve shape the default scopes did; the 16-scope table in #1080 [settled] says no other DEFAULT scope does.

RULED THIS SESSION, CLOSED AS AN OPEN LOOP. The two design-reference PDFs under `docs/design/requirements/`. Surfaced with routing facts, ruled the same session: both are intended repository-tracked references and both ship in this sync. The residue is disclosure, not a queue item -- the 3.8 MB PDF is coupled into GHI #1079 [settled]'s fix commit b100117a4, whose stated scope was two source files, and the only remedy is a history rewrite policy forbids. No custodian is needed because nothing remains to decide.

CARRIED, NOT MINE TO MOVE. ADR-0.35.0 and its six blocked OBPIs, owned by GHI #930. GHI #1028 remains open under the explicit three-pillars hold recorded in the campaign's 2026-09-19 amendment and read back by `gz status`; it is not a next action until the operator resumes it.

ACCEPTED AND DISCLOSED, STILL TRUE. Commit 84ea8e435 touches src/ and carries no Task or Ceremony trailer, permanently unrepairable because the only remedy is a history rewrite policy forbids. Its custodian is an insight under scope gzkit.commit-trailers, not this document.

STILL OPEN, UNTOUCHED. The doctrine-declared-without-mechanism family, and the open queue at 55 -- counted this session with the GitHub CLI, unchanged from the 2026-09-21 count despite three closures, so three arrived in the same interval.

## Verification Checklist

Every figure below was observed in THIS session on 2026-09-22 against HEAD b100117a4. They are dated observations of this tree, not thresholds. Re-run rather than quoting them forward.

`uv run gz check` -> All checks passed, 62 steps, 70.87s wall (sum 177.45s), real exit code 0 read from the process rather than through a pipe. Run twice; identical verdict both times. The gate printed "not recorded as verified: the tree has unstaged or untracked changes" -- correct and expected, because the untracked PDF was deliberately left unstaged. Two standing advisories fired and neither affects exit code: spec-test-code drift at 713 unlinked REQs, and one flag approaching deadline (ops.product_proof).

`git rev-list --left-right --count origin/main...HEAD` -> 0 0. `git status --short` at gate time -> one staged handoff bookmark and one untracked PDF, nothing else. The PDF was ruled for commit after the gate ran, so the tree this document is committed from carries it staged.

`uv run gz obpi lock list` -> No active locks. No lock claim in this document is possible and none is made.

`uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` -> Pending, heavy, pre_closeout, Closeout Readiness BLOCKED, with every enumerated blocker reading "ledger proof of completion is missing". Run the command for the live OBPI count; this document deliberately carries no transcription of it.

`uv run gz handoff resume` on the previous handoff -> Fresh, requires human verification False, 5 steps, 2 flagged CITES SETTLED (#1076 and #1077, both closed), lineage 19 ancestors with the walk hitting its depth bound.

GitHub CLI issue reads on 1076, 1077, 1078, 1079 and 1080 -> all CLOSED with the timestamps quoted above. Open-issue listing capped at 200 -> 55.

NOT VERIFIED IN THIS SESSION, AND MUST NOT BE RELAYED AS IF IT WERE. Every per-test count, mutation-control result and before/after timing attributed to #1078, #1079 and #1080 is QUOTED FROM THEIR CLOSE COMMENTS; this session re-ran none of them individually. The whole-gate numbers above are the exception -- those are this session's own observation. Whether pool ADRs belong in the artifact graph. Whether the extractor's OBPI truncation pattern is a defect. What session db0f0fa4 considered and rejected without recording.

## Evidence / Artifacts

Commits in the interval, HEAD b100117a4: b7d87e7a5 and db817eb58 (GHI #1078), 330aa24b9 (GHI #1080), b100117a4 (GHI #1079), plus sync chores 347a65458, 7a29f4138, cc5fc4073 and e12acc206.

Source changed in the interval: `src/gzkit/commands/reference_checker.py`, `src/gzkit/ledger.py`, and the four gz-session-handoff mirrors including `.gzkit/skills/gz-session-handoff/SKILL.md`.

Tests changed or added: `tests/commands/test_reference_checker.py` (34 tests at close), `tests/governance/test_ledger_derived_stream_cache.py` (9 tests, new). The gate witness repaired at the surface rather than loosened lives in `tests/test_ontology_corpus.py`.

Issues: GHI #1078, #1079 and #1080 filed and closed in the interval, each with a closure contract and cause-to-test table in its final comment. GHI #930 and #1028 remain open and are cited above.

Insight tail read this session: `.gzkit/insights/agent-insights.jsonl`, last six rows, scopes gzkit.handoff.rulings, gzkit.handoff, gzkit.skills.gz-obpi-pipeline, gzkit.check (two rows) and gzkit.commit-trailers. The final row is the Arm 2 blocker that next step 1 discharges.

Unrouted artifacts observed: `docs/design/requirements/CSE372Week10-IEEE.pdf`, committed in b100117a4, and a second untracked ISO/IEC/IEEE 12207 PDF beside it in `docs/design/requirements/`.

Ruling store: `.gzkit/handoffs/rulings.jsonl`, 1023 rows, 1022 booked rulings before this document. Ledger: `.gzkit/ledger.jsonl`.

Canon read this session: `docs/governance/build-to-1.0-campaign-2026-09-20.md` workflow fronts, through `gz status`.

Predecessors: `.gzkit/handoffs/20260921T111028Z-gate-cost-instrumented-and-four-fences-landed.md` (last authored, chained) and `.gzkit/handoffs/20260922T063506Z-session-exit-bookmark.md` (mechanical exit beat for session db0f0fa4, superseded by this document).

## Settled Rulings

1026 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
