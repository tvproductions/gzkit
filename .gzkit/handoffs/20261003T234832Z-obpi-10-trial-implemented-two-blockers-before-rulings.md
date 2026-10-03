---
mode: CREATE
adr_id: ADR-0.35.0
branch: main
timestamp: '2026-10-03T23:48:32Z'
agent: claude-code
obpi_id: OBPI-0.35.0-10-classification-reader-and-ownership
session_id: a0f543a5-5dc2-41ff-949b-f036f79ce0a1
continues_from: .gzkit/handoffs/20261003T120228Z-obpi-08-cost-measured-obpi-10-trial-ruled.md
---

## Current State Summary

The operator launched the single-session trial on OBPI-0.35.0-10 in this session, and later ruled to take it through the closing ceremony up to the two operator rulings. The implementation is written and green. The OBPI is NOT complete and NOT attested. At 12:27Z all ten commands in the brief's verification list exited 0 and all 7 behavior REQs had passing covering tests. After that: the lock was claimed (12:35Z, agent claude-code-a0f543a5, 24 hour TTL); ARB receipts were recorded for lint, typecheck, unittest and mkdocs; req_atomic was added to the brief frontmatter; the acceptance record was initialized and ten proofs executed, 9 valid and REQ-0.35.0-10-10 invalid. gz obpi precomplete exits 3 on two checks: plan_audit_receipt and adversarial_validation. The work was uncommitted when this handoff was written and is committed by the git sync that follows it.

## Important Context

