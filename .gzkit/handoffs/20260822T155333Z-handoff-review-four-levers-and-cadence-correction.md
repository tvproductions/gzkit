---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-22T15:53:33Z'
agent: claude-code
session_id: a03b052d-1b15-47c7-b7a3-ac1c15d408fa
continues_from: 20260822T142817Z-cycle-time-levers-and-ruling-store.md
---

## Current State Summary

Handoff review session. Tree clean, origin/main in sync at 6b2a1c67 (0 0), no locks, no hangar open. Four of five advised steps from the resumed handoff are discharged; step 5 (ADR-0.35.0) is untouched and is the whole remaining subject.

Landed: 78823e4b booked the orphaned session-exit bookmark; 63ce179a named all seven new-CLI-verb coupled obligations in one authority (GHI #854); 6b2a1c67 named both MX floor opt-in mechanisms and recorded the Stage-2 fence ruling (GHI #855). Decisions posted without code: the ratchet raise-direction question on GHI #853, and the cycle-time measurement on GHI #856 / #835.

THE SESSION FAILED ON CADENCE, NOT ON WORK. The operator asked "are you waiting on me?", "are you done?", "say which what?", "what decision?" and "what are you even investigating?" -- five corrections, all the same defect: announcing work instead of doing it, and escalating a one-line change into a blocking question asked three times. Read that as the first-order lesson of this handoff.

## Important Context

STEP 5 IS THE ONLY REMAINING WORK AND IT IS NOT A TAIL-END ITEM. ADR-0.35.0-canon-entry-corpus-landing is heavy lane, Pending, closeout BLOCKED, with one brief landed and the rest outstanding -- run `uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` for the live figure; no count is transcribed here. It is the lowest-semver feature ADR holding unlanded work, so ascending-semver canon puts it ahead of ADR-0.36.0 and ADR-0.37.0. It has now been set aside in three consecutive rulings (11:46, 13:30, and this session by deferral). The gz-obpi-pipeline skill is MANDATORY for it -- operator verbatim: "you are NEVER to work on an obpi without runnung the skill".

THE MEASUREMENT THAT INVERTED STEP 3. The advised remedy for the module-size ratchet was a fence diffing the entry against git history. It is not needed. fc3f0956 raised validate_cmd 1242 -> 1309 while the module stayed at 1242, so the raise landed as SLACK, and total slack moved 861 -> 928, exactly the 67 lines raised. GHI #853s unbuilt slack arm already catches the raise direction with no git history. Residual disclosed: a raise landed in the SAME COMMIT as a growth that exactly consumes it evades both arms.

THE MEASUREMENT THAT INVERTED STEP 2. The suite is not the bottleneck and parallelism is not missing -- it landed in GHI #512 and gz check has always used it. Measured 2026-08-22 at 6b2a1c67, same 8677 tests, both OK: unittest-parallel 42.11s versus uv run -m unittest -q 128.55s, 3.05x. The SLOW one is CANONICAL_STEP_COMMANDS["unittest"], which AGENTS.md § Attestation locks as the command proving "Tests pass". The figures in .gzkit/rules/tests.md (268.1s / 71.4s) are STALE against this tree.

THE STEP-4 RECOMMENDATION WAS NARROWED BY EVIDENCE THAT ALREADY EXISTED. The floor-pin question was recommended before reading GHI #852, closed the same day in this sessions own commit chain. 84519da5 had already settled it: pin by LEVEL, not by NAME, because registering a narrower proxy under the floor name is forbidden by ADR-0.0.74 § Consequences/Negative #7 and NAME is a BI#3 one-way door. Recorded as an improvement insight. The substance never moved -- "never demotes" was right throughout -- only the target of the prose fix.

## Decisions Made

- [operator-ruled] Proceed on advised steps 1, 2, 3 and 5 (verbatim selection: "1, 2, 3 and 5"). Booked via gz handoff decide, session a03b052d.
- [operator-ruled] The Stage-2 production-code fence NEVER demotes inside an open hangar, and the residual is fixed as vocabulary (verbatim: "Never demotes - fix vocabulary"). Carried unresolved across three prior sessions; discharged in 6b2a1c67 as documentation, with NO code change, because post-authoring-src-commits already survives by emitting CRITICAL.
- [operator-corrected] Announcing work instead of doing it is the defect, not a courtesy ("are you waiting on me?", "are you done?"). Twice in one session.
- [operator-corrected] Narrating a narrowing as a reversal reads as flip-flopping ("this is all you do is flip flop around"). Say narrowed when it is narrowed; read the closing commit body of any recent GHI before recommending on what it touched.
- [operator-corrected] A question buried in prose is not a question ("say which what?", "what decision?"). Asking three times about 86 seconds was over-escalation of a filed GHI that needed no ruling to sit open.
- [agent-chose] Scored GHI #854s scorecard row 86 Promotable, not Mechanical. Each of the seven obligations has an arm, but nothing witnesses that the rules prose list matches the enforced set -- which is the drift being repaired. gz validate --advisory-scorecard refused the Mechanical score; the fence was right.
- [agent-chose] Scored GHI #855s row 62e Judgment. Whether a guard covers its floor concern IN FULL or only a slice is not a property any surface models; grading it would be shape-graded-not-substance.
- [agent-chose] Did NOT swap CANONICAL_STEP_COMMANDS["unittest"] to the parallel invocation. It redefines what a Gate-5 tests-pass receipt means, and one clean run is not proof of order-independence. Left as the open question on #856.

## Immediate Next Steps

1. Resume ADR-0.35.0-canon-entry-corpus-landing through the gz-obpi-pipeline skill. The only remaining advised step, semver-topmost, deferred three sessions. Start with the lowest-numbered pending brief; run uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing for live lifecycle rather than trusting any count transcribed here. Budget it a fresh session -- heavy lane, most briefs still outstanding.
2. Rule on GHI #856: is unittest-parallel acceptable as ATTESTATION evidence, or only as a gate accelerator? If yes it is a one-line change to CANONICAL_STEP_COMMANDS plus a RETIRED_STEP_COMMANDS row (the mechanism exists and keeps prior receipts valid), worth 86s on the most-repeated command in the loop. If the answer should be evidence-led, run the serial suite several times in randomized order first; a real ordering dependence would be worth more than the 86 seconds.
3. Build both arms of the module-size ratchet gate under GHI #853 -- slack (an entry looser than its module; 928 lines re-consumable today) and raise, which slack subsumes. Keep the operator raise available: recorded-and-visible, never blocked.
4. GHI #835 -- roughly 46 serial validator steps, about 55s, the largest single bucket in gz check and a real build rather than a one-liner.

## Pending Work / Open Loops

GHI #853 -- open. Module-size ratchet has no arm reporting an entry looser than its module. Now measured at 928 lines of unrecorded slack across four entries (parser_artifacts 666, obpi_complete 127, parser_maintenance 68, validate_cmd 67); was 861 when filed. The raise-direction decision is posted in its comments.

GHI #856 -- open, filed this session, BLOCKED on an operator ruling. The canonical attestation test command is 3.05x slower than the one every gate runs. Body carries the measurement and the order-independence question.

GHI #835 -- open, cross-linked to #856 this session. Its measurements finally reached the issue; they had lived only in the db6ec623 and 4b543052 commit bodies across four handoffs.

GHI #849 (ARB RED witness inert on landed work) and GHI #611 (no general append-only corrective-action primitive) -- both open, both carried unchanged across five handoffs, both untouched again.

Two advisory findings gz check reports and this session did not address, both pre-existing: AGENTS.md renders 42235 B against the codex 32768 B delivery cap, with operator-doctrine-verbatim-canon straddling it and architectural-boundaries starting past it, so undelivered canon is not in force; and 715 REQs carry no covering test.

adr_audit.py remains at 1034 == 1034 -- zero headroom, untouched because nothing is trying to add a line there.

## Verification Checklist

uv run gz check  # expect: exit 0, All checks passed
uv run gz validate --advisory-scorecard  # expect: exit 0 (rows 86 and 62e scored)
uv run gz validate --bullet-retention  # expect: exit 0
uv run python -c "from radon.raw import analyze; import pathlib,json; d=json.loads(pathlib.Path(\"data/module_size_grandfather.json\").read_text()); print(sum(max(0,e[\"sloc_at_cutover\"]-analyze(pathlib.Path(e[\"path\"]).read_text(encoding=\"utf-8\")).sloc) for e in d[\"grandfathered_modules\"]))"  # expect: 928
git rev-list --left-right --count origin/main...HEAD  # expect: 0 0
uv run gz obpi lock list  # expect: No active locks
uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing  # expect: heavy lane, Pending, closeout BLOCKED; read the landed count from the output, never from this line

## Evidence / Artifacts

.gzkit/rules/cli.md -- § Adding CLI Features now carries all seven obligations; § Command shape gains the scored bullet; § Consistency stops restating a subset
.gzkit/rules/tool-skill-runbook-alignment.md -- § When to apply points at the one authority instead of naming one obligation
.gzkit/rules/mx-mode.md -- new § Opting a guard into the floor: two mechanisms, default to LEVEL, Stage-2 fence pin recorded permanent
docs/governance/advisory-rules-audit.md -- row 86 (Promotable) and row 62e (Judgment) added; three Coverage Ledger versions bumped
.gzkit/insights/agent-insights.jsonl -- improvement record on recommendation sequencing
63ce179a, 6b2a1c67, 78823e4b -- the three commits this session pushed
84519da5 -- GHI #852s fix, the precedent that narrowed the step-4 remedy
.gzkit/handoffs/20260822T142817Z-cycle-time-levers-and-ruling-store.md -- the resumed handoff this one supersedes

## Settled Rulings

468 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
