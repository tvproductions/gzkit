---
mode: CHECKPOINT
adr_id: ADR-0.35.0
branch: main
timestamp: '2026-10-06T09:32:43Z'
agent: claude-code
obpi_id: OBPI-0.35.0-10-classification-reader-and-ownership
session_id: 29e22289-02c1-4bc3-ac62-be4b2237ed50
continues_from: .gzkit/handoffs/20261006T083010Z-item-10-round-5-ruled-redesign-and-round-6-not-started.md
---

## Current State Summary

This document supersedes the 08:30Z checkpoint of 2026-10-06. That checkpoint's five advised steps are worked through the first four; the fifth is open at its human gate.

Item 10 (OBPI-0.35.0-10-classification-reader-and-ownership) is NOT complete and NOT attested. It is in Stage 4 with acceptance reading ready: no blocker, no open finding. Step 4b round 6 (Codex, tier 1, receipt arb-step-codexadversary-60bd7975823d4d7182d839b10f419579, reviewed commit d14696086) returned CORROBORATED-WITH-CAVEATS, not-refuted, with the review object reading accepted. It approved all ten current proofs, recorded 28 replays, closed all seven findings and raised none. The review is imported. Precomplete passes all eleven checks. Stage 4 was presented to the operator in the session that wrote this document; the attestation had not been given when this was written, so Stage 5 has not started.

Done and pushed this session, oldest first. (1) The 08:30Z handoff was presented with each claim checked against live state, and the operator ruled proceed. (2) Repair, commit 92c12bdd5: the pinned identities file alone decides whether the pinned check runs. A project whose file lists any identity, or cannot be read, is read strictly whatever the scorecard, the ownership declarations or the attributions say. A file the audit cannot decode as UTF-8 is a finding where the audit raised: the scorecard, the pinned file, a per-turn surface file, an attributed source file and an advisor-QC receipt. Seven tests written first; the behave feature has an eighth scenario; the manpage and the scorecard paragraph state the rule. (3) The receipted baseline on a clean tree at 33f36a47e: lint, typecheck, the full unit suite (11476 tests, 7 skipped), the module's 71 tests, the strict docs build and the behave feature passed. (4) The operator ruled the scope of coordinated edits; the brief carries a Threat Model section with the text the operator selected. (5) All ten proofs re-executed valid against the amended brief, 28 controls each killed on its own assertion; the packet was rewritten by the narrator and replayed VERIFIED. (6) Round 6 dispatched at 09:13Z, returned at 09:26Z, imported. (7) The packet and the brief's Change Log state the round 6 result; the packet replays VERIFIED; the per-change check passed; synced at 192437a55.

## Important Context

The repair in one sentence: in src/gzkit/governance/trust_audits/bullet_retention.py the function _pins_identities is read first by _resolve_population, and the legacy return now needs nothing pinned AND no ownership declaration AND no attributed row. Rounds 4 and 5 each found an entry decision made before the pinned check; the round 6 reviewer found no clean result reachable with identities pinned and a pinned identity lost.

The boundary is now the operator's and lives in the brief's Threat Model section: an edit confined to the scorecard, or to the pinned file, fails closed; a change made to both in one edit is out of scope, as is anyone who can write the files of record directly. Measured on a copy of the live inputs at 33f36a47e: every single-file edit failed closed, and a row removed with its identity, or the scorecard emptied or removed with the pinned list emptied or the file removed, passed clean. The section is part of the proof contract: adding it staled all ten proofs, which were re-run. Any later edit to the brief outside its Change Log and history sections does the same.

The round 6 reviewer's weakest point is a verification gap, not a counterexample: historical byte preservation for REQ-0.35.0-10-05 cannot be compared in a checkout with no git history. It also could not authenticate the six quality receipts and did not rerun the full suite, lint, typecheck, the docs build or behave. The packet lists these under Limits and disclosures.

A defect outside the brief is recorded as an insight and not repaired: load_registry in src/gzkit/registries.py raises a raw UnicodeDecodeError for a registry file that is not UTF-8. The Draft brief OBPI-0.39.0-02-tolerance-contract under ADR-0.39.0 names that file for absent and malformed handling, so the route is the operator's. Item 10's audit catches the error locally for the pinned file.

