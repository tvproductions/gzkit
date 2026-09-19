---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-19T11:20:07Z'
agent: claude-code
session_id: 66ff7d9b-39d7-42b2-bafa-fab50266d15d
continues_from: .gzkit/handoffs/20260919T100023Z-diet-pass-two-closed-three-src-remainders-fixed.md
---

## Current State Summary

READ FIRST: docs/governance/control-surface-overhaul.md. It is the program record for the control-surface overhaul run under GHI #921 since 2026-09-12: the target, each surface's authoring model today against its target, what landed, what is owed and who owns it. This handoff is a delta on that record, not a substitute for it. The record exists because the predecessor handoffs framed the day's work as 'diet pass two' and the agent mistook that slice for the whole; the operator caught it (verbatim in Decisions). Landed after the predecessor, each behind a full gz check exit 0 on a fully staged tree: 945db8431 the record; 626bd1e97 the root AGENTS.md destination as a range (15,000 ideal, 20,000 ceiling; file is 19,872 B); d279d7ebf new rule .gzkit/rules/skill-authoring.md 0.1.0 (scorecard rows 94-97, all Judgment; distribution baseline manifest updated); a8c1ed428 three chore declarations amended, each in its own class (instructions-files-diet 3.4.0 widened to skill bodies, skill-authoring-quality 2.2.0 governed by the new rule, frontier-model-card-currency 1.4.0 reaching skill wording); e1145a681 loads re-measured and chore runs logged. GHI #1037 filed, authoring only (gz skill new scaffolds a stub body; gz skill audit reads no body). GHI #1036 filed earlier (configured attestor handle). Chore runs today: instructions-files-diet PASS; all five control-surface-* chores exit 1 on proof freshness, because their audits date from 2026-09-12 and have not been performed against the rewritten surfaces. No pipeline, OBPI, lock or TASK is active; ADR-0.35.0 is TOPMOST and Draft.

## Important Context

Workflow fronts source: docs/governance/build-to-1.0-campaign-2026-08-16.md#workflow-fronts. Only the ghi-triage front and the #921 chore work moved; the handoff, adr/obpi and R&D fronts were not inspected. Authorities the agent failed to read before advising, and which settle most design questions here: docs/governance/agent-control-surface-rendering-substrate.md § Binding claim (corpus construction applies to agents/claude and rules; skills are canonical files and are NOT corpus constructed, operator ruling 2026-09-09); docs/governance/chore-class-system.md (five classes, four rungs; class is why a chore exists and fixes its staleness signal; uniformity within class; a repair touching a skill is operator-only-repair; admission of a new chore is operator-directed on recurrence evidence); ADR-0.35.0 Feature Checklist, where OBPI-0.35.0-12 rules-corpus-onboarding is the owner of bringing rules and nested AGENTS.md under the CMS, behind OBPI-05 and OBPI-07. Correction carried from earlier handoffs: they called 15,000 'the budget' for AGENTS.md; the enforced budget is 50000 in data/instructions_files_budget.json, advisory until 1.0, and the destination is now the range above. Mechanics learned: a new shipped rule must be added to data/distribution_baseline_manifest.json surfaces.rules in sort order or the Behave distribution scenario fails; advisory-scorecard row ids must match digits plus an optional letter or the validator silently does not count them, and the totals table is machine-checked; ChoreDeclaration.governingRule holds exactly one rule clause; gz chores run only executes acceptance criteria, the chore itself is performed by doing its workflow and writing fresh proofs; CHORE.md ships in the wheel, so a pointer to a gzkit-only doc belongs in the project-local proofs/CHORE-LOG.md. The load script measure_load2.py lives only in this session's scratchpad; its on-edit totals add nested files and mirrors together, which describes no consumer since GHI #1021, so read them per consumer as proofs/load-2026-09-19.txt does. The full gz check takes several minutes and dominated the session; git stash --staged with a pathspec reverts the working tree.

## Decisions Made

