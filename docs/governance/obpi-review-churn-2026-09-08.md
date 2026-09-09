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

## GHI #985 reopened repair, September 9

The reopened [work order](https://github.com/tvproductions/gzkit/issues/985)
was executed on `main`, starting from clean commit
`417154bd4210c020fe194bc0c25fb551f1d68311`. The work preserves the existing
acceptance ledger and reducer. Disposable fixtures supply the process evidence;
this correction does not execute or complete the live content OBPI.

### Acceptance and proof cases

| Case / failure mechanism | Decisive witness | Disposition |
|---|---|---|
| AS-1: stale-subject rejection discards a delayed finding | `test_delayed_mapped_finding_is_retained_without_current_approval` | Store retains a known historical subject; its approval cannot satisfy newer proof |
| AS-2: repeated historical finding erases a newer closure | `test_repeated_historical_finding_preserves_newer_independent_closure` | Identical older observation preserves closure; the current observation still reopens |
| AS-3: a later equivalent proof retroactively hides a current counterexample | `test_future_equivalent_proof_cannot_erase_a_recorded_current_counterexample` | Review position in immutable ledger determines then-current proofs; replay preserves the reopening |
| AS-4: UUID-only replacement invalidates unchanged proof claims | `test_equivalent_successful_execution_preserves_approval_and_closure` plus real BDD reexecution | Consecutive successful explicit claim equivalence preserves applicable approval and closure |
| AS-5: changed evidence or intervening invalid execution reuses approval | `test_changed_claim_or_failed_execution_cannot_reuse_prior_approval`, producer claim controls, declared-condition consumer test | Controls/results/specification/contract/input/declared conditions stay bound; legacy and invalid runs break equivalence |
| AS-6: one intersecting review loses scoped approvals and fallback provenance | `test_scoped_reviews_preserve_complete_completion_provenance` | Completion event retains every necessary review ID and actual receipt/tier provenance |
| AS-7: rejection has no demonstrated route back to acceptance | `features/acceptance_recovery.feature`, first scenario | Real proof, finding, repair, explicit synthetic independent closure, ledger reload, equivalent rerun, and real ceremony reach human-attestation request |

The AS-3 regression came from independent review of the first correction: a
review already recorded as current could become historical when a later
equivalent proof was appended. The test failed before ledger-position binding
and passed afterward. The reviewer reproduced the repaired behavior and checked
legacy receipt replay, repeated historical observations, and duplicate imports.
Neither raw receipts nor earlier ledger rows are rewritten. This independent
review passed 63 focused tests with no remaining findings in that population.

| Finite proof case | Witness and limit |
|---|---|
| TQ-G01: runtime, setup, import, skip, absent/ambiguous nomination | Existing `test_mutation_witness.py` controls plus BDD module-import failure; none earns valid behavioral credit |
| TQ-G02: unrelated or masking assertion | Existing unrelated-test control plus BDD same-test diagnostic masking; actual failure traces distinguish diagnostic from required assertion |
| TQ-C01: documented unittest output | Existing documented-result and documented-skip tests retain the parser correction |
| TQ-C02: actual process exit | Existing CLI process tests reject blocked state; BDD accepts ready state through both console and module entrypoints at Stage 2 and Stage 4 |
| TQ-C03: coherent shared oracle | BDD shared-helper expectation survives the identical production defect that an independent literal expectation kills |
| TQ-R01: interrupted active mutation | BDD inspects activated LF/CRLF bytes, injects a timeout during the active compilation command, verifies exact restoration and no proof append, then executes successful recovery |
| TQ-R02: source residue despite a real kill | Existing producer test creates extra production source during the mutant run and requires invalidation independently of the assertion kill |

This finite population does not prove arbitrary semantic oracle adequacy. The
same-test masking case deliberately demonstrates why a generic assertion
classification cannot replace independent review of the actual cause. The new
process demonstrations live in BDD. The older process tests' placement under
`tests/` is recorded separately through `gz insights remember`; no whole-suite
migration is required for this repair.

### Reviewer handoff through the real consumer

The acceptance response model now owns both the imported schema and the generated
reviewer example. Current context carries canonical obligations, input components,
proof history and findings. Missing or contradictory local context fails before
dispatch, including a changed initialized obligation roster. The latter was a
second independent-review finding, observed red and then closed with its focused
regression. Examples grant no approval and contain the actual closure shape;
reviewer-owned fields remain distinct from receipt-derived provenance and the
legacy result envelope. Formatting repair uses a new invocation with original
subject, judgment and receipt reference; it never edits a captured receipt.
Final independent review requested a connected formatting-repair witness.
`test_format_only_recapture_preserves_original_refutation_and_subject` now starts
with a malformed substantive refutation, preserves its raw receipt, imports a
separate disclosed synthetic recapture referencing it, and verifies the same
subject, finding, verdict and approval fields through reload. It remains blocked
despite earlier approvals; source bytes and proof history remain unchanged.

The [actual handoff receipt](../evals/obpi-review-985-actual-handoff.json)
and [delivered prompt](../evals/obpi-review-985-handoff-prompt.txt) preserve a native
Claude spec-review invocation, requested model `claude-opus-5`, effort `xhigh`,
through `gz arb step --name specreview`. Receipt
`arb-step-specreview-7a90f0ac89884e83a4bcce30293fb6a7` exited zero. The actual
unedited model output imported as review
`e10ccf08134f14dc4716e3444500e0ca235681156d5a53ee58a77e44cfe74507` at tier 2,
explicitly closing the fixture's `F-negative-boundary` finding against current
proof. Reload retained the closure. Readiness remained false because quality and
adversarial approval were still absent, and the actual precompletion consumer
refused advancement. The historical finding was a disclosed synthetic seed;
current proof execution and this model response were real.

The reviewer disclosed that the single mutant failed at the positive literal
assertion before reaching the negative case. It judged the shared multiplication
expression and negative literal baseline sufficient for that bounded fixture;
the artifact does not establish an independent kill for every assertion. The
native spec-review route does not demonstrate tier-1 adversarial plugin delivery.

Two failed prompt invocations exposed an independent ARB argument issue:
`parser_arb.py` removes every `--`, including child separators. The successful
invocation placed the prompt first, avoiding variadic option consumption. The
defect is recorded through `gz insights remember`, separately from acceptance.

### Instruction authoring disposition

The read-only source-to-delivery audit confirmed a contradiction, resolved by
the operator on September 9:

- Substrate doctrine calls `.gzkit/skills/**/SKILL.md` derived output and prescribes
  corpus authoring for every surface.
- `skill-surface-sync.md` declares `.gzkit/skills/` the canonical authoring source
  and prescribes editing it before surface sync.

Operator verbatim: "skills are not corpus constructed. only agents/claude and rules."
The operator accepted the rest of the source-authoring proposal. This correction
rejects its assumption that skills were awaiting corpus migration. The owning
substrate doctrine now distinguishes corpus construction
from content-model registration and canonical-file skill authoring. Skills are
authored under `.gzkit/skills/`; package/vendor copies remain derived through sync.
The ruling is also captured through `gz insights remember` as an improvement,
timestamp `2026-09-09T11:58:02.085947+00:00`.

The pipeline correction replaces contradictory same-turn freshness and raw-verdict
repair commands with current proof applicability and mapped finding closure. It
also requires one writer per governed checkout. Required review channels, tier
order, operator initiation and human completion attestation remain binding. The
sixteen actual instruction trials are recorded in the
[evaluation](../evals/obpi-review-985-evaluation.md); they demonstrate the selected
actions under both contexts, without an improvement claim. No Rule-family
onboarding, root-contract rendition, or live OBPI was initiated.