Things that cost time this session. A search of src, tests, features and scripts for callers of a private function missed a dated evidence script under docs, and the commit hook's typecheck caught it; search the whole repository with git grep before changing a signature. The narrator persona stopped at its ten-turn limit having only read; resuming it with an instruction to copy the packet and apply one script of exact replacements produced the packet in a few calls. The Codex reviewer returned only the review object as its final message and wrote its prose report into its checkout; copy that directory out before deleting the checkout. The reviewer's report and logs from round 6 are in this session's scratch directory and are not committed. The red witness for a requirement whose covering tests are old runs against a reconstructed base and returns an inconclusive error class; it cannot witness a repair made in flight.

If the operator attests: Stage 5 begins with the closure-narrative preview, then gz obpi complete with the attestation text, then the Step 4b section in the brief, marker cleanup, two syncs and the sync verb. The brief's Implementation Summary and Key Proof sections are still unfilled and are supplied at completion. The lock is held by agent claude-code-b4d3b30a until 2026-10-06T20:20Z; precomplete accepted it from this session.

Workflow fronts (source: docs/governance/build-to-1.0-campaign-2026-09-20.md, Workflow fronts section). Handoff system: worked (resume presented and ruled; this document written). GHI triage: not run; no issue filed or closed. ADR and OBPI campaign: ADR-0.35.0 still reads 9 of 20; item 10 ready at its human gate. New R&D: not touched. The three-pillars hold on GHI #1028 is unchanged.

## Decisions Made

- [operator-ruled] The 08:30Z handoff's advised steps are worked (verbatim: "proceed").
- [operator-ruled] A coordinated edit of the scorecard and its pinned identities file is outside what item 10's audit must catch, and the boundary is written into the brief as a Threat Model section (verbatim selection: "Out of scope, in the brief (Recommended)"). Rejected alternatives offered: in scope, with a shrink-only guard on the pinned file before round 6; leave it unruled; hold item 10.
- [agent-chose] Continued single-driver under the 2026-10-03 declaration. The operator was asked single-driver or dispatch when the handoff was presented, answered "proceed" and did not choose. Unreviewed by the operator.
- [agent-chose] Counted a pinned file that cannot be read as pinning, so the round 4 behaviour for an absent scorecard holds and a corrupt pinned file is never read as nothing pinned. The round 6 reviewer judged that appropriate.
- [agent-chose] Repaired the whole class the round 5 reviewer's decode observation belonged to, five reads in the one module, each test first, instead of the scorecard alone.
- [agent-chose] Kept the signatures of the two private readers and put the decode check in front of them, after the commit hook showed a dated evidence script under docs imports one of them. The scorecard is read up to three times in one audit as a result.
- [agent-chose] Caught the pinned file's decode error in the audit module and did not edit the registry loader, because a Draft brief of another ADR names that file. Recorded as an insight.
- [agent-chose] Asked the scope question after the repair and the first proof run and before the packet, so the measured results could be shown; the answer staled the proofs once and they were re-run.
- [agent-chose] Wrote the round 6 paragraphs of the packet directly from the reviewer's report, without a second narrator dispatch; the packet says so.
- [agent-chose] Wrote this checkpoint at the Stage 4 gate so the two rulings are booked and the state is carried if the session ends before the attestation.

## Immediate Next Steps

1. Confirm against live state that acceptance still reads ready and nothing under the audited population changed since 192437a55, then put Stage 4 to the operator from the packet with the replay verdict and the round 6 verdict, and wait for the attestation in the operator's own words.
2. On attestation, run Stage 5 through the pipeline: preview the Implementation Summary and Key Proof, run the completion verb with the operator's words and the receipt ids, write the brief's Step 4b section, remove the pipeline markers, sync, run the OBPI sync verb and the ADR status, sync again.
3. If the operator rejects, record the feedback in the brief's Change Log and return to the repair stage with it.
4. Put the registry loader's decode defect to the operator for routing, naming the Draft brief OBPI-0.39.0-02-tolerance-contract and ADR-0.39.0.
5. If the lock was reaped after 2026-10-06T20:20Z, claim it again before Stage 5.

## Pending Work / Open Loops

Open on item 10: the operator's attestation. The brief's evidence sections are unfilled, its body status line still reads Draft while its frontmatter reads Active, and the Step 4b section the heavy lane requires is written at Stage 5.

Unreviewed by the operator and named in the packet: the allowlist addition of data/config_registry.json; five repairs done single-driver; the round 5 and round 6 packet paragraphs written without the narrator.

