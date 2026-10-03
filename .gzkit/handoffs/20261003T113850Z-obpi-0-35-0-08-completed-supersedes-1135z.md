---
mode: CREATE
adr_id: ADR-0.35.0
branch: main
timestamp: '2026-10-03T11:38:50Z'
agent: claude-code
session_id: 553e5afb-48e8-4cae-be4a-db046a3690ba
continues_from: .gzkit/handoffs/20261003T113554Z-obpi-0-35-0-08-completed-batch-rescinded-cost-concern.md
---

## Current State Summary

Resumed the predecessor. The operator rescinded batch initiation of OBPIs; it is recorded as campaign plan § Amendments 2026-10-03 (2), with the Topmost line and the evidence README updated. The operator then initiated OBPI-0.35.0-08 through gz-obpi-pipeline. It is attested_completed (attestor g0, "attest completed"): the shared rendition-drift advisory now cites the corpus->rendition seam and prints the attested gz content land command, guards its own emission, and shell-quotes the surface. Commits 2f39139d7 (the OBPI) and bc447b652 (git-sync) are pushed; a first handoff written at 11:35Z transcribed an ADR count, which the pre-push gate refuses, so this one supersedes it and rides the next sync. Read the landed OBPI count from uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing. The run was expensive and the operator objected to it: six Stage-2 review rounds, two Step-4b Codex rounds plus a re-issue, about ten full proof runs, and one covering test added after attestation because the orchestrating agent had carried a blocking RED verdict past Stage 3.

## Important Context

