---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-03T07:15:27Z'
agent: claude-code
session_id: bc424b0b-1972-483e-9aa0-de527a759d1e
continues_from:
- .gzkit/handoffs/20261102T082512Z-ro12-specification-next.md
- .gzkit/handoffs/20261102T082800Z-session-exit-bookmark.md
---

## Current State Summary

The R&D run repair-work-organization reached its close: the frontier is empty, all six disposition rows carry a decision, the challenge is restated, and the account for sign-off is written at docs/rnd/repair-work-organization/review.md, rewritten after the operator's corrections at the first walk-through, committed 5ee473c6c. Sign-off (kill or fund) has not been put. The RO-12 specification draft at docs/governance/harbor-ro12-contractor-kit.md holds one ruling (a position is told by its dispatch record) and is paused; its open point 2 was withdrawn when the operator questioned the work organization, which opened the run. The run's outcome changes RO-12's ground: under it RO-12 reads RP-12, the work order is the OBPI's successor, and Gate 5 sits at the order. The session-exit bookmark of 2026-11-02T08:28Z is folded here: it recorded only the exit beat.

## Important Context

The run's record is docs/rnd/repair-work-organization.md; its sources are under docs/rnd/repair-work-organization/sources/: the chore census, the letter-check research, and a verbatim extract of FAA Order 8900.1 Volume 20 from PDFs the operator placed. The placed PDFs, the 8900.1 contents .accdb, .zip and .xlsx stay local through that folder's .gitignore; the .xlsx was placed late and is unread; the Volume 16 PDF is unmanned aircraft and not relevant. Order 8900.1 Vol. 20 Ch. 8 Sec. 1 is the FAA text that names the four check levels, A and B line and C and D heavy; faa.gov refused automated retrieval, so the operator supplied the PDFs. The review is a view and holds no authority; the record governs. Nothing in the run is executed: rows 2 to 5 each need the operator's go on that row after sign-off. Shift turnover: no tag was hung and no package commenced; the tag-out log does not exist yet, so this session read gz obpi lock list, which shows the mx-session lock held by claude-code-e8f344c7 with its lease expired, booked and announced and not evicted (token-block Sub-Invariant 4); this session never held it. CI for 832e22a58 was in progress at session start and was not read again. The operator raised whether R&D should run at higher effort or a stronger model; the agent recommended Opus at high, Fable where purpose is at stake, and nothing was changed.

## Decisions Made

