---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-07T06:51:52Z'
agent: claude-code
session_id: 91906a01-8d11-430c-9750-4bbe389354aa
continues_from: .gzkit/handoffs/20261006T094607Z-item-10-completed-and-attested.md
---

## Current State Summary

This document supersedes the 09:46Z handoff of 2026-10-06 (item 10 completed and attested) and the three exit bookmarks written after it. It also carries the account of the R&D session that ran between them, which had no authored handoff.

The session resumed the 09:46Z handoff, verified its claims against live state, and the operator directed four pieces of work. All four are done and pushed; main matches origin at 0e33a0ac4 and the tree is clean. No OBPI was initiated, no lock was claimed and none is held.

1. Tautological debt chore: three ops retired through the decommission-tautological-tests chore (commit f09214592). Debt reads 223 against a ceiling of 227 on 2026-10-07 UTC. The baseline file is regenerated at 223 identities and the chore run is logged.
2. GHI #1177: fixed and closed (commit e93725878). The debt check computes its ceiling on the UTC date through one named clock read, schedule_date, in both the authored script and its generated copy.
3. GHI #1039: fixed and closed (commits 75903fb73 and 1869b6265). The skills audit no longer imports the skills package; the shared report types and the frontmatter parser live in the leaf module gzkit.skill_contract, where the parser has the public name parse_frontmatter.
4. GHI #1179: fixed and closed (commit 0d96826ce). A test run that exceeds the hang bound during the arb red witness is an inconclusive row or a void experiment, with a receipt, in both forms of the command.

GHI #1028 was under the operator's hold of 2026-09-19. The operator lifted it for the measurement only. The production comparison for items 14 and 10 against items 05 and 06 is posted on the issue, with two corrections under it, and the issue stays open. The campaign plan carries the lift as its amendment of 2026-10-07 (commit 0e33a0ac4).

Verification on the final code tree: the full unit suite passed with 11495 tests and 7 skipped, and the per-change gate exited 0 before each sync. CI finished green on 9226f9508, the push that carried the four fixes. CI on 0e33a0ac4, the campaign amendment, was still running when this was written.

The R&D session (24f0562f-2e6d-46b4-978a-a506149330a6, 2026-10-06 09:50Z to 11:07Z) opened the run renewing-vows on the operator's invocation and pushed it as 1fa80c7e7: the record, 27 source files and two defect insights. The run is open, with nine frontier items and no sign-off.

## Important Context

What changed in the code, for whoever works near it.

The debt check reads the UTC date. A caller west of UTC sees the next day's date in the evening, and the report line says UTC for that reason. The declining ceiling therefore steps at 00:00 UTC, which is 19:00 the evening before in US Central daylight time.

The shared skill types moved. SkillAuditIssue, SkillAuditReport and the frontmatter parser are defined in src/gzkit/skill_contract.py. The skills package re-exports all three and keeps _parse_frontmatter as its own name for the public parse_frontmatter. A new import of a private name across package directories is refused by tests/policy/test_import_boundaries.py, and its roster is shrink-only; that test is what caught the first version of the #1039 fix.

The arb red witness now reports a hung run instead of crashing. A hung mutant is one inconclusive row and the sweep continues. A hung baseline in the commit form returns the verdict inconclusive with a detail that the experiment is void, and the command prints that detail. In the REQ form a hung run on either tree is not-applicable. The bound is still 600 seconds, so a hung hunk that is regraded statement by statement costs ten minutes per statement.

Three things about the witness that cost time this session. It grades a generated mirror copy as its own production file, so a fix to a mirrored chore script needs a test that drives both copies. It grades code moved verbatim as new guards, so a move exposes whatever the commit's own test modules do not exercise. A guard whose removal raises an error instead of failing an assertion reads inconclusive, not killed.