Recorded as an insight and unrouted: the registry loader's raw decode error. Seen and not tracked: running the type checker over the whole tree, outside the scope the project gate uses, reports 14 diagnostics in the behave step files, one of them in item 10's own steps file; the project gate passes. The per-change check prints an advisory that the flag ops.product_proof is past its deadline.

After item 10 the operator initiates items 15, 16, 17 and 20 with 18 and 19 among them, then 11 to 13. GHI #1179 is open and unselected.

Everything in the Pending Work of the 01:01Z checkpoint of 2026-10-06 still stands and is not restated here: the tautological debt schedule (breach on 2026-10-09 unless more ops are retired), GHI #1177 and GHI #1039 open and unselected, the insight on the mis-bound covering test, the untracked run of malformed covers warnings, the unverified items inherited from the 19:48Z handoff of 2026-10-05, the design dialogue of session 3e386d1a-fbc8-4e8c-bacd-0c6f024b2723 with no authored account, and the two rulings the operator still owes.

Left alone: stale Codex broker processes and earlier disposable review checkouts from other sessions. This session's checkout was deleted.

## Verification Checklist

The ahead and behind count of main against origin: expect 0 0 after the sync. The last three CI workflow runs: expect success on completed runs. The OBPI lock list: expect one ACTIVE lock for OBPI-0.35.0-10 held by claude-code-b4d3b30a until 2026-10-06T20:20Z, or none if a session start after that reaped it. The OBPI status of OBPI-0.35.0-10-classification-reader-and-ownership: expect Runtime State IN PROGRESS and Completion PENDING. The stage4 acceptance status JSON: expect ready true, six reviews, no blocker, no open finding, input digest beginning 829bd985fc73. The precomplete check: expect exit 0 and all eleven preconditions met. The bullet-retention scope: expect exit 0 with no advisory lines. A count of audited_population rows: expect 178, 31 with authority corpus. A count of the identities in data/advisory_scorecard_identities.json: expect 178. The unit module tests.governance.test_bullet_retention: expect 71 tests OK. The behave feature features/classification_ownership.feature: expect 8 scenarios passed. The packet replay with colour disabled: expect VERIFIED. The brief: expect a Threat Model section after the Identity and Reconciliation Contract. The ADR status of ADR-0.35.0-canon-entry-corpus-landing: expect 9 of 20. GHI #1179: expect open. A rulings search for "Out of scope, in the brief": expect this handoff's ruling.

## Evidence / Artifacts

Commits this session, oldest first: 92c12bdd5 (the round 5 repair), 33f36a47e (records sync, the baseline's commit), d14696086 (the Threat Model section, the packet as reviewed in round 6, and records), 192437a55 (the round 6 record), and the sync commit that carries this handoff.

Item 10 surfaces: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-10-classification-reader-and-ownership.md` (its Threat Model section and its Change Log, which indexes every correction and ruling, round 6 included), `.gzkit/evidence/OBPI-0.35.0-10-classification-reader-and-ownership.stage4a.md`, `src/gzkit/governance/trust_audits/bullet_retention.py`, `tests/governance/test_bullet_retention.py`, `data/advisory_scorecard_identities.json`, `features/classification_ownership.feature`, `features/steps/classification_ownership_steps.py`, `docs/governance/advisory-rules-audit.md`, `docs/user/manpages/validate.md`.

Outside the brief, named above: `src/gzkit/registries.py`, `docs/governance/obpi-run-cost-2026-10-03-evidence/trial_eval_probes.py`.

Receipts, held under artifacts/receipts: arb-ruff-890637c24ed94fa590f5e9e5ef6c5f2c, arb-step-typecheck-1f68cbe2743f47f289d58add74c71e7a, arb-step-unittest-ff410e92a866415ca8c76d3746c019af (full suite), arb-step-unittest-cad416370b9045f4a0e5c5d81a7efd84 (module), arb-step-mkdocs-0b67da2c160042f0a21e77fc1a256065, arb-step-behave-672c45b33af5432fb42e2a703d275e20, arb-step-codexadversary-60bd7975823d4d7182d839b10f419579 (round 6, imported), arb-red-REQ-0.35.0-10-02-5e63772bebc34ff9a2abff163591b6ba (inconclusive, reconstructed base). Current proof ids are in the packet.

Predecessor: `.gzkit/handoffs/20261006T083010Z-item-10-round-5-ruled-redesign-and-round-6-not-started.md`, superseded by this document.

## Settled Rulings

1413 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
