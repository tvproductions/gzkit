# OBPI acceptance-review churn investigation

Date: 2026-09-08. Work order: [GHI #984](https://github.com/tvproductions/gzkit/issues/984).
Prepared by Codex agents for operator g0.

## Question and boundary

Why did OBPI-0.35.0-04 and OBPI-0.35.0-05 require repeated acceptance-review
repairs, and which existing pipeline surfaces can be corrected using that evidence?

This investigation reads the two briefs, recorded independent-review receipts,
preserved recovery evidence, relevant commit history, current pipeline instruction
producers and consumers, and related GHIs. It does not re-attest either OBPI or
adopt the active OBPI-05 session's proposed evidence-record contract. The active
content implementation, brief and evidence repairs belong to that session.

Two read-only investigators separately reconstructed the OBPI histories. A third
traced Stage-2 prompt producers and consumers. Historical defects below are
reviewer-recorded observations, not reproductions newly executed by this
investigation. The repaired pipeline code is tested separately.

## Findings from primary review records

### OBPI-04: partial repairs and masked tests

1. **Incomplete obligation carried between rounds.** Round 3 explicitly says:
   "recovery must re-establish directory durability before appending the witness."
   Round 10 records `REAL_WRITER retry_exit 0 fsync_calls 0 witnesses 1 journal False`.
   The receipt distinguishes the observed missing sync from inferred crash loss.
   Journal retention had not completed the retry-durability obligation.
2. **New repair paths missed old invariants.** Round 1 found declaration/ledger
   non-atomicity and weak proof. Round 2 found that the new recovery journal could
   write an insufficiently validated declaration. Later recovery changes again
   conflated witness completion, source reconciliation and cleanup. These are
   implementation defects and incomplete repairs, not merely narrative disputes.
3. **Rejection was mistaken for proof of the intended guard.** Rounds 6, 8 and 9
   record controls masked by other guards. The preserved recovery assessment also
   found a directory-durability test accepting a sync of the wrong directory.
4. **Review framing and capability were mismatched.** The round-1 dispatch says:
   "Your job is to REFUTE the completion claim, not confirm it." Later reviews
   exercised bounded claims. Recorded filesystem-test setup failures limited
   independent execution. Those failures must not be counted as product defects.

Primary receipts (under `artifacts/receipts/`):

- Round 1: `arb-step-codexadversary-f7a101da3ba3498e94249f2bdb39969f.json`
- Round 2: `arb-step-codexadversary-d04634100678415daada4acd3a6f2881.json`
- Round 3: `arb-step-codexadversary-209abafb666f4572ae68ab464d0a99fe.json`
- Round 6: `arb-step-codexadversary-a73a8257b2bf4b72bcff42b19e09792c.json`
- Round 10: `arb-step-codexadversary-658c8ce606114de39730cd01a66e5f3d.json`
- Round 11: `arb-step-codexadversary-cc9aa913064b4550807e717c51982f4b.json`

The linked [OBPI-04 brief](../design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-04-section-ownership-and-ratchet.md)
preserves round histories. Its
[recovery test evidence](../design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/appendices/obpi-04-recovery-2026-09-05/test-evidence.md)
records the wrong-directory and staging-enumeration findings. Receipt timestamps
inspected run from September 2 through September 5. They establish a multiday
sequence, not a breakdown of every elapsed hour into implementation or review.

### OBPI-05: evidence repair became another engineering subject

1. **Early rounds found real implementation defects.** Round 1 reproduced entry
   whitespace corruption, incorrect lineage, candidate newline translation,
   stale lineage after explicit replacement, and fence handling failures.
   Rounds 3–4 then exposed and repaired the weaker ID-set check where actual
   boundary comparison was needed. Commit `c4055edf` carries that latter repair.
2. **Failure attribution was not observed before publication.** Round 5's
   explanation identified a length assertion; subsequent inspection located the
   actual failure in a body-slice assertion. Author and reviewer explanations
   both require support. A killed mutant does not establish which check killed it.
3. **Stronger claims created new proof obligations.** Claims of exclusive
   detection, shared-parser blindness and comparative assertion strength were
   added and then withdrawn. The same-length control was optional in the
   round-5 review; it became entangled with stronger claims in the repair record.
4. **An auxiliary diagnostic displaced acceptance.** Round 12's dispatch states:
   "THE CONTRACT DOCUMENT ITSELF IS THE PRIMARY TARGET." Rounds 10–14 inspect
   assertion counts, classifications and explanations. Their receipts share HEAD
   `1cef5d80` with dirty trees; round-12–14 records report no source/test delta.
   This does not independently identify every dirty artifact. The primary
   subject had nevertheless explicitly changed from generator acceptance to
   claims about a proposed evidence contract and classifier.
5. **Removing the diagnostic did not remove relevant findings.** A boundary
   observation from round 11 still affected REQ-02. Sorting findings by the
   artifact or round in which they appeared can conceal a required-proof gap.

The [OBPI-05 brief](../design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-05-corpus-candidate-generator.md)
contains the recorded round sequence. Representative primary receipts:

- Round 1: `arb-step-codexadversary-eee752c4e22645739c0e20a0451aa563.json`
- Round 4: `arb-step-codexadversary-e82f72ebb97543668d9a86790ee4d0a2.json`
- Round 5: `arb-step-codexadversary-27a74d68972e47d4b26f7e6bcad878d5.json`
- Round 12: `arb-step-codexadversary-3e166363a03243adb5fc29f6d71bd7db.json`
- Round 14: `arb-step-codexadversary-4c68317c1adc427b8c1ffd92279d1316.json`

The investigator read all fourteen receipt metadata records, selected primary
review outputs, the round histories and current packet. One review stdout record
(round 3) is truncated. The fourteen timestamps span September 7 23:28:20Z to
September 8 07:25:51Z; these receipts alone do not substantiate four days for
OBPI-05. No historical mutation suite or native Windows run was repeated here.

## Diagnosis and implemented repair boundary

**Interpretation:** the common failure is loss of the subject and complete
obligation when work passes between implementation, evidence narration and
review. Repeated independent review usefully detected defects; it did not by
itself ensure each repair carried the original obligation through every path.

| Observed opening | Existing surface repaired | What the repair establishes |
|---|---|---|
| Quality coverage criterion asks that tests exist; dispatch instructions omit an explicit failure-record handoff | Stage-2 composers, coupled reviewer definitions and skill dispatch instructions | Both composed prompts instruct inspection of production behavior, independently derived expectations and observed failure records; the skill instructs the orchestrator to supply artifact paths |
| Capability frame says anything unverified is never a finding | Shared reviewer capability frame | Tool limitations remain separate; identified missing or invalid required proof remains a finding |
| Partial repairs and guard masking recur | Existing repair and verification instructions | Carry the full finding across relevant fresh/retry/cleanup paths and inspect actual failure attribution before claiming closure |
| Auxiliary diagnostics become acceptance subjects | Existing Step-4b dispatch and repair instructions | Findings trace to requirements or acceptance claims; irrelevant diagnostics may leave the argument without discarding relevant findings |
| Severity-only pass text contradicts the later operator ruling | Earlier skill pass summaries | Same independent-closure rule throughout; no severity-based escape added |
| Runtime recovery prescribes forbidden raw dispatch and refutation framing | Completion refusal messages | Recovery directs the caller to the permitted plugin through the governing skill and ARB receipt path; boundary changes require operator ruling and independent revalidation |

These changes preserve runtime verdict vocabulary, Stage-2 review limits,
reviewer tool grants, pipeline stages, required quality checks and human
completion attestation. They do not add a classifier, universal mutation
requirement, new validator gate, or a maximum number of Step-4b rounds.

## Unresolved and separately owned concerns

- **Reviewer execution:** closed issue #961 records the plugin restriction and its subsequent
  policy corrections; #968 owns the broader capability/effect distinction. This
  repair preserves the current division of execution and review. Changing the
  plugin or tool grants requires that separate work, not a silent workaround.
- **Vendor tuning:** #943 remains the model-profile work order. This investigation
  does not attribute observed failures to a particular model generation.
- **Active OBPI-05 allegations:** each requires a requirement-specific disposition
  in its own session. For example, JSON newline translation does not by itself
  prove offsets into a separate candidate are corrupt; an unreachable defensive
  helper refusal does not by itself disprove a generator invariant established
  by construction. False end-to-end proof claims still require correction.
- **Coverage of the investigation:** receipt and archive review cannot establish
  every action taken during the elapsed period. No percentage of time saved or
  reduction in future review rounds is claimed.
- **Adjacent reviewer thresholds:** the authored quality-reviewer definition still
  lists literal size limits while the composed prompt reads the threshold file.
  This observation is recorded separately from the evidence-handoff correction;
  this investigation did not establish a threshold mismatch for the reviewed work.

## Verification

Deterministic tests check emitted prompt/recovery contracts, not whether every
agent obeys them. Separate scenario sampling exercises the decisions that the
instruction repair intends to support. Results and limitations are recorded in
the [evaluation](../evals/obpi-review-984-evaluation.md), using the
[scenario packet](../evals/obpi-review-984-scenarios.json).

| Output contract exercised | Test witness |
|---|---|
| Both reviewer roles receive requirement-derived expectation and failure-attribution instructions | `TestReviewEvidenceInstructionsOutputContract.test_both_review_roles_receive_semantic_proof_instructions` |
| Missing required proof remains a finding for both roles, with and without Bash | `TestPromptDisclosesCapabilityOutputContract.test_tool_limits_do_not_hide_identified_required_evidence_defects` |
| Missing verdict, missing receipt, failed receipt and unsupported cross-vendor claim prescribe the permitted plugin route | `TestAdversaryRecoveryOutputContract.test_missing_and_failed_evidence_prescribe_the_plugin_review` |
| Both refutation tokens require operator authority for boundary changes and independent revalidation | `TestAdversaryRecoveryOutputContract.test_refutation_recovery_requires_operator_ruling_for_boundary_changes` |

A focused independent read-only review found a remaining boundary-amendment
instruction in the refutation refusal that omitted operator authority. The repair
corrected that branch and the coupled Stage-5 instruction. The new test failed
on both refutation tokens before the change; afterward the complete adversarial
validation module ran 60 tests successfully. The reviewer inspected the correction
and reported the finding closed with no remaining findings in that review; it
did not independently rerun those tests. The earlier combined five-module run
passed 284 tests before the additional boundary-amendment test was added.

The full `uv run gz check` rerun exited 0 with all 60 steps passing, including
tests, BDD, documentation, lint, formatting, type checking and governance audits.
The first run exposed a formatting error in the recovery edit and failed to
initialize radon under the filesystem sandbox, with related validator and test
failures. Formatting was corrected; the successful rerun had approved access to
uv's tool directory. The checkout also contained the separate active OBPI's
changes. Because those changes were unstaged, the check did not record a reusable
commit-tree verification fingerprint. No completion attestation is asserted here.
