---
mode: CREATE
adr_id: ADR-0.35.0
branch: main
timestamp: '2026-10-06T09:46:07Z'
agent: claude-code
obpi_id: OBPI-0.35.0-10-classification-reader-and-ownership
session_id: 29e22289-02c1-4bc3-ac62-be4b2237ed50
continues_from: .gzkit/handoffs/20261006T093243Z-item-10-round-6-accepted-stage-4-awaiting-attestation.md
---

## Current State Summary

This document supersedes the 09:32Z checkpoint of 2026-10-06, written by the same session at the Stage 4 gate.

Item 10 (OBPI-0.35.0-10-classification-reader-and-ownership) is COMPLETE and ATTESTED. The operator attested after Stage 4 was presented with the packet, the replay verdict and the round 6 verdict. The completion verb recorded the attestation, wrote the brief's Implementation Summary and Key Proof, flipped the brief to Completed, emitted the receipt and surrendered the lock through its own exchange record. The pipeline ran to the end of Stage 5: the brief carries its Step 4b section, both pipeline markers are removed, the OBPI sync verb passed, and both syncs are pushed. ADR-0.35.0 reads 10 of 20. All ten of the OBPI's tasks read completed. No lock is held.

One gate fired during Stage 5 and was cleared by its own named recovery: the first completion call exited 3 because the brief's reconcile receipt predated the round 6 Change Log entry; the brief-drift verb refreshed it and the second call succeeded. No override flag was used.

## Important Context

What item 10 delivered, for whoever works the next items: the bullet-retention audit reads a corpus-owned row's class from its corpus entry and every other row's from the scorecard; a scorecard row is identified by its section id and row number; the row identities are pinned in data/advisory_scorecard_identities.json and that file alone decides whether the pinned check runs. Adding a scorecard row means adding its identity to the pinned file in the same commit, or the audit fails closed. Removing an identity removes a row from the audited population and follows an operator ruling. The brief's Threat Model section states what the audit does not defend against.

The round 6 reviewer's report and logs sit in the completing session's scratch directory and are not committed. The review object and its 28 replay records are in the ledger through receipt arb-step-codexadversary-60bd7975823d4d7182d839b10f419579.

A defect outside item 10 is recorded as an insight and is unrouted: load_registry in src/gzkit/registries.py raises a raw UnicodeDecodeError for a registry file that is not UTF-8. Draft brief OBPI-0.39.0-02-tolerance-contract under ADR-0.39.0 names that file for absent and malformed handling, so the route is the operator's. Item 10's audit catches the error locally for the pinned file; when the loader is repaired that local catch can go.

The campaign order inside ADR-0.35.0, by the amendment of 2026-10-05, is the tune-up items 15 to 20 next, then items 11 to 13. Only the operator initiates each. Item 09 reads repudiated in the ADR status and is listed outstanding with the others.

Workflow fronts (source: docs/governance/build-to-1.0-campaign-2026-09-20.md, Workflow fronts section). Handoff system: worked (one resume presented and ruled, two authored documents). GHI triage: not run; no issue filed or closed. ADR and OBPI campaign: item 10 completed and attested; ADR-0.35.0 reads 10 of 20. New R&D: not touched. The three-pillars hold on GHI #1028 is unchanged.

## Decisions Made

- [operator-ruled] Item 10 is attested complete (verbatim: "attest completed").
- [agent-chose] Supplied the Implementation Summary and Key Proof by flag at completion. The summary carries the parent ADR's Decision item 9 verbatim, as the brief's Discovery Checklist asks, and the six reconciliation id sets the Change Log said it would hold, each checked against the corpus tail.
- [agent-chose] Cleared the stale reconcile receipt with the brief-drift verb the gate named, and used no override flag.
- [agent-chose] Wrote the brief's Step 4b section from the acceptance record's six imported reviews and the packet's review history.
- [agent-chose] Wrote this document as a concluding handoff, not a checkpoint, because the OBPI is complete and its lock was surrendered by the completion verb.

## Immediate Next Steps

1. Present this handoff's state to the operator and confirm it against live state: item 10 reads ATTESTED COMPLETED, no lock is held, main is in sync, and the CI runs on the last two commits have finished green.
2. Put the registry loader's decode defect to the operator for routing, naming Draft brief OBPI-0.39.0-02-tolerance-contract and ADR-0.39.0.
3. Tell the operator the tautological debt check breaches on 2026-10-09 unless more ops are retired, and that the chore for it is overdue.
4. Wait for the operator to initiate the next item of ADR-0.35.0 through the pipeline skill. The campaign order names the tune-up items 15, 16, 17 and 20, with 18 and 19 among them, ahead of items 11 to 13.

