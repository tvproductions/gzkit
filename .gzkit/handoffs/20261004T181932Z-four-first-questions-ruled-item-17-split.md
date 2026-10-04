---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-04T18:19:32Z'
agent: claude-code
session_id: 9c2ae708-89a4-4ea2-8ed7-8b2ebaa37c77
continues_from: .gzkit/handoffs/20261004T154706Z-tune-up-briefs-15-19-in-flight-adr-law.md
---

## Current State Summary

This session resumed the 15:47Z handoff, verified its claims against live state, and worked its advised step 1 as far as the four questions that handoff put first. All four are ruled and recorded in the briefs. Before that it landed the sync the prior session had left stranded. Every push since 13:33Z had been failing the pre-push check on one unit test, the orphaned-implementation audit, because the session-start reap of the OBPI-0.35.0-10 lock is a forced release after in-window brief edits with no completion. The operator re-claimed the lock and the push went through. The operator then ruled the audit is working as designed, and its failure message was repaired to name the re-claim (commit c9cb95cb2, a direct fix with tests). The ADR-0.13.0 escalation was put to the operator one question at a time and ruled: the marker's current_stage advances with the run, next_command is one field derived from the run's position, three attested requirements are amended in place when the repairs land, and five misplaced covers bindings move to the tests that assert them. Further rulings: a stage transition becomes a ledger event rebuilt by the state repair verb, a continuing session takes over the lock by transfer, and brief 17 is split in two. ADR-0.35.0 now has 20 checklist items with 9 landed; OBPI-0.35.0-20-pipeline-skill-cutover is new. Briefs 15, 16, 17, 19 and 20 pass the authored-brief validation, and the req-kind-discipline, cli-alignment, brief-reconcile and documents scopes exit 0. No OBPI was initiated and nothing in the five repair assignments was implemented. OBPI-0.35.0-10 is unchanged in the ledger: in progress, not complete, not attested. Its lock is held by this session, claude-code-9c2ae708, claimed by the operator at about 16:02Z on 2026-10-04 with the default 24-hour lifetime. The tree was clean and level with origin/main at a3164df53 before this handoff was written.

## Important Context

The OBPI-0.35.0-10 lock will be reaped at the first session start after about 16:02Z on 2026-10-05 unless OBPI-10 is completed or surrendered first. A reap makes every push fail the orphaned-implementation audit until the operator re-claims the lock; this has now happened twice (OBPI-0.35.0-04 on 2026-09-05, OBPI-0.35.0-10 on 2026-10-04). The operator ruled that behaviour correct, so the recovery is the operator's lock claim and never a skip marker. The next session resolves to a different agent id, so it is not the holder of that lock.

The operator asked for decisions one at a time, each as a short bounded choice with a recommendation, and answered each with a single letter. Keep that form. Recording a ruling in a brief needs the operator's direction; it was given once in general ("yes, make the edits") and the later brief edits followed announced intent.

Six details of the brief 17 split were the agent's and were put to the operator for confirmation at the end of the session without an answer: the scorecard records a State Anchor split adder and not a baseline raise; three criteria were added beyond the five the question named (brief 20 re-runs the inventory check after the cutover, brief 17 asserts the body digest equals the baseline, brief 17 covers its manpage change); the audit widening stays in brief 20 but must precede any removal from the skill body; brief 17's criteria were renumbered 01 to 07 with the mapping written under its Q6 ruling; its Q2 and Q5 moved to brief 20; the delivery estimate was divided between items 17 and 20.

Two ADR amendments now rest on the in-flight law that an ADR in flight may take more OBPIs: the 19-item amendment and the 20-item split. The law's wording is still not in canon, and its draft is in the transcript of session 0b94f0b0, not in this one.

Brief 20 names two paths that brief 17 creates. Each is marked as created in OBPI-0.35.0-17 so the path validator passes; the validator has no notion of a path a predecessor brief creates. Brief 15's note on REQ-0.13.0-03-02 must name no command line, so that brief 16 does not have to amend it again. Brief 15 no longer pins a next_command value at launch.

Two slips by the agent this session, both repaired before the push they affected: a commit message claimed the sensitivity scope passed when it exits 3 (the pushed message is correct), and an accidental git stash held two ledger rows, restored through the ledger merge driver. The sensitivity scope exits 3 on two ADR-0.39.0 briefs, outside the per-change check, recorded as an insight on 2026-09-27. The verifier-pipe hook reads a verifier name inside a commit-message heredoc as a command; commit from a message file instead.

Workflow fronts (source: docs/governance/build-to-1.0-campaign-2026-09-20.md, Workflow fronts section). Handoff system: worked (resume, one decision booked, this successor; the 15:53Z exit bookmark is superseded here). GHI triage: not run; no issue was filed, commented or closed. ADR and OBPI campaign: ADR-0.35.0 reads 9 of 20 by the ADR status command; five briefs amended, one created, nothing initiated. New R&D: not touched. The three-pillars hold on GHI #1028 is unchanged.

## Decisions Made