Direct-fix commits that touch src or tests must carry a Task trailer of the form TASK-slug-#ghi. The commit hook does not refuse its absence; the per-change gate does. This session committed five times without it, then reworded all five before pushing and re-ran the witnesses on the new commits. The ledger therefore holds red-commit receipt events that cite commits no longer reachable from main: c47f30201, fd90c2d09, 43f3138a6, 59df0c6ed, b3c37b4f6, d3ebfba83, 08257961b and 778c83861. The receipts cited in the three close comments are the ones bound to the pushed commits.

The Bash hook verifier-pipe-gate refuses a verifier whose exit status would be masked: piped into a filter, followed by another statement, or followed by an or-branch. Use set -e, set -o pipefail, or redirect to a file and read the status.

The chores board still lists decommission-tautological-tests as unmeasured after this session's logged run. The 09:46Z handoff called the chore overdue; the board did not say that then and does not now.

Workflow fronts (source: docs/governance/build-to-1.0-campaign-2026-09-20.md, Workflow fronts section). Handoff system: worked; one resume presented, verified and ruled, one decision booked, this document authored. GHI triage: not run as a skill; three issues fixed and closed on the operator's direct selection, one measured and left open. ADR and OBPI campaign: no OBPI work; ADR-0.35.0 reads 10 of 20, unchanged; the campaign plan gained the amendment of 2026-10-07. New R&D: not touched this session; the run renewing-vows opened in the session before it and is open. The three-pillars thread: the production observation is recorded on GHI #1028 and the hold stands for that issue's remaining text findings.

## Decisions Made

- [operator-ruled] The tautological debt chore and GHIs #1179, #1177, #1039 and #1028 are worked next (verbatim: "do these next:", followed by two pasted rows of the resume report, one naming the debt chore and one reading "GHI #1179, #1177, #1039, #1028 open").
- [operator-ruled] The hold on GHI #1028 is lifted for the measurement only: the production comparison is posted and the issue stays open (verbatim: "A"). Rejected alternatives offered: keep the hold and post nothing; lift the hold fully and work the issue's remaining text findings.
- [operator-ruled] The campaign plan is amended to record the lift of the #1028 hold for the measurement only, with its hold line updated to match (verbatim: "A"). Rejected alternative offered: leave the campaign plan as it was.
- [operator-ruled] A successor handoff covering this session is written (verbatim: "write a successor handoff covering this session").
- [agent-chose] Did not treat the pasted row as lifting the #1028 hold. Worked the chore and the other three issues first, then put the hold and the newly available figures to the operator.
- [agent-chose] Retired three ops and not one: the router-files test now asks the product's own skill listing, and two existence tests were deleted because the test beside each fails on the same absence. Two candidates were left alone because they are bound to runbook-documentation requirements they do not test, which is a rebinding question and not a retirement.
- [agent-chose] For #1039, moved the shared definitions to a leaf module instead of delaying the package's re-export, because the move removes the mutual dependency and the delay only hides it.
- [agent-chose] For #1179, graded a hung mutant inconclusive and not killed. The mutation-sweep rule makes killed a claim about the guard and inconclusive a claim about the run; the rule text was not edited and still does not name the timeout case.
- [agent-chose] Added Task trailers by rewording the five unpushed commits through the commit hooks, and re-ran every witness on the new commits, instead of leaving receipts bound to commits that would not reach main.
- [agent-chose] Left the campaign plan unedited until the operator ratified the amendment text, and flagged the disagreement on the issue in the meantime.

## Immediate Next Steps

