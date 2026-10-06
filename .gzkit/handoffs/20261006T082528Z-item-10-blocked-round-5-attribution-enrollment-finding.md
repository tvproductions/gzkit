---
mode: CHECKPOINT
adr_id: ADR-0.35.0
branch: main
timestamp: '2026-10-06T08:25:28Z'
agent: claude-code
obpi_id: OBPI-0.35.0-10-classification-reader-and-ownership
session_id: 199aeb4b-2daf-4a9f-8812-17747bc4769e
continues_from: .gzkit/handoffs/20261006T063550Z-item-10-blocked-round-4-absent-scorecard-finding.md
---

## Current State Summary

This session resumed the 06:35Z checkpoint of 2026-10-06, presented its claims against live state, and worked two operator rulings. Item 10 (OBPI-0.35.0-10-classification-reader-and-ownership) is NOT complete and NOT attested. It is in Stage 4 and recorded as blocked on the operator a third time: round 5 refuted with one new finding, no repair was attempted and no sixth round was dispatched.

Done and pushed, oldest first. (1) GHI #1178 fixed and closed: commit eeb4f2758 makes the Windows branch of the file lock repeat its bounded call while it expires with a deadlock error; two tests run that branch on every platform; CI passed on both platforms. (2) GHI #1179 filed, open and unselected: the red witness for a commit crashes with no receipt when a mutant makes the tests hang. (3) The round 4 block was cleared with the unblock verb carrying the ruling. (4) Repair, commit 4839e2cf1: with the scorecard absent the audit holds that absence against the pinned identities and fails closed while any is pinned; a project with no scorecard and nothing pinned still has nothing to audit. Three tests written first; the behave feature has a seventh scenario; the manpage and the scorecard paragraph list the case. (5) The refresh on a clean tree at a6fe3e0d6: lint, typecheck, the full unit suite (11469 tests, 7 skipped), the module's 64 tests, the strict docs build, the behave feature and nine validator scopes passed; all ten proofs re-executed valid, twenty-three controls each killed on its own assertion; brief-drift clean; the packet rewritten by the narrator and replayed VERIFIED. (6) Round 5 by Codex, tier 1, receipt arb-step-codexadversary-b1e97958254b472193064ffcee97e1bf, reviewed commit b1c510a7a: approved all ten proofs, recorded 23 replays, closed all six findings then open, and raised codex-035010-attribution-enrollment-bypasses-pins-r5 on REQ-0.35.0-10-02. The review is imported. (7) The block is recorded; the packet and the brief's Change Log state the round 5 result; the packet replays VERIFIED.

## Important Context

The open finding. In a project with no ownership declaration, one scorecard row attributed to a skill file and one pinned identity, emptying the scorecard makes the audit report 0 errors and 0 rows with the pinned file untouched. Cause: _resolve_population (src/gzkit/governance/trust_audits/bullet_retention.py) returns on its not-enrolled path, before the pinned check, when no declaration exists and the legacy reader sees no attributed row. The orchestrator reproduced it on a copy of the reviewer's fixture. The live repository carries an ownership declaration and is not on this route: the reviewer observed its emptied, prose-only, directory and unreadable scorecards each failing closed.

The root repeats. Round 4's weakest point was an entry-point early return before the pinned check; round 5's is a second entry decision before the pinned check, and that decision depends on what the legacy reader still reads. The orchestrator's reading of the repair, unruled and not attempted: let the pinned file decide whether the pinned check runs. A project whose pinned file lists any identity goes to the strict path whatever the scorecard, the declarations or the attributions say; the absent-scorecard function of 4839e2cf1 then becomes one case of that rule. What would remain is the removal of the pinned file together with every sign of enrollment, which is a coordinated edit of committed files.

Unruled scope statements. Rounds 4 and 5 were each told that a coordinated edit of the scorecard and the pinned file is out of scope, and round 5 also that a coordinated removal of both is. Both are the orchestrator's statements. Neither reviewer found a requirement that contradicts them, and the round 5 finding uses neither.

Also from round 5, as an observation and not a finding: a scorecard holding invalid UTF-8 raises an unhandled decode error and exits 1, which is neither a clean result nor the audit's normal error. It sits in the same function a repair would touch.

What a further round needs is unchanged from the 06:35Z checkpoint: any edit under the audited population stales all ten proofs and all imported reviews, so the six closures of round 5 will be listed open again and the reviewer must be asked to close seven findings. This session's order worked and took about ninety minutes end to end: failing test, repair, commit with the Task trailer TASK-0.35.0-10-02-01, sync so the ledger is committed, the receipted baseline on the clean tree, all ten proofs from specifications rebuilt from the newest record per requirement, the narrator, the replay with colour disabled, stage all, the per-change check, sync, the adversary workspace, then dispatch. Round 5 took fifteen minutes.

