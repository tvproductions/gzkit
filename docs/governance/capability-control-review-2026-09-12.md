# Capability and control review — 2026-09-12 UTC

## Purpose and authority

Operator-requested application of the discussion about growing OBPI completion
cost. This is a diagnostic record and a reusable reading framework, not a
campaign amendment, a new requirement, or initiation of OBPI work.

The governing campaign is identified by
[`data/active_campaign.json`](../../data/active_campaign.json). Its
[2026-07-18 disposition amendment](build-to-1.0-campaign-2026-08-16.md)
already names re-entry cost as a concern. This review connects that concern to
existing affordances and observed evidence. It does not change the campaign's
work order.

The pasted discussion refers to four concerns without identifying them. The
five diagnostic hypotheses below are drawn from the subsequent discussion;
they are not a reconstruction of those missing four concerns.

## Question being tested

Why does completing a bounded OBPI take more work: necessary integration and
verification, unresolved specification, lost intent during decomposition,
session reconstruction, or repeated correction?

Completion time alone cannot distinguish those explanations. Calendar duration
also includes time when the operator is not working. No claim about increasing
active labor, average OBPI cost, or time saved is established by this review.

## Evidence standard

- Read the intended guarantee before judging the implementation.
- Distinguish an affordance's existence, observed invocation, and effectiveness.
- Treat current command output as a working-tree observation, historical
  evaluations as dated records, and handoff narrative as a claim to corroborate.
- Require evidence of degraded steering before proposing retirement. A low use
  count or large governance surface is not sufficient.
- Preserve useful detection: discovering a real contract contradiction is work
  that can establish correctness. Repeating a review because its input changed
  is a different cost category.

