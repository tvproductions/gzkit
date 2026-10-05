---
mode: CREATE
adr_id: ADR-0.35.0
branch: main
timestamp: '2026-10-05T23:30:08Z'
agent: claude-code
obpi_id: OBPI-0.35.0-10-classification-reader-and-ownership
session_id: a1f3e3b6-ba47-4c08-940f-7d29d7a22302
continues_from: .gzkit/handoffs/20261005T201134Z-item-10-proceed-ruled-design-thread-pointer.md
---

## Current State Summary

This session resumed the 19:59Z handoff, booked the operator's ruling as proceed, and worked item 10 (OBPI-0.35.0-10-classification-reader-and-ownership) through the pipeline from its recorded resume point until the operator called for a handoff because the context window was filling. The OBPI is NOT complete and NOT attested. It is in Stage 4 with one review round left. CI went green: the pipeline launch rewrote the two stale markers, the preflight scan is clean, and the CI workflow succeeded on 7c05949ee, 3c53720ab and e8617ba90 after failing since 2026-10-04. Done and pushed before this handoff: the plan file and a PASS plan audit; the parent ADR's Decision item 9 amended to carry the retention scope; the REQ-0.35.0-10-10 witness clause repaired; the 31-row mapping reviewed by the operator; six corpus entries reclassified to the scorecard's class by governed retire and remember (12 appended rows, AGENTS.md byte-unchanged, zero advisories afterwards); Stage 3 green; ten proofs executed; the Stage 4 packet composed by the narrator and replayed VERIFIED; Step 4b round 1 by Codex (refuted, three findings) and its repair in 60e622dee; round 2 by Codex (refuted, both SUPPORT findings closed, nine proofs approved, one REQ-02 finding open and one new one). Done after round 2 and committed as ca8ab6534: the operator-ruled design repair, a strict rule-table reader that refuses any row it cannot read, plus the repair of five live Mechanical scorecard rows the audit had never read, plus the freeze of Model Selection #52 as witness debt. The per-change check passed on that tree. NOT done: the Stage 3 baseline receipts, the ten proofs, the packet and its replay have not been refreshed for ca8ab6534, and the third and last review round has not been dispatched.

## Important Context

What remains for item 10, in order. (1) Re-run the baseline under ARB on the final tree: lint, typecheck, the full unit suite, the strict docs build, the behave feature, each read by its receipt. (2) Re-run all ten proofs with the acceptance prove command. The proof specifications are not files in the repository: rebuild each from the newest proof record for its requirement in the stage4 acceptance status JSON (fields selectors, and source and mutations inside evidence). REQ-0.35.0-10-02 now has twelve selectors and six controls, last recorded valid as proof-f9ab2edc3684493089d335cc691cb7d1 before the data files changed. (3) Brief-drift, then present-evidence, then update the Stage 4 packet: new proof ids and input digest, new receipt ids and test counts (the gate run counted 11460 unit tests; the module has 57), a population of 178 rows with 31 answered by the corpus, the round 2 history, the five repaired rows, the frozen row. Replay it with verify-packet. (4) Stage all, run the per-change check, sync. (5) Build an adversary workspace, then the final focused Codex follow-up through the plugin's task --write path under an ARB step named codexadversary, in the background; rounds took about ten minutes. (6) Import the review by its receipt. If the stage4 acceptance status reads ready, present the packet, its replay verdict and the review to the operator and wait for the attestation in the operator's own words. If a mapped finding is still open, the loop bound is reached: record an OBPI block and put the decision to the operator; do not dispatch a fourth round. (7) Stage 5 as the pipeline skill writes it; the closure narrative must quote parent ADR Decision item 9 verbatim and name the six retirement and replacement ids, which are in the packet.