Operator concern, verbatim: "you even wanted to codex again? something is very broken." The ruling that goes with it is booked in the rulings store by the superseded handoff (gz handoff rulings --search unacceptable); neither is canon in the pipeline skill yet. What cost the rounds, so the next run does not repeat it: a RED witness of failure_class none is never erased by an acceptance proof (red_parity.py), and the validator only bites once the brief is Completed, so treat none as blocking at Stage 3 and repair it before the ceremony. The acceptance digest covers src, tests, features, data, scripts, canonical rules and schemas, workflows and config files, plus the brief's normative sections including Demo; any edit there stales every proof and review, while the brief's Evidence section and docs do not. gz obpi present-evidence runs the brief's Demo and requires every line to exit 0. The acceptance importer refuses a review that reuses an earlier finding id with different text; tell a reviewer to mint new ids for unmapped observations. gz obpi adversary-workspace copies tracked and modified files only, so an untracked packet must be copied in by hand. The Codex plugin's task subcommand treats an unknown flag as a prompt and has no help flag; resume a reviewer thread with --resume-last at the same cwd. gz git-sync refuses to sweep src or tests changes: commit them first under their own message with Task trailers. Launching the pipeline sets the parent ADR to Accepted (GHI #1014) and does not regenerate adr-status.md, so run gz register-adrs or the unit suite fails. gz obpi dispatch records only while a pipeline marker exists. zsh does not split an unquoted variable into words. Workflow fronts (source: the campaign plan § Workflow fronts): adr/obpi campaign and handoff system were worked; ghi triage was not run; new R&D was not touched.
 A handoff may not transcribe an ADR's landed count: name the gz adr status command instead, or the pre-push gate refuses the push.

## Decisions Made

- [agent-chose] Superseded the handoff written at 11:35Z the same day, because it transcribed an ADR count that the transcribed-counts validator refuses at push; the operator rulings of this traversal were booked by that handoff and are carried here by reference, not restated.
- [agent-chose] Read the rescission as covering batch initiation only; the 2026-10-03 draw order was left standing.
- [agent-chose] Filed no GHI; every out-of-brief discrepancy is recorded with gz insights remember and in the OBPI-0.35.0-08 brief's Change Log.

## Immediate Next Steps

1. Decision for you: the pipeline cost concern. Whether the post-attestation rule (move forward, note the discrepancy, GHI it) and a bound on proof, review and gate re-runs per OBPI become canon in the gz-obpi-pipeline skill, and whether OBPI-0.35.0-10 through OBPI-0.35.0-13 are re-scoped smaller before the next one is drawn.
2. Decision for you: route the recorded discrepancies to GHIs through ghi-author. They are: the compose-and-commit recovery prose still in the gz-content-remember skill, docs/user/runbook.md, the rendition-freshness gate and retire.py; the gzkit.ledger_events import cycle; the pipeline launch not regenerating adr-status.md, with the campaign plan's stale 2026-08-12 Draft-holds paragraph; red-parity not biting on a none witness until after completion; the OBPI-0.35.0-08 brief frontmatter allowlist omitting src/gzkit/core/attestor_names.py; and whether Requirement 1 of that brief reaches an output fault on the success line or ledger append in remember.py.
3. Drain tautological-test debt before 2026-10-06, when the ceiling in data/tautological_test_debt_target.json falls below the 228 measured on 2026-10-03. Measure with uv run python .gzkit/chores/decommission-tautological-tests/check_debt_target.py. The chore is operator-paced.
4. The next unlanded OBPI of ADR-0.35.0 is OBPI-0.35.0-10 (pending); OBPI-0.35.0-09 is repudiated and needs your ruling on re-completion. Only you initiate either, through gz-obpi-pipeline.
5. Carried decisions for you: the 2026-10-03 draw order does not say what a session draws when no OBPI is initiated and no GHI blocks feature work; ADR-0.36.0 names obpi_complete_adversarial.py as the Step-4b surface in Boundary Invariant #1, REQ-0.36.0-07-05, REQ-0.36.0-09-07 and its briefs' denied paths, and briefs 02 and 08 cite symbols that were renamed or removed; GHI #1154; re-completion of OBPI-0.0.24-04, OBPI-0.0.26-02 and OBPI-0.34.0-02.

## Pending Work / Open Loops

Open: the predecessor handoff's resume decision was never booked with gz handoff decide; its step 1 (batch initiation) is void by the rescission. The rulings store still carries the P3 batch-initiation ruling; this handoff books the rescission beside it. Unrepaired and unmapped to any REQ in OBPI-0.35.0-08, all in its Change Log: the emission handler's ValueError arm has no covering assertion; sys.stdout.flush shares the emission try; a retire-test docstring still says retirement only shrinks the floor; the drift test class is past the class-size guidance; REQ-06 and REQ-01 share one discriminating substitution; the dated "still UNASSERTED" and "Brief is Draft" sentences remain in three acceptance criteria as contract text. The cross-vendor reviewer did not see the test added after attestation. About 24 Codex broker processes from earlier sessions are still running; none was killed. Reviewer subprocess sessions wrote ten or more session-exit bookmark handoffs, now committed. Not run this session: ghi-triage, and the ancestor handoffs were not read. Carried from the predecessor: GHI #1154 and GHI #1155; the chore_decommission_processed emitter gap; the typecheck control excluding features; the QC rendition-lineage advisory on every gz check; trackers #611, #921, #978, #1028 and #799; 35 chores overdue.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD: expect 0 0 after git-sync; uv run gz obpi status OBPI-0.35.0-08-remember-post-append-advisory: expect ATTESTED COMPLETED; uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing: expect OBPI-0.35.0-08 attested completed, OBPI-0.35.0-09 repudiated and OBPI-0.35.0-10 through OBPI-0.35.0-13 pending; uv run gz obpi lock list: expect no active locks; uv run gz validate --red-parity: expect exit 0; uv run gz validate --adversarial-validation: expect exit 0; uv run -m unittest tests.commands.test_content_remember tests.commands.test_content_retire: expect 80 tests OK; uv run -m behave features/content_remember.feature: expect 7 scenarios passed; uv run python .gzkit/chores/decommission-tautological-tests/check_debt_target.py: re-measure the debt; session orientation's Topmost line: expect it to say batch initiation is RESCINDED.

## Evidence / Artifacts

Commits 2f39139d7 (OBPI-0.35.0-08) and bc447b652 and 8d9da7de6 (git-sync). Receipts: arb-step-codexadversary-c811f6d7391a45ca9b339d772f89b0db (round 1, refuted), arb-step-codexadversary-786f351877904100a29553682a505316 (round 2, accepted), arb-step-unittest-36689e12c5c948b5ba56d8c81d43c322 (11408 tests), arb-red-REQ-0.35.0-08-06-e102516d2600415e879c371edc281c80. Files: `docs/governance/build-to-1.0-campaign-2026-09-20.md`, `docs/governance/completion-cost-2026-10-02-evidence/README.md`, `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-08-remember-post-append-advisory.md`, `src/gzkit/commands/content/_drift.py`, `tests/commands/test_content_remember.py`, `tests/commands/test_content_retire.py`, `features/content_remember.feature`, `features/steps/content_remember_steps.py`, `docs/user/manpages/content.md`, `docs/governance/GovZero/adr-status.md`, `.gzkit/evidence/OBPI-0.35.0-08-remember-post-append-advisory.stage4a.md`, `.gzkit/locks/exchange/20261003T111626Z-OBPI-0.35.0-08-remember-post-append-advisory-complete.md`, `.gzkit/insights/agent-insights.jsonl`. Superseded handoff: `.gzkit/handoffs/20261003T113554Z-obpi-0-35-0-08-completed-batch-rescinded-cost-concern.md`. Its predecessor: `.gzkit/handoffs/20261003T061711Z-amendment-ratified-1163-closed-debt-drained.md`.

## Settled Rulings

1289 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
