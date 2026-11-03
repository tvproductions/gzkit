---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-03T09:33:19Z'
agent: claude-code
session_id: 080c4789-7d04-49a6-8733-c040f48f9ee4
continues_from: .gzkit/handoffs/20261103T071527Z-rnd-repair-work-organization-review-next.md
---

## Current State Summary

The repair-work-organization R&D run is signed off and funded (operator: "yes, read in full - fund") after a section-by-section walk of docs/rnd/repair-work-organization/review.md that landed five rulings: the review's level table is canon, a remodel supersedes into a new REQ, return to service is the package's close apart from each order's Gate 5, design for service gets its own R&D run, and further research is a seventh disposition row (amended into docs/governance/rnd-discipline.md, gz-rnd 0.8.0 and its template). Rows 2, 3 and 4 then got their go and are done. Row 2 filed GHIs #1302 (RO-n/RP-n alias), #1303 (gz mx enter requires a return to service package), #1304 (--level retired), #1305 (five chore statements against their mechanism). Row 3 was advised (docs/rnd/repair-work-organization/row3-chore-levels.md) and admitted as advised, marked provisional: every chore declares check {level, provisional} and a periodDays, due at whichever comes first, and gz chores status shows the level and filters by --check (dfc6da93f). Row 4 landed one commit per surface: requirements model § 12 (62fa1a52a), safe-mode doctrine (4f43398d6), the contract with RP-n in live text (c415267da), Part 0 and four records (9a7f2486c), gz-mx, mx-mode.md and the template (236cbd5bd), the fifteen specifications and the brief (fdff604e9), the chore class system's check levels and RP-12's care rule (1da1fde51). Row 5 was put and not yet answered; the operator asked for this handoff instead.

## Important Context

The record docs/rnd/repair-work-organization.md governs; its disposition map now has seven rows, and rows 5 and 7 await the operator. Row 5 is a one-shot refactoring program the operator routes: every chore classified A to D and cut to its level (the levels admitted today are provisional, from the census through the rung); the checkpoint read through standard disconnect lists as RP-13 retires its group entry; RP-12 landing the order record, Gate 5 at the order and the repair requirement with supersedes; RP-14 migrating OBPI to the work order. Row 7 commissions the design-for-service R&D run (components built with their own tests, alarms, tripwires, access panels, MX procedures, safeguards and switches; each construction or repair tracking the subsystems it touches), opened only on the operator's word through gz-rnd; the standard disconnect lists wait on it. Canon now states three open points it does not answer: what revision still counts once a change makes a new REQ, how Gate 5's four outcomes apply to an order, and how RP-13 re-reads its level per standby level. Where the code lags the model, canon says so: gz mx enter still takes --level and asks for no package until #1303 and #1304. The schema change for check levels went direct, not through an OBPI, because safe mode suspends OBPI initiation and the operator's admission named it. Shift turnover: no tag hung, no finding awaiting buy-back, no package commenced; the tag-out log does not exist yet, so this session read gz obpi lock list, which shows the mx-session lock held by claude-code-080c4789 (this session) since the lease renewal at the operator's word; the relieving session takes it over by name or renews through gz-mx. CI for the session's code commit dfc6da93f was not read after push.

## Decisions Made

