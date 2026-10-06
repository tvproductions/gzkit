---
mode: CHECKPOINT
adr_id: ADR-0.35.0
branch: main
timestamp: '2026-10-06T08:30:10Z'
agent: claude-code
obpi_id: OBPI-0.35.0-10-classification-reader-and-ownership
session_id: 199aeb4b-2daf-4a9f-8812-17747bc4769e
continues_from: .gzkit/handoffs/20261006T082528Z-item-10-blocked-round-5-attribution-enrollment-finding.md
---

## Current State Summary

This document supersedes the 08:25Z checkpoint of 2026-10-06, written by the same session five minutes earlier, and adds one thing to it: the operator has ruled on the round 5 block. Everything else in that checkpoint stands and should be read first.

Item 10 (OBPI-0.35.0-10-classification-reader-and-ownership) is NOT complete and NOT attested. It is in Stage 4 with one open finding, codex-035010-attribution-enrollment-bypasses-pins-r5 on REQ-0.35.0-10-02. It is no longer blocked: the operator ruled that the finding is repaired by redesigning the entry decision and that a sixth focused Codex round is run, and asked for this handoff and a sync before that work. The ruling is booked on the 08:25Z handoff as proceed and the block was cleared with the unblock verb carrying the operator's words. No repair has been started. Nothing under the audited population has been edited since round 5 was imported, so the ten proofs and the round 5 approvals and closures are still current.

## Important Context

The repair that was ruled, as it was described to the operator: a pinned identities file that lists any identity puts the project on the strict path by itself, whatever the scorecard, the ownership declarations or the attributions say. In src/gzkit/governance/trust_audits/bullet_retention.py that means the not-enrolled return in _resolve_population no longer fires for a project that pins identities, and the absent-scorecard function added in 4839e2cf1 becomes one case of the same rule. The operator was also told the repair would fold in what the round 5 reviewer observed outside its finding: a scorecard holding invalid UTF-8 raises an unhandled decode error and exits 1, where the audit should return its normal error.

The counterexample to turn into the first failing test: no ownership declaration, one Mechanical scorecard row attributed to .gzkit/skills/demo/SKILL.md with matching text in that file, and a pinned file listing that one identity. Baseline prints 0 errors and 1 row. Emptying the scorecard, replacing it with prose, or removing the row's leading pipe each print 0 errors and 0 rows today, and each must fail closed. Positive controls to keep: a project with no declaration, no attribution and no pinned file stays on the legacy path; an enrolled project with no scorecard and nothing pinned stays clean; a project whose pinned list is empty is not sent to the strict path by that file alone.

A question the operator has not answered, and which bounds the next reviewer's prompt: rounds 4 and 5 were told that a coordinated edit of the scorecard and the pinned file, and a coordinated removal of both, are out of scope because each is visible as a diff of committed files. Both statements are the orchestrator's. After the redesign the remaining route is the removal of the pinned file together with every sign of enrollment, which is the same kind of edit. Ask before the round 6 prompt is written, not before the repair.

The order that worked for round 5, about ninety minutes end to end, is in the 08:25Z checkpoint's Important Context, with the things that cost time. Round 6's reviewer must be asked to close seven findings: the round 5 one and the six round 5 closed, which a re-run of the proofs lists open again against new proof ids. The reusable inputs of this session are in its scratchpad if the host still has them: the reviewer prompt head for round 5, the packet facts file, the proof specifications and the two scripts that run the baseline and the proofs.

The lock is held by agent claude-code-b4d3b30a until 2026-10-06T20:20Z. The next session start after that reaps it, and the pipeline then needs a fresh claim.

Workflow fronts (source: docs/governance/build-to-1.0-campaign-2026-09-20.md, Workflow fronts section). Handoff system: worked (two rulings booked this session, two authored documents). GHI triage: not run; GHI #1178 fixed and closed, GHI #1179 filed and open. ADR and OBPI campaign: ADR-0.35.0 still reads 9 of 20; item 10 in Stage 4, unblocked, repair ruled and not started. New R&D: not touched. The three-pillars hold on GHI #1028 is unchanged.

## Decisions Made

- [operator-ruled] The round 5 finding is repaired by redesigning the entry decision, with a sixth focused Codex round, and a handoff and a sync come first (verbatim: "A, but we need a h/o and git sync"). Rejected alternatives offered: the same redesign closed by the operator's own review as the human-adversary tier; rule a project enrolled by attribution alone out of scope in the brief; hold item 10 and move to the tune-up items.
- [agent-chose] Read "we need a h/o and git sync" as a direction to stop before the repair and hand the work to a later session, so no source or test was edited after the ruling.
- [agent-chose] Booked the ruling on the 08:25Z handoff as proceed and cleared the block with the operator's words, because the decision the block was waiting for has been given.
- [agent-chose] Wrote this document as a checkpoint, as every document in this chain was, because the lock stays held and the work is mid-flight.

## Immediate Next Steps

