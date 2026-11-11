---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-11T06:12:25Z'
agent: claude-code
session_id: 28be5a76-7522-4bcb-89d2-5979ba71b97e
continues_from:
- .gzkit/handoffs/20261110T105134Z-hex-spec-groups-e-to-g.md
- .gzkit/handoffs/20261111T004658Z-session-exit-bookmark.md
---

## Current State Summary

The hexagonal specification R&D run (gz-rnd, docs/rnd/hexagonal-specification.md) is in diamond 1. Session 4d976f7c resumed it from the groups E to G handoff, renewed the MX lease, and recomputed the frontier from the subject: critique 2's remaining half (a limit on tests per requirement) was still open and was put and ruled, then the name of a Table 8.3 row was put and ruled (commit 67c110bf6). That session ended without an authored handoff; its exit bookmark (20261111T004658Z) is folded here. This session authored nothing in the record; it verified state and wrote this successor. All seven disposition rows carry a decision; the challenge is not restated, the review is not written, sign-off is not put.

## Important Context

Safe mode (drydock) is active under the MX hangar session 57346836, whose lease was renewed 2026-11-11T00:24Z for 1440 minutes; the hangar has carried advisory debt for about 600 hours and closes only through gz mx exit via gz-mx. The run licenses no ADR, OBPI, chore, GHI or canon change; canon rule 7 of .gzkit/rules/hexagonal-architecture.md stands unchanged. The term variant is held in the R&D record until the project glossary's home is named; earlier entries that say outcome row mean a variant. Khononov's text is not held in the repo: the operator must paste the passages before the remaining items can be read. Every act in safe mode is one commit with its Task trailer (TASK-ro6-classic-adr for this run).

## Decisions Made

- [operator-ruled] Fold the session-exit bookmark into a superseding authored handoff before resuming the R&D run (verbatim: "Yes, fold it").

## Immediate Next Steps

1. Put this handoff to the operator and book the ruling with uv run gz handoff decide under this session's own id.
2. On the operator's go, resume under gz-rnd: append a decision entry quoting the resume words, check the record against git, and recompute the frontier from the subject rather than from this handoff.
3. When the operator pastes Khononov's passages (ch. 3, ch. 4, aggregates and event sourcing), take aggregates and bounded contexts, the ontology's DDD role, 'one team per context', and each of the 78 ledger event types' owning entity and drydock name, read against Montenegro's 'an event with no consumer is pure cost' (section 9.2.4).
4. Revisit disposition rows 1 and 5 once those are ruled, then restate the challenge on purpose, write docs/rnd/hexagonal-specification/review.md, and put sign-off: kill or fund.

## Pending Work / Open Loops

- Khononov passages not yet supplied; every remaining frontier item is held behind them.
- Glossary home for the term variant is unnamed; the term stays in the R&D record until it is.
- MX hangar advisory debt keeps aging; gz mx exit is the close, through gz-mx, once the drydock work is done.
- 32 chores overdue and 6 due per gz chores status; announced, not gating.

## Verification Checklist

- uv run gz handoff resume shows this handoff as newest and Fresh.
- uv run gz obpi lock list shows the mx-session claim ACTIVE within its TTL.
- git rev-list --left-right --count origin/main...HEAD reads 0 0 after push.
- tail docs/rnd/hexagonal-specification.md shows the variant ruling and the Close section waiting on Khononov.

## Evidence / Artifacts

- `docs/rnd/hexagonal-specification.md`
- `.gzkit/handoffs/20261110T105134Z-hex-spec-groups-e-to-g.md`
- `.gzkit/handoffs/20261111T004658Z-session-exit-bookmark.md`
- `.gzkit/rules/hexagonal-architecture.md`
- `.gzkit/ledger.jsonl`

## Settled Rulings

2155 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
