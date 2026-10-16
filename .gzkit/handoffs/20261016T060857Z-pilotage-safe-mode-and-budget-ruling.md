---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-10-16T06:08:57Z'
agent: claude-code
session_id: 4fd13b45-724e-4433-ab23-fd6c5df2b932
continues_from: .gzkit/handoffs/20261015T121703Z-pipeline-skill-cutover-under-pilotage.md
---

## Current State Summary

Second pilotage handoff of 2026-10-16, superseding `20261015T121703Z-pipeline-skill-cutover-under-pilotage.md`. Landed on main since it, in order: the full unit tier repaired after the cutover (`31576beba`; two modules the per-change gate never ran); WO-2 run to its operator consult with the stop-and-ask finding filed as GHI #1243 (`5c6e9a493`); the contract amended with two civil-rule items from the operator's words, ADRs are not releases and safe mode (`2fc0ba206`); safe mode landed as a mode of the MX hangar under GHI #1244 (`ac3b0005e`, 21 tests red first, witness 18 killed, 0 survived after four cuts); the AGENTS.md budget recorded at the attested invariant floor plus margin by the operator's ruling on GHI #1243, closed `fixed` (`e0dab8ee4`); passage-log rows for each act. Exit conditions 1, 2 and 3 of the contract are met. Last action: the passage-log commit `5e86df8cf` succeeded; the git-sync that follows this handoff commits the insights and pushes. The operator then asked whether the pilot was designing or executing; the answer, recorded as an insight, is that the last stretch was mostly deterministic execution the contract assigns to cheaper sessions, and this handoff is where the pilot stops executing.

## Important Context

- Martial law remains in force under `docs/governance/harbor-pilotage-candidate-2026-10-15.md`. Gate 5 was never suspended: OBPI-0.35.0-17 and -20 are executed but `Draft` in the ledger until the operator attests them through `gz obpi complete`.
- Safe mode exists now: `gz mx enter --mode safe --contract <path> --reason … --attestor g0`. The present pilotage is still a hand-written arrangement until the operator enters it through the verb (the gz-mx skill is the route; the verb is operator-only). Under safe mode no guard demotes; only `mode: mx` does.
- The AGENTS.md budget is 25,000 chars by the 2026-10-16 ruling (history entry of that date); the doctrine destination of 15,000 ideal and 20,000 ceiling is unchanged and is destination work for ADR-0.35.0 § Decision 3 or an operator re-tiering. The 2026-08-17 advisory stay is unchanged.
- The commit witness (`src/gzkit/commit_witness.py`) counts `features/` as test code since `4e424fa2b`; before that every commit carrying Gate 4 scenarios read `undriven`.
- The per-change gate (`gz check`) runs only the tests a change touches; two breakages surfaced only in the full tier (`gz test`), found by the diet chore's advise step. Run `gz test` before claiming a tier green across module boundaries.
- Division of labor, re-stated by the operator's correction: the pilot (Fable) plans, measures, diagnoses and takes rulings; deterministic execution of a ruled work order goes to a cheaper session as a GHI with a closure contract.
- Open GHIs owned by this work: #1244 (safe mode, landed; close after the operator enters the pilotage through the verb), #1230 to #1241 (gz check step verdicts, unrouted), #1229, #1228, #1227, #1226, #1225, #1224 (2026-10-14 sweep), #1210, #1209.

## Decisions Made

