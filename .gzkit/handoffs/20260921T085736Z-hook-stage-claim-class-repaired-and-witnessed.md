---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-21T08:57:36Z'
agent: claude-code
session_id: 0e453148-0bd7-4dc9-a6a5-0dd4c62017d1
continues_from: .gzkit/handoffs/20260921T073259Z-ledger-ts-ordering-pair-closed.md
---

## Current State Summary

Resumed the fresh handoff `20260921T073259Z-ledger-ts-ordering-pair-closed.md` under the Claim Verification Gate. Two of its four advised steps were ruled on and both are discharged; two remain unruled and untouched. The gate found advised step 3 VOID at read-time: its premise that ADR-0.39.0's interview had "7 of 19 fields outstanding" was false, all 19 fields having been filled and committed at `1f1207e5f` on 2026-09-20, and three of the named fields already sat in the ruling corpus as booked rulings. That void is booked as a `--set-aside` on a `handoff_resume_decided` record rather than left to decay through another successor. Advised step 4's subject was a real defect and is repaired: four governed surfaces told agents the pre-commit hook runs `unittest` on every commit, when the hook is declared `stages: [manual]` and fires at neither commit nor push. Landed at `d98b520f3` together with a mechanical witness that pins the class. HEAD is `d98b520f3`, level with origin/main, clean tree, `gz check` green at real exit 0.

## Important Context

WHY THE REPAIR WENT WIDER THAN THE TWO ROWS NAMED. The operator pointed at one false sentence in the git-sync skill. The same sentence was live in three more governed surfaces, so it was repaired as a class: `git-sync` (1.4.0 to 1.4.1), `gz-session-handoff` (7.6.0 to 7.6.1, its own Trust Model parenthetical), `gz-obpi-pipeline` (6.59.1 to 6.59.2) and the adopter template. The pipeline instance is the one that mattered most and the one a grep for the shipped sentence had missed: there the false premise was load-bearing, carrying the Stage 3 scope-discipline rationale that "the full unittest suite isn't bypassed". The safety net is real but sits at the pre-push `gz check`, not at commit. The adopter template was wrong in a second way as well: gzkit ships NO `.pre-commit-config.yaml`, so that copy stated gzkit's own hook roster as fact to adopters who never receive it.

TWO MECHANICAL CONSTRAINTS SHAPED THE WORK AND WILL SHAPE THE NEXT EDIT THERE. First, `.gzkit/skills/gz-obpi-pipeline/SKILL.md` is AT its grandfathered body ceiling of 1710 lines; a six-line correction was refused outright by the sync post-check, and the text was compressed to the original's three lines rather than the file being grown or material extracted. The next correction in that skill has to buy its space from something else. Second, the tautological-test audit refused the witness's first draft because filesystem ops co-occurred with assertions inside test bodies; the reads were hoisted into a module-level helper rather than a file waiver being taken, since a waiver would have ratcheted measured debt to buy one new test a pass.

WHY THE SECOND FINDING WAS ROUTED AND NOT BUILT. `src/gzkit/commands/reference_checker.py` lines 49 to 53 document the ADR/OBPI `UNKNOWN` verdict as a DELIBERATE state-doctrine refusal, on the ground that `adr-status.md` is a Layer-3 derived view. That rationale is right about the index and wrong that it is the only repo-local surface: `_derive_obpi_runtime_state` in `src/gzkit/ledger_semantics.py` derives OBPI state from the ledger, which is Layer 2, and `gz obpi status` already consumes it. Editing that docstring silently would be exactly the doctrine drift AGENTS.md forbids, so the finding became GHI #1076 and the issue is the recorded witness that makes the change available.

A CAUSATION CLAIM MADE EARLY IN THE SESSION WAS WRONG AND IS CORRECTED IN THE ISSUE BODY. The ADR/OBPI resolution gap would NOT have caught the stale ADR-0.39.0 claim. ADR-0.39.0 is `Pending`, so a working resolver returns LIVE, and `NextStep.cites_settled` fires only on SETTLED; the step would still have rendered clean. The falsehood was in prose detail, not in the cited artifact's lifecycle state. GHI #1076 says so explicitly so that nobody builds it expecting that protection.

FRONT DELTAS, against the standing map in the registered campaign. handoff system: heavy activity. The resume gate was exercised end to end, one advised step was found void and booked as set aside, the skill's own false parenthetical was repaired, and a gap in the gate itself was filed as #1076. ghi triage: the open queue moved 56 to 57; one filed, none closed. adr/obpi campaign: untouched. No OBPI initiated, no ADR authored. ADR-0.39.0 was READ and measured only: interview complete at 19 of 19 fields, seven briefs all `Draft`, 0 of 7 done, closeout BLOCKED. new R&D: untouched.