1. Present this handoff's state to the operator and confirm it against live state: GHIs #1177 [settled], #1039 [settled] and #1179 [settled] read closed, GHI #1028 reads open, no lock is held, main is in sync, and the CI runs on 0e33a0ac4 have finished green.
2. Put the registry loader's decode defect to the operator for routing, naming Draft brief OBPI-0.39.0-02-tolerance-contract and ADR-0.39.0. The agent's recommendation is a direct fix under a new issue, because the loader's own docstring already promises a single RegistryError.
3. Put the first frontier question of the R&D run renewing-vows to the operator: whether the concept of operations is the apex or a sidecar to the campaign plan. The prior session recommended apex. Eight more frontier items follow it in the record's Close section.
4. Tell the operator four defect insights are unrouted: the Task trailer gap in the ghi-close skill and the commit hook; the two tests bound to runbook requirements they do not test; the subagent effort mechanism that model-selection.md describes and the Agent tool does not have; and the Markdown lint that nothing runs.
5. Wait for the operator to initiate the next item of ADR-0.35.0 through the pipeline skill. The campaign order names the tune-up items 15 to 20 ahead of items 11 to 13.

## Pending Work / Open Loops

Tautological debt: 223 outstanding. The ceiling reaches 222 on 2026-10-14 UTC, which is the evening of 2026-10-13 in US Central time, and the check breaches then unless more ops are retired. Each retirement is a judgment about a test.

GHI #1028 is open. Its remaining text findings are under the hold: Stage 4 does not point at the block verb, and no numeric cap on total review rounds exists. The comparison comment lists what was not established: model configuration per run, why item 10 has no spec-review or quality-review acceptance records, and the reason for each proof input change.