These standards follow [trust doctrine](trust-doctrine.md),
[state doctrine](state-doctrine.md), and the evidence bar for subtraction in
[the advisory scorecard](advisory-rules-audit.md#recommended-promotion-order-highest-leverage-first).

The health-audit skill says, verbatim, "Budget the audit by net surface reduction,
not by findings count." The root contract says, verbatim, "Governance is the
steering and accountability surface for agent-driven work, not overhead. Volume
follows steering need; 'lighter ceremony' alone is never the tradeoff axis."
This review uses the root contract's steering criterion. It records no mandate
to remove a control or alter either source.

## Applied lenses

| Hypothesis | Existing affordances | Governing question | Evidence and failure signature | Boundary |
|---|---|---|---|---|
| Specification ambiguity | Semantic OBPI authoring, ADR substance evaluation, justification | Did the contract settle the behavior needed for implementation? | Compare original guarantee, review finding, and ratified disposition; look for mutually incompatible guarantees or unresolved failure behavior. | Structural completeness is not semantic determinacy. |
| Decomposition loss | Parent Decision discovery, decomposition matrix, plan audit, REQ proof channels | Did each smaller unit preserve its parent's guarantee and identify its dependencies? | Trace a claim through ADR, brief, implementation, and evidence; look for missing consumers or responsibility crossing brief boundaries. | More named tasks do not by themselves preserve intent. |
| Accumulated coupling | Allowed Paths, brief reconciliation, airlock seam maps, coupled-surface verification | Were the consumers required to complete the change known before implementation? | Examine scope amendments and the surfaces they add; separate necessary integration from late discovery. | A zero-seam readout proves only what the current instrument observed. |
| Session reconstruction | Session handoffs, attributed decisions, settled-ruling transport, entry orientation | Could the next session recover the needed rationale and distinguish it from current state? | Compare successor actions with the carried decision and its provenance; look for lost attribution or re-adjudication. | A handoff file's presence is not proof that its contents were delivered or used. |
| Correction cycles | Independent reviews, proof bindings, negative controls | Did another pass detect a new defect, or repeat evidence invalidated by sequencing? | Match the finding, reviewed input, intervening change, and repeated check. | A reopened proof may be the correct response to changed behavior; its cause must be classified. |

The intellectual lineage here is internal: trust-boundary verification, the
three-layer state model, and the decomposition matrix's feedback calibration.
No external theory or industry comparison was evaluated.

## Three applications to existing evidence

### 1. A substantive review resolved a contract contradiction

The September 5
[ADR-0.35.0 substance evaluation](../design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/EVALUATION_SUBSTANCE.md)
records a conflict between whole-set atomicity and interruption after the first
file publication. Its recorded disposition is an operator-ratified journaled
per-file publication contract. The closure table also identifies missing parser
scope and a shared scanner responsibility.

**Reading:** the review provided useful detection. It supports the possibility
of specification ambiguity and decomposition loss in this instance, not a
conclusion that every OBPI is poorly specified.

The [deterministic scoring module](../../src/gzkit/adr_eval_scoring.py)
explicitly assesses structural completeness; its size heuristic counts allowed
paths. Those measures cannot establish engineering effort or semantic difficulty.
The semantic review and structural score answer different questions.

**Disposition:** preserve the semantic review's role. For the next retrospective,
trace which decisions it settled and whether implementation later had to settle
those same decisions again.

### 2. One checkpoint records integration discovery and evidence invalidation

The September 11
[OBPI-0.35.0-06 checkpoint](../../.gzkit/handoffs/20260911T082702Z-obpi-0.35.0-06-stage2-complete-awaiting-req03-reclosure.md)
records three allowlist amendments to connect one gate to coupled quality
surfaces. Separately, it records a repair dispatched during specification review,
invalidating the reviewed digest and superseding a proof-bound closure.

**Reading:** classify these separately. The first records integration work and
late scope discovery. The second records repeated verification caused by changed
inputs. The checkpoint is historical narrative; this review does not establish
the current pipeline state or independently reproduce its account.

**Disposition:** use the two episodes as a candidate retrospective sample. Check
the original scope, amendments, dispatch records, and proof revisions before
assigning avoidability or cost. Do not reopen the OBPI or change its machinery.

### 3. Session memory has concrete transport and parsing failure modes

The [session-handoff skill](../../.gzkit/skills/gz-session-handoff/SKILL.md)
records a case where copied settled rulings occupied 91.4% of a handoff before
transport moved to a persistent store and pointer. The
[handoff validator](../../src/gzkit/handoff_validation.py) contains an explicit
guard for attributed decisions lacking list markers, documenting a case in which
ten operator rulings disappeared from successor composition.

**Reading:** memory quality is a question about what survives delivery and
parsing. Neither document size nor document existence establishes that the next
session received usable intent. These records demonstrate named failure modes
and targeted responses, not measured savings from those responses.

**Disposition:** trace one settled decision through capture, validation,
successor composition, and subsequent use. Evaluate transport end to end before
proposing another memory mechanism.

## Current instrument observations

Base commit at inspection: `d773603e9207d33daab9385087e96cdaddec5460`.
The checkout already contained staged and unstaged OBPI-0.35.0-06 work,
handoffs, and ledger changes. Observations are not a clean-commit certification.

The existing health-audit method orders reachability/conformance before ledger
inertness, rule coherence, and sampled intent tracing. Its saved reports are
historical evidence, not current findings. This application is a bounded
capability review; it does not certify a complete rule-pair walk or ADR audit.

The first chore was inspected through `show`, `plan`, and `advise` using the
`gz-chore-runner` skill. Observed advice: exit 3, proof freshness failed,
self-test passed, and the ungated-scope ratchet passed.

The canonical reachability report returned exit 0:

```text
runnable scopes: 98
  A gated       47
  B test-only   27
  C doc-only    23
  D orphan       1
ungated (B+C+D): 51
orphans (delete candidates): --doc-surface-parity
```

These are classifications produced by the scanner, not independent proof that
each classified check fires in practice. Its implementation scans the quality
registry and invocation text. **The orphan inference is refuted in this case:**
[`validate_audits.py`](../../src/gzkit/commands/validate_audits.py) includes
`check_doc_surface_parity` in `AUDITS_AGGREGATE_MEMBERS`, and the live umbrella
run below reported that member passing. The scanner's textual caller search
does not model this Python dispatch. This demonstrates an instrument limitation;
it does not establish that the scope is automatically gated. No deletion is
warranted by the reported orphan label.

The proof-freshness command returned exit 3: both saved reachability proofs were
last committed August 15 while an audited surface last moved September 11. The
freshness control correctly refused to accept those old reports as current.
This is a stale-evidence finding, not proof of an implementation failure.

The canonical individual-scope sweep returned exit 3:

```text
swept 98 scope(s); 3 non-zero
  exit 3  --audits  [UNGATED (tier B)]
  exit 3  --evaluation-justify-binding  [UNGATED (tier B)]
  exit 3  --sensitivity  [UNGATED (tier B)]
```

Each failure was then run directly to read its diagnostics:

| Scope | Observed diagnostic | Disposition |
|---|---|---|
| `--sensitivity` | The active OBPI-0.35.0-06 brief omits a sensitivity declaration while its allowed paths overlap registered security surfaces. | Surface to the operator-controlled OBPI session. This is a classification finding, not a demonstrated security vulnerability; this review does not edit the brief. |
| `--audits` | Repeats that sensitivity finding; its six aggregate scopes, including `doc_surface_parity`, pass. | Count the shared finding once. The umbrella is propagating a member failure, not demonstrably broken itself. |
| `--evaluation-justify-binding` | Three artifact identifiers lack the qualifying justification artifact for a low Feature Checklist score: ADR-0.33.0-airlock-membrane, ADR-0.35.0, and ADR-0.35.0-canon-entry-corpus-landing. | Investigate the recorded evaluations and justification linkage. The short and long ADR-0.35.0 identifiers are not evidence of two independent ADR defects. |

The [justification validator](../../src/gzkit/governance/trust_audits/evaluation_justify_binding.py)
matches evaluation events by exact artifact identifier and searches justification
filenames. Its failure establishes that particular binding check's result; it
does not by itself prove that no substantive reasoning was ever done.

Next, the ledger-inertness chore was inspected through `show`, `plan`, and
`advise`. Advice returned exit 3 because its saved proof was stale; its self-test
and disclosure/isolated-producer check passed. Its canonical report returned
exit 0:

```text
declared event types: 76
fired at least once:  66
never fired:          10
    blocked_by
    blocks
    constitution_created
    discovered_from
    intrinsic-complexity-attestation
    ledger_event_corrected
    obpi_superseded
    section_ownership_unowned
    task_escalated
    validates
```

The report also counted `mx_session_opened` and `mx_session_closed` at one each.
The saved August 15 report had counted neither as fired. This is why an old
inertness label must be refreshed before reuse. Event occurrence alone does not
prove correct end-to-end behavior. No paired-event ratio is interpreted here.

**Audit boundary:** no fresh exhaustive rule-pair walk, formal sampled ADR
intent-trace ceremony, chore completion, or full quality certification is
claimed. The three historical applications above are a purposive evidence
reading, not an exhaustive audit. Existing chore proofs were not overwritten or
marked fresh. The observed exceptions remain disclosed in this report and the
governed insights store.

## How to use the review

For each sampled episode, record the concern, intended guarantee, existing
control, exact input and output evidence, finding, disposition, and confidence.
Use these dispositions: retain, clarify, reconnect an existing control, repair
an observed failure, investigate, or retire with steering-failure evidence.

Keep health, opportunity, strategy, and tactics distinct:

- **Health:** did the control do what it claims on the sampled episode?
- **Opportunity:** can an existing affordance resolve uncertainty earlier?
- **Strategic fit:** does that improvement support the campaign's governing
  purpose and sequence?
- **Tactical refinement:** what is the smallest complete correction supported
  by the evidence?
- **Retirement:** has a control's assumption failed, or does it demonstrably
  degrade steering? If not established, do not infer retirement from cost.

The [decomposition matrix](GovZero/obpi-decomposition-matrix.md) already names
rework rate, failed gates, attestation churn, and delivery predictability as
calibration signals. Use those categories before inventing a new scoring scheme.
Include uneventful completions as comparison cases; a sample selected only for
failures cannot establish their prevalence.

The useful outcome is an evidence-backed account of which work established
durable correctness and which work repeated because intent, scope, memory, or
evidence failed to carry forward. This record does not establish a general cause
for longer OBPI completion time.

## Reproduction record

The following commands produced the current observations, in the order shown.
The two chore invocations were preceded by their respective `show` and `plan`.
No baseline-writing flags were used.

```bash
uv run gz chores advise control-surface-validator-reachability
uv run python src/gzkit/chores/control-surface-validator-reachability/check_reachability.py --report
uv run python src/gzkit/chores/control-surface-validator-reachability/check_reachability.py --sweep
uv run python scripts/check_proof_freshness.py control-surface-validator-reachability
uv run gz validate --evaluation-justify-binding
uv run gz validate --sensitivity
uv run gz validate --audits
uv run gz chores advise ledger-vocabulary-inertness
uv run python src/gzkit/chores/ledger-vocabulary-inertness/check_ledger_inertness.py --report
```

Report verification: 13 local file-link targets resolved; no trailing-whitespace
lines. This checks the report's references and formatting, not the product's
quality gates. Findings were captured with `gz insights remember` under scope
`capability-control-review`.