## Decisions Made

- [operator-ruled] Fix both rows the resume gate surfaced (verbatim: "fix these") — the stale ADR-0.39.0 interview claim and the git-sync skill's assertion that the pre-commit hook runs unittest.
- [operator-ruled] Solve both findings the repair had routed rather than leaving them merely recorded as insights (verbatim: "solve").
- [operator-ruled] Sync the session's work (verbatim: "git-sync").
- [agent-chose] Repaired the unittest claim as a CLASS across four governed surfaces and the adopter template, not only the one row the operator pointed at, on DO IT RIGHT 1. The widening found the pipeline instance, which a grep for the shipped sentence had missed.
- [agent-chose] Booked the resume ruling as `proceed` with ONLY advised step 3 set aside, and stated plainly that steps 1 and 2 were never ruled, rather than letting a blanket `proceed` imply authorization the operator never gave.
- [agent-chose] Compressed the gz-obpi-pipeline correction to the original's three lines rather than growing the file or extracting material, the skill being at its 1710-line body ceiling.
- [agent-chose] Hoisted the witness's filesystem reads into a module-level helper to satisfy the tautological-test audit, rather than taking a file waiver that would have ratcheted measured debt to buy one new test a pass.
- [agent-chose] Routed the ADR/OBPI resolution gap to GHI #1076 instead of building it, because reference_checker.py documents the UNKNOWN as deliberate state doctrine and a silent edit is the doctrine drift AGENTS.md names.
- [agent-chose] Classified #1076 `enhancement` rather than `defect`: the gap is disclosed in the handoff skill's own prose with a stated rationale, so the surface works as designed and the design is what could be tighter.
- [agent-chose] Left #1076 open with a blocker comment naming three candidate answers and a recommendation, rather than closing it against a destination it does not yet have.
- [agent-chose] Corrected a causation claim in flight: the #1076 gap would not have caught the ADR-0.39.0 staleness, and the issue body records that limit.

## Immediate Next Steps

1. Rule GHI #1076's blocker: what SETTLED means for an ADR citation. Three candidates and a recommendation are in the issue's blocker comment; the recommendation is (C) — resolve OBPI from the ledger, leave ADR at UNKNOWN, and repair `src/gzkit/commands/reference_checker.py`'s incomplete survey, which is the part that is unambiguously wrong today. The OBPI arm is buildable now; the ADR arm cannot be built without this ruling.
2. Rule the two notes still parked on closed issues #1074 [settled] and #1075 [settled]. Carried unruled from the predecessor and untouched by this session. #1074 [settled]'s note asks whether to build the missing ts fence, and whether the sibling stores claim the ledger's ordering invariant at all. #1075 [settled]'s note asks whether byte-identical additions present on both sides should be deduplicated.
3. The option A gate instrumentation is still unimplemented, now across three sessions. It holds an operator ruling and this chain is its only destination. Read `src/gzkit/check_fingerprint.py` first: it carries no timing or cost surface and has not been touched since `4b5430527` on 2026-08-22.
4. Decide whether the sibling stores' construction-time stamps are a defect. `src/gzkit/insights/append.py` stamps `ts` at construction with no lock, structurally the same shape as the closed #1074 [settled]. Whether that is wrong turns on whether the insights and corpus stores claim an ordering invariant, which needs a READ of their model, validators and audits — a grep is not a read, and none was performed.

## Pending Work / Open Loops

DISCHARGED THIS SESSION, NOTHING OUTSTANDING. Both rows the operator ruled on are closed out: the unittest claim is repaired in four surfaces with a witness, and the void ADR-0.39.0 step is booked as a set-aside.

OPEN ON ONE OPERATOR RULING. GHI #1076, filed this session, left open with a blocker comment. It is not a tracker for work in flight; it is blocked on the ADR-SETTLED semantics question and nothing else.

CARRIED UNRULED, NOW A THIRD SESSION. The option A quality-gate instrumentation. It has an operator ruling behind it and no queue can see it, because it was never filed as an issue and lives only in this handoff chain. Each session that passes makes the chain its sole custodian.

CARRIED UNRULED, A SECOND SESSION. The doctrine notes on closed issues #1074 [settled] and #1075 [settled]. They live only on closed issues and in insight `next_action` fields, which the predecessor correctly identified as the longest-lived place a stale item hides.

VOID AND BOOKED, NOT MERELY DROPPED. The ADR-0.39.0 interview step. Its premise was measured false and the set-aside record carries the measurement, so a successor cannot revive it by inheritance.

