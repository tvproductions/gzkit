---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-19T00:43:06Z'
agent: claude-code
continues_from: .gzkit/handoffs/20260918T112540Z-diet-close-parallel-everywhere-and-next-pass.md
---

## Current State Summary

Third handoff of 2026-09-18, continuing the control-surface diet thread (GHI #921). State at writing: `main` level with `origin/main`, tree clean apart from this handoff and one preserved proposal file, no OBPI locks, no pipeline, no open TASK, no pending Gate 5.

Since the predecessor the session opened diet pass two on the operator's prized skill, `gz-obpi-pipeline`, and the pass changed character: a full read (1,671 lines) showed a byte diet is the wrong frame for it, and found a looping defect in Stage 4 instead.

What landed: `6b440453e` — GHI #1028, skill 6.59.0. Stage 4 now has a map; "The pass condition — stated once" (a lead deferring to `gz obpi acceptance <OBPI> status --stage stage4`, with the seven existing statements gathered VERBATIM beneath it); "The review window, the bound, and the exit" (finish every edit, prove every obligation, refresh and replay the packet, record the revision, dispatch, edit nothing until the review is imported; one batched repair round per set of findings; two follow-up rounds, then `gz obpi block`). § The Iron Law names that second legitimate stop. Step 4b dispatches through the Codex plugin's `task --write` path everywhere, including the completion gate's recovery message in `src/gzkit/commands/obpi_complete_adversarial.py`. 443 of Stage 4's 461 non-blank lines were moved byte-identical; none of the operator's wording was reworded. Skill size went 122,302 B to 125,656 B: this was not a trim.

What was found and filed, not fixed: GHI #1029. Acceptance proof and review currency is ONE digest over the whole audited population (`src/`, `tests/`, `features/`, `data/`, `scripts/`, rules, schemas, workflows, config, plus the brief contract; `src/gzkit/acceptance_execution.py` `input_digest`, `src/gzkit/acceptance.py` `_proof_blockers`). Any edit stales every proof and every imported review for the OBPI. That is the mechanical cause of the 4a/4b loop the operator reported; the skill-side change makes a round cheap, bounded and honest about it, and cannot remove it.

Measured, for the record: Stage 4 grew 13,851 B (2026-07-15) to 44,437 B (2026-09-18) with emphasis tokens nearly flat (46 to 51) and cited GHIs 5 to 15; pipeline launches per OBPI about 1.2 in July against 4, 2, 4, 2, 3, 6, 1 under ADR-0.35.0; `acceptance_recorded` shows 74 proof and 9 review records on OBPI-0.35.0-05, 83 and 19 on OBPI-0.35.0-06, the latter ending in a tier-3 human review.

Parked, awaiting the operator: a 17-passage proposal for the REST of the pipeline skill (5 fixes of stale pointers, 12 lifts of dated history to a new `references/history.md`, 3,362 B saved), preserved at `.gzkit/chores/instructions-files-diet/proofs/pipeline-skill-trim-proposal-2026-09-18.md`. Its line numbers are against skill 6.58.0; six of its passages sit inside Stage 4, whose text is unchanged but whose lines moved by about 52 in 6.59.0. Rebuild it from the live file before presenting it again.

The two items the prior handoff carried with care are unchanged and still the operator's: root `AGENTS.md` is 19,872 B against a 15,000 destination and needs either OBPI-0.35.0-10 or an ADR-0.0.33 Invariant 1 ruling; and the unaudited material is every rule at or under about 8 KB plus 71 of 72 skill bodies.

## Important Context

- The pipeline skill is the operator's gold standard (verbatim: "BE VERY, VERY, VERY careful with the pipeline, it is a PRIZED skill, it was my gold standard among my skills"). The method that earned a ruling: build every candidate in scratch from exact line ranges of the live file so moved text is byte-identical, account for every original line, check every test-bound string and both section titles `data/mandated_tier1_dispatch.json` cites by name ("THE PLUGIN IS THE ONLY TIER-1 DISPATCH SURFACE", "THE REVIEWER REPLAYS IN A DISPOSABLE WRITABLE CHECKOUT"), and show the operator a generated before/after file. Do not retype the skill's prose.
- Determinism is not the problem and must be kept: fixed stage order, exact commands, mandatory templates, runtime-derived readiness. What conflicts with current model guidance is emphasis used as the forcing mechanism, a persistence mandate with no exit, and one condition restated many times (`docs/governance/opus-tuning.md`: system prompts "that emphasize sustained persistence" amplify unbounded persistence). The skill's "why this gate exists" paragraphs are steering, not history: leave them.
- Tests bound to the pipeline skill: `tests/skills/test_skill_surface_sync_justify.py` (REQ-0.0.19-04-06, amended 2026-09-18), `tests/governance/test_skill_self_close_drift.py` (needs the phrase dead-letter; REQ-0.0.36-05-06), `tests/test_obpi_skill_migration.py` (the three `gz obpi` verbs), `tests/governance/test_agent_contract_fold.py` (needs "Stage 5"), `tests/test_adversarial_validation_gate.py` (recovery message), `tests/governance/test_mandated_tier1_dispatch.py`.
- The agent may edit the pipeline skill and may never run it: only the operator initiates OBPI work.
- GHI #1028 is deliberately OPEN. Its exit condition is a measurement on the next operator-initiated OBPI, not the text landing.
- ADR-0.36.0's Draft briefs read Step 4b as the model for the critic's resolution flow and are fenced from editing it. They were not re-read against the new Stage 4 layout.
- The verifier-pipe-gate hook refuses any verifier that is piped or not the last statement; `ruff`, `coverage` and `gz arb` count. Pattern: `cmd > log 2>&1; echo "REAL EXIT: $?"`.
- Workflow fronts (source: `docs/governance/build-to-1.0-campaign-2026-08-16.md` § Workflow fronts). Handoff system: this document and its two same-day predecessors. GHI triage: this thread leaves #921, #943, #1019, #1023, #1028, #1029 open; the wider queue was not inspected. ADR/OBPI campaign: ADR-0.35.0 TOPMOST and Draft, no locks; both #1028 and #1029 bear on how its remaining OBPIs will run; not freshly inspected with `gz adr status`. New R&D: untouched; #1029 is a candidate if the operator wants the design explored before an OBPI.

## Decisions Made

- [operator-ruled] Open diet pass two on `gz-obpi-pipeline` with full before and after, under extreme care (verbatim: "start diet pass two with gz-obpi-pipeline, show full before/after - BE VERY, VERY, VERY careful with the pipeline, it is a PRIZED skill, it was my gold standard among my skills.").
- [operator-ruled] File the Stage 4 issue and draft the consolidation (verbatim: "file the GHI and draft the Stage 4 consolidation"). Filed as GHI #1028.
- [operator-ruled] Stage 4 round bound, dispatch surface, draft disposition and the digest, in one ruling (verbatim: "N=2, D1 A, draft A, file a GHI for the digest"). N=2 is two focused follow-up rounds after the first Step 4b round; D1 A makes the plugin's `task --write` path the Step 4b dispatch; draft A landed the consolidation as shown; the digest is GHI #1029.
- [agent-chose] Advised that a byte diet is the wrong frame for the pipeline skill and recommended holding the 17-passage trim; the operator did not rule on that proposal, so it is parked, not declined.
- [agent-chose] Consolidated by MOVING the seven pass-condition statements verbatim under one heading rather than rewriting them into one paragraph; a tightened single statement was not drafted.
- [agent-chose] Left GHI #1028 open after landing, because its exit condition is an observed comparison on the next OBPI.
- [agent-chose] Filed GHI #1029 as a design question with three candidate shapes and chose none; nothing was proposed for landing.
- [agent-chose] Struck the Stage 4 instruction to record the narrator dispatch through `SubagentDispatchRecord`, which accepts Stage-2 roles only and whose promised validator belongs to a superseded pool ADR.

## Immediate Next Steps

1. Present these steps to the operator and wait for a ruling; none is authorized by this document.
2. Ask whether GHI #1029 (whole-tree acceptance digest) should be explored as an R&D run or taken toward an OBPI under a named ADR; until it is decided, every OBPI run pays a full re-prove and re-review per repair round.
3. When the operator next initiates an OBPI, record its `pipeline_launched`, proof-record and review-record counts on GHI #1028 against the ADR-0.35.0 figures, and close or amend #1028 on that evidence.
4. Ask for a ruling on the parked 17-passage pipeline proposal (land, fixes only, or drop) and on D3, the plan-audit receipt filename named two ways in the skill; rebuild the proposal from skill 6.59.0 first.
5. Ask for the `AGENTS.md` ruling carried from the prior handoff: initiate OBPI-0.35.0-10, or rule on ADR-0.0.33 Invariant 1.

## Pending Work / Open Loops

- GHI #1028 open by design (measurement owed). GHI #1029 open (design decision owed). GHI #921 open as the diet umbrella. GHI #943 (paired Opus and Fable evaluation set), GHI #1019 (GPT-6 Astra card), GHI #1023 (a `gz` verb for BDD) open and unselected.
- Pipeline skill, noticed and not changed: Stage 1's numbered list skips step 4; D3 (Stage 1 step 1 reads `.plan-audit-receipt.json` while § The Plan-Mode Gate names the per-OBPI form; the code carries both); the Completion Contract's step numbers and the Error Recovery "enter plan mode" row are wrong and sit in the parked proposal as F3 and F4; three "Behavior Rules — Always #N" citations no longer resolve (F6).
- The rest of diet pass two is not started: `ghi-close` 46,465 B, `gz-session-handoff` 42,238 B, `ghi-author` 31,152 B, `gz-adr-closeout-ceremony` 27,240 B, and the rules at or under about 8 KB, `pythonic.md` first. Expect the pipeline lesson to repeat: read for contradictions before counting bytes, and grep tests for `@covers` REQs first.
- `docs/governance/attested-req-subject-retirement.md` still says no instance exists of a REQ literally asserting retired doctrine; GHI #1025 [settled] was one. Wants the operator's wording.
- ADR-0.36.0 Draft briefs not re-read against the new Stage 4 layout.
- Re-measure per-turn and on-edit loads after GHI #1021 [settled] and write a new proof beside `post-trim-2026-09-18.txt`; still not done.

## Verification Checklist

- `git rev-list --left-right --count origin/main...HEAD` prints `0	0` and `git status --short` prints nothing.
- `grep -n "skill-version" .gzkit/skills/gz-obpi-pipeline/SKILL.md` shows 6.59.0, and `grep -c "^#### The pass condition\|^#### The review window" .gzkit/skills/gz-obpi-pipeline/SKILL.md` prints 2.
- `grep -c "adversarial-review" src/gzkit/commands/obpi_complete_adversarial.py` prints 0.
- `uv run -m unittest tests.test_adversarial_validation_gate tests.governance.test_mandated_tier1_dispatch tests.skills.test_skill_surface_sync_justify tests.governance.test_skill_self_close_drift tests.test_obpi_skill_migration tests.governance.test_agent_contract_fold > out.log 2>&1; echo "REAL EXIT: $?"` exits 0 (112 tests).
- `gh issue list --state open --search "1028 OR 1029"` shows both open.
- `uv run gz check > out.log 2>&1; echo "REAL EXIT: $?"` exits 0 on a clean tree.

## Evidence / Artifacts

- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` (6.59.0; Stage 4 as landed)
- `.gzkit/chores/instructions-files-diet/proofs/pipeline-skill-trim-proposal-2026-09-18.md` (the parked 17-passage proposal, full before and after, against 6.58.0)
- `src/gzkit/acceptance_execution.py` and `src/gzkit/acceptance.py` (the whole-tree digest and the staleness check)
- `src/gzkit/commands/obpi_complete_adversarial.py` and `tests/test_adversarial_validation_gate.py` (recovery message and its re-derived tests)
- `data/mandated_tier1_dispatch.json` (cites two Stage 4 section titles by name; unchanged)
- `docs/governance/acceptance-obligations.md` and `docs/governance/opus-tuning.md`
- `.gzkit/chores/instructions-files-diet/proofs/CHORE-LOG.md`

## Settled Rulings

925 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
