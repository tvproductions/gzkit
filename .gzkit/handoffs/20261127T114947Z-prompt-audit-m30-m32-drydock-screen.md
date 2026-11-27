---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-27T11:49:47Z'
agent: claude-code
session_id: 59945d19-546e-4429-9437-3452d196f06f
continues_from: .gzkit/handoffs/20261127T092454Z-construction-ruled-w9-stands-audit-walk-next.md
---

## Current State Summary

Resumed on the operator's 'resume m30' (booked through gz handoff decide). Prompt-audit walk: M30 filed, repaired and closed as GHI #1399 (content pipeline teaches only the root AgentContract consumer; land manpage captures re-taken on the land tests' fixture; a routing witness test added); reviewed CONFIRMED on the third pass. M31 closed as #1400 (Rule of Three marked legacy in gz-adr-promote, gz-plan and adr-lifecycle.md), reviewed CONFIRMED on the second pass; gz-adr-promote added to CO-1 as held ruling H7. M32 went wrong: the agent proposed a foundation-kind arm for the receipt policy; the operator ruled foundation-kind work no longer exists and adopters may not use it; #1401 withdrawn, its three-surface commit reverted (880325584). #1402 then retired the foundation kind in code, tests, templates, skills, docs and the AGENTS.md corpus (0da00cf36, 0b45fad78, attested 'this change is approved') before the operator ruled it all drydock work: one ADR kind, 'feature' a misnomer to deprecate. Held ruling H8 recorded on CO-1 (3b4c653b8); #1402 closed superseded by CO-1/CO-2, its commits kept. Last action: this handoff, then git-sync.

## Important Context

Safe mode still open (docs/governance/harbor-pilotage-candidate-2026-10-15.md); every act is one commit with a Task: trailer. Shift turnover, reviewed 2026-11-27: gz wp tag show --all: no tag issued; gz wp runs: no work package in flight; gz obpi lock list: mx-session ACTIVE (elapsed 195m of 1440m). The buy-back record is not built. The three-level brief is given by hand at resume; its specification is docs/design/briefs/SPEC-session-handoff-picture.md and its open line is the drydock contract's list of discrepancies (harbor-pilotage-candidate-2026-10-15.md:1645). Method learned this session (insight prompt-audit:screen-against-drydock): before filing or repairing any walk row that touches ADR kinds, semver, checklists, decomposition or OBPI ceremony, screen it against the classic-ADR change orders CO-1 to CO-4 (docs/governance/harbor-classic-adr-change-order.md) and the RP orders; stop at the screen when an order retires the subject and put the routing to the operator. Read lifecycle state, never counts, before calling work open. Corpus changes to AGENTS.md go through gz content remember / retire / land with a retention map and the operator's words, as in c3a63c36f and 0b45fad78.

## Decisions Made

- [operator-ruled] Resume the walk at M30 (verbatim: "resume m30 (is the tactical|operational|strategic report vibe coded or included in the skill?)").
- [operator-ruled] M30 takes the code over the audit map: AgentContract routes to root only, and S38 and M30 are corrected (verbatim: "yes").
- [operator-ruled] M30 is repaired directly under its GHI with OBPI-0.35.0-09 as owner of record, none of its REQs moving (verbatim: "A").
- [operator-ruled] The land manpage examples are re-captured on the land tests' fixture with a sentence that AGENTS.md routes to root alone (verbatim: "A").
- [operator-ruled] gz-adr-promote is added to CO-1's skill list, held ruling H7 (verbatim: "A").
- [operator-ruled] There is no foundation-kind work (verbatim: "there is no longer \"foundation-kind\" work. what receipts are we talking about?").
- [operator-ruled] Adopters may not do foundation work (verbatim: "adopters may NOT do foundation work.").
- [operator-ruled] Foundation ADRs must not persist and adopters must not use them (verbatim: "we WERE using foundation ADRs but have stopped doing so. They must not persist and we must not permit adopters to use them.").
- [operator-ruled] 'Must not persist' covers the kind, not the frozen records (verbatim: "A").
- [operator-ruled] #1402 relates to OBPI-0.34.0-02 as owner of record, repaired directly (verbatim: "A").
- [operator-ruled] The AGENTS.md Gate Covenant change is attested (verbatim: "this change is approved").
- [operator-ruled] ADR kinds are drydock work: one kind of ADR, feature deprecated (verbatim: "this whole thing is a waste, these all refer to work that the drydock supersedes - there is only one kind of ADR and it is the actual Architecture Decision Record. The \"feature\" kind is a misnomer and should be deprecated. this is all slated dry dock work.").
- [operator-ruled] Keep #1402's commits, close it superseded by CO-1/CO-2, record H8 (verbatim: "A").
- [operator-ruled] Hand off and git-sync before screening M33 to M51 (verbatim: "b").
- [agent-chose] Recorded the lane-keyed default_dimension_scores (scoring.py:73) as an insight for CO-1 rather than patching legacy scorecard code.
- [agent-chose] Kept WHY_FOUNDATION_TIER_SECTION and restored the invariance-test pointer in three skills so attested REQ-0.0.35-02-01 stays true at its surface.