Things that cost time in this session and will again. The pipeline-gate hook and the staged-diff commit guard both refuse production code unless the marker reads implement: re-enter by launching the OBPI pipeline with no from flag, and stage the two marker files in the same commit, because pre-commit stashes unstaged files and the guard then reads the committed marker. A launch from verify is refused while a mapped finding is open, yet it still rewrites the marker to verify first. The sync command refuses to sweep src or tests changes: commit them under their own fix message with a Task trailer (TASK-0.35.0-10-02-01 was used), then sync the records. The session was forked mid-run and its environment now carries FORCE_COLOR=3; the packet replay reports passing transcripts as unreproduced under colour, so run it with FORCE_COLOR unset and NO_COLOR=1. The verifier-pipe hook refuses any verifier that is piped or followed by another statement, and it matches verifier names inside heredoc text too: redirect to a file and echo the exit status immediately, or begin the command with errexit. The acceptance importer refuses a review that relists an existing finding id with new text: tell the reviewer to leave an unclosed finding out of findings, give a new counterexample a new id, and put verified repairs in closures with the current proof id. The reviewer's checkout has no git metadata; give it a diff file. The lock is held by agent claude-code-b4d3b30a, claimed 2026-10-05T20:20Z with a 24 hour TTL; precomplete accepted it from the forked session, and brief 19 (lock continuity) is not built.

Open findings in the acceptance record: codex-035010-missing-row-number and codex-035010-empty-number-cell-dropped-r2, both on REQ-0.35.0-10-02. The repair in ca8ab6534 addresses both; only an independent closure clears them. The reviewer named the same weakest point in rounds 1 and 2: the live population test took its expected identities from the scorecard it audits. The test oracle was rewritten to read rule tables structurally, independent of the audit's row grammar; no pinned baseline of identities was added, and the reviewer said REQ-02 does not require one.

Disclosures the packet must carry. The implementation and every repair were single-driver under the operator-ruled trial declaration; no implementer or Stage 2 reviewer was dispatched. The resolver module is 773 lines against a 600 line authoring guidance that nothing gates. The seven RED witnesses were inconclusive on a reconstructed base. Pythonic #22 and Data Models #27 are Mechanical with no property-level witness and remain invisible to the advisory-scorecard scope.

The design dialogue in session 3e386d1a-fbc8-4e8c-bacd-0c6f024b2723 still has no authored account; this session did not read it. Read the Important Context of the 19:48Z handoff of 2026-10-05 for the standing cautions on the preflight cleanup and on content land.

Workflow fronts (source: docs/governance/build-to-1.0-campaign-2026-09-20.md, Workflow fronts section). Handoff system: worked (resume booked proceed, one successor at 20:11Z, this successor). GHI triage: not run; no issue filed, commented or closed. ADR and OBPI campaign: ADR-0.35.0 still reads 9 of 20; item 10 in Stage 4. New R&D: not touched. The three-pillars hold on GHI #1028 is unchanged.

## Decisions Made