NOT ADVANCED, AND ONLY THE OPERATOR CAN. ADR-0.39.0's seven briefs are all `Draft`, 0 of 7 done, closeout BLOCKED. Its interview is complete. What remains is OBPI execution, which only the operator initiates.

STILL OPEN, UNCHANGED. GHI #1069, two implementation choices unruled.

NEW CONSTRAINT WORTH KNOWING BEFORE THE NEXT EDIT. `.gzkit/skills/gz-obpi-pipeline/SKILL.md` sits AT its 1710-line body ceiling. Any further correction there must compress or extract first; growth is refused by the sync post-check, observed this session.

RESIDUAL LIMIT ON THIS SESSION'S OWN WITNESS. `tests/governance/test_hook_stage_claims.py` detects a non-commit hook named inside a commit-time claim sentence. It does not parse arbitrary prose, so a stage claim phrased in words outside its pattern set would pass. The registered claim phrases are explicit in the module and are the place to widen it.

## Verification Checklist

Ran and observed, not inferred. `uv run gz check` -> All checks passed, real exit 0, on a fully staged tree; run four times, and the two intermediate failures were genuine (ruff format, then the tautological-test audit naming two co-occurrences) and were repaired rather than waived. `uv run python -m unittest tests.governance.test_hook_stage_claims` -> Ran 7 tests, OK.

THE WITNESS WAS OBSERVED FAILING AGAINST THE LIVE TREE before the fourth surface was repaired, naming `.gzkit/skills/gz-obpi-pipeline/SKILL.md` and quoting the offending sentence. That is the control proving it is not vacuous, and it is also how the fourth instance was found. Two negative controls inside the module replay both retired sentences and assert the detector fires on each.

The hook roster was read from `.pre-commit-config.yaml` by `yaml.safe_load`, not from prose: `unittest` resolves to stage `manual`; `pre-commit` carries 15 hooks and the suite is not among them; `pre-push` carries only `gz-check-pre-push`. Independently confirmed at commit time, where the pre-commit run printed 15 cheap gates and no unittest.

`git rev-list --left-right --count origin/main...HEAD` -> `0 0`. `git status --short` -> empty. `gh issue view` -> #1074 CLOSED, #1075 CLOSED, #1069 OPEN. Open queue counted twice: 56 at session open, 57 after filing #1076.

ADR-0.39.0's interview was measured, not assumed: all 19 fields read and each found non-empty with substantive content, and `uv run gz adr status ADR-0.39.0` -> 0/7 OBPIs done, closeout BLOCKED.

NOT VERIFIED, AND SHOULD NOT BE RELAYED AS IF IT WERE. Whether the insights and corpus stores claim the ledger's ordering invariant: only a grep was run, and AGENTS.md is explicit that a search is not a read. Whether the option A instrumentation's design still fits `check_fingerprint.py`. Whether the witness's claim-phrase set is wide enough for prose not yet written.

## Evidence / Artifacts

Commit, pushed, HEAD `d98b520f3` level with origin/main: `fix(skills): four surfaces claimed the pre-commit hook runs unittest`, 16 files.

New test: `tests/governance/test_hook_stage_claims.py`, 7 tests, deriving the non-commit-staged hook set from `.pre-commit-config.yaml` on every run so a genuine stage change silences it rather than requiring the test be edited.

Surfaces repaired: `.gzkit/skills/git-sync/SKILL.md` (1.4.0 to 1.4.1), `.gzkit/skills/gz-session-handoff/SKILL.md` (7.6.0 to 7.6.1), `.gzkit/skills/gz-obpi-pipeline/SKILL.md` (6.59.1 to 6.59.2), `src/gzkit/templates/skills/git-sync/SKILL.md`. Vendor mirrors regenerated via `gz agent sync control-surfaces` and verified at single-md5 parity across all four copies of each skill.

Read but not modified, and cited by GHI #1076: `src/gzkit/commands/reference_checker.py`, `src/gzkit/ledger_semantics.py`.

Canon read for the front deltas: `docs/governance/build-to-1.0-campaign-2026-09-20.md` section Workflow fronts.

Predecessor: `.gzkit/handoffs/20260921T073259Z-ledger-ts-ordering-pair-closed.md`, resumed Fresh, with a `handoff_resume_decided` record booked against it carrying the operator's verbatim words and one set-aside.

Issue: GHI #1076 filed `enhancement` + `runtime`, left open with a blocker comment carrying three candidate rulings and a recommendation.

Insights: two records, scopes gzkit.skills.git-sync (defect-resolution) and gzkit.handoff (defect).

## Settled Rulings

1015 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