- [operator-ruled] Start with the stranded sync (verbatim: "landing the stranded sync"). Rejected alternative offered: start with the ADR-0.13.0 escalation.
- [operator-ruled] The orphaned-implementation audit firing after a lock reap is working as designed, the re-claim is the clearance, and the only repair is the audit's failure message (verbatim: "A. Working as designed (recommended)."). Rejected alternatives offered: the audit exempts reaping releases; hand the question to brief 19.
- [operator-ruled] Decisions are put one at a time (verbatim: "one at a time please").
- [operator-ruled] OBPI-0.35.0-15 Open Design Question 4: the marker's current_stage advances with the run (verbatim: "A"). Rejected alternative offered: a separate position key with current_stage kept at the launch value.
- [operator-ruled] OBPI-0.35.0-16 Open Design Question 2: next_command is one field derived from the run's position (verbatim: "A"). Rejected alternatives offered: two fields; launch instants keep the attested values.
- [operator-ruled] REQ-0.13.0-03-01, REQ-0.13.0-03-02 and the command clause of REQ-0.13.0-03-04 are amended in place when the repairs land (verbatim: "A"). Rejected alternatives offered: leave the lines untouched as history; reverse one of the two rulings above.
- [operator-ruled] Each misplaced covers binding for an ADR-0.13.0 requirement moves to the test that asserts it (verbatim: "A"). Rejected alternatives offered: add a binding and leave the old ones; leave the bindings alone.
- [operator-ruled] Record the rulings and their consequences in briefs 15 and 16 (verbatim: "yes, make the edits").
- [operator-ruled] OBPI-0.35.0-15 Open Design Question 2: each recorded boundary appends one stage-transition event, ledger first and marker second (verbatim: "B"). Rejected alternatives offered: infer position from existing events; a mix of the two.
- [operator-ruled] The state repair verb rebuilds a deleted pipeline marker, and nothing else does (verbatim: "A"). Rejected alternatives offered: the pipeline launcher; both.
- [operator-ruled] OBPI-0.35.0-19 Open Design Question 1: a continuing session takes over the lock by transfer (verbatim: "A"). Rejected alternative offered: record a second occupant beside the first lock.
- [operator-ruled] OBPI-0.35.0-17 Open Design Question 6: brief 17 is split in two (verbatim: "A"). Rejected alternative offered: keep it whole.
- [operator-ruled] Write this handoff and sync, then resume (verbatim: "contex is full, write to handoff, then git sync. then we resume. proceed.").
- [agent-chose] Committed the stranded work with a descriptive message before syncing, so the brief and ADR changes did not land under a records-only commit subject.
- [agent-chose] Added a citation of state doctrine Rule 1 to the audit's failure message, beyond the ruled recovery text, because the guardrail-prose rule requires a cited reason.
- [agent-chose] Recorded the reap-blocks-push finding and its resolution as two insights and filed no issue.
- [agent-chose] Scored the brief 17 split as a State Anchor split adder on the ADR scorecard, and made the five other split details listed in Important Context; all six await the operator's confirmation.
- [agent-chose] Recorded brief 19's ruling in its Change Log as well as at the question, because that brief's Requirement 12 asks for it; briefs 15, 16 and 17 record rulings at the question only.

## Immediate Next Steps

1. The operator confirms or changes the six split details the agent chose (listed in Important Context), starting with the scorecard dial: a State Anchor split adder, or a baseline raise.
2. The operator approves or replaces the wording of the in-flight law. Read the draft from the transcript of session 0b94f0b0 first and present it. Then land it in three places: a dated campaign amendment carrying the operator's words; an AGENTS.md Operator Doctrine corpus entry through gz-content-remember that names the work-order wording it replaces for in-flight work; and a ruling entry in docs/governance/ieee/OPEN-QUESTIONS.md for the successor direction.
3. The operator rules the remaining Open Design Questions, one at a time, each recorded in its brief: brief 15 questions 1 and 3; brief 16 questions 1 and 3; brief 17 questions 1, 3 and 4; brief 18 questions 1 to 5; brief 19 questions 2 to 6; brief 20 questions 2 and 5. Brief 18 question 1 is coupled to the ledger-first ruling already made for brief 15.
4. After the operator has reviewed the briefs, close GHI #1172 to #1176 as superseded through ghi-close, each citing its brief; GHI #1174 cites both OBPI-0.35.0-17 and OBPI-0.35.0-20.
5. The operator invokes gz-obpi-pipeline for OBPI-0.35.0-10 before its lock lapses at about 16:02Z on 2026-10-05, or re-claims the lock after the reap. Then for each repudiated OBPI in turn: OBPI-0.0.24-04, OBPI-0.0.26-02, OBPI-0.34.0-02 and OBPI-0.35.0-09. The human-review judgment and the attestation are the operator's words; never author them.

## Pending Work / Open Loops

The predecessor's open loops that this session did not touch are unchanged and are not restated here. Carried from its advised steps, still unruled: whether one unit of work per session ended by a handoff becomes advisory canon; where items 15 to 20 sit in the working order relative to the unlanded corpus items 10 to 13; and whether four consecutive healthy windows-latest runs close GHI #1165 as fixed.

