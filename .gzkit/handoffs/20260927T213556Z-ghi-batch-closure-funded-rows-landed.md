---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-27T21:35:56Z'
agent: claude-code
session_id: 9e0af062-d35a-45fd-8dbb-22d2edb24197
continues_from: .gzkit/handoffs/20260927T202407Z-amendment-funded-adr-work-first.md
---

## Current State Summary

The operator invoked gz-rnd on the GHI queue growing faster than it drains (140 opened vs 113 closed, 2026-09-13 to 27). R&D run ghi-batch-closure opened, measured, ruled Q1-Q5, and was signed off FUNDED with a row-level go on rows 2 and 4; both landed. Measurement: all 76 open GHIs read in full by four parallel read-only agents (35 ready, 28 awaiting ruling, 4 sequence, 9 design); the residue filed before 09-13 is 30 of 36 operator-bound; the fast path closes 100 of 140 new findings at a 1.7 h median. Landed: GHI #1139 filed and fixed at 3db5f97c9 (three pool-ADR drifts amended), dead anchors repaired at 4ea5f5de1, the R&D record at 72c1ec73f and 7df21f771, and ghi-triage 5.4.0 at ead445895 (readiness enum in triage.py, grouped landing queue and ruling docket, compressed 270 to 242 lines). gz check exit 0 on the staged tree before the ead445895 commit. Five commits were ahead of origin at authoring; this handoff is followed by git-sync.

## Important Context

The binding lever on the residue is operator rulings, not agent speed: parallel Read serves the ready population, and the ruling docket (a live one-question-per-issue session) is the lever on the rest. GHI #424 still binds ghi-triage: the rank input is structural-only; readiness was admitted as an enum, and the docket prose lives in the live questions, never in the rank input. The ledger is git-tracked and about half of fix commits append to it, so worktree agents must write no Layer-2 events; Phase-2 fan-out is held behind ADR-pool.ledger-concurrency-substrate criterion 2 (RED-receipt replay). GLOSSARY.md does not exist; three terms (readiness, landing queue, ruling docket) are held in docs/rnd/ghi-batch-closure.md under design-amendment Q8 until the DDD run names the glossary's home. The readiness verdicts in docs/rnd/ghi-batch-closure/sources/readiness-2026-09-27.json are one reader's judgment per issue and route nothing; one of five spot-checked verdicts cited a false fact (#907 said #611 had landed; it is open). The open count moved 76 to 77 during the session.

## Decisions Made

- [operator-ruled] Q1: the batch capability targets both populations from one fan-out (verbatim: "Both, one fan-out (Recommended)").
- [operator-ruled] Q2: extend ghi-triage rather than author a ghi-batch skill (verbatim: "Extend ghi-triage (Recommended)").
- [operator-ruled] Q3: the fan-out stops at Read; the single writer executes (verbatim: "No — Read only for now (Recommended)").
- [operator-ruled] Q4: the three pool-ADR drifts go to one GHI repaired as dated amendments (verbatim: "One GHI, three amendments (Recommended)").
- [operator-ruled] Sign-off of R&D run ghi-batch-closure (verbatim: "Fund, go on rows 2 and 4").
- [operator-ruled] Q5, after re-entry on the GHI #424 conflict: readiness is one structural enum and the docket's rulings are asked live (verbatim: "Enum in input; rulings asked live (Recommended)").
- [agent-chose] Disposition 1 not pursued on canon: the ghi-triage extension is a reversible skill edit and fails the admission question.
- [agent-chose] Terms held in the R&D record, carrying design-amendment Q8 forward, rather than creating GLOSSARY.md.
- [agent-chose] Reworded the speculative gz ghi verbs in the record to 'the proposed ghi CLI verb group' to satisfy gz validate --cli-alignment rather than splitting paragraphs with skip markers.

## Immediate Next Steps

1. Present ADR-0.35.0 so the operator can initiate its next OBPI through gz-obpi-pipeline (carried from the predecessor; the campaign's TOPMOST box).
2. On the operator's go, draw the landing queue: run ghi-triage 5.4.0 with readiness, then ghi-close one ready issue at a time, starting with today's audit batch (the adr promote / plan create cluster first, one writer).
3. On the operator's go, run a ruling session over the ruling docket: one AskUserQuestion per R2 issue with a recommended answer, residue filed before 09-13 first.
4. On the operator's go per row, file the design-amendment run's disposition-2 GHIs through ghi-author (carried from the predecessor).
5. When the operator invokes gz-rnd for DDD discipline, seed it with the terms held in docs/rnd/ghi-batch-closure.md as well as design-amendment Q8.

## Pending Work / Open Loops

GHI #837 is open: the sibling class of #1139 [settled] (pool-ADR text never re-derived against later canon) has no class-level witness; not filed as its own GHI, and it is the operator's to route. GHI #921 carries 40 trailered commits in the window and is still open, an epic in GHI clothing; not routed. The chunk readers flagged R2/R3/R4 boundaries as least certain (#978/#983, #1003, #1131/#1134). The predecessor's open loops carry unchanged: ADR-0.40.0 promote-versus-fresh with GHI #1131 first; the design-amendment run's queued GHIs; the DDD R&D run.

## Verification Checklist

git log --oneline -6 shows 7df21f771, ead445895, 72c1ec73f, 4ea5f5de1 and 3db5f97c9. gh issue view 1139 --json state returns CLOSED. uv run -m unittest tests.skills.test_ghi_triage_deliverable passes, including TestReadinessGrouping. uv run python .gzkit/skills/ghi-triage/scripts/triage.py --format rank --rank-input <a cache file with readiness> renders the four groups. git rev-list --left-right --count origin/main...HEAD returns 0 0 after git-sync.

## Evidence / Artifacts

`docs/rnd/ghi-batch-closure.md`, `docs/rnd/ghi-batch-closure/sources/readiness-2026-09-27.json`, `docs/rnd/ghi-batch-closure/sources/rubric.md`, `.gzkit/skills/ghi-triage/SKILL.md`, `.gzkit/skills/ghi-triage/scripts/triage.py`, `tests/skills/test_ghi_triage_deliverable.py`, `docs/design/adr/pool/ADR-pool.worktree-parallel-agents.md`, `docs/design/adr/pool/ADR-pool.ledger-concurrency-substrate.md`, `docs/design/adr/pool/ADR-pool.ghi-triage-closeout.md`, `src/gzkit/hooks/scripts/ghi.py`

## Settled Rulings

1142 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
