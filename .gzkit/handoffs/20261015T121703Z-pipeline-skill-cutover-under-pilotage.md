---
mode: CREATE
adr_id: ADR-0.35.0-canon-entry-corpus-landing
branch: main
timestamp: '2026-10-15T12:17:03Z'
agent: claude-code
obpi_id: OBPI-0.35.0-20-pipeline-skill-cutover
session_id: 4fd13b45-724e-4433-ab23-fd6c5df2b932
continues_from:
- .gzkit/handoffs/20261015T002823Z-slice-size-survey-no-obpi-work.md
- .gzkit/handoffs/20261015T053609Z-session-exit-bookmark.md
- .gzkit/handoffs/20261015T054557Z-session-exit-bookmark.md
- .gzkit/handoffs/20261015T084754Z-session-exit-bookmark.md
---

## Current State Summary

Session under the ratified harbor-pilotage contract (`docs/governance/harbor-pilotage-candidate-2026-10-15.md`), martial law in force by the operator's word. Landed on main, in order: the orientation campaign block cut to pointers (GHI #1242, `99acdc8a0`); the pipeline control inventory checker and skeleton (`8306625ad`), the inventory mapped over all 471 blocks (`9451ed057` to `6c403c912`), attested by the operator ("attest the inventory, keep going with the load cuts"); OBPI-0.35.0-17's serving, one pinned procedure file per stage printed at every stage entry (`fbe298c26`); OBPI-0.35.0-20's cutover, the skill body reduced to the invocation text with the stage files and the rationale record rendered from the inventory (`d47de23c8`, "nothing was compressed"); a direct repair so the commit witness counts a behave step module as test code (`4e424fa2b`); passage-log rows for each act (`b230b3e04`, `871482f85`). Last action: the passage-log commit succeeded; the ledger and insights changes from the witness runs are uncommitted until the git-sync that follows this handoff. Measured: skill file 125,923 B to 11,445 B; at Stage 4 entry 55,611 B loaded instead of 181,212 B under brief 17 alone; `gz check` green on every commit; cutover witness 55 killed, 0 survived, 36 inconclusive; fix witness driven.

## Important Context