- [operator-ruled] ADRs are not releases: verbatim "adrs are not releases, i am surprised you recommend this". An ADR records a decision and lands contracts on REQs; a separate release artifact governs which REQ states advance in a version and which work packages ship. The pilot's recommendation to reshape the feature ADR into the release plan is withdrawn.
- [operator-ruled] Safe mode: verbatim "we need a 'safe mode' that allows this sort of unencumbered 'martial law' as a toggle." and "A, extend gz mx with a safe mode - which is 'martial law' toggle". Built as a mode of the MX hangar (GHI #1244).
- [operator-ruled] The AGENTS.md budget: verbatim "A, record the budget at the invariant floor" (GHI #1243). The enforced budget records the attested invariant floor plus margin; options B (operator re-tiering of invariant canon) and C (per-consumer delivery) declined for now.
- [operator-ruled] Model economy: verbatim "fable extra is expensive if you have a deterministic plan you are now executing, discuss." The pilot stops executing ruled work orders itself; cheaper sessions execute them under § Records.
- [agent-chose] Repaired the full unit tier as a direct fix with a public seam in the retention module rather than keeping private cross-package imports. **Rationale:** the import-boundary roster is shrink-only.
- [agent-chose] Filed WO-2's stop-and-ask finding as GHI #1243 with three options rather than editing operator canon. **Rationale:** the chore's § 4 gate; the compressible remainder is operator words.
- [agent-chose] Re-cut unpushed commits by soft reset and amend rather than hard reset, after the earlier slip that discarded ledger receipts. **Rationale:** the ledger is the system of record; a dirty ledger is never discarded.

## Immediate Next Steps

1. Operator enters the pilotage through the verb so the ledger carries the toggle: `uv run gz mx enter --mode safe --contract docs/governance/harbor-pilotage-candidate-2026-10-15.md --reason "harbor pilotage" --attestor g0` (through the gz-mx skill). Then close GHI #1244 `fixed` citing `ac3b0005e`.
2. Operator rules on the four cutover disclosures in the passage log and attests OBPI-0.35.0-17 and -20 (`gz obpi complete` with attestation text naming the reclassified inventory row).
3. Operator rules WO-4, the three catalog shapes (id grammar, home, assignment channel); then the pilot authors the first entries from briefs 16 to 20.
4. Cheaper sessions execute the remaining load cuts as GHIs with closure contracts: the rules narrative lift (`.claude/rules/*.md`, 150 KB over 26 path-scoped files) and the per-turn skill descriptions (15,085 chars over 73 skills); then WO-5, WO-6 and WO-8. The pilot writes each order; it does not execute them.
5. Operator rules the release artifact's shape (a separate rung with its own closeout) under civil rule; it is booked in the contract's civil-rule list and is not pilot execution.

## Pending Work / Open Loops

- OBPI-0.35.0-17 and -20: executed, `Draft` in the ledger, awaiting the operator's Gate 5 attestation.
- GHI #1244 open until the operator enters safe mode through the verb; then close `fixed`.
- WO-4 rulings; WO-5, WO-6, WO-8 unassigned; the rules and skill-description cuts not yet written as orders.
- Carried from the anchor: the four slice-size findings and the Decomposition Matrix re-cut; GHI #1230 to #1241 routing; the tracker for the 27 helper-or-loop gates.
- Exit conditions 4 to 7 of the contract not met; 1 to 3 met.

## Verification Checklist

- `git log --oneline -8` shows `5e86df8cf`, `e0dab8ee4`, `85535ddba`, `ac3b0005e`, `2fc0ba206`, `d2a427f0f`, `5c6e9a493`, `31576beba` on main, synced.
- `uv run gz validate --instructions-files-budget` exits 0 with no `WARNING instructions-files-budget` line.
- `uv run -m unittest tests.mx.test_marker tests.mx.test_checkpoint tests.hooks.test_mx_awareness tests.commands.test_mx_enter tests.commands.test_mx_exit` passes.
- `uv run gz mx enter --help` lists `--mode {mx,safe}` and `--contract PATH`.
- `uv run gz test` passes the full tier (11,889 tests at `31576beba`).
- `gh issue view 1243 --json state` is CLOSED; `gh issue view 1244 --json state` is OPEN until step 1.

## Evidence / Artifacts

- `docs/governance/harbor-pilotage-candidate-2026-10-15.md` (contract, civil-rule items, passage log, exit conditions)
- `src/gzkit/mx/marker.py`, `src/gzkit/mx/checkpoint.py`, `src/gzkit/mx/awareness.py`, `src/gzkit/commands/mx_cmd.py` (safe mode)
- `.gzkit/rules/mx-mode.md`, `.gzkit/skills/gz-mx/SKILL.md`, `docs/user/manpages/mx-enter.md`
- `data/instructions_files_budget.json`, `docs/governance/instructions-files-budget-history.md`, `docs/governance/agents-md-doctrine.md`
- `.gzkit/chores/instructions-files-diet/proofs/recommendation-2026-10-15.md`, `.gzkit/chores/instructions-files-diet/proofs/CHORE-LOG.md`
- `src/gzkit/content/retention.py`, `src/gzkit/governance/pipeline_control_inventory.py`, `src/gzkit/commit_witness.py`
- `.gzkit/insights/agent-insights.jsonl` (the day's rulings and corrections)

## Settled Rulings

1546 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
