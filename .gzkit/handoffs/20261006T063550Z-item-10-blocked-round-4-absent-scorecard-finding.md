---
mode: CHECKPOINT
adr_id: ADR-0.35.0
branch: main
timestamp: '2026-10-06T06:35:50Z'
agent: claude-code
obpi_id: OBPI-0.35.0-10-classification-reader-and-ownership
session_id: 8c49dc52-403b-4eba-99be-fa394029d770
continues_from: .gzkit/handoffs/20261006T010112Z-item-10-blocked-round-3-leading-pipe-finding.md
---

## Current State Summary

This session continued from its own 01:01Z checkpoint of 2026-10-06. The operator ruled "A" on the round 3 block, the repair landed, and a fourth Step 4b round ran. Item 10 (OBPI-0.35.0-10-classification-reader-and-ownership) is NOT complete and NOT attested. It is in Stage 4 and recorded as blocked on the operator a second time: round 4 refuted with one new finding, no repair was attempted and no fifth round was dispatched.

Done and pushed since the checkpoint. (1) The block was cleared with the unblock verb carrying the ruling. (2) Repair, commit 2346d91c5: a rule table runs to its first blank line or heading and a line inside it with no leading pipe is refused by name; an enrolled project's rows are held against 178 pinned identities in data/advisory_scorecard_identities.json, and the audit fails closed on a pinned identity it no longer reads, on a row that is not pinned, and on a pinned file that is missing or unreadable. Four tests were written first; the live-population test compares against the pinned file and the structural oracle is removed; the behave feature gained a sixth scenario. (3) The refresh on the repaired tree: lint, typecheck, the full unit suite (11464 tests, 7 skipped), the strict docs build, the behave feature, the module's 61 tests and nine validator scopes passed; all ten proofs re-executed valid, nineteen controls each killed on its own assertion; brief-drift clean; the packet rewritten by the narrator, corrected in two sentences, replayed VERIFIED. (4) Round 4 by Codex, tier 1, receipt arb-step-codexadversary-25f144e1dcdd4461984e783878b6eb4e, reviewed commit 0171dd746: approved all ten proofs, recorded 19 replays, closed all five findings then open, and raised codex-035010-missing-scorecard-bypasses-pins-r4 on REQ-0.35.0-10-02. The review is imported. (5) The block is recorded; the packet and the brief's Change Log state the round 4 result; the packet replays VERIFIED.

## Important Context

The open finding. Removing only docs/governance/advisory-rules-audit.md, with the pinned identities, the ownership declaration, the corpus and the ledger untouched, makes the audit report 0 errors and 0 rows. Cause: validate_bullet_retention and audited_population (src/gzkit/governance/trust_audits/bullet_retention.py) each return early when the scorecard file is absent, before the enrolled path and the pinned check. The orchestrator reproduced it in the reviewer's checkout. The reviewer's weakest point is that entry-point early return: every recorded control operates below it. This is a different root from the row-shape exclusions rounds 1 to 3 named, and the reviewer asserted no contradiction between any requirement and the stated boundary on coordinated edits of the scorecard and the pinned file.

The orchestrator's reading of the repair, unruled and not attempted: when the scorecard is absent, run the pinned check against zero rows if the pinned file exists, and keep returning nothing otherwise. Requiring a pinned file from every project with an ownership declaration would be wrong, because a project can enroll a surface for section ownership and have no advisory scorecard at all. The other entry conditions were read for the same hole: an unreadable scorecard already reaches the pinned check, because the strict reader returns no rows and the pinned check then names every identity. The manpage and the scorecard's authority paragraph, changed in 2346d91c5, say a pinned identity the audit no longer reads fails closed; that is false for an absent scorecard until the repair lands, and the packet discloses it.

