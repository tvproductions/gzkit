---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-04T09:28:49Z'
agent: claude-code
session_id: ca285de3-287c-4138-ae08-838643d6f22e
continues_from: .gzkit/handoffs/20261103T105425Z-rp12-ruling2-row5-route-a.md
---

## Current State Summary

The RP-12 specification, docs/governance/harbor-ro12-contractor-kit.md, is specified and accepted by the operator 2026-11-04 (verbatim: "accept"). Across 2026-11-03 and 2026-11-04 every agent-drafted open point (3 to 12) was ruled one at a time as rulings 3 to 28, then the operator reviewed the page and five more rulings (29 to 33) came out of it. GHI #1296 is closed as superseded. The mx-session lease was renewed. The contract's RP-12 row now links the specification, and the requirements model's two canon open points that O2 needs (Gate 5's four outcomes at an order; what revision counts) are answered there by rulings 30 and 31. Nothing is built: O1 is the next work.

## Important Context

Safe mode is open under the pilotage contract; every act is one commit with Task: TASK-rnd-repair-work-organization, and editing the contract books mx_contract_amended, whose ledger row is left unstaged after the commit and needs its own chore(ledger) commit. RP-12 is a repair package (repair strata ruling); its nine repair orders are ruling 25, O1 the dispatch record with a Bash updatedInput probe first, then O2 the order record through O9 the carry of the contract's open lines. Out of service is one state (2026-11-03): hangar and drydock are synonyms, and .gzkit/rules/mode-contract.md still names three conditions, which is RP-13's canon open point, not RP-12's. The witness floor is fifteen rows on the page; the contract's row keeps its nine as the minimum. Ruling 3: tags and the lease are held by the MX session 57346836-b4d2-414f-b5b1-04898f13456f, never the harness session, so the mx-session lock's agent field (claude-code-ca285de3) goes stale after a /clear by design; gz mx renew still writes the harness id until O3. Shift turnover: no tag hung, no finding awaiting buy-back, no package commenced; the tag-out log does not exist yet, read gz obpi lock list and the contract's § List of discrepancies in its place. Three insights were recorded this session: the open point 2 framing error, the wrong lease renewal advice, and ruling 28 first written on the retired three standby levels.

## Decisions Made

- [operator-ruled] Renew the mx-session lease (verbatim: "A").
- [operator-ruled] The holder of tags and the lease is the MX session (verbatim: "mx session makes sense").
- [operator-ruled] RP-12 rulings 4 to 10 on the tag-out log, its line item, its acts, the not-available mark, the maintenance record, the list of discrepancies and the carry of open lines (verbatim: "A", each).
- [operator-ruled] RP-12 ruling 11, a stop holds what its trigger reaches (verbatim: "a").
- [operator-ruled] RP-12 rulings 12 to 22 on stops as the extended block, typed resolutions, the (I) points, the (I) mark, buy-back, the hook stamp, refusal 8 at restoration, the composed turnover, the crosswalk as data, the term witness and gz-repair-pipeline (verbatim: "A", each).
- [operator-ruled] RP-12 ruling 23, the surveillant has its own persona file, against the agent's recommendation of B (verbatim: "A").
- [operator-ruled] RP-12 rulings 24 to 28 on the surveillance dispatch gate, nine repair orders, the hand-kept log ending at O3, each order's dock trial and the kit's mode contract (verbatim: "A", each).
- [operator-ruled] RP-12 ruling 29, the witness floor grows by four rows on the page only (verbatim: "b").
- [operator-ruled] RP-12 rulings 30 to 33 on Gate 5's four outcomes at the order, what revision counts, the operator's acts gated on verbatim words, and the transfer of custody composed (verbatim: "A", each).
- [operator-ruled] The RP-12 specification is accepted (verbatim: "accept").
- [agent-chose] Corrected ruling 28 and § Mode Contract to on the line and out of service after finding they used the retired standby levels, recording a defect insight; brought the page's front text to its rulings where canon already ruled (RP-n, strata terms, C10 and C11 amendments, the 2026-11-04 re-measure).
- [agent-chose] Amended the RP-13 specification, the requirements model, gz-session-handoff (7.8.1) and gz-mx (1.10.1) where a ruling changed what they say.

## Immediate Next Steps

1. Put to the operator whether to begin RP-12's O1 (the dispatch record, the hook stamp and the verb refusal), starting with the probe of PreToolUse updatedInput on Bash, as the bootstrap ruling has it: the operator and a working session, each task one commit with an independent reviewer subagent.
2. Before O1's first disconnection, keep it as an isolation line on the contract's § List of discrepancies (ruling 26).
3. Read CI for the session's last pushes, which were docs and ledger only.

## Pending Work / Open Loops

GHIs #1302, #1303, #1304, #1305, #1185 and #1200 stay open. Canon's remaining open point is RP-13's re-reading of its standby levels under the one out-of-service state, with .gzkit/rules/mode-contract.md naming three conditions until then. The § Mode Contract table's self-test column is the agent's draft and was not ruled line by line. The pipeline-side GHIs from the record's crosswalk await their go. MX advisory debt keeps aging until gz mx exit; thirty-two chores read overdue.

## Verification Checklist

Run git rev-list --left-right --count origin/main...HEAD and expect 0 and 0. Read docs/governance/harbor-ro12-contractor-kit.md and expect status specified, rulings 1 to 33, a fifteen-row witness floor and an empty open-points list. Run gh issue view 1296 and expect CLOSED. Run uv run gz obpi lock list and expect the mx-session lock. Run gh run list --branch main --limit 3.

## Evidence / Artifacts

`docs/governance/harbor-ro12-contractor-kit.md`
`docs/governance/harbor-ro13-mode-contract.md`
`docs/governance/ieee/requirements-model.md`
`docs/governance/harbor-pilotage-candidate-2026-10-15.md`
`.gzkit/skills/gz-session-handoff/SKILL.md`
`.gzkit/skills/gz-mx/SKILL.md`
`.gzkit/insights/agent-insights.jsonl`

## Settled Rulings

1983 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
