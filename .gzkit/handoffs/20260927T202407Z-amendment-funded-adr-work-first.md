---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-27T20:24:07Z'
agent: claude-code
session_id: cd5536cb-c5e8-452f-9c8d-24b97fc4c5ed
continues_from: .gzkit/handoffs/20260927T201211Z-design-amendment-rnd-funded.md
---

## Current State Summary

Design session, no source code changed. Resumed the chunking checkpoint (operator ruled proceed, booked). Closed chunking: parallel research subagents are already ruled by AGENTS.md; no policy needed. Settled skills packaging: gzkit's shipped tooling belongs to gzkit and adopter edits are overwritten on upgrade. Ran and closed the design-amendment R&D run (docs/rnd/design-amendment.md): funded pre-1.0 as ADR-0.40.0, combining the pool ADR's mid-flight case with amendments to attested designs, authored after ADR-0.38.0 with no order exception. Wrote three Magna Carta amendments dated 2026-09-27: DDD-discipline R&D run is pre-1.0; the amendment ADR is funded; ADR work first, ahead of Movement C refactoring. Added a funded-pointer to ADR-pool.adr-amendment-tracking. The first git sync stopped on gz validate --cli-alignment (the run record named the unlanded verb gz adr amend); fixed by rewording two mentions and marking the one verbatim quote with the command-shape skip marker. A second sync follows this handoff.

## Important Context

Campaign order now (Magna Carta 2026-09-27 (3)): feature ADRs in ascending order, 0.35.0 TOPMOST 8/14, then 0.36.0, 0.37.0, 0.38.0 (reserved, unauthored), 0.39.0, 0.40.0; Movement C refactoring resumes after. The 2026-09-02 NEXT-IN-PRIORITY placement and the 2026-09-15 drawn-work order are superseded; pointers sit at the Topmost block and the Movement C header. Only the operator initiates OBPI or ADR work. A feature ADR number is identity, release version and queue position at once; the operator says the campaign already plans to fix that coupling and does not want current behaviour broken meanwhile. Tooling vs aircraft: in an adopter repo gzkit's tooling is gzkit's and upgrades replace it; the adopter's records under .gzkit/ are theirs. DDD's language arm has no mechanism; PRD section 2.1 is the only glossary and is barely maintained; the DDD run decides its home.

## Decisions Made

- [operator-ruled] Combine the pool ADR's design with the funded amendment design in ADR-0.40.0 (verbatim: 'we combine both uses of the verb - today's design and the pool's design.').
- [operator-ruled] Do not author ADR-0.40.0 ahead of ADR-0.38.0 (verbatim answer: 'Wait for 0.38.0').
- [operator-ruled] ADR-0.40.0 covers both mid-flight changes and amendments to attested designs (verbatim answer: 'Both cases (Recommended)').
- [operator-ruled] ADR work first, Movement C refactoring after (verbatim: 'A, ADR work first, record it').
- [operator-ruled] Add a pointer from the pool ADR to the run record, then sync (verbatim: 'yes, add the pointer, then git sync').
- [agent-chose] Cleared the cli-alignment failure by rewording the two agent-authored mentions of the unlanded verb and marking only the verbatim pool quote with the skip marker, rather than marking all three; the verb's final shape is the ADR's to decide.

## Immediate Next Steps

1. Present ADR-0.35.0 (8/14) so the operator can initiate its next OBPI through gz-obpi-pipeline.
2. On the operator's go per row, file the design-amendment run's disposition-2 GHIs through ghi-author: the agent-contract-rationale.md:349 false claim; the gz-rnd destinations ruling plus the false no-glossary premise in rnd-discipline.md; the ADR-0.0.32 amendment work order.
3. When the operator invokes gz-rnd for DDD discipline, seed it from the run's Q8 decision and Magna Carta amendment 2026-09-27, including Pocock's CONTEXT.md naming convention.
4. When ADR-0.40.0's turn comes, decide promote-versus-fresh; promotion needs GHI #1131 fixed first.

## Pending Work / Open Loops

Disposition 5 (move eight prose-superseded REQs onto the superseded state) waits for ADR-0.40.0. The glossary term 'amendment' waits for the DDD run. Option A for vendor skill mirrors stays held behind ADR-0.40.0. GHI #1138 routing awaits the operator. The AGENTS.md rule for planned CLI surfaces also asks for a GHI; the unlanded amend verb is tracked by Magna Carta amendment 2026-09-27 (2) and the funded ADR-0.40.0 instead, which the operator may want to confirm. Everything carried in predecessor handoffs stays open, including the #1119-#1137 queue.

## Verification Checklist

uv run gz validate --cli-alignment exits 0. uv run gz check passes before the sync commit. The three newest entries at the top of the Amendments section of docs/governance/build-to-1.0-campaign-2026-09-20.md quote the operator. The Close section of docs/rnd/design-amendment.md carries the restated challenge and the sign-off. git rev-list --left-right --count origin/main...HEAD reads 0 0 after the sync.

## Evidence / Artifacts

- `docs/rnd/design-amendment.md`
- `docs/governance/build-to-1.0-campaign-2026-09-20.md`
- `docs/design/adr/pool/ADR-pool.adr-amendment-tracking.md`
- `.gzkit/handoffs/20260927T201211Z-design-amendment-rnd-funded.md`
- `.gzkit/insights/agent-insights.jsonl`

## Settled Rulings

1136 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