What a further round needs, if the operator authorizes one. Any edit under the audited population stales all ten proofs and all imported reviews, so the five closures of round 4 will be listed open again against new proof ids and the reviewer must be asked to close six findings. The order: failing test first, repair, commit under a fix message with the Task trailer TASK-0.35.0-10-02-01, the ARB baseline, all ten proofs from the specifications (REQ-02's must gain the new test and a control for the early return), brief-drift, present-evidence, the packet through the narrator, the replay with colour disabled, stage all, the per-change check, sync, an adversary workspace, then dispatch through the plugin's task path with write enabled under an ARB step named codexadversary, in the background. Round 4 took about twelve minutes. The alternative closure route is the operator's own review recorded with the acceptance human-review verb as the degraded human-adversary tier; it also needs current proofs first.

Things that cost time and will again. The pipeline refuses to launch while the block stands. The narrator agent has a small turn budget: tell it to make one read of both input files and return text only; its final report can be lifted from its transcript with a script instead of retyped. A new file under data/ needs a declaration in data/config_registry.json, and a name matching the waiver globs (ending in waivers, grandfather or grandfathering) would instead be claimed by the waiver ratchet. Every enrolled test fixture needs a pinned file. ARB receipts recorded while the ledger has uncommitted rows read dirty in their git field. The verifier-pipe hook and the heredoc rule from the 01:01Z checkpoint still apply. The lock is held by agent claude-code-b4d3b30a until 2026-10-06T20:20Z.

Workflow fronts (source: docs/governance/build-to-1.0-campaign-2026-09-20.md, Workflow fronts section). Handoff system: worked (two checkpoints this session, each ruling booked). GHI triage: not run; nothing filed, commented or closed since the checkpoint. ADR and OBPI campaign: ADR-0.35.0 still reads 9 of 20; item 10 blocked in Stage 4. New R&D: not touched. The three-pillars hold on GHI #1028 is unchanged.

## Decisions Made

- [operator-ruled] The round 3 finding is repaired by a committed baseline of row identities together with the narrow reader fix, with one more review round authorized past the two-follow-up bound (verbatim: "A"). Rejected alternatives offered: the narrow reader and oracle fix alone; a contract boundary stating that a rule-table row begins with a pipe; hold item 10 and move to the tune-up items.
- [agent-chose] Made the pinned set an equality check in both directions, so a row that arrives unpinned fails as well as one that leaves.
- [agent-chose] Required the pinned file of every project on the enrolled path and failed closed when it is missing or unreadable; a project with no ownership declaration and no attributed row needs none.
- [agent-chose] Named the file advisory_scorecard_identities.json so the waiver ratchet's filename globs do not claim it, and declared it in data/config_registry.json; added that second path to the brief's allowlist on a reading of the ruling, which named one data file. Unreviewed by the operator.
- [agent-chose] Removed the structural test oracle instead of repairing it, since the pinned file is now what the live test compares against.
- [agent-chose] Did the repair single-driver, as the two earlier repairs were. Unreviewed by the operator.
- [agent-chose] Told the round 4 reviewer that a coordinated edit of the scorecard and the pinned file in one change is out of scope, on the same footing as an edit of the ownership declaration, and asked it to flag any requirement that contradicts that; it flagged none.
- [agent-chose] Stopped after round 4: imported the refuting review, reproduced its counterexample, recorded the block, attempted no repair and dispatched no fifth round.

## Immediate Next Steps

1. Put the item 10 decision to the operator and wait: whether the absent-scorecard early return is repaired, and how the repair is independently closed. The options drafted this session: repair it and run a fifth focused Codex round (recommended); repair it and have the operator close it by their own review, recorded as the human-adversary tier; rule the absent-scorecard case out of scope in the brief, which still needs independent closure; or hold item 10 and move to the tune-up items.
2. On the operator's ruling, clear the block with the unblock verb carrying their words, then act through the pipeline in the order given in Important Context.
3. If acceptance reads ready after the closure, present Stage 4 and wait for the attestation in the operator's own words, then run Stage 5.
4. Before 2026-10-06T20:20Z, tell the operator the item 10 lock reaches its TTL then and will be reaped by the next session start after that.
5. After item 10: the operator initiates items 15, 16, 17 and 20 with 18 and 19 among them, then 11 to 13.

## Pending Work / Open Loops

Open on item 10: finding codex-035010-missing-scorecard-bypasses-pins-r4 awaits a ruled repair and independent closure. The ten proofs and the round 4 approvals and closures are current only until the next edit under the audited population. The manpage and the scorecard's authority paragraph overstate the pinned check for an absent scorecard until the repair lands. The brief's evidence sections are unfilled, its body status line still reads Draft while its frontmatter reads Active, and the Step 4b section the heavy lane requires is written at Stage 5.

Unreviewed by the operator and named in the packet: the allowlist addition of data/config_registry.json; three repairs done single-driver; the scope statement on coordinated edits given to the round 4 reviewer.

Everything in the Pending Work of the 01:01Z checkpoint of 2026-10-06 still stands and is not restated here: the tautological debt schedule (226 outstanding, breach on 2026-10-09 unless more ops are retired), GHI #1177 and GHI #1039 open and unselected, the insight on the mis-bound covering test, the untracked run of malformed covers warnings, the unverified items inherited from the 19:48Z handoff of 2026-10-05, the design dialogue of session 3e386d1a-fbc8-4e8c-bacd-0c6f024b2723 with no authored account, and the two rulings the operator still owes.

Left alone: stale Codex broker processes and earlier disposable review checkouts from other sessions. Both of this session's checkouts were deleted.

## Verification Checklist

The ahead and behind count of main against origin: expect 0 0 after the sync. The last three CI workflow runs: expect success on completed runs. The OBPI lock list: expect one ACTIVE lock for OBPI-0.35.0-10 held by claude-code-b4d3b30a until 2026-10-06T20:20Z. The OBPI status of OBPI-0.35.0-10-classification-reader-and-ownership: expect Runtime State IN PROGRESS and Completion PENDING. The stage4 acceptance status JSON: expect ready false, four reviews, one open finding codex-035010-missing-scorecard-bypasses-pins-r4, and no stale-proof blocker while the audited population is untouched. Launching the pipeline for item 10: expect a refusal naming the block. The bullet-retention scope: expect exit 0 with no advisory lines. A count of audited_population rows: expect 178, 31 with authority corpus. A count of the identities in data/advisory_scorecard_identities.json: expect 178. The unit module tests.governance.test_bullet_retention: expect 61 tests OK. The behave feature features/classification_ownership.feature: expect 6 scenarios passed. The packet replay with colour disabled: expect VERIFIED. The ADR status of ADR-0.35.0-canon-entry-corpus-landing: expect 9 of 20. A rulings search for "committed baseline of row identities": expect this handoff's ruling.

## Evidence / Artifacts

Commits since the 01:01Z checkpoint, oldest first: 2346d91c5 (the round 3 repair), 0171dd746 (packet and records as reviewed in round 4), and the sync commit that carries this handoff with the round 4 record.

Item 10 surfaces: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-10-classification-reader-and-ownership.md` (its Change Log indexes every correction and ruling, round 4 included), `.gzkit/evidence/OBPI-0.35.0-10-classification-reader-and-ownership.stage4a.md`, `src/gzkit/governance/trust_audits/bullet_retention.py`, `tests/governance/test_bullet_retention.py`, `data/advisory_scorecard_identities.json`, `data/config_registry.json`, `features/classification_ownership.feature`, `features/steps/classification_ownership_steps.py`, `docs/governance/advisory-rules-audit.md`, `docs/user/manpages/validate.md`.

Receipts, held under artifacts/receipts: arb-ruff-fff92a26b85243e3957ff797ea8ad5c6, arb-step-typecheck-40be8d4f425f48228dedca95f2a07213, arb-step-unittest-39a14a00921a4dd987621ca43480f455 (full suite), arb-step-unittest-a333abd5b3a341f791e12b41d7c7a18a (module), arb-step-mkdocs-c3ee352e744843edbf3e7e4a0dbc6eb4, arb-step-behave-839b6efceda64c1eafc7a3ae3270103c, arb-step-codexadversary-25f144e1dcdd4461984e783878b6eb4e (round 4, imported). Current proof ids are in the packet.

Predecessor: `.gzkit/handoffs/20261006T010112Z-item-10-blocked-round-3-leading-pipe-finding.md`, superseded by this document.

## Settled Rulings

1408 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
