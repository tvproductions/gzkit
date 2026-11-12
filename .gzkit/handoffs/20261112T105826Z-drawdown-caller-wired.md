---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-12T10:58:26Z'
agent: claude-code
session_id: 6f525f87-8c83-490e-b38e-e2765dbe53e4
continues_from: .gzkit/handoffs/20261112T084842Z-rp15-tranche6-landed.md
---

## Current State Summary

RP-15 tranche 6 stays landed and pushed (2aee45ba2). The waiver-ratchet-drawdown chore now has an automatic caller: .github/workflows/ratchet-drawdown.yml runs uv run gz chores advise waiver-ratchet-drawdown (self-test, then report) on the 1st and 15th of each month at 07:00 UTC, with a manual trigger, matching the chore's elapsed-time/14d cadence. The chore's CHORE.md § Workflow names that caller. Committed as aafa0f554 and pushed through the hooks; gz validate --gate-callers exits 0 with 49 gates inventoried, 9 called and 40 accepted as uncalled, so gz check no longer carries the gate-callers advisory.

## Important Context

Safe mode is active; every act is one commit with the Task: TASK-ro6-classic-adr trailer. The caller is a scheduled CI workflow on the queue-hygiene.yml precedent rather than a gz check step, because the chore is a read-only report that gates nothing a commit changes; moving it into gz check through quality.py's _run_project_local_ratchet shape remains available if the operator prefers. The gate-callers audit counts a chore as called when its slug appears in src/gzkit/quality.py, .pre-commit-config.yaml or a .github/workflows file. The new workflow has not yet run on GitHub; its first scheduled or dispatched run is its first observation there. The kernel name and the package map remain drafts.

## Decisions Made

- [operator-ruled] The waiver-ratchet-drawdown chore's missing caller is fixed by wiring a caller, not by grandfathering it (verbatim: "Wire a caller").
- [agent-chose] Wired the caller as a fortnightly scheduled workflow mirroring queue-hygiene.yml, keeping the per-change gate unchanged, since the chore is a read-only report on a 14-day cadence.

## Immediate Next Steps

1. Put this handoff to the operator and book the ruling with uv run gz handoff decide under the new session's own id.
2. Ask which work moves next: an independent review of tranche 6, RP-7's hexagon test gates (fakes only, the labels, @covers on hexagon tests), RP-7's held rulings H1 to H14, the hexagonal run's row 7 follow-on runs, or routing GHIs 1318 to 1324.
3. Trigger the ratchet-drawdown workflow once by workflow_dispatch, or read its first scheduled run, to observe it pass on GitHub.

## Pending Work / Open Loops

The tranche 6 discrepancy line stays open until cleared with the alarms on, and no independent review of tranche 6 has run. GHI 1267's mechanism is addressed by the widened checker, but the issue closes only after a reviewer that did not do the fix confirms it. The insight recorded for the drawdown chore's missing caller is now resolved by aafa0f554. The ratchet-drawdown workflow has not run on GitHub yet. GHIs 1318 to 1324 remain open and unrouted. RP-7's hexagon test gates are unbuilt and H1 to H14 are held. Fakes and the core/ inner packages do not exist yet; gzkit's use cases migrate after return to service.

## Verification Checklist

git status -sb shows main level with origin; uv run gz validate --gate-callers exits 0 with 9 called gates; uv run gz chores advise waiver-ratchet-drawdown passes both criteria; uv run gz validate --hexagon-dependencies exits 0; gh run list --workflow ratchet-drawdown.yml shows the workflow once it has run.

## Evidence / Artifacts

`.github/workflows/ratchet-drawdown.yml`, `.gzkit/chores/waiver-ratchet-drawdown/CHORE.md`, `src/gzkit/governance/trust_audits/gate_callers.py`, `data/uncalled_gate_grandfather.json`

## Settled Rulings

2181 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