## Immediate Next Steps

1. Give the operator the strategic, operational and tactical brief at resume, short, vital facts first.
2. Screen prompt-audit rows M33 to M51 (docs/rnd/conceptual-model/sources/prompt-audit-2026-11-25.md, Revised mechanism map) against CO-1 to CO-4 in docs/governance/harbor-classic-adr-change-order.md and the RP orders; bring the operator the list of rows that survive as real defects and the rows a drydock order already carries, before filing any.
3. On the operator's ruling, walk the surviving rows: file through ghi-author, repair, reviewer subagent confirms, close through ghi-close.
4. Then the R&D's T37 and sub-ids, W44 to W50 against the separated model, the open frontier from the construction ruling, the disposition map, review.md and sign-off.

## Pending Work / Open Loops

- Prompt audit M33 to M51 unscreened; #1357 (M1) still open.
- #1388 awaits the operator's ruling on the gz chores run exit code.
- RP-6 CO-1 now carries H7 (gz-adr-promote) and H8 (one ADR kind, feature deprecated, adopters included); AGENTS.md's Gate Covenant entry still names feature as a kind until CO-1 lands.
- Insight scoring:default_dimension_scores-lane-keyed: lane-keyed defaults in src/gzkit/core/scoring.py:73, an input for CO-1.
- The root rendition renders the re-captured Gate Covenant kind bullet at the section's end (append-only render order).
- The three-level brief is not built (drydock contract list of discrepancies).
- skill-surface-sync.md rule 6 and scorecard row 33c contradict the review-only last_reviewed ruling; diamond-2 work.
- #1332: unsound-assignment and unsound-return still growing while off.
- The MX hangar's advisory debt keeps aging; gz mx exit re-runs every guard at full strength.

## Verification Checklist

- git rev-list --left-right --count origin/main...HEAD: 0 0 after the sync.
- gh issue view 1399 / 1400 --json state,stateReason: CLOSED COMPLETED; 1401 and 1402: CLOSED NOT_PLANNED.
- grep -n 'H8. Ruled 2026-11-27' docs/governance/harbor-classic-adr-change-order.md: the ruling's entry.
- uv run gz validate --invariant-coherence --rendition-freshness: passes.
- uv run -m unittest tests.commands.test_foundation_kind_closed tests.commands.test_content_help_routes: OK.
- uv run gz handoff resume: names this handoff and step 1, the brief.

## Evidence / Artifacts

- `docs/governance/harbor-classic-adr-change-order.md` (H7, H8)
- `docs/rnd/conceptual-model/sources/prompt-audit-2026-11-25.md` (S38, M24, M30 corrected)
- `tests/commands/test_content_help_routes.py`
- `tests/commands/test_foundation_kind_closed.py`
- `.gzkit/chores/instructions-files-diet/proofs/retention-map-2026-11-27-foundation-closure.json`
- `.gzkit/insights/agent-insights.jsonl` (four records of this session)
- GHIs #1399, #1400, #1401, #1402
- Commits 778393bc3, 9490f0485, a42df9c42, ec198b9c2, e6a1a4b02, 92a80440c, a6144d437, db8a144ba, 3bc94188c, 01da22151, 880325584, 0da00cf36, 0b45fad78, 3b4c653b8

## Settled Rulings

2636 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