- Martial law is a temporary arrangement under the contract's § Exit; Gate 5 was never suspended. Briefs 17 and 20 are executed but remain `Draft` in the ledger: their completion needs the operator's attestation through `gz obpi complete`, which the pilot cannot give.
- The cutover deviates from brief 20 in four disclosed ways, listed in the passage-log row of `871482f85`: run outside the OBPI pipeline and before 17's ledger completion (Requirements 2 and 10); the renderer `src/gzkit/governance/pipeline_procedure_render.py` and its test module sit outside the brief's Allowed Paths; one non-control row of the attested inventory was reclassified from `rationale` to `structure` (the Stage 1-2 block's citation of invariant 11, kept because attested REQ-0.0.19-04-06 requires it); a `git reset --hard` discarded two uncommitted red receipts for SHAs the rewrite retired (insight recorded, both witnesses re-run).
- The five stage files under `.gzkit/skills/gz-obpi-pipeline/references/` are derived views of `data/obpi_pipeline_control_inventory.json`: never hand-edit them; `tests/governance/test_pipeline_procedure_render.py` holds them to the render and `src/gzkit/pipeline_procedure.py` pins their digests. The skill body is canon and is held to the controls by the checker, not to the render.
- The inventory's baseline (commit `072317673`, skill 6.67.0) is read from git history by the before-state tests; a shallow clone skips them.
- Every reader of the old skill body now reads the delivered whole (body plus stage files): `tests/test_obpi_skill_migration.py`, `tests/skills/test_skill_surface_sync_justify.py`, `tests/governance/test_skill_self_close_drift.py`, `tests/governance/test_agent_contract_fold.py`, and `data/mandated_tier1_dispatch.json` points at the Stage 4 file.
- The commit witness (`src/gzkit/commit_witness.py`) now treats `features/` as test code; before the fix any commit carrying Gate 4 scenarios read `undriven`.
- Skill 6.69.0; the skill-body grandfather entry for `gz-obpi-pipeline` is removed (238 lines, contract 300).

## Decisions Made

- [operator-ruled] Martial law entered: verbatim "I basically want a VERY POWERFUL model to take over, like a harbor pilot, and bring me into port. we can then resume gzkit's normal ceremony. BOOK THAT MODEL NOW." and "this is a TEMPORARY ARRANGEMENT until we get to port and dry dock."
- [operator-ruled] The contract and its exit: verbatim "contract for entering and exiting martial law so I can resume, using the redesign, back towards the magna carta." and "ratify the contract, draft the three catalog shapes".
- [operator-ruled] Scope of the pilot's authority: verbatim "in the meantime, you can take control of everything. I think the ledger writing still matters, but let's talk about that." and "If you need to override to do lots of hand-authoring, that's part of what martial law means. I'll leave it up to you."
- [operator-ruled] The control plane is in the mandate: verbatim "take charge of the control plane, take charge of a lot of things, and get them back on the right track until we can stabilize in the new model and resume the Magna Carta. So control plane and control surface misalignment and overinflation are also problems right now."
- [operator-ruled] Planning in Fable, not all execution: verbatim "I wanted to PLAN in Fable, but not do all the work in fable."
- [operator-ruled] REQ primacy: verbatim "REQ is the value we want, task is what to do to get it - so intention is in the REQ, design exists within the REQ" and "i never said that a REQ is a single value".
- [operator-ruled] The unit of work may be named WP: verbatim "if WP- fits better, then that is fine"; the AirlineOps remark was an observation, verbatim "i am not asking you to readopt that airlineops model, i am just pointing out the observation".
- [operator-ruled] The inventory gate: verbatim "attest the inventory, keep going with the load cuts".
- [agent-chose] Executed brief 20's cutover as pilot work under Mandate 1 and 5 without the OBPI pipeline run and before 17's ledger completion; the ledger completion of both briefs is left to the operator's attestation. **Rationale:** the contract suspends initiation, not Gate 5. **Alternatives rejected:** waiting for 17's attestation before any cut (the directive was to keep going).
- [agent-chose] Made the served set a function of the inventory through a production renderer with a real-tree byte-equality test, rather than a scratchpad script. **Rationale:** reproducibility; the stage files become derived views.
- [agent-chose] Reclassified one inventory non-control row (invariant-11 citation) from rationale to structure instead of editing the attested REQ's test. **Rationale:** `docs/governance/attested-req-subject-retirement.md` repairs the surface so the REQ stays true.
- [agent-chose] Repaired the commit witness's `features/` blind spot as a direct fix in its own commit. **Rationale:** small, one surface, in flight, two tests observed red.
- [agent-chose] Landed brief 17's Gate 4 scenarios in the cutover commit. **Rationale:** they drive the real launcher against the cut-over files.

## Immediate Next Steps

1. Present the two passage-log rows of `871482f85` to the operator and take rulings on disclosures (a) to (d) of the cutover row.
2. On the operator's word, record the completion of OBPI-0.35.0-17 and OBPI-0.35.0-20 with their attestation text (`uv run gz obpi complete`), naming the reclassified inventory row; both briefs are `Draft` in the ledger today.
3. Continue the load cuts in the contract's work orders: WO-2 the AGENTS.md diet (operator consult at its step 4), the per-turn skill descriptions, the rules narrative lift; then WO-5, WO-6 and WO-8.
4. Take the operator's rulings on WO-4, the three catalog shapes (id grammar, home, assignment channel), and on the slice-size findings the anchor handoff carried.
5. Re-read the contract's § Exit against the witnesses and report which conditions are met.

## Pending Work / Open Loops

- OBPI-0.35.0-17 and OBPI-0.35.0-20: executed, not completed in the ledger; awaiting the operator's Gate 5 attestation.
- Carried from the anchor handoff, still unruled: the four slice-size findings (extract_plan_tasks dispatching alternatives; dispatch on plan prose rather than the TASK; `gz arb red` not separating a weak test from a new symbol; nothing bounding a BEHAVIOR REQ) and the Decomposition Matrix re-cut; GHI #1230 to #1241 routing; the tracker for the 27 helper-or-loop gates.
- WO-2, WO-4 (rulings), WO-5, WO-6, WO-8 open under the contract.
- The three session-exit bookmarks since the anchor are folded here and superseded.

## Verification Checklist

- `git log --oneline -6` shows `871482f85`, `4e424fa2b`, `d47de23c8` on main, synced.
- `uv run -m unittest tests.governance.test_pipeline_procedure_render tests.governance.test_pipeline_control_inventory tests.test_pipeline_procedure` passes (the real-tree tests hold the stage files to the render and the checker to zero violations).
- `uv run -m behave features/obpi_pipeline_stage_procedure.feature` passes 5 scenarios.
- `uv run gz validate --distribution` and `uv run gz skill audit` report no finding for `gz-obpi-pipeline`.
- `uv run gz check` passes on a fully staged tree.
- Ledger holds `red_commit_receipt_emitted` for `d47de23c85a4` (inconclusive, 0 survived) and `4e424fa2ba52` (driven).

## Evidence / Artifacts

- `docs/governance/harbor-pilotage-candidate-2026-10-15.md` (contract and passage log)
- `data/obpi_pipeline_control_inventory.json` (attested inventory, one row reclassified)
- `src/gzkit/governance/pipeline_procedure_render.py` and `tests/governance/test_pipeline_procedure_render.py`
- `src/gzkit/pipeline_procedure.py` (resolver and pins)
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` and `.gzkit/skills/gz-obpi-pipeline/references/stage-4-present-evidence.md`
- `docs/governance/obpi-pipeline-control-rationale.md` (rationale record)
- `features/obpi_pipeline_stage_procedure.feature` and `features/steps/obpi_pipeline_stage_procedure_steps.py`
- `src/gzkit/commit_witness.py` and `tests/test_commit_witness.py`
- `docs/user/manpages/obpi-pipeline.md`, `docs/user/manpages/arb-red.md`

## Settled Rulings

1542 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