Things that cost time. The red witness for a commit hangs for ten minutes and then crashes when a mutant produces an endless loop (GHI #1179): a test of code that waits forever must bound itself with a thread and a timeout. The narrator's packet comes back as a hand-back message; its text can be lifted from its transcript by searching for the string that begins with the packet's first heading. The acceptance frame function returns a list of lines, not a string. Running the receipted steps from a script file that records each exit status avoids the verifier-pipe hook's refusals. The proofs mutate source in place, so nothing else may run against the tree while they execute. The lock is held by agent claude-code-b4d3b30a until 2026-10-06T20:20Z; precomplete accepted it from this session.

Workflow fronts (source: docs/governance/build-to-1.0-campaign-2026-09-20.md, Workflow fronts section). Handoff system: worked (resume presented and ruled; this document folds in the 06:43Z exit bookmark). GHI triage: not run; one issue fixed and closed (#1178), one filed (#1179). ADR and OBPI campaign: ADR-0.35.0 still reads 9 of 20; item 10 blocked in Stage 4. New R&D: not touched. The three-pillars hold on GHI #1028 is unchanged.

## Decisions Made

- [operator-ruled] GHI #1178 is drawn now, ahead of the item 10 decision (verbatim: "yes to 1178").
- [operator-ruled] The round 4 finding is repaired and a fifth focused Codex round is run (verbatim: "A"). Rejected alternatives offered: repair it and close it by the operator's own review as the human-adversary tier; rule the absent-scorecard case out of scope in the brief; hold item 10 and move to the tune-up items.
- [agent-chose] Booked the ruling "A" on the resumed handoff as proceed, and did not book "yes to 1178" there because it ruled on none of the handoff's advised steps.
- [agent-chose] Put the retry loop inside the Windows branch of the file lock and tested it by executing a second copy of the module with the platform reading win32 and a stand-in lock module, after two earlier shapes left a production line no test on this platform could fail.
- [agent-chose] Amended the unpushed fix commit for GHI #1178 three times instead of stacking corrections, so that the red witness graded one commit carrying the final tests.
- [agent-chose] Filed GHI #1179 for the red witness crash and did not fix it, because it is an independent discovery outside the GHI #1178 work order.
- [agent-chose] Left audited_population returning no rows for an absent scorecard and reported the failure through validate_bullet_retention alone; the round 5 reviewer judged that this reports what was read.
- [agent-chose] Kept a project with no scorecard and nothing pinned clean, because a surface can be enrolled for section ownership with no advisory scorecard.
- [agent-chose] Did the repair single-driver under the 2026-10-03 declaration, as the three earlier repairs were. Unreviewed by the operator.
- [agent-chose] Told the round 5 reviewer that a coordinated removal of the scorecard and the pinned file is out of scope, and asked it to flag any requirement that contradicts that; it flagged none. Unreviewed by the operator.
- [agent-chose] Wrote the round 5 paragraphs of the packet directly from the reviewer's report and the reproduction, without a second narrator dispatch; the packet says so.
- [agent-chose] Stopped after round 5: imported the refuting review, reproduced its counterexample, recorded the block, attempted no repair and dispatched no sixth round.

## Immediate Next Steps

1. Put the item 10 decision to the operator and wait: whether the entry decision is redesigned so that a pinned identities file alone puts a project on the strict path, and how that repair is independently closed. The options drafted this session: redesign and run a sixth focused Codex round (recommended); redesign and have the operator close it by their own review, recorded as the human-adversary tier; rule a project enrolled by attribution alone out of scope in the brief, which still needs independent closure; or hold item 10 and move to the tune-up items.
2. Ask the operator, as a separate question, to rule the two scope statements on coordinated edits given to the round 4 and round 5 reviewers, since they bound whatever the next reviewer is asked.
3. On the operator's ruling, clear the block with the unblock verb carrying their words, then act through the pipeline in the order given in Important Context. A repair folds in the unhandled decode error the round 5 reviewer observed.
4. If acceptance reads ready after the closure, present Stage 4 and wait for the attestation in the operator's own words, then run Stage 5.
5. Before 2026-10-06T20:20Z, tell the operator the item 10 lock reaches its TTL then and will be reaped by the next session start after that.

## Pending Work / Open Loops

Open on item 10: finding codex-035010-attribution-enrollment-bypasses-pins-r5 awaits a ruled repair and independent closure. The ten proofs and the round 5 approvals and closures are current only until the next edit under the audited population. The brief's evidence sections are unfilled, its body status line still reads Draft while its frontmatter reads Active, and the Step 4b section the heavy lane requires is written at Stage 5.

Unreviewed by the operator and named in the packet: the allowlist addition of data/config_registry.json; four repairs done single-driver; the two scope statements on coordinated edits; the round 5 packet paragraphs written without the narrator.

GHI #1179 is open and unselected. After item 10 the operator initiates items 15, 16, 17 and 20 with 18 and 19 among them, then 11 to 13.

Everything in the Pending Work of the 01:01Z checkpoint of 2026-10-06 still stands and is not restated here: the tautological debt schedule (breach on 2026-10-09 unless more ops are retired), GHI #1177 and GHI #1039 open and unselected, the insight on the mis-bound covering test, the untracked run of malformed covers warnings, the unverified items inherited from the 19:48Z handoff of 2026-10-05, the design dialogue of session 3e386d1a-fbc8-4e8c-bacd-0c6f024b2723 with no authored account, and the two rulings the operator still owes.

Left alone: stale Codex broker processes and earlier disposable review checkouts from other sessions. This session's checkout was deleted.

## Verification Checklist

The ahead and behind count of main against origin: expect 0 0 after the sync. The last three CI workflow runs: expect success on completed runs. The OBPI lock list: expect one ACTIVE lock for OBPI-0.35.0-10 held by claude-code-b4d3b30a until 2026-10-06T20:20Z. The OBPI status of OBPI-0.35.0-10-classification-reader-and-ownership: expect Runtime State IN PROGRESS and Completion PENDING. The stage4 acceptance status JSON: expect ready false, five reviews, one open finding codex-035010-attribution-enrollment-bypasses-pins-r5, input digest beginning 73fa08cc456b, and no stale-proof blocker while the audited population is untouched. Launching the pipeline for item 10: expect a refusal naming the block. The bullet-retention scope: expect exit 0 with no advisory lines. A count of audited_population rows: expect 178, 31 with authority corpus. A count of the identities in data/advisory_scorecard_identities.json: expect 178. The unit module tests.governance.test_bullet_retention: expect 64 tests OK. The unit module tests.test_file_lock: expect 8 tests OK. The behave feature features/classification_ownership.feature: expect 7 scenarios passed. The packet replay with colour disabled: expect VERIFIED. The ADR status of ADR-0.35.0-canon-entry-corpus-landing: expect 9 of 20. GHI #1178: expect closed. GHI #1179: expect open. A rulings search for "fifth focused Codex round": expect this handoff's ruling.

## Evidence / Artifacts

Commits this session, oldest first: eeb4f2758 (the file-lock fix for GHI #1178), d9a5bf5bc (records sync), 4839e2cf1 (the round 4 repair), a6fe3e0d6 (records sync, the baseline's commit), b1c510a7a (packet and records as reviewed in round 5), ce75fbe5d (the round 5 record), and the sync commit that carries this handoff.

Item 10 surfaces: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-10-classification-reader-and-ownership.md` (its Change Log indexes every correction and ruling, round 5 included), `.gzkit/evidence/OBPI-0.35.0-10-classification-reader-and-ownership.stage4a.md`, `src/gzkit/governance/trust_audits/bullet_retention.py`, `tests/governance/test_bullet_retention.py`, `data/advisory_scorecard_identities.json`, `features/classification_ownership.feature`, `features/steps/classification_ownership_steps.py`, `docs/governance/advisory-rules-audit.md`, `docs/user/manpages/validate.md`.

File-lock surfaces: `src/gzkit/file_lock.py`, `tests/test_file_lock.py`.

Receipts, held under artifacts/receipts: arb-ruff-82c1c0a0960344f8b9dd20ca6bccee08, arb-step-typecheck-1c8f1bf7588449c9a96869fa1185120c, arb-step-unittest-95997dbe75684cfdb5c96e47ca40b7a9 (full suite), arb-step-unittest-8c0ef40be3064fc4a7657ff97c39b43a (module), arb-step-mkdocs-8676554c2a6f48abb3e5b44246347790, arb-step-behave-51a785b4f3244307b110b09b5db7f109, arb-step-codexadversary-b1e97958254b472193064ffcee97e1bf (round 5, imported), arb-red-commit-eeb4f2758575-b3e374ea71ad483d837daab3ed904bd4 (the file-lock fix, verdict driven). Current proof ids are in the packet.

Predecessor: `.gzkit/handoffs/20261006T063550Z-item-10-blocked-round-4-absent-scorecard-finding.md`, superseded by this document. Folded in: `.gzkit/handoffs/20261006T064310Z-session-exit-bookmark.md`.

## Settled Rulings

1410 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
