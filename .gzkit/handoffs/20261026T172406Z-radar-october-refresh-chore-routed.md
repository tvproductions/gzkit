---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-26T17:24:06Z'
agent: claude-code
session_id: 15ccb03e-0293-4b54-a7de-76369e7d7d0d
continues_from: .gzkit/handoffs/20261026T083114Z-rnd-contractor-kit-mode-contract-census-filed.md
---

## Current State Summary

After the contractor-kit handoff, the session turned to the competitor radar on the operator's request. A new project-local chore, competitor-radar-currency, puts the radar on a 30-day elapsed-time staleness clock, and the gz-competitor-radar skill's cadence line was corrected (skill 1.1.2). The October 2026 landscape refresh ran: 16 competitors re-sourced by three research tracks, headline claims checked against GitHub, tstack added (reference watch) and four stale registry links fixed. The operator ruled on all eleven suggested moves in a grill, and every approved move was routed: dated 2026-10-26 amendments in five pool ADRs, evidence-only amendment to ADR-0.37.0, comments on #1252, #1185 and #1250, and GHIs #1281 and #1282 filed. adrkit was then read in full and admitted to secondary watch, with five new moves (112 to 116) pending the next grill. The contractor-kit R&D run is untouched since the previous handoff.

## Important Context

The radar's registry and scans live under artifacts/reports/competitor-radar/, and artifacts/ is gitignored: scan JSON and rendered reports must be added with git add -f, as the May files were. radar.py validate is offline and byte-compares the rendered Markdown, so the JSON is edited and then rendered and validated, never the Markdown. A move routes only after the operator rules it in the grill. ADR-0.37.0's alternatives 2 and 2a already measured diff-to-decision governance: brief Allowed Paths gave a median of 86 co-claimants, so adrkit's narrow declared scope is a candidate answer to that boundedness question and must be measured before adoption. Safe mode stays open, and the pre-push gz check is alarm-wrapped off (#1273 finding 4).

## Decisions Made

- [operator-ruled] Add tstack to the radar, refresh the landscape and put it on a staleness chore (verbatim: 'add this to it: https://github.com/t3dotgg/tstack, refresh the landscape and get it on a chore rotation (staleness) - yes, chore it.').
- [operator-ruled] Open the grill on the October moves (verbatim: 'yes, open grill and tell me how speckit is "moving in on" gzkit.').
- [operator-ruled] Approve MOVE-101, 102, 103, 106 and 108 to their existing pool ADRs; MOVE-105 as a comment on #1252; MOVE-107 and MOVE-110 as GHIs; apply MOVE-109 (Better Spec to discovery, Specledger to reference); MOVE-104 discussion only (each selected in the grill).
- [operator-ruled] Route adrkit's diff-to-decisions query as evidence for ADR-0.37.0 after asking 'don't we have that with the airlock?' (selected 'Evidence for ADR-0.37.0 (Recommended)').
- [operator-ruled] Reject distributing gzkit through Spec Kit; gzkit stays standalone (selected 'Reject' on MOVE-111b).
- [operator-ruled] Do the routing (verbatim: 'yes, do routing').
- [operator-ruled] Capture adrkit's useful mechanisms on the radar (verbatim: "let's capture what's useful and put on the radar.").
- [agent-chose] Recorded adrkit's lessons as moves 112 to 116 pending the next grill rather than routing them unruled.

## Immediate Next Steps

1. Ask the operator whether to grill MOVE-112 to MOVE-116 (adrkit lessons) now or leave them for the November scan.
2. Resume docs/rnd/contractor-kit.md through gz-rnd: append a decision entry with the operator's words, check the record against git, and recompute the frontier from the subject.
3. Put the mode contract's syntax: the candidate Python affordances for code controls (decorators, typing.Protocol ports, context managers, class registration, entry points), after reading the census and the seven chore --self-test arms.
4. Put the ADR admission question on the permanent mode-contract design requirement, then the remaining proposed matrix rows (C5, C10, C11, C12, C13, B1, B11, C1).
5. Close the run: the kit's RO number, the audit chore's shape, disposition rows 1 and 6, the restated challenge, review.md and sign-off.

## Pending Work / Open Loops

- MOVE-112 to MOVE-116 (adrkit lessons) are pending-grill in artifacts/reports/competitor-radar/scans/2026-10.json.
- GHIs #1271 to #1282 are filed and unworked; #1273 is the MX-system review the operator ordered.
- The competitor-radar-currency chore next falls due 30 days after the October scan.
- adrkit's lessons 1 to 3 (two-sided bounding, claims without exit-code authority, as-of queries) bear on ADR-0.37.0, which carries only the evidence-only amendment so far.
- Everything carried from the previous handoff's Pending Work still stands: the matrix gap rows to re-check, the unread construction-period hypothesis, the row 4 drafts awaiting the operator's go, the unretrieved 8900.1 V4C4, and the mx-session lock and MX advisory debt.

## Verification Checklist

- uv run python .gzkit/skills/gz-competitor-radar/scripts/radar.py validate prints 'competitor-radar validation passed'.
- uv run gz chores advise competitor-radar-currency shows both criteria PASS.
- gh issue view 1281 and gh issue view 1282 show each issue open with its closure contract.
- git rev-list --left-right --count origin/main...HEAD shows 0 0 after the sync.

## Evidence / Artifacts

- `artifacts/reports/competitor-radar/scans/2026-10.json`
- `artifacts/reports/competitor-radar/2026-10.md`
- `artifacts/reports/competitor-radar/registry.json`
- `.gzkit/chores/competitor-radar-currency/CHORE.md`
- `.gzkit/chores/registry.json`
- `.gzkit/skills/gz-competitor-radar/SKILL.md`
- `docs/design/adr/pool/ADR-pool.review-receipt-taxonomy.md`
- `docs/design/adr/pool/ADR-pool.skill-control-surface-contract.md`
- `docs/design/adr/pool/ADR-pool.content-injection-scanning.md`
- `docs/design/adr/pool/ADR-pool.solved-problem-pattern-corpus.md`
- `docs/design/adr/pool/ADR-pool.graduated-oversight-model.md`
- `docs/design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/ADR-0.37.0-airlock-calibration-and-compulsion.md`
- GHIs #1281, #1282; comments on #1252, #1185, #1250

## Settled Rulings

1753 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