- [operator-ruled] Amend parent ADR Decision item 9 to carry the source-aware retention scope the brief gained on 2026-09-29 (verbatim selection: "A: Amend Decision 9 (Recommended)"). Rejected alternatives offered: record the drift in the brief only; hold item 10.
- [operator-ruled] The REQ-0.35.0-10-10 witness clause cites docs/user/manpages/validate.md only (verbatim selection: "A: Cite the manpage (Recommended)"). Rejected alternatives offered: split into two requirements; cite the scorecard.
- [operator-ruled] The trial's 31-row mapping, the mandatory attribution, the two self-attributed rows and the requote of Local Agent Rules #8 stand as measured (verbatim selection: "A: Accept as measured (Recommended)"). Rejected alternatives offered: review all 31; review the six paraphrases.
- [operator-ruled] The six scorecard and corpus class disagreements are resolved by the corpus adopting the scorecard's class (verbatim selection: "A: Corpus adopts scorecard (Recommended)"). Rejected alternatives offered: leave the advisories standing; rescore the scorecard; keep row 8 Mechanical.
- [operator-ruled] Corpus attestation for the twelve appended rows, promoted with an unchanged candidate through content commit (verbatim: "attest to this corpus change").
- [operator-ruled] The open REQ-02 finding is repaired by design: fail closed on any unparseable rule-table row (verbatim: "A"). Rejected alternatives offered: a pinned baseline of row identities; both; declare malformed rows out of scope.
- [operator-ruled] The five live rows the strict reader surfaced are requoted to verbatim rule-file wording and attributed, row 22 to models.md, and a compound score cell binds its leading class (verbatim selection: "A: Apply as drafted (Recommended)"). Rejected alternatives offered: show full text first; retire row 22; split rows 58 and 65.
- [operator-ruled] Model Selection #52 is frozen as witness debt the census missed, raising the shrink-only baseline from 64 to 65 (verbatim selection: "A: Freeze as missed debt (Recommended)"). Rejected alternatives offered: write a real negative control; rescore to Promotable.
- [operator-ruled] Write a handoff and sync because the context window is filling (verbatim: "context window is filling, we need a h/o and git sync").
- [agent-chose] Wrote the plan file after the implementation and labelled it so, because the plan audit had no subject and the operator had ruled the audit is re-run to a pass.
- [agent-chose] Continued under the 2026-10-03 single-driver declaration for the two repairs instead of dispatching an implementer and Stage 2 reviewers. Unreviewed by the operator.
- [agent-chose] Corrected the Stage 4 packet to state the resolver arm that passed for the two SUPPORT requirements, and wrote no ledger row to manufacture the witness the packet had wrongly claimed.
- [agent-chose] Stopped after round 2 and took the design to the operator, because the reviewer repeated its weakest point and the parser dropped five malformed shapes, not one.
- [agent-chose] Replaced the brief's third Demo command, split one Allowed Paths bullet, corrected the REQ-05 atomicity note, and added three data files to the allowlist under the row 52 ruling; each is in the brief's Change Log.
- [agent-chose] Kept the legacy row reading for unenrolled projects and removed the round 1 guard the strict reader subsumes.
- [agent-chose] Asked the reviewer for a formatting-only re-emission of round 2 after the importer refused a rewritten finding id; no judgment was changed.
- [agent-chose] Recorded seven insights and filed no issue.

## Immediate Next Steps

1. Confirm main is level with origin and read the last three CI workflow runs; expect success on the run for ca8ab6534 or its sync commit, since the preflight scan is clean.
2. Finish item 10's refresh for ca8ab6534: the ARB baseline, all ten proofs rebuilt from the ledger's proof records, brief-drift, present-evidence, the packet update and its replay with colour disabled, then the per-change check and a sync. The order and the pitfalls are in Important Context.
3. Dispatch the third and last Codex review as a focused follow-up on the two open REQ-0.35.0-10-02 findings and the changed code, in a fresh adversary workspace, and import it by its receipt.
4. If acceptance reads ready, present Stage 4 to the operator and wait for the attestation in the operator's own words; then run Stage 5. If a finding is still open, record an OBPI block and put the decision to the operator.
5. After item 10: the operator initiates items 15, 16, 17 and 20 with 18 and 19 among them, then 11 to 13. The design dialogue in session 3e386d1a-fbc8-4e8c-bacd-0c6f024b2723 still needs an authored account. The operator still owes rulings on whether red CI being invisible locally gets a work order and on who owns the content land reorder.

## Pending Work / Open Loops

Open on item 10: the two REQ-02 findings await independent closure; every proof is stale against ca8ab6534 until re-run; the packet on disk describes the round 1 repair state and names proof ids and receipts that are superseded; the brief's evidence sections are unfilled. The brief's status line in its body still reads Draft while its frontmatter reads Active.

Recorded as insights this session and not repaired: the pipeline skill says the plan-audit skill authors the plan and it does not; the plan audit reads one path per Allowed Paths bullet; the packet replay depends on the caller's colour setting; two unit tests in tests/governance/test_enforcement_floor_wiring.py run the commit guard against the live checkout, and a refused verify launch still advances the marker; the advisory-scorecard scope cannot read a row whose rule cell carries an escaped pipe, so its 2026-08-10 freeze census undercounts by at least three and Pythonic #22 [settled] and Data Models #27 [settled] pass unwitnessed.