What was built: gz validate --bullet-retention now reads a scorecard row's classification from the corpus entry it cites when the row's section is corpus-owned, and from the scorecard otherwise; a broken owned mapping fails closed; an owned section with a live Ambiguous entry refuses to bind; a row attributed to a SKILL.md or an ADR file is retained against that file. Every row names its source in the Notes column as source=<path>[#<section-id>] [entry=<entry-id>]. Measured on the live repo: the effective corpus has zero Ambiguous entries (107 entries), so no retire, remember or land was run and the corpus is untouched. Six owned rows disagree with their corpus entry and print an advisory on every run: Local Agent Rules #7 and #10 and Governance Core #14, #16 and #17a are Mechanical in the scorecard and Judgment in the corpus, so they are no longer retention-enforced; Local Agent Rules #8 is Judgment in the scorecard and Mechanical in the corpus, so it is newly enforced. Proof fragility: the acceptance input digest covers source, tests, features, rules and the brief outside its evidence sections, so any edit there invalidates the ten proofs. The proof specifications were session-local files; the ledger's proof records retain each mutation label. The lock belongs to this session's agent id, and the ARB receipts are scoped to that claim. Cost, measured with the evidence README's script: at tests-green 65 calls and 14.1M cache-read tokens; at 12:41Z after the ceremony 86 calls and 21.3M, peak context 371K, no subagents or siblings; the OBPI-0.35.0-08 baseline was 557 calls and 153.9M. The change is 427 added and 27 removed source lines in two files against 63 and 34 in one file for the baseline. A regex bucketing of the baseline orchestrator's 260 calls put editing and testing at about 7 percent of its tokens, ceremony at 23 percent, review traffic at 12 percent, reading at 31 percent and prose-only turns at 15 percent; the bucketing is heuristic. Operator statements this session, verbatim, recorded as concerns and not as rulings: "the differences in this test were stark"; "I am at a all-time low with gzkit, this is massively discouraging. the overhead of the apparatus does NOT prove itself." Workflow fronts (source: the campaign plan, Workflow fronts section): handoff system was worked (the resume was booked and this handoff written); adr/obpi campaign: OBPI-0.35.0-10 implemented and not completed, ADR-0.35.0 still at 9 of 14; ghi triage was not run; new R&D was not touched.

## Decisions Made

- [operator-ruled] Launch the trial in this session (verbatim: "do this: docs/governance/obpi-run-cost-2026-10-03-evidence/README.md").
- [operator-ruled] Take the OBPI through the closing ceremony and stop before the human-review judgment and the attestation (verbatim: "yes, proceed and stop at my two rulings").
- [operator-ruled] Write this handoff and sync (verbatim: "new handoff, git sync").
- [agent-chose] Made the source attribution mandatory for every scorecard row once a project has an ownership declaration, and wrote it into all 173 live rows; a project with no declaration keeps the old audit. Unreviewed by the operator.
- [agent-chose] Made a corpus and scorecard disagreement a non-failing advisory in which the corpus value binds, reading the brief's Key Proof as requiring it. Unreviewed by the operator.
- [agent-chose] Mapped 31 scorecard rows by hand to AGENTS.md corpus entries; the brief says this mapping is reviewed during planning and no planning step ran. Unreviewed by the operator.
- [agent-chose] Requoted row Local Agent Rules #8 to the surface's wording, and attributed rows Local Agent Rules #12 and Governance Core #13 to the scorecard itself because their rule text is in no per-turn surface.
- [agent-chose] Did not write a plan file after the fact to satisfy the plan audit, and did not reword REQ-0.35.0-10-10; both are left for the operator.
- [agent-chose] Left the lock held at handoff, because the ARB receipts are scoped to that claim and the operator did not ask for a release.

## Immediate Next Steps

1. Ask the operator to rule on REQ-0.35.0-10-10: its witness clause says "citing both paths", the support resolver reads the word after citing as the path, and the proof returns unproven-support. The proposed repair is to cite docs/user/manpages/validate.md in the clause; that changes the contract digest, so all ten proofs are re-run with gz obpi acceptance prove.
2. Ask the operator to rule on the plan audit: no plan file exists because the single-session route skipped plan mode, so the plan_audit_receipt check in gz obpi precomplete is FAIL. The choices are to accept that check red or to write a plan record labelled as written after implementation. Whether gz obpi complete itself checks it is read from code and not run.
3. Once those are settled, show the operator the current proofs from gz obpi acceptance status --stage stage4 and ask for the human-review judgment in the operator's own words; record it with the human-review operation of gz obpi acceptance. Never author it.
4. Then ask for the attestation in the operator's own words and record it with gz obpi complete; the implementation summary must quote parent ADR Decision item 9 verbatim. Never author it.
5. Ask the operator how to reconcile the six rows whose scorecard and corpus classes disagree: reclassify the corpus entries by attested retire and remember, or rescore the rows.
6. After completion, re-run the cost script for session a0f543a5-5dc2-41ff-949b-f036f79ce0a1 and add the trial's figures to the evidence README beside the baseline; the README does not yet hold them.

## Pending Work / Open Loops

Offered to the operator and not started: a gate-by-gate review, from the ledger and the insights history, of which gates have caught something a plain test run would have missed. An independent reviewer session on this diff was suggested to measure what the single session lost in review quality, and was not run. The lock expires 24 hours after 2026-10-03T12:35Z and is owned by this session's agent id; a later session cannot use it as its own, and a release needs a register entry or an abandon category. The brief's evidence sections (Implementation Summary, Key Proof, the gate outputs) are unfilled. bullet_retention.py is about 670 lines against a 600 line authoring guidance that nothing gates. The pipeline's verify stage was not run through gz obpi pipeline, so gate results are in ARB receipts and not in pipeline stage events. Six findings outside the brief's REQs were recorded once each with gz insights remember and not repaired: the brief's Demo command that cannot run, a blank line splitting a scorecard table, scorecard headings that cite sources no longer holding their rows, the Malformed REQ warning lines on every gz call, two oddities in the single-session launch output, and the plan-audit gap on the single-session route. The gz-obpi-pipeline skill is unedited; the operator has seen the comparison and has not ruled on what changes. The predecessor handoff's carried open loops were not worked and stand as written there.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD: expect 0 0 after the sync. uv run gz obpi status OBPI-0.35.0-10-classification-reader-and-ownership: expect Runtime State IN PROGRESS and Completion PENDING. uv run gz obpi lock list: expect one ACTIVE lock for OBPI-0.35.0-10 held by claude-code-a0f543a5 until its TTL passes. uv run gz obpi precomplete OBPI-0.35.0-10-classification-reader-and-ownership: expect exit 3 with plan_audit_receipt and adversarial_validation failing and the other checks passing. uv run gz obpi acceptance OBPI-0.35.0-10-classification-reader-and-ownership status --stage stage4 --json: expect ready false, no open findings, nine valid proofs and REQ-0.35.0-10-10 invalid; a changed input digest means the proofs must be re-run. uv run -m unittest tests.governance.test_bullet_retention: expect 52 tests OK. uv run -m behave features/classification_ownership.feature: expect 5 scenarios passed. uv run gz validate --bullet-retention: expect exit 0 with six advisory lines. uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing: expect 9/14.

## Evidence / Artifacts

Files: `src/gzkit/governance/trust_audits/bullet_retention.py`, `src/gzkit/content/models/corpus.py`, `tests/governance/test_bullet_retention.py`, `features/classification_ownership.feature`, `features/steps/classification_ownership_steps.py`, `docs/user/manpages/validate.md`, `docs/governance/advisory-rules-audit.md`, `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-10-classification-reader-and-ownership.md`, `.gzkit/insights/agent-insights.jsonl`. Receipt ids, held outside the repository tree: arb-ruff-84583a90eb0547419406659b5af9d39a, arb-step-typecheck-3ec1cbf10f374e2cb15e2d95c9a20aa5, arb-step-unittest-76935505860e4c44adff7c0ec8e6e2b0, arb-step-mkdocs-d290d3af4f9f4de3b4f43bebfea967cb. Baseline record and script: `docs/governance/obpi-run-cost-2026-10-03-evidence/README.md`, `docs/governance/obpi-run-cost-2026-10-03-evidence/session_token_cost.py`. Predecessor: `.gzkit/handoffs/20261003T120228Z-obpi-08-cost-measured-obpi-10-trial-ruled.md`, whose resume decision is booked as proceed with the operator's words. Proof ids for REQ-01 through REQ-10 are in the ledger's acceptance records for this OBPI.

## Settled Rulings

1295 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
