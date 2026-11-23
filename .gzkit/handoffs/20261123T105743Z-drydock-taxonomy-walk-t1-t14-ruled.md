---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-23T10:57:43Z'
agent: claude-code
session_id: e870dccc
continues_from: .gzkit/handoffs/20261122T205648Z-drydock-taxonomy-draft-findings.md
---

## Current State Summary

This session resumed the drydock taxonomy handoff, made docs/governance/drydock-taxonomy.md exhaustive, walked the operator through it in the terminal one step at a time, and took the operator's rulings W1 to W38 as it went. Every ruling is booked in the page's section 9 with its question, options and verbatim words, and pushed.
- The gathering: seven read-only tracks (A to G) read every source section 9 named in full and checked each term against the booked rulings; their dated records landed under docs/governance/drydock-taxonomy/sources/ (ee333216b).
- The walk-through: eleven steps, then the REQ chain disentangled link by link, then the FIX questions, then T1 to T14 in order.
- The repair discipline now ruled: repair package (RP) contains repair orders (RO); an order holds its FIXes (the repair requirement) and its tasks; a task sits under one REQ or FIX; one discipline at every check level, A and B on the line, C and D out of service.
- Identifiers ruled: PREFIX-nnnn-<slug>, slug frozen at minting, the number the key, the short form resolving; four-digit minimum, six for TASK-. Prefixes: WP, RP, WO, RO, FIX, REQ, TASK, FP (feature package), RTS (return to service package).
- The catalog store collated in one place: docs/governance/ieee/requirements-model.md section The store (54040c2a5).
- X1 to X12 filed as GHIs #1345 to #1355 through ghi-author (X9 posted as evidence on #1188; X10's premise withdrawn and its narrower defect filed as #1355).
- The MX lease renewed on the operator's word at 2026-11-22T23:35Z.

## Important Context