Not verified this session: the CI run for 1ef19594e was in progress when last read at 22:59Z; the CI runs for ca8ab6534 and this handoff's sync have not been read. The 16 orphaned-implementation tests and the five code findings the 19:48Z handoff listed as unverified were not touched. The lineage walk hit its depth bound; this session read four handoffs of it.

Two stale Codex broker processes for earlier review checkouts of items 06 and 08 were seen running and left alone. Two disposable review checkouts for item 10 remain in the system temp directory and can be deleted.

The Pending Work of the 19:48Z handoff of 2026-10-05 is otherwise unchanged and is not restated here.

## Verification Checklist

The ahead and behind count of main against origin: expect 0 0 after the sync. The last three commits: expect the handoff sync commit above ca8ab6534. The last three CI workflow runs: expect success on completed runs. The preflight scan: expect clean. The OBPI lock list: expect one ACTIVE lock for OBPI-0.35.0-10 held by claude-code-b4d3b30a until 2026-10-06T20:20Z. The OBPI status of OBPI-0.35.0-10-classification-reader-and-ownership: expect Runtime State IN PROGRESS and Completion PENDING. The stage4 acceptance status JSON: expect ready false, two reviews, open findings codex-035010-missing-row-number and codex-035010-empty-number-cell-dropped-r2, and stale proofs until they are re-run. The bullet-retention scope: expect exit 0 with no advisory lines. The advisory-scorecard and waiver-ratchet scopes: expect exit 0 each. The unit module tests.governance.test_bullet_retention: expect 57 tests OK. A count of audited_population rows: expect 178, 31 with authority corpus. The current_stage field of .claude/plans/.pipeline-active.json: expect implement. The ADR status of ADR-0.35.0-canon-entry-corpus-landing: expect 9 of 20. A rulings search for 'fail closed on any unparseable rule-table row': expect this handoff's ruling.

## Evidence / Artifacts

Commits this session, oldest first: a4ad8178f (the 20:11Z handoff), 7c05949ee (plan, ADR amendment, brief repairs, markers), 3c53720ab (corpus reconciliation and scorecard repoint), e8617ba90 (packet and frozen state reviewed in round 1), 60e622dee (round 1 repair), 1ef19594e (state reviewed in round 2), ca8ab6534 (design repair, five rows, row 52 freeze).

Item 10 surfaces: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-10-classification-reader-and-ownership.md` (its Change Log under Evidence indexes every correction and ruling), `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`, `.claude/plans/classification-reader-and-ownership-OBPI-0.35.0-10.md`, `.claude/plans/.plan-audit-receipt-OBPI-0.35.0-10-classification-reader-and-ownership.json`, `.claude/plans/.pipeline-active.json`, `.gzkit/evidence/OBPI-0.35.0-10-classification-reader-and-ownership.stage4a.md`, `.gzkit/evidence/OBPI-0.35.0-10-classification-reader-and-ownership.evidence.json`.

Code, tests and data: `src/gzkit/governance/trust_audits/bullet_retention.py`, `tests/governance/test_bullet_retention.py`, `docs/governance/advisory-rules-audit.md`, `docs/user/manpages/validate.md`, `.gzkit/corpus/AGENTS.md.jsonl`, `.gzkit/renditions/AGENTS.md/root.corpus.json`, `data/mechanical_witness_grandfather.json`, `data/waiver_ratchet_registry.json`, `data/waiver_identity_baseline.json`.

Review receipts, held under artifacts/receipts: arb-step-codexadversary-c47b21f19ded456989a48f7dbb25e5e6 (round 1, imported), arb-step-codexadversary-7ad9ace1ea1e488390fa039a0847de2a (round 2, refused by the importer for a rewritten finding id), arb-step-codexadversary-89c8da29860546c38621432ec67acf05 (round 2 re-emitted, imported). Insights: `.gzkit/insights/agent-insights.jsonl`, seven rows from this session.

Predecessor: `.gzkit/handoffs/20261005T201134Z-item-10-proceed-ruled-design-thread-pointer.md`, superseded by this document.

## Settled Rulings

1406 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