Left open by the three fixes and tracked only here and in their close comments: other gates that read the local date were not surveyed (the #1177 [settled] body raised it); the syntax check of a mutant still lets a hang propagate; the hang bound is unchanged at 600 seconds. GHI #1146, a neighbouring surface with no hang bound at all, is open and unselected.

Recorded as insights this session and unrouted: the ghi-close skill's commit step names only the issue trailer and the commit hook passes a src or tests commit with no Task trailer; test_tests_use_tempfile_and_covers in tests/hooks/test_complexity_advisor_auto_chain.py is bound to a runbook requirement and reads its own file, the same class as the test_no_subprocess_spawned binding already on file.

Recorded as insights by the R&D session and unrouted: model-selection.md declares a subagent effort mechanism no surface witnesses; nothing lints Markdown under docs, because run_pymarkdown has no caller and pymarkdown is not installed.

The R&D run renewing-vows is open. Its disposition map has six rows awaiting the operator's go on each, and its Close section lists nine frontier items. Four texts were unreached by automated retrieval (JP 3-30, JP 3-60, JO 7110.65 and AC 121-22), and the paid-standard claims need licensed copies.

ADR-0.35.0 has ten items outstanding: 09 (repudiated, to be re-completed), 11, 12, 13 and 15 to 20.

Still standing from the 09:46Z handoff and the 01:01Z checkpoint of 2026-10-06, and not restated in full: the registry loader's raw decode error; the 14 type-checker diagnostics in the behave step files outside the gate's scope; the advisory that the flag ops.product_proof is past its deadline; the run of malformed covers warnings, which the R&D record now carries as its disposition row 2(b) and which has no issue; the unverified items inherited from the 19:48Z handoff of 2026-10-05; and the two rulings the operator still owes, on whether red CI being invisible locally gets a work order and on who owns the content land reorder. Resolved since those documents: GHIs #1177 [settled] and #1039 [settled] are closed, and the design dialogue of session 3e386d1a-fbc8-4e8c-bacd-0c6f024b2723 now has an authored account in the R&D record.

Not read this session: the transcript of session ea522053-be1e-4e5b-af9d-2255a0488062, which left one of the exit bookmarks.

Left alone: stale Codex broker processes and earlier disposable review checkouts from other sessions.

## Verification Checklist

The ahead and behind count of main against origin: expect 0 0. The last CI workflow runs on main: expect success on completed runs, including 0e33a0ac4. The OBPI lock list: expect no active locks. GHIs #1177, #1039 and #1179: expect closed. GHI #1028: expect open, with a comparison comment and two corrections under it. The debt check script under the chore directory: expect exit 0 and a line reading 223 outstanding with the date labelled UTC, unless ops were retired or added since. The unit module tests.chores.test_tautological_debt_target: expect 17 tests OK. The unit module tests.test_skills_audit run alone: expect 41 tests OK. A fresh interpreter importing gzkit.skills_audit first: expect exit 0. The unit modules tests.test_mutation_witness, tests.test_commit_witness and tests.test_red_witness: expect OK. The unit module tests.policy.test_import_boundaries: expect OK. The tautological-test-audit validation scope: expect exit 0. The ADR status of ADR-0.35.0-canon-entry-corpus-landing: expect 10 of 20. The campaign plan: expect an Amendments entry dated 2026-10-07 marked latest. A rulings search for "measurement only": expect this handoff's ruling among the results.

## Evidence / Artifacts

Commits on main from this session, oldest first: f09214592 (the chore's three retirements and the staged exit bookmark), e93725878 (GHI #1177), 75903fb73 and 1869b6265 (GHI #1039), 0d96826ce (GHI #1179), 9226f9508 and fd85315a9 (ledger and insight syncs), 0e33a0ac4 (the campaign amendment), and the sync commit that carries this handoff.

Chore surfaces: `tests/skills/test_namespace_routers.py`, `tests/governance/test_req_coverage_record.py`, `tests/governance/test_evaluation_event.py`, `data/tautological_test_baseline.json`, `.gzkit/chores/decommission-tautological-tests/proofs/CHORE-LOG.md`.

GHI #1177 surfaces: `.gzkit/chores/decommission-tautological-tests/check_debt_target.py`, `src/gzkit/chores/decommission-tautological-tests/check_debt_target.py`, `tests/chores/test_tautological_debt_target.py`.

GHI #1039 surfaces: `src/gzkit/skill_contract.py`, `src/gzkit/skills/__init__.py`, `src/gzkit/skills_audit.py`, `tests/test_skills.py`.

GHI #1179 surfaces: `src/gzkit/mutation_witness.py`, `src/gzkit/commit_witness.py`, `src/gzkit/red_witness.py`, `src/gzkit/commands/arb.py`, `tests/test_mutation_witness.py`, `tests/test_commit_witness.py`, `tests/test_red_witness.py`, `docs/user/manpages/arb-red.md`.

GHI #1028 and the campaign: `docs/governance/build-to-1.0-campaign-2026-09-20.md`, `.gzkit/chores/instructions-files-diet/proofs/pipeline-review-2026-09-19/README.md`.

The R&D run: `docs/rnd/renewing-vows.md`.

Insights: `.gzkit/insights/agent-insights.jsonl`.

Receipts, held under artifacts/receipts. Falsifiability: arb-red-commit-e93725878041-754b61d6eda24d83bac75564732549fb (driven), arb-red-commit-75903fb732f8-dc838d884ba546a98c4356f13ad48e7e (inconclusive, no survivor), arb-red-commit-1869b6265328-52cb63ba93874ac2955647a503424429 (driven), arb-red-commit-0d96826ce527-0d22603295b14bae8c491f6723f3a608 (inconclusive, no survivor). Final tree: arb-ruff-83ed53f05d944756af4047bb96281459, arb-step-typecheck-395570f5133f4fbdaaa213d2498081d8, arb-step-unittest-705369f21e4f4e74bee84c8f26c76c04 (11495 tests), arb-step-mkdocs-130eff7f74ea416787384bd2bb3e7d8d. The failing full-suite run that caught the private import: arb-step-unittest-d8c60bef14b74525bc358ac99698dd31.

Predecessor: `.gzkit/handoffs/20261006T094607Z-item-10-completed-and-attested.md`, superseded by this document. Exit bookmarks superseded: `.gzkit/handoffs/20261006T095005Z-session-exit-bookmark.md`, `.gzkit/handoffs/20261006T095027Z-session-exit-bookmark.md`, `.gzkit/handoffs/20261006T223805Z-session-exit-bookmark.md`.

## Settled Rulings

1418 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