- WHERE THE WALK STANDS. Ruled: T1 (W26), T2 (W29), T3 (W30), T4 (settled by W29), T5 (W31), T6 (W32), T7 (W33), T8 (settled by W2 and RP-11 ruling 4), T9 (W34), T10 (W35), T11 (W14), T12 (W36), T13 (W37), T14 (W38), T38 (W10), T40 (W13, done), T31 for the word order (W26). Open, to be put one at a time in order: T15 (work order meaning a GHI), T16 (squawk), T17 (hangar and drydock depth, the level field), T18 (letters A to E against A to D), T19 (the amendment AMD- against the ladder), T20 (the ladder's supplement record; whether a revision may change a contract row), T21 (control roles: tripwire, alarm, dispatcher), T22 (positions, personas, dispatch roles), T23 (the construction side's one name; the maintenance visit as a package), T24 (lane's home), T25 (who opens and closes the hangar; the floor's one list), T26 (handback), T27 (the briefing gates nothing against kit ruling 19), T28 (passage log), T29 (task trailer, mostly settled by W22), T30 (page file names, RP-0's page, sub-id namespacing), T31 (the other overloaded words), T32 (marking superseded rulings in the corpus), T33 (ADR and pool identifiers), T34 (legacy ADR and OBPI vocabularies), T35 second half (no separate document against the feature package), T36 (the Release Package id; the operator suggested GZ- with semver), T37 (numbered page rulings), T39 (Gate 5 on a line order).
- HOW THE OPERATOR WANTS IT RUN. In the terminal, one step or one question per turn, the content shown here and never a pointer to the page; plain lists, no wide tables; define every short name before using it; list what W rulings already settle before putting a T decision and put only the remainder; never claim something is captured before the edit's tool result is in hand, and commit after each ruling. Insights booked this session under scope drydock-formalism record each correction.
- THE DIRECTION (W5): "nuke the planet from orbit"-level repair, everything except the spent ledger. After the walk: the execution plan (the operator deferred an 8-step rectification plan until the hierarchy and rulings are settled), then the documentation R&D run (W15: 2,030 doc pages, no governance index, 183 pages claiming sole authority; "dry dock fodder").
- WHAT T10 (W35) ROUTES: one contract amendment adopting the walk's rulings as canon in the requirements model (W14) and correcting the contract's text, plus a revision on each owning package: RP-2 (the seam, W34), RP-4 (release, feature package), RP-6 (canon retirement), RP-11 (catalog parents W3, the shipped seed), RP-12 (FIX, the order's REQ list, records for its past work; rulings 30, 43, 45, 46, 165 reversed), RP-14 (construction on work orders: W17, W20 to W22). None of that is executed yet.
- Shift turnover, hangar open, measured 2026-11-23T10:56Z: gz wp tag show --all reads no tag issued; gz wp runs reads no work package in flight; the contract's list of discrepancies is unchanged this session; gz obpi lock list reads mx-session ACTIVE at 679 minutes, renewed 2026-11-22T23:35Z, so the lease lapses near 2026-11-23T23:35Z. The buy-back record is not built.
- RP-12's repair order 5 is still not opened; under W31 open work is minted as records before any more work is done.

## Decisions Made

- [operator-ruled] Resume from the predecessor handoff (verbatim: "resume from h/o").
- [operator-ruled] W1: the three release disagreements stay with RP-4 and RP-6 (verbatim: "agreed, leave them with their owners").
- [operator-ruled] W2: family single letters superseded; capability, outcome, REQ and ADR ids confirmed; the REQ-to-catalog relation and the identity seam need review (verbatim: "family, those single letters are superseded. capability, yes. outcome, yes. REQ - yes. but how does a REQ relate to its place in the catalog? there seems to be drift here. We need review").
- [operator-ruled] W3: a catalog record's parent lives in a field on the record (verbatim: "A, a field on each record").
- [operator-ruled] W4: the repair hierarchy is repair package, repair orders, tasks (verbatim: "We should have Repair Package, that contains Repair Orders. Repair Orders can then have tasks (and perhaps repair REQs?). Let's get that clear first").
- [operator-ruled] W5: total repair except the spent ledger (verbatim: "nuke the planet from orbit, it's the only way to be sure"-level repair here"; "Let's get this repair-side hierarchy down first before we worry about an 8-step rectification plan").
- [operator-ruled] W6: FIX is the repair requirement, living in its repair order (verbatim: "yes, that's the concept ==> fix is the repair requirement, otherwise, we have a bad name and semantic collision").
- [operator-ruled] W7: a FIX belongs to one order at a time (verbatim: "A, one order at a time").
- [operator-ruled] W8: a FIX is unique to its package and order; a redirect writes new FIXes (verbatim: "A, a redirect writes new FIXes (the referene chains will help with traceability and analyses)").
- [operator-ruled] W9: one GHI yields many FIXes, each FIX answers one GHI (verbatim: "A").
- [operator-ruled] W10: one repair discipline at every check level, A and B on the line, C and D out of service (verbatim: "yes, and I wanted that to be solidly confirmed as we now have an organizational discipline for repair work that gzkit has never had").
- [operator-ruled] W11: a GHI closes when every FIX answering it holds (verbatim: "A").
- [operator-ruled] W12: the catalog store stands for now (verbatim: "it stands for now, finish FIX question 3 - (that design is fine, I hope it is well-documented)").
- [operator-ruled] W13: FIXes stored in data/catalog/fixes.json naming their order; the store documentation collated now (verbatim: "A, and for God's sake, please tighten up that documentation, NOW").
- [operator-ruled] Renew the MX lease (verbatim: "yes, renew the lease now").
- [operator-ruled] W14: the requirements model is the taxonomy's one home (verbatim: "A, the requirements model is the one home").
- [operator-ruled] W15: finish the walk, then open a documentation R&D run (verbatim: "finish the taxonomy walk first, then open the R&D (this is most CERTAINLY dry dock fodder too, the vibe code kudzu is excessive and accelerating)").
- [operator-ruled] W16 and W17: FIX-<n>, and one id rule for every record id, PREFIX-<n>-<slug> (verbatim: "A, FIX-<n>"; "yes, one rule for every record id").
- [operator-ruled] W18: one proof path for REQ and FIX (verbatim: "A, one proof path for both").
- [operator-ruled] W19: fix cycle renamed rework, the bound and exit and field likewise (verbatim: "yes, confirm the renaming as listed").
- [operator-ruled] W20: a work package declares its outcomes at initiation (verbatim: "B, a declared outcomes list at initiation").
- [operator-ruled] W21: the work order's record lists the REQs it binds (verbatim: "A").
- [operator-ruled] W22: a task sits under one REQ or FIX and records its order (verbatim: "A, a task under one REQ or FIX").
- [operator-ruled] W23: construction orders stay with RP-14 (verbatim: "keep it with RP-14").
- [operator-ruled] W24: the 2026-10-16 WP-4 shapes withdrawn (verbatim: "withdraw them").
- [operator-ruled] File the walk's defects as GHIs before the T rulings (verbatim: "file them as GHIs first"); X10's narrower defect filed (verbatim: "A").
- [operator-ruled] W26: the tasking order is the work package's charge; bare order names the Order level only (verbatim: "tasking order is the purpose or goal of the work package the way that an mADR would have had"; "yes, confirm A for the rest").
- [operator-ruled] W27: the change order returns to JFMM's revision (verbatim: "c").
- [operator-ruled] W28: the REQ and FIX editorial counter is edits (verbatim: "a").
- [operator-ruled] W29: WP- for work packages, RP- for repair packages (verbatim: "a").
- [operator-ruled] W30: WO-nnnn and RO-nnnn, ids padded to four digits at least and TASK- to six (verbatim: "ID-nnnn-<slug>? what about that? we already decided this earlier."; "b").
- [operator-ruled] W31: every past and open repair unit becomes a record; past Gate 5s only on re-attestation (verbatim: "a").
- [operator-ruled] W32: the return to service package is RTS-nnnn-<slug>, its contract the specification (verbatim: "A").
- [operator-ruled] W33: the feature package is FP-nnnn-<slug> (verbatim: "A").
- [operator-ruled] W34: one domain module of identifier value objects, a correction under RP-2 (verbatim: "yes, A in code, one domain module").
- [operator-ruled] W35: one contract amendment and a revision per owning package (verbatim: "A").
- [operator-ruled] W36: Gate 5 at the order, defined once in the charter (verbatim: "A gate 5 came at obpi closeout/completion").
- [operator-ruled] W37: nothing below the task (verbatim: "A").
- [operator-ruled] W38: the 2026-10-05 ladder retired whole; the pool is intentions, not ADRs (verbatim: "A - and, i need a fresh handoff and git sync now").
- [agent-chose] Ran the exhaustive gathering as seven parallel read-only tracks and committed their records as the page's sources, local paths stripped.
- [agent-chose] Withdrew taxonomy row X10 when its premise did not reproduce, rather than file it.

## Immediate Next Steps

1. Resume the taxonomy rulings at T15 (work order meaning a GHI), putting each remaining decision one at a time in the terminal, recording each ruling in docs/governance/drydock-taxonomy.md section 9 and committing after each.
2. Renew the mx-session lease through the gz-mx skill on the operator's word before it lapses near 2026-11-23T23:35Z.
3. When the rulings are done, draft the execution plan for the operator: the contract amendment and the per-package revisions T10 (W35) routes, in an order the operator rules.
4. Then open the documentation R&D run through gz-rnd (W15).
5. Ask the operator whether the false settled marks in the committed handoff 20261122T051329Z are corrected or kept as the defect's record (carried from the predecessor).

## Pending Work / Open Loops

- The open T decisions listed in Important Context (T15 to T37 and T39, less those settled).
- The execution plan for W35's route: one contract amendment plus revisions on RP-2, RP-4, RP-6, RP-11, RP-12 and RP-14; nothing executed.
- The documentation R&D run (W15).
- GHIs filed this session, open: #1345, #1346, #1347, #1348, #1349, #1350, #1351, #1352, #1353, #1354, #1355. Operator questions sit in #1350 (an attested REQ asserts the retired mechanism), #1349 (open ruling 11 of the renewing-vows run), #1353 (RP-12 ruling 175 against RP-14 ruling 9) and #1354 (widening a closed set).
- From the predecessor: the check-outcome-reporting R&D's row 1 change order on RP-13 awaits the operator; #1341, #1342, #1343, #1302, #1337 and #1331 stay open; OBPI-0.35.0-20 reads PENDING.

## Verification Checklist

- git rev-list --left-right --count origin/main...HEAD reads 0 0.
- uv run gz obpi lock list reads mx-session ACTIVE, renewed if the session runs past 2026-11-23T23:35Z.
- docs/governance/drydock-taxonomy.md section 9 holds W1 to W38; section 8 marks T1 to T14, T38 and T40 ruled or settled.
- gh issue view 1345 through 1355 read OPEN.
- data/catalog/work_packages.json still holds WP-01-astral-toolchain alone and data/catalog/orders.json no order: no ruling of this session has been executed in code or store.

## Evidence / Artifacts

- `docs/governance/drydock-taxonomy.md` — the taxonomy, rulings W1 to W38 in section 9, decisions T1 to T40 in section 8
- `docs/governance/drydock-taxonomy/sources/gather-A-drydock-vocab.md` — track A
- `docs/governance/drydock-taxonomy/sources/gather-B-roles-personas.md` — track B
- `docs/governance/drydock-taxonomy/sources/gather-C-rp-subunits.md` — track C
- `docs/governance/drydock-taxonomy/sources/gather-D-reqs-gates-states.md` — track D
- `docs/governance/drydock-taxonomy/sources/gather-E-events-aliases-census.md` — track E
- `docs/governance/drydock-taxonomy/sources/gather-F-rnd-ghi-chores-hex.md` — track F
- `docs/governance/drydock-taxonomy/sources/gather-G-naming-lineage.md` — track G, the naming lineage
- `docs/governance/ieee/requirements-model.md` — section The store, collated
- `.gzkit/insights/agent-insights.jsonl` — scope drydock-formalism

## Settled Rulings

2502 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