1. Present this handoff's state to the operator and confirm the ruling still stands before acting, then resume item 10 through the pipeline from the existing marker and lock. If the lock was reaped after 2026-10-06T20:20Z, claim it again first.
2. Write the failing tests for the counterexample in Important Context, observe each fail on its assertion, then make a pinned identities file that lists any identity sufficient for the strict path, and return the audit's normal error for a scorecard that cannot be decoded. Update the manpage, the scorecard's authority paragraph, the behave feature and the brief's Change Log in the same commit, under the Task trailer TASK-0.35.0-10-02-01.
3. Ask the operator to rule the scope statements on coordinated edits of the scorecard and the pinned file before writing the round 6 prompt.
4. Run the refresh in the order the 08:25Z checkpoint gives, extending the REQ-02 proof specification with the new tests and a control for each new guard, and dispatch round 6 through the plugin's writable task path under an ARB step named codexadversary. Import it by its receipt.
5. If acceptance reads ready, present Stage 4 and wait for the attestation in the operator's own words, then run Stage 5. If round 6 refutes, record the block and put the result to the operator; no seventh round without a ruling.

## Pending Work / Open Loops

Open on item 10: finding codex-035010-attribution-enrollment-bypasses-pins-r5 has a ruled repair that is not started. The operator's answer on the coordinated-edit scope statements is owed before round 6. The brief's evidence sections are unfilled, its body status line still reads Draft while its frontmatter reads Active, and the Step 4b section the heavy lane requires is written at Stage 5.

Unreviewed by the operator and named in the packet: the allowlist addition of data/config_registry.json; four repairs done single-driver; the round 5 packet paragraphs written without the narrator. Whether the next repair is done single-driver or with dispatch has not been put to the operator.

GHI #1179 is open and unselected. After item 10 the operator initiates items 15, 16, 17 and 20 with 18 and 19 among them, then 11 to 13.

Everything in the Pending Work of the 01:01Z checkpoint of 2026-10-06 still stands and is not restated here: the tautological debt schedule (breach on 2026-10-09 unless more ops are retired), GHI #1177 and GHI #1039 open and unselected, the insight on the mis-bound covering test, the untracked run of malformed covers warnings, the unverified items inherited from the 19:48Z handoff of 2026-10-05, the design dialogue of session 3e386d1a-fbc8-4e8c-bacd-0c6f024b2723 with no authored account, and the two rulings the operator still owes.

Left alone: stale Codex broker processes and earlier disposable review checkouts from other sessions.

## Verification Checklist

The ahead and behind count of main against origin: expect 0 0 after the sync. The last three CI workflow runs: expect success on completed runs. The OBPI lock list: expect one ACTIVE lock for OBPI-0.35.0-10 held by claude-code-b4d3b30a until 2026-10-06T20:20Z, or none if a session start after that reaped it. The OBPI status of OBPI-0.35.0-10-classification-reader-and-ownership: expect Runtime State IN PROGRESS and Completion PENDING. The stage4 acceptance status JSON: expect ready false, five reviews, one open finding codex-035010-attribution-enrollment-bypasses-pins-r5, input digest beginning 73fa08cc456b, and no stale-proof blocker while the audited population is untouched. The precomplete check operator_block: expect no outstanding operator ruling. The bullet-retention scope: expect exit 0 with no advisory lines. A count of audited_population rows: expect 178, 31 with authority corpus. The unit module tests.governance.test_bullet_retention: expect 64 tests OK. The behave feature features/classification_ownership.feature: expect 7 scenarios passed. The packet replay with colour disabled: expect VERIFIED. The ADR status of ADR-0.35.0-canon-entry-corpus-landing: expect 9 of 20. GHI #1178: expect closed. GHI #1179: expect open. A rulings search for "sixth focused Codex round": expect this handoff's ruling.

## Evidence / Artifacts

Commits since the 08:25Z checkpoint: eb41e96f9 (the sync that carried that checkpoint) and the sync commit that carries this handoff with the ruling and the unblock record. No source, test, data or doc file changed between them.

Item 10 surfaces: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-10-classification-reader-and-ownership.md`, `.gzkit/evidence/OBPI-0.35.0-10-classification-reader-and-ownership.stage4a.md`, `src/gzkit/governance/trust_audits/bullet_retention.py`, `tests/governance/test_bullet_retention.py`, `data/advisory_scorecard_identities.json`, `features/classification_ownership.feature`, `features/steps/classification_ownership_steps.py`, `docs/governance/advisory-rules-audit.md`, `docs/user/manpages/validate.md`.

Receipts are unchanged from the 08:25Z checkpoint, which lists them. The round 5 review is arb-step-codexadversary-b1e97958254b472193064ffcee97e1bf, held under artifacts/receipts.

Predecessor: `.gzkit/handoffs/20261006T082528Z-item-10-blocked-round-5-attribution-enrollment-finding.md`, superseded by this document.

## Settled Rulings

1411 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
