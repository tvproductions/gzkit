---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-01T03:11:23Z'
agent: claude-code
session_id: 63a4e8a8-02b8-40ae-be37-ff789c2cc4bc
continues_from: .gzkit/handoffs/20261031T114023Z-ro14-specified-bound-landed.md
---

## Current State Summary

RO-14 tranche 1 act 2 is landed. #1198 is repaired in cli.main and closed after independent review; #1208 is half answered and stays open for act 3. Commits 961c972d6 and fd85b1ad5, CI green on both. f6663f5c8, the schema fix after act 1, is folded in here: it is the commit act 1's CI evidence rests on, not 825e76198.

## Important Context

The contract moved the pipeline preconditions to tranche 1 because a repair to gz obpi would guard no run (harbor-pilotage-candidate § Rulings of 2026-10-31). Read that before touching any gz obpi surface. A concurrent session is writing the handoff-picture specification in this tree: docs/design/briefs/SPEC-session-handoff-picture.md, agent-insights rows and ledger rows are its work, so stage by path and never with git add -A. Pushing in quick succession cancels CI runs. A held Ledger instance caches reads; tests open a fresh one.

## Decisions Made

- [agent-chose] #1198 repaired in cli.main rather than per parser entry: the measured population was two of 134 handlers and the closure contract names this route.
- [agent-chose] A repair of record_dispatch was built, then withdrawn before landing, once the contract's sentence was read.
- [agent-chose] #1208 stays open for act 3 because the transition row it protects has no successor yet; it closes there by reading its exit condition on the successor, which the operator sees at the close.

## Immediate Next Steps

1. Act 3: run position and markers, #1203, #1205 and #1209, and #1208's open half, recording position ledger first.
2. Act 4: #1206 and #1028, with #1028's stop-and-ask boundary.
3. Act 5: acceptance on the work package, which gives the block its refutation count.
4. File the rebase trap and the cwd-escape guard through ghi-author.

## Pending Work / Open Loops

#1200 stays open for tranche 2 and the advisory score. #1208 stays open for act 3. #1194 is a direct fix in place. The operator still owes a look at the Mermaid drawing that opens at docs/governance/harbor-pilotage-candidate-2026-10-15.md line 83, and a ruling on the same-subject arming clause if they disagree with it. gz obpi dispatch keeps two known defects until tranche 3, recorded in the specification's § Act 2's reading.

## Verification Checklist

Run gh run list --commit fd85b1ad5 and read each job. Run uv run gz check after git add by path. Run gh issue view 1198 and 1208.

## Evidence / Artifacts

`docs/governance/harbor-ro14-obpi-forward-migration.md`
`src/gzkit/cli/main.py`
`tests/cli/test_handler_exit_codes.py`
`tests/commands/test_wp_run.py`

## Settled Rulings

1911 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
