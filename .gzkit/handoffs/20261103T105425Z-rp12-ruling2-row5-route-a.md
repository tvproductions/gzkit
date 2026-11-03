---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-03T10:54:25Z'
agent: claude-code
session_id: ca285de3-287c-4138-ae08-838643d6f22e
continues_from: .gzkit/handoffs/20261103T093319Z-rnd-funded-rows-2-4-landed-row5-next.md
---

## Current State Summary

Resumed the handoff of 09:33Z and worked its four advised steps with the operator, one question each. Row 5 of docs/rnd/repair-work-organization.md got its go on route A: RP-12 first, then RP-14, then the chore classification and RP-13 (b77158efa; the operator's word booked with gz handoff decide). Row 7, the design-for-service R&D run, is held until RP-12 lands and opens ahead of RP-13 (3e6a87462). RP-12 open point 2 is ruled as ruling 2, two pipelines on one runtime, with the repair pipeline's stages written into docs/governance/harbor-ro12-contractor-kit.md (682a6ae2a). GHI #1296 was ruled closed as superseded by that specification, which already carried its three acceptance cases as refusal 9; the specification records the ruling (e011afede), but the gh close was refused by the harness permission check, so #1296 is still OPEN and awaits the operator's own close.

## Important Context

Ruling 2 rests on RO-14's ruling 4 in docs/governance/harbor-ro14-obpi-forward-migration.md: one runtime, kind selecting the procedure; dispatch, the bound, block and unblock, acceptance and locks shared; the boundary between procedures tested. Construction and repair share only the runtime plus the order record and Gate 5 at the order; the regime is the mode's, never the column's; construction's pipeline is RP-14's to migrate. The agent first drafted open point 2 as runtime shapes without reading ruling 4, re-offering its declined option C; the operator's question caught it and an improvement insight is recorded. Shift turnover: no tag hung, no finding awaiting buy-back, no package commenced; the tag-out log does not exist yet, so this session read gz obpi lock list, which shows the mx-session lock held by claude-code-080c4789, the previous session; this session did not take it over by name, so the relieving session takes it over or renews through gz-mx. CI for e011afede was in progress at writing; the earlier docs runs were cancelled by newer pushes, and dfc6da93f, the one code commit, passed.

## Decisions Made

- [operator-ruled] Row 5 is given its go on route A, RP-12 first, then RP-14, then the chore classification and RP-13 (verbatim: "A").
- [operator-ruled] Row 7's design-for-service run is held until RP-12 lands, opening ahead of RP-13 (verbatim: "A").
- [operator-ruled] Construction and repair are two pipelines on one runtime (verbatim: "yes, two pipelines on one runtime").
- [operator-ruled] GHI #1296 closes as superseded by the RP-12 specification (verbatim: "A").
- [agent-chose] Recorded each ruling in its canon surface as one commit, and wrote the repair pipeline's stages into ruling 2 from the run's level table.

## Immediate Next Steps

1. Close GHI #1296 as superseded, by the operator's own gh issue close or after a permission rule allows it; the comment points to docs/governance/harbor-ro12-contractor-kit.md § The cwd-escape guard.
2. Take over the mx-session lock by name or renew it through gz-mx.
3. Put RP-12 open point 3, the tag-out log (its store, its fields, hanging, clearing and the not-available mark), to the operator in ruling 2's terms.

## Pending Work / Open Loops

GHI #1296 open until closed. RP-12 open points 3 to 12 await rulings, one at a time. Rows 5 and 7 are ruled; RP-14, the chore classification and RP-13 follow RP-12. GHIs #1302, #1303, #1304, #1305, #1185 and #1200 stay open as before. Canon's three open points (revision, Gate 5 outcomes on an order, RP-13's standby levels) await rulings. MX advisory debt keeps aging until gz mx exit.

## Verification Checklist

Run gh issue view 1296 --json state and expect CLOSED once the operator closes it. Run uv run gz obpi lock list and read who holds mx-session. Run git rev-list --left-right --count origin/main...HEAD and expect 0 and 0. Run gh run list --branch main --limit 3 and read the run for the newest commit. Read docs/governance/harbor-ro12-contractor-kit.md § Rulings and expect rulings 1 and 2, with open points starting at 3.

## Evidence / Artifacts

`docs/rnd/repair-work-organization.md`
`docs/governance/harbor-ro12-contractor-kit.md`
`docs/governance/harbor-ro14-obpi-forward-migration.md`
`.gzkit/insights/agent-insights.jsonl`

## Settled Rulings

1973 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