## Pending Work / Open Loops

Nothing is open on item 10. Named in its packet and unreviewed by the operator: the allowlist addition of data/config_registry.json; five repairs done single-driver; the round 5 and round 6 packet paragraphs written without the narrator.

Recorded as an insight and unrouted: the registry loader's raw decode error. Seen and not tracked: running the type checker over the whole tree, outside the scope the project gate uses, reports 14 diagnostics in the behave step files; the project gate passes. The per-change check prints an advisory that the flag ops.product_proof is past its deadline.

ADR-0.35.0 has ten items outstanding: 09 (repudiated, to be re-completed), 11, 12, 13 and 15 to 20. GHI #1179 is open and unselected.

Everything in the Pending Work of the 01:01Z checkpoint of 2026-10-06 still stands and is not restated here: the tautological debt schedule (breach on 2026-10-09 unless more ops are retired), GHI #1177 and GHI #1039 open and unselected, the insight on the mis-bound covering test, the untracked run of malformed covers warnings, the unverified items inherited from the 19:48Z handoff of 2026-10-05, the design dialogue of session 3e386d1a-fbc8-4e8c-bacd-0c6f024b2723 with no authored account, and the two rulings the operator still owes.

Left alone: stale Codex broker processes and earlier disposable review checkouts from other sessions. This session's checkout was deleted.

## Verification Checklist

The ahead and behind count of main against origin: expect 0 0 after the sync. The last three CI workflow runs: expect success on completed runs. The OBPI lock list: expect no active locks. The OBPI status of OBPI-0.35.0-10-classification-reader-and-ownership: expect Runtime State ATTESTED COMPLETED, Proof State recorded, Attestation State recorded and Completion COMPLETE. The OBPI sync verb for it: expect PASS. The task list for it: expect ten tasks completed. The ADR status of ADR-0.35.0-canon-entry-corpus-landing: expect 10 of 20. The brief: expect frontmatter status Completed, a Threat Model section, and a Step 4b section under Evidence. The adversarial-validation scope: expect exit 0. The bullet-retention scope: expect exit 0 with no advisory lines. The unit module tests.governance.test_bullet_retention: expect 71 tests OK. The pipeline marker files under .claude/plans: expect none for item 10. GHI #1179: expect open. A rulings search for "attest completed": expect this handoff's ruling among the results.

## Evidence / Artifacts

Commits since the 09:32Z checkpoint: 4b593dfb8 (the sync that carried that checkpoint), eb33c9aa9 (the completion: the brief's evidence sections, Step 4b section and status, the completion exchange record, the removed markers and the ledger), fdfbc1bfd (the reconcile output), and the sync commit that carries this handoff.

Item 10 surfaces: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-10-classification-reader-and-ownership.md`, `.gzkit/evidence/OBPI-0.35.0-10-classification-reader-and-ownership.stage4a.md`, `src/gzkit/governance/trust_audits/bullet_retention.py`, `tests/governance/test_bullet_retention.py`, `data/advisory_scorecard_identities.json`, `features/classification_ownership.feature`, `features/steps/classification_ownership_steps.py`, `docs/governance/advisory-rules-audit.md`, `docs/user/manpages/validate.md`.

The lock's exchange record: `.gzkit/locks/exchange/20261006T093904Z-OBPI-0.35.0-10-classification-reader-and-ownership-complete.md`.

Receipts, held under artifacts/receipts: arb-ruff-890637c24ed94fa590f5e9e5ef6c5f2c, arb-step-typecheck-1f68cbe2743f47f289d58add74c71e7a, arb-step-unittest-ff410e92a866415ca8c76d3746c019af (full suite, 11476 tests), arb-step-unittest-cad416370b9045f4a0e5c5d81a7efd84 (module, 71 tests), arb-step-mkdocs-0b67da2c160042f0a21e77fc1a256065, arb-step-behave-672c45b33af5432fb42e2a703d275e20, arb-step-codexadversary-60bd7975823d4d7182d839b10f419579 (round 6, imported, accepted).

Predecessor: `.gzkit/handoffs/20261006T093243Z-item-10-round-6-accepted-stage-4-awaiting-attestation.md`, superseded by this document.

## Settled Rulings

1414 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
