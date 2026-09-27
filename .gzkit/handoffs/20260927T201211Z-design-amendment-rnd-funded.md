---
mode: CHECKPOINT
adr_id: null
branch: main
timestamp: '2026-09-27T20:12:11Z'
agent: claude-code
session_id: cd5536cb-c5e8-452f-9c8d-24b97fc4c5ed
continues_from: .gzkit/handoffs/20260927T194532Z-design-amendment-rnd-in-flight.md
---

## Current State Summary

The design-amendment R&D run (docs/rnd/design-amendment.md) is CLOSED and FUNDED. Q9 resolved (AMD-<semver>-NN amendment IDs; REQ-<semver>-ANN-NN REQs; TASK-<semver>-ANN-NN-NN). Q10: build now in legacy identifiers, shaped to map onto the 2026-09-25 requirements catalog. Prior art found late and recorded: ADR-pool.adr-amendment-tracking, gz obpi supersede (never used). The operator ruled the remaining detail questions are ADR design, funded the run as pre-1.0, and declined any exception to ascending ADR order. Two Magna Carta amendments were written today: DDD-discipline R&D run pre-1.0, and the amendment ADR funded pre-1.0 in ascending order. The operator then directed that ADR work in the campaign comes first.

## Important Context

Queue as of today: ADR-0.35.0 TOPMOST 8/14, 0.36.0 0/9, 0.37.0 0/6, 0.38.0 reserved and unauthored, 0.39.0 authored by exception 0/7; the amendment ADR takes the next number after 0.39.0 and is authored and completed in turn. A feature ADR number is identity, release version and queue position at once; the operator says the campaign already carries a plan to fix that coupling and does not want gzkit's current working broken meanwhile. The run record is the amendment ADR's design input, as config-surface-design-2026-09-20.md was for ADR-0.39.0. Its Q11 (ledger events: opened plus completed recommended) and the other open questions travel to the ADR.

## Decisions Made

- [operator-ruled] Q9: amendment identifiers take option A as first offered (verbatim: 'A as offered, if that makes more sense to you. A in the way you previously presented it.').
- [operator-ruled] Q10: build the amendment capability now in legacy identifiers and map it onto the requirements catalog later (verbatim: 'A, build it now and map to the catalog later').
- [operator-ruled] The amendment verb family is heavy ADR design, not R&D detail (verbatim: 'we clearly have convergence on the verb being needed - this is why my ADR system is so broken, we need this family of verbs now. we are now into ADR heavy design territory and to pretend otherwise is asinine').
- [operator-ruled] Sign-off: fund, pre-1.0 (verbatim: 'fund it, pre-1.0, we need it now.').
- [operator-ruled] No exception to ADR order; ADR work in the campaign comes before other refactoring (verbatim: 'no, we have campaign plans to fix this, so until it is fixed, I don't want to break how gzkit currently works. this makes it clear ot me that we need to get going on adr work in the campaign. get these all made, then go back to other refactoring').

## Immediate Next Steps

1. Ask the operator how far 'get these all made, then go back to other refactoring' reaches: it may reorder the 2026-09-02 amendment that put Movement C's doctrine-declared-without-mechanism box NEXT-IN-PRIORITY, and the 2026-09-15 rebalancing; record the answer as a Magna Carta amendment before acting on it.
2. Present ADR-0.35.0 (8/14) for the operator to initiate its next OBPI through gz-obpi-pipeline; only the operator starts OBPI work.
3. On the operator's go per row, file the run's disposition-2 GHIs through ghi-author: the agent-contract-rationale.md:349 false claim, the gz-rnd destinations ruling plus the false no-glossary premise, and the ADR-0.0.32 amendment work order.
4. When the operator invokes gz-rnd for DDD discipline, seed it from the run's Q8 decision and the 2026-09-27 Magna Carta amendment.

## Pending Work / Open Loops

Uncommitted: docs/rnd/design-amendment.md (staged), two 2026-09-27 amendments in docs/governance/build-to-1.0-campaign-2026-09-20.md, two insight records, the ledger change present at session start. Disposition 5 (move eight prose-superseded REQs onto the superseded state) waits for the amendment ADR to land. The glossary term 'amendment' waits for the DDD run. Option A for vendor mirrors stays held behind the amendment ADR. GHI #1138 routing still awaits the operator. Everything carried in predecessor handoffs stays open, including the #1119-#1137 queue.

## Verification Checklist

Read the Close section of docs/rnd/design-amendment.md: challenge restated, frontier empty, sign-off quoted. The two newest entries at the top of the Amendments section of docs/governance/build-to-1.0-campaign-2026-09-20.md quote the operator. uv run gz adr report lists 0.35.0, 0.36.0, 0.37.0 and 0.39.0 as pending feature ADRs.

## Evidence / Artifacts

- `docs/rnd/design-amendment.md`
- `docs/governance/build-to-1.0-campaign-2026-09-20.md`
- `docs/design/adr/pool/ADR-pool.adr-amendment-tracking.md`
- `docs/governance/ieee/design-candidates.md`
- `src/gzkit/events.py`
- `.gzkit/handoffs/20260927T194532Z-design-amendment-rnd-in-flight.md`

## Settled Rulings

1131 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