New in this session. The eight code findings the predecessor listed as unverified are partly checked: the misplaced covers bindings for ADR-0.13.0 are confirmed for six requirements (REQ-0.13.0-02-01, -02-02, -03-01, -03-02, -03-03 are misbound; -03-04 is correct), and the three lock code sites behind brief 19 question 1 read as the brief says. The rest remain unverified: a claim over another agent's expired lock deletes it with no reaping record; the agent option lets a session act as the holder; the dispatch aggregation miscounts production records; Stage 3 verification records fail to load as dispatch records; a blocked marker still states a verify next command in two readers; the pipeline manpage is stale on marker clearing; the pipeline skill has two internal contradictions.

The attested sync command in the ceremony marker cannot run as stated: the sync entry exits without an attestor and an evidence payload. Brief 16 row 10 records it and ruling 2 retires the value, so no separate work order exists.

The per-change check printed one advisory after the audit-message fix, "Unjustified code changes: 1", which was not investigated. The sensitivity scope exits 3 on OBPI-0.39.0-01 and OBPI-0.39.0-02 and sits outside the per-change check; recorded as an insight on 2026-09-27 with no work order. A governed lock reap still blocks every push until the operator re-claims, by ruling.

The docs for the split were not carried beyond the ADR and the two briefs: GHI #1174 has no comment naming OBPI-0.35.0-20, and the campaign plan's sequencing text still describes the tune-up without the split. ADR-pool.skill-runtime-authority-inversion overlaps briefs 17 and 20 and was not amended.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD: expect 0 0 after the sync. git stash list: expect no entries. uv run gz obpi lock list: expect OBPI-0.35.0-10-classification-reader-and-ownership ACTIVE under agent claude-code-9c2ae708 until about 16:02Z on 2026-10-05, or no lock after a reap. uv run gz validate --orphaned-implementation: expect exit 0 while that lock stands, and exit 3 naming OBPI-0.35.0-10 after a reap, cleared by the operator's lock claim. uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing: expect 9 of 20. uv run gz obpi status OBPI-0.35.0-10-classification-reader-and-ownership: expect Runtime State IN PROGRESS and Completion PENDING. uv run gz obpi validate --authored on each of the briefs OBPI-0.35.0-15, -16, -17, -19 and -20: expect a pass. uv run gz validate --req-kind-discipline --cli-alignment --brief-reconcile --documents: expect exit 0. uv run gz validate --sensitivity, run alone: expect exit 3 naming only the two ADR-0.39.0 briefs. grep -n 'RULED 2026-10-04' in the obpis directory of ADR-0.35.0: expect five lines: two in brief 15, one each in briefs 16, 17 and 19, and none in briefs 18 and 20. grep -n 'AMENDED 2026-10-04 (2)' on the ADR-0.35.0 document: expect the Intent paragraph and the scorecard note. uv run -m unittest tests.governance.test_orphaned_implementation: expect 16 tests passing. gh issue view for 1172, 1173, 1174, 1175 and 1176 with --json state: expect OPEN. uv run gz handoff rulings --search 'split in two': expect this handoff's ruling.

## Evidence / Artifacts

Commits, oldest first: 402510908 (the stranded briefs, ADR amendment and session records), c9cb95cb2 (the audit's failure message names the re-claim), f411e9b79 (four rulings recorded in briefs 15 and 16), e32e3d6c5 (the ledger-event and rebuild rulings in brief 15), b296498c1 (the lock-transfer ruling in brief 19), 0a26521cb (the split of item 17 into items 17 and 20), with records-only sync commits between them; HEAD when written a3164df53.

Amended: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`, `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-15-pipeline-run-position.md`, `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-16-next-command-for-position.md`, `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-17-stage-procedure-served-by-runtime.md`, `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-19-lock-continuity-across-sessions.md`. New brief: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-20-pipeline-skill-cutover.md`.

Direct fix: `src/gzkit/governance/trust_audits/orphaned_implementation.py`, `tests/governance/test_orphaned_implementation.py`, `docs/user/manpages/validate.md`.

Records read: `docs/governance/attested-req-subject-retirement.md`, `docs/governance/pipeline-marker-migration-path.md`, `docs/governance/trust-doctrine.md`, `docs/governance/state-doctrine.md`, `docs/governance/advisory-rules-audit.md`, `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/obpis/OBPI-0.13.0-03-structured-stage-outputs.md`, `docs/governance/GovZero/obpi-decomposition-matrix.md`.

Insights: `.gzkit/insights/agent-insights.jsonl` (two rows from this session under scope orphaned-implementation-audit: the defect and its resolution).

Predecessor: `.gzkit/handoffs/20261004T154706Z-tune-up-briefs-15-19-in-flight-adr-law.md`, whose resume decision is booked proceed under session 9c2ae708-89a4-4ea2-8ed7-8b2ebaa37c77 with the operator's words. The exit bookmark `.gzkit/handoffs/20261004T155354Z-session-exit-bookmark.md` is superseded by this document. No issue was filed, commented or closed.

## Settled Rulings

1361 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