- [operator-ruled] Renew the MX lease and review the run with the operator before funding (verbatim: "renew mx lease, review docs/rnd/repair-work-organization/review.md with me here prior to funding decision.").
- [operator-ruled] The review's level table is the canon form of the model, its epic row reading none (new) (verbatim: "yes, it stands; use "none (new)" the table needs to kept and associated as canon - it captures the design very well.").
- [operator-ruled] A remodel supersedes a REQ rather than changing it (verbatim: "we don't change a req with a model as much as we supersede it - we remodel to refocus, refurbish, and redescribe. we transcend the prior req in the remodel. this precerves the value of prior work that was realized in the prior req").
- [operator-ruled] A remodel revises forward into a new REQ carrying supersedes (verbatim: "yes, A and it is cleaner and addresses the discussion of revision - we revise forward into a new req.").
- [operator-ruled] Return to service is a separate operator act at the return to service package's close, apart from each order's Gate 5 (verbatim: "Option A").
- [operator-ruled] Design for service gets its own R&D run (verbatim: "B, its own R&D run - we are building an integrated system and the requirements of integration are part of the spec that constrains design and integration.").
- [operator-ruled] Further research is a seventh disposition row of every R&D run (verbatim: "A, add row 7 further research").
- [operator-ruled] The run is funded (verbatim: "yes, read in full - fund").
- [operator-ruled] Row 2 is given its go (verbatim: "yes, go for row 2").
- [operator-ruled] Row 3 is given its go and admitted as advised (verbatim: "row 3 is a go"; "A, admit as advised, marked provisional").
- [operator-ruled] Row 4 is given its go (verbatim: "row 4 is go").
- [operator-ruled] An outcome's validated is derived from its REQs and their orders' Gate 5 (verbatim: "c - it is possible that a release package includes some completed work orders from a work package without completing the whole package, this is the decoupling we were working towards.").
- [operator-ruled] RP-n replaces RO-n in the contract's live text only, dated records kept as written (verbatim: "A").
- [agent-chose] Filed row 2's five census disagreements as one GHI (#1305) naming the doctrine-declared-without-mechanism family, since they share one class of failure.
- [agent-chose] Kept every interval the operator had already set and added the level default (A 14, B 30, C 90, D 180 days) only where a chore had none.
- [agent-chose] Wrote canon's unanswered consequences as open rather than drafting answers to them.

## Immediate Next Steps

1. Put row 5 of docs/rnd/repair-work-organization.md to the operator for its go; the operator selects the program's route.
2. Put row 7 to the operator: whether to open the design-for-service R&D run now through gz-rnd.
3. Resume the RP-12 specification at docs/governance/harbor-ro12-contractor-kit.md on the run's ground: re-put open point 2 in its terms, keeping ruling 1.
4. Carry #1296's three acceptance cases into that specification, then close #1296 as superseded against it.

## Pending Work / Open Loops

Row 5 and row 7 await the operator. GHIs #1302, #1303, #1304 and #1305 are filed and open; #1303 carries the operator's open question whether a patch release is mandatory at gz mx exit. Canon's three open points (revision, Gate 5 outcomes on an order, RP-13's standby levels) await rulings. Every chore's check level is provisional until row 5's classification program. #1296 stays open until the RP-12 specification carries it; #1185 and #1200 stay open as before. MX advisory debt keeps aging until gz mx exit; thirty-two chores read overdue by date.

## Verification Checklist

Run git rev-list --left-right --count origin/main...HEAD and expect 0 and 0. Run gh run list --branch main --limit 3 and read the run for dfc6da93f and later. Run uv run gz obpi lock list and expect the mx-session lock held by claude-code-080c4789. Run uv run gz chores status --check B and expect 21 chores with provisional levels. Read docs/rnd/repair-work-organization.md § Disposition map and expect seven rows, row 4 landed with its commits and row 5 commissioned without a go.

## Evidence / Artifacts

`docs/rnd/repair-work-organization.md`
`docs/rnd/repair-work-organization/review.md`
`docs/rnd/repair-work-organization/row3-chore-levels.md`
`docs/governance/rnd-discipline.md`
`docs/governance/ieee/requirements-model.md`
`docs/governance/safe-mode-doctrine.md`
`docs/governance/harbor-pilotage-candidate-2026-10-15.md`
`docs/governance/chore-class-system.md`
`docs/governance/harbor-ro12-contractor-kit.md`
`.gzkit/chores/registry.json`
`src/gzkit/commands/chores_staleness.py`
`tests/commands/test_chores_check_level.py`
`.gzkit/skills/gz-mx/SKILL.md`
`.gzkit/rules/mx-mode.md`
`.gzkit/skills/gz-rnd/SKILL.md`

## Settled Rulings

1969 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