- [operator-ruled] RO-12 ruling 1: a position is told by its dispatch record (verbatim: "Dispatch record (Recommended)").
- [operator-ruled] The repair package sits at today's RO level, the repair order at the tranche, the task at the act (verbatim: "Package at RO level (Recommended)").
- [operator-ruled] Four levels on both sides, package, order and task beneath a why (verbatim: "yes, that's the structure").
- [operator-ruled] Out of service means the MX marker is open; gate work stays on the line under GHI direct repair (verbatim: "yes, out of service means the marker is open is also very strong").
- [operator-ruled] Hangar and drydock are synonyms, gz mx keeps its name, and out of service has one state (verbatim: "These are synonyms for sure, so option A").
- [operator-ruled] The alarm test decides between the line and out of service (verbatim: "the alarm test decides, and I like it").
- [operator-ruled] The top repair row is the return to service package; out of service is a flag (verbatim: "it should be called a return to service package").
- [operator-ruled] gzkit adopts four check levels by what the work needs (verbatim: "yes, adopt the four levels - use the rich detail we found").
- [operator-ruled] Each level means more disassembly and disconnection, by a standard disconnect list, the manual (verbatim: "each level means more disassembly and disconnection").
- [operator-ruled] A finding above a chore's level leaves the run as a problem report (verbatim: "A").
- [operator-ruled] One requirement concept, specialized by inheritance into catalog and repair requirements (verbatim: "sounds an opportunity for classic inheritance - they likely have some specialization").
- [operator-ruled] An order is a real record with its own id, freeze and inspection (verbatim: "a").
- [operator-ruled] RP-n replaces RO-n in live text, RO-n kept as an alias for history (verbatim: "A").
- [operator-ruled] Every opening of the marker has a return to service package (verbatim: "a").
- [operator-ruled] The unit of action is the task; card is dropped (verbatim: "1. no 2. let's discuss 3. ask it").
- [operator-ruled] A restoring repair or a refactor advances the patch; a remodel rides a minor release (verbatim: "we'd do a minor release", "refactor advances patch").
- [operator-ruled] The pivot happens in this drydock, each change noted in the manual as an airworthiness directive (verbatim: "this is the best time to pivot, this is exactly why we are in dry dock").
- [operator-ruled] The work order is the OBPI's successor and the work package groups orders for cohesion, a correction (verbatim: "I'm saying that the WO IS the OBPI, which is a correction").
- [operator-ruled] Gate 5 sits at the order, as on every OBPI (verbatim: "answer was A").
- [operator-ruled] With the governors off the work still takes care, and running past a disabled limit is a noted act of diagnosis or test (verbatim: "while the governors are disabled don't overrev the engine").
- [operator-ruled] The feature package is the epic and the work package, the mADR's successor, is the story; MX work advances patches through the patch release skill (verbatim: "A wins because you elevate the feature pack to epic and keep the WP (mADR) as a story").
- [operator-ruled] Checks are due by date for now; A and B are GHI-driven and recommended at a GHI drawdown; C and D are MX-driven and recommended at a minor release and gz mx exit (verbatim: "B for now until we have more maturity").
- [agent-chose] Paused the RO-12 open points when the work organization was questioned, because the specification keys on the levels the run would settle.
- [agent-chose] Carried B's exact boundary and the waiver-list drawdown to the classification program and the chore row as advice, not put as questions.

## Immediate Next Steps

1. The operator reads docs/rnd/repair-work-organization/review.md in full and says so; then put the sign-off, kill or fund, and record it in the record's Close.
2. On fund, take each of disposition rows 2 to 5 to the operator for its go, one row at a time; row 2's GHIs go through ghi-author.
3. Resume the RP-12 specification at docs/governance/harbor-ro12-contractor-kit.md on the run's model: re-put open point 2 in its terms, keeping ruling 1.
4. Carry #1296's three acceptance cases into that specification, then close #1296 as superseded against it.

## Pending Work / Open Loops

Sign-off on the repair-work-organization run is unput. The RP-12 specification is a draft with one ruling. #1296 stays open until the specification carries it. #1185 stays open until a real package completes; #1200 stays open for the pipeline skill's sentence. The run commissions, awaiting the operator's go per row: the RP-n alias, gz mx enter requiring a return to service package, --level retired, and the census's five statement-mechanism disagreements (row 2); the chore registry's levels and intervals and the waiver drawdown (row 3); the canon amendments, among them the requirements model's work package row and the four-records succession (row 4); the chore classification program, the checkpoint read through disconnect lists, RP-12's order record and RP-14's migration to the work order (row 5). The mx-session lock's lease is expired and stays held until its holder or the operator frees it. MX debt keeps aging until gz mx exit. Thirty-one chores are overdue, and none has recorded a run since 2026-10-17.

## Verification Checklist

Run git rev-list --left-right --count origin/main...HEAD and expect 0 and 0 after the sync. Run gh run list --branch main --limit 3 and read the run for this session's commits. Run uv run gz obpi lock list and expect only the mx-session lock. Run uv run gz handoff rulings --search "return to service package" and expect this session's rulings. Read docs/rnd/repair-work-organization.md § Close and expect the frontier empty and sign-off blank.

## Evidence / Artifacts

`docs/rnd/repair-work-organization.md`
`docs/rnd/repair-work-organization/review.md`
`docs/rnd/repair-work-organization/sources/census-chores.md`
`docs/rnd/repair-work-organization/sources/letter-checks.md`
`docs/rnd/repair-work-organization/sources/faa-8900-1-vol20-extract.md`
`docs/rnd/repair-work-organization/sources/.gitignore`
`docs/governance/harbor-ro12-contractor-kit.md`

## Settled Rulings

1956 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