- [operator-ruled] On the agent's grasp of the effort, verbatim: "we have been actively engaged in a comprehensive review and overhaul of all control surfaces and you do not seem to have a comprehensive grasp of that broad effort. I am troubled by this." And: "do you even remember that this was our main task over the last two days?" Remedy ruled: one comprehensive governance document, read first by any session on this work.
- [operator-ruled] The target, verbatim: "all agents.md and rules must eventually be cms rendered. skills should be reviewed as a part of a chore (new or existing), where parsimony and new model alignment are part of the review." On skill review: "its both an authoring AND chore scope".
- [operator-ruled] On recommending a chore design before reading the chore doctrine, verbatim: "chores are different - LOOK before you make design recommendations".
- [operator-ruled] Root AGENTS.md destination, verbatim: "make target 20k", then "state a range: 15K is ideal, 20K a ceiling".
- [operator-ruled] Completing the record, verbatim: "I want to complete this: docs/governance/control-surface-overhaul.md and I want chores to attend to this. if we need to tighten authoring skills/tools too?" Ruled by selection: the order standard, chore declarations, tooling GHI, evidence runs, skill-body size pass; the standard lives in a new rule skill-authoring.md; parsimony clause 5 stays (rationalization and red-flag tables are not required sections, a row earns its place by naming a failure observed here); chore amendments A, B and C as proposed; skill-body parsimony by widening instructions-files-diet, no new chore.
- [operator-ruled] Rulings are requested as clickable options, recommendation first (carried from the predecessor; applied throughout).
- [agent-chose] Put the pointer to the record in the diet chore's project-local CHORE-LOG.md, not its CHORE.md, because CHORE.md ships to adopters.
- [agent-chose] Scored the new rule as four Judgment rows and wrote its enforcement posture as advisory, because no check reads a skill body; the countable arms are routed to GHI #1037.
- [agent-chose] Left instructions-files-diet's governingRule as the budget rule, since the field holds one clause, and named the skill standard in its CHORE.md.
- [agent-chose] Logged the five control-surface chore runs as they came out (FAIL on stale proofs) rather than performing five audits unruled; each is propose-rung reading work ending in recommendations for the operator.

## Immediate Next Steps

1. Present these steps to the operator and wait for a ruling; none is authorized by this document.
2. Read docs/governance/control-surface-overhaul.md end to end, then the chore about to be run, before advising on anything in this effort.
3. Offer record item 3, the skill-body size pass under instructions-files-diet § 5d with skill-authoring.md in force: start with gz-obpi-pipeline (1,722 lines), read every @covers REQ bound to it first, lift dated narrative to references or a rationale doc, keep every stage, and present a full before and after. Rebuild from the current skill version; the parked 17-passage proposal predates three landings. The operator may prefer this after the next OBPI is measured against GHI #1028.
4. Offer record item 6, performing the five control-surface audits one at a time against the rewritten surfaces, each ending in recommendations; start with control-surface-rule-conflicts, since a new rule and four rule edits landed since its last proof.
5. Ask whether to pull GHI #1037 (needs the operator's 'fix #1037'; the first severity for oversized bodies is the operator's call) and GHI #1032.

## Pending Work / Open Loops

Owed per the record and unstarted: rules and nested AGENTS.md into the corpus (OBPI-0.35.0-12, operator-initiated); root AGENTS.md from 19,872 B toward the 15,000 ideal (OBPI-0.35.0-10 for the pinned rows, the operator for Operator Doctrine and Gate Covenant wording), with only 128 B under the ceiling so any addition needs a removal; nothing mechanical reads the range, the budget file carries one number per file; 50 skills swept and never read in full; the instructions-files-diet CHORE.md opens with about 95 lines of version-history quotes before its Overview, and its § 5 table still cites AGENTS.md sections the rewrite removed. Open GHIs from this effort: #921, #943, #1019, #1023, #1028, #1029, #1030, #1032, #1034, #1036, #1037. Carried and unruled: whether patch-release.md carries the Foundation-skip rule; whether gz-adr-audit Step 8 survives a fix to #1015; whether a rule's version belongs in frontmatter; the attests-at-Gate-5 wording shared by gz-complexity-distill, its manpage and complexity-doctrine.md; whether 300 lines is the right oversized threshold. The new rule costs about 4.5 KB on every skill edit for each consumer. The #921 comment of 2026-09-19 corrected the budget claim but predates the range ruling; it says the destination is 20,000.

## Verification Checklist

git status --short prints nothing and git rev-list --left-right --count origin/main...HEAD prints 0 0. uv run gz validate --advisory-scorecard exits 0 and the Coverage Ledger lists skill-authoring.md at 0.1.0. uv run gz chores run instructions-files-diet exits 0; each of the five control-surface-* chores exits 1 on check_proof_freshness until its audit is performed. gh issue view 1036 and 1037 report OPEN. wc -c AGENTS.md prints 19872. grep -c skill-authoring data/distribution_baseline_manifest.json prints 1.

## Evidence / Artifacts

`docs/governance/control-surface-overhaul.md`, `.gzkit/rules/skill-authoring.md`, `docs/governance/agents-md-doctrine.md`, `docs/governance/instructions-files-budget-history.md`, `docs/governance/advisory-rules-audit.md`, `docs/governance/chore-class-system.md`, `docs/governance/agent-control-surface-rendering-substrate.md`, `.gzkit/chores/registry.json`, `.gzkit/chores/instructions-files-diet/CHORE.md`, `.gzkit/chores/skill-authoring-quality/CHORE.md`, `.gzkit/chores/frontier-model-card-currency/CHORE.md`, `.gzkit/chores/instructions-files-diet/proofs/load-2026-09-19.txt`, `.gzkit/chores/instructions-files-diet/proofs/CHORE-LOG.md`, `data/distribution_baseline_manifest.json`. Commits 945db8431, 626bd1e97, d279d7ebf, a8c1ed428, e1145a681. Issues tvproductions/gzkit #1036, #1037; #921 comment 5741168072.

## Settled Rulings

951 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
