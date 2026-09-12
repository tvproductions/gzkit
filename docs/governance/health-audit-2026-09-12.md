# Health audit — 2026-09-12

Operator request: “okay, apply the skill now”. Method:
`.gzkit/skills/gz-health-audit/SKILL.md` **1.2.1**. This is a diagnosis and routing
record, not an ADR/OBPI completion or a full quality-suite certification.

Base commit: `464dd4ff8fa2ee12d98afe99a867280e1b82b431`. The working tree included
the preceding health-skill changes, their generated copies, insight/ledger
records, and session bookmarks. Those changes were preserved. Audit work changes
proofs and this report; no production implementation, baseline, rule or OBPI
state is repaired as a side effect.

## Assessment

The reading frame is usable and exposed meaningful differences between a
declared control, its implementation, its callers, and its evidence. The result
is **not an all-clear**: the completed evaluation loop accepts empty reasoning
evidence and its recurring clustering chore runs fixture tests instead of live
clustering. Airlock calibration and corpus publication also remain visibly
incomplete, with explicit governing qualifications that a green exit cannot erase.

Repair and reconnect these existing controls before proposing more machinery.
No finding establishes that reducing governance volume would improve steering,
or that low-use events should be retired.

## Execution and evidence

The order was conformance/reachability → ledger vocabulary → doctrine coherence
→ sampled intent trace. Each chore went through show, plan, advise, its substantive
procedure, run and audit. The run log's mere existence is not a pass.

| Axis | Observed result | Evidence |
|---|---|---|
| Conformance and reachability | 98 runnable scopes; 97 zero exits, one nonzero: evaluation-to-justification binding. Static tiers A47/B27/C23/D1; 51 ungated against baseline 52, ratchet holds. | [98-row matrix](../../.gzkit/chores/control-surface-validator-reachability/proofs/reachability-matrix.md), [sweep](../../.gzkit/chores/control-surface-validator-reachability/proofs/conformance-sweep.md) |
| Ledger vocabulary | 76 declared types, 66 used, 10 never fired. Disclosure gate passes against baseline 11; the unowned-ratchet event has now fired. No baseline changed. | [Vocabulary and producer dispositions](../../.gzkit/chores/ledger-vocabulary-inertness/proofs/vocabulary-inertness.md) |
| Doctrine coherence | 29 files, 406 unordered pairs reviewed; source hashes unchanged. Six concrete conflicting/stale prescriptions; all evidence rows validate. Twenty prior findings explicitly disposed. | [Conflict matrix](../../.gzkit/chores/control-surface-rule-conflicts/proofs/conflict-matrix.md), [complete pair record](../../.gzkit/chores/control-surface-rule-conflicts/proofs/pair-review.json) |

The freshness criterion failed for all three recorded chore runs: its old proofs preceded
the audited source changes. The refreshed files remain uncommitted; the current
freshness script compares last commit times and still rejects modified tracked
proofs. The recorder therefore logs a failure, while `chores audit` returns zero
because it reports log presence. Those are distinct observations. No timestamp,
baseline or receipt was changed to manufacture a green result.

### F1 — Reachability scanner falsely classifies a used validator as orphaned

**Lenses:** invariant, change point. The scanner's D category means “No caller
anywhere”, and its chore prescribes deletion. It assigns D to doc-surface parity.
However, [the umbrella](../../src/gzkit/commands/validate_audits.py) dispatches
that scope through Python keyword arguments, and
[five tests](../../tests/governance/test_doc_surface_parity.py) directly call
the audit, including one against the live repository. Those five tests passed;
the standalone scope and the umbrella both passed in the sweep.

The scanner reads literal CLI invocations and does not resolve those function
calls. Its census is reproducible, but its orphan inference is false for this
case. **Disposition: retain the validator; correct the scanner's caller model
and retirement advice.** Do not interpret all 51 ungated scopes as useless or
fixture-only. Tier A is also static wiring evidence, not proof that a hook
executed in this session. This extends the already recorded observation in
`agent-insights.jsonl` dated 2026-09-12T00:19:56.203608+00:00.

### F2 — Evaluation-to-justification binding fails live and accepts empty evidence

**Lenses:** invariant, escalation. The live scope returned exit 3 with three
rows: ADR-0.33.0-airlock-membrane, ADR-0.35.0, and
ADR-0.35.0-canon-entry-corpus-landing. Their latest exact-ID evaluation records
have Feature Checklist score 1.0 and no matching justification artifact.
The short and long corpus IDs are evaluated independently by
[`_scan_all_evaluation_justify_binding`](../../src/gzkit/commands/validate_cmd.py);
three error rows therefore must not be presented as three independent features.

The same consumer's
[`_has_justify_artifact`](../../src/gzkit/governance/trust_audits/evaluation_justify_binding.py)
only inspects a matching name. An isolated probe copied a real triggering
evaluation event into a disposable project and called the real validator:

```text
missing_artifact_errors: 1
empty_matching_file_bytes: 0
empty_matching_file_errors: 0
live_ledger_mutated: false
```

This proves acceptance of empty evidence; it does not claim that anyone exploited
that weakness in production. The existing walkthrough parser has a structural
completion check, but this consumer does not call it. A separate live command,
`uv run gz justify ADR-0.35.0`, exited 1 and said:

```text
justify reasons about change instances (GHIs, OBPIs, drafts), not governance packages.
Invoke on the tracking GHI or an OBPI under the ADR.
```

**Disposition: inspect and reconcile producer/consumer identity and validated
evidence binding under the owning evaluation ADR, with the live corpus work
remaining operator-owned.** Do not create empty files, retrospectively invent
reasoning, or re-score the ADR merely to clear the gate.

### F3 — Intrinsic-complexity attestation retains a transport prerequisite

**Lenses:** jurisdiction, escalation, invariant. The live producer exists at
[`complexity_advise.py`](../../src/gzkit/commands/complexity_advise.py), but
refuses a noninteractive invocation before recording an otherwise eligible
attestation. Its error is “requires an interactive TTY; headless invocation
refused”. Root operator canon says:

> No TTY, PTY, interactive-terminal, or transport mechanism may EVER be cited as
> a reason an agent 'cannot' record human attestation

All seven tests in `tests.commands.test_complexity_advise_attest_intrinsic`
passed, including the test asserting this refusal. Passing those tests witnesses
the implemented restriction, not agreement with the newer operator contract.
Zero live intrinsic-attestation events cannot establish whether this restriction
caused non-use. **Disposition: corrective review under ADR-0.0.29, preserving
operator attestation and atomicity while removing transport as authority.** No
attestation was attempted, supplied or recorded by this audit.

### F4 — Zero-use and pair ratios require trigger and subject attribution

**Lenses:** escalation, jurisdiction. Ten never-fired event types are explicitly
disclosed. Six have wired command producers, including supersession, TASK
escalation and ledger correction. The other four work-edge types share
[`emit_work_edge`](../../src/gzkit/ontology/work.py), an append-capable library
path guarded by vocabulary attestation; caller inspection found no production
integration. This is an integration question under ADR-0.32.0, not proof that
graph edges should be fabricated or the declarations retired.

The current pairs are lock 394/374, park 377/6, airlock 63/21, MX 1/1. Lock
replacement can add claims without releases. Parking records demotion, not
abandonment or negated completion. MX's one open/close pair shares a session ID
and replaces the prior proof's zero-use claim. Airlock records encounters by
target, without a unique transit ID, so 63/21 cannot establish 42 abandoned
transits. The proof records actual producer paths and limits for each pair.

**Disposition: retain legitimate conditional producers; investigate integration
and encounter attribution.** No lock, TASK, OBPI or MX session is initiated to
make counts balance. Airlock use and evaluation weakness select it for intent
tracing after doctrine review.

## Intent-trace sample — recorded before ADR reads

The first three axes have completed their substantive procedures and recorded
their chore-run results. This sample is fixed before opening the selected ADR
bodies for the trace. Producer code inspected in the preceding axes is prior
evidence, not an independent confirmation obtained after selection.

| ADR | Selecting signal | Bounded question |
|---|---|---|
| ADR-0.33.0 | Live evaluation-binding failure; 63 entry / 21 exit events whose subjects do not establish paired transits; default producer reach is empty. | Does the delivered airlock observe the ecosystem and disturbance needed for its orientation/control purpose? |
| ADR-0.35.0 | Two exact-ID evaluation-binding failures; doctrine's current corpus/shape dependency; active operator-owned campaign work. | Which corpus guarantees are delivered, and which are still expressly unfinished? |
| ADR-0.0.26 | Its evaluation-binding consumer fails live and accepts a zero-byte matching artifact in isolation. | Does the binding establish the reasoning and identity required by its declared intent? |

This is an operator-requested diagnosis, not a competing campaign work order.
The campaign still sequences ADR-0.35.0 first; no OBPI is drawn. Signals for
ADR-0.32.0 work-edge integration and ADR-0.0.29 attestation are retained for a
future intent sample, without widening this one.

## Intent-trace results

| Sample | Observed disposition | Detailed claims, commands and limits |
|---|---|---|
| ADR-0.0.26 | Validated, 5/5 completed in ledger. Evaluation persistence is observed; reasoning qualification and recurring clustering are corrections under its existing intent. | [Evaluation trace](health-audit-2026-09-12-evidence/intent-0026.md) |
| ADR-0.33.0 | Validated, 6/6 completed. Shared primitive, menu and encounter events exist. Empty production reach and diagnostic-only operation match the explicitly attested calibration frontier; meaningful orientation/impact accounting is not certified. | [Airlock trace](health-audit-2026-09-12-evidence/intent-033.md) |
| ADR-0.35.0 | Pending, 7/13 completed. Live pure generator preserves all 10 unowned sections; bytes reconcile; ordinary ratchet increase and unattested invariant retirement refuse. Publication remains pending07, final advisory undrawn08. | [Corpus trace](health-audit-2026-09-12-evidence/intent-035.md) |

The live lineage scope exits0 while expressly reporting **12 sections /41,846
bytes UNGRADED, with 0/22 sections graded**. This implements OBPI06's September11
operator ruling for never-published lineage; it is not a successful live
derivation comparison. Likewise airlock IN's 12 bodies, zero push/pull edges and
PROCEED, followed by OUT CLEAN, do not prove no disturbance. The stated rollout
qualification must travel with both outputs.

### F5 — Doctrine and audit-evidence drift

The [six-row matrix](../../.gzkit/chores/control-surface-rule-conflicts/proofs/conflict-matrix.md)
records opposing chore authoring sources, Lite evidence that invokes BDD, stale
shape-check status/subject, misplaced skill metadata, obsolete canonical test
command and release review mislabeled Gate5. R21–R23 have already-settled
authority; the repair is to make the example or term agree, not ask for a new
ruling. Their encounter frequency was not established, so none is inflated to
monthly/blocking severity.

Twenty prior rows were individually reviewed: three carried, five retired,
eleven refuted as conflicts and one unproven. Two old mechanical claims were
wrong: the orphaned-implementation audit was described backwards, and the
exchange audit's event-type discriminator was said not to exist. The new proofs
correct those descriptions. Shared rules agreeing without a gate are an
enforcement question, not opposing directives. **Lenses:** invariant and
jurisdiction. **Disposition:** clarify source prescriptions; retain explicit
exceptions; retire refuted audit claims while preserving their review trail.

### F6 — Evaluation clustering runs fixtures instead of the live operation

**Lenses:** change point, invariant, escalation. Decision3 promises periodic
clustering of evaluation and justification evidence. The library works against
the actual project: a temporary-output probe emitted six proposals. But the
chore's prescribed execution and acceptance criteria only run fixture tests and
layout checks. Ten passing tests therefore do not witness operational clustering.
**Disposition:** reconnect the existing operation, tracked as
[GHI #997](https://github.com/tvproductions/gzkit/issues/997) under ADR-0.0.26.
Proposal novelty and quality were not established; nothing was automatically
promoted into canon.

F2's same empty-file defect also permits Draft→Proposed in the real lifecycle
object when injected with the temporary project. It is separately tracked as
[GHI #996](https://github.com/tvproductions/gzkit/issues/996), with identity,
qualification and lifecycle consumers in its bounded closure contract. These
are independent discovery captures; neither work order was executed here.

### F7 — Completed evidence names a different OBPI

**Lenses:** invariant, jurisdiction. OBPI-0.0.26-02's completion evidence describes
OBPI-0.0.24-04. The mismatch is present in both the brief and the attached
evidence of ledger receipt at line4637, not merely a derived status view. The
operator's attestation remains recorded; its copied enrichment is not proof of
the binding gate's implementation. **Disposition:** investigate and correct the
evidence attribution under ADR-0.0.26 through append-only governance. Preserve
operator words and history. Do not rewrite the ledger or silently alter a
completed brief during an audit.

### F8 — Freshness witnesses ignore edits to tracked proofs

**Lenses:** invariant, escalation. `scripts/check_proof_freshness.py` says
"Uncommitted proofs are treated as fresh", but only never-committed files take
that arm; modified tracked proofs retain their old commit time. All three
refreshed chore proofs therefore still fail freshness. Their schema/self-tests
and the substantive audit results are separate evidence; `chores audit` only
reports log presence. **Disposition:** reconcile the documented uncommitted
case with a meaningful freshness witness; do not equate a dirty file with a
completed procedure or commit merely to manufacture a green audit. Existing
[GHI #936](https://github.com/tvproductions/gzkit/issues/936) concerns surfacing
overdue chores, an adjacent but distinct observation.

## Four-dimensional reading

The lineage below identifies the skill's interpretive lenses; local authority
and the observed mechanisms carry every finding. It does not claim the cited
authors proved anything about gzkit.

### Change point

- **Concern:** the intended operation and the thing its verifier exercises can diverge.
- **Governing question:** what is the narrowest legitimate seam that restores the behavior?
- **Intellectual lineage:** Feathers, Fowler, Hunt and Thomas; the skill's seams cluster.
- **Current mechanisms:** chore criteria, validator dispatch, pure generator and shared airlock primitive.
- **Evidence to inspect:** canonical reachability sweep; live/temp-output `run_cluster`; generator preservation probe; GHI997's operation-versus-test distinction.
- **Failure signatures:** fixture execution presented as operational work; literal-call scan presented as a full caller model.
- **Boundaries:** repair the clustering caller/inputs/outputs together; do not widen into new graph infrastructure or treat diagnostic reach as calibrated impact analysis.

Fresh-agent reconstruction: **partial**. Source and pure APIs reveal the seam,
but the chore labels its test command "Run clustering". This report and the
bounded issue make the missing connection explicit.

### Jurisdiction

- **Concern:** available mutation authority can exceed the authorized change surface, and shared terms can hide different subjects.
- **Governing question:** which decisions/artifacts may this agent disturb, and which authority governs?
- **Intellectual lineage:** Parnas plus Saltzer/Schroeder's least-privilege anchor; design boundaries and mutation authority remain distinct.
- **Current mechanisms:** brief Allowed Paths, operator-only OBPI initiation, canonical/mirror ownership, corpus attestation, distinct transit/exchange/session event types.
- **Evidence to inspect:** full-context rule pairs; corpus retirement refusal; actual airlock producers; root rulings and current brief ownership.
- **Failure signatures:** opposite canonical authoring directions; terminal transport made a prerequisite for operator authority; attestation enrichment bound to the wrong work.
- **Boundaries:** this audit records proofs/issues/insights; no OBPI machinery, rule promotion, corpus mutation or lock action follows. Read broadly and write within the diagnosis contract.

Fresh-agent reconstruction: **partial**. Root canon settles important cases,
but old examples and the intrinsic-attestation producer still contradict it.
An allowlist in prose does not prove least-privilege enforcement.

### Invariant

- **Concern:** the ADR, the implementation and its proof must describe the same property and subject.
- **Governing question:** what must remain true across the change and its representations?
- **Intellectual lineage:** Meyer and Brooks; the skill's contracts and conceptual-integrity cluster.
- **Current mechanisms:** threshold-driven binding, walkthrough parser, corpus generator/lineage validator, decrease-only ratchet, rule version/audit checks.
- **Evidence to inspect:** empty-file/lifecycle probe; actual12-section UNGRADED disclosure; ten byte-identical carried sections and complete byte partition; receipt4637.
- **Failure signatures:** presence substituted for procedure; copied proof from another OBPI; green result with zero measured coverage read as fulfillment.
- **Boundaries:** keep operator-ratified ungraded/staged states visible. Structural completeness is not semantic correctness; a representation analogy needs actual preservation evidence.

Fresh-agent reconstruction: **partial**. Corpus accounting and explicit
ungraded disclosure are useful; contradictory evidence enrichment prevents
reconstructing the evaluation gate's proof from its completion record alone.

### Escalation

- **Concern:** a control must expose insufficient knowledge and carry a useful impact argument into the next authorized action.
- **Governing question:** when the seam is inadequate, what stops or reports, and what evidence travels with that decision?
- **Intellectual lineage:** Arnold and Bohner; the skill's impact/control cluster, with the airlock's operator-defined orientation purpose preserved.
- **Current mechanisms:** airlock findings/menu, lifecycle refusal, post-append advisory, chore failure log, GHI/insight routing and session handoff.
- **Evidence to inspect:** actual IN/OUT previews; evaluation exit3; zero-byte bypass; all three failed freshness logs; corpus08's undrawn-status annotation.
- **Failure signatures:** expected escalation bypassed by empty evidence; diagnostic CLEAN mistaken for measured disturbance; status residue mistaken for permission to start work.
- **Boundaries:** findings recommend fresh authorized work; they do not execute it. Transit orients an ecosystem encounter, exchange accounts for block occupancy, and handoff preserves session understanding.

Fresh-agent reconstruction: **partial**. The corpus08 annotation prevents a
specific mistaken resumption; airlock calibration and captured broader purpose
must accompany the green preview so a successor knows what is still unknown.

### Five checks before disposition

| Dimension | Health | Opportunity | Strategic fit | Tactical tweak | Retirement |
|---|---|---|---|---|---|
| Change point | Clustering operation exists but recurring caller misses it. | Reconnect existing operation with live inputs. | Directly serves the completed evaluation ADR. | Correct chore execution and observe outputs. | Retain useful library/validator; no low-count deletion. |
| Jurisdiction | Root authority is clearer than several inherited prescriptions. | Align mutation/attestation routes with that authority. | Preserves operator initiation and canonical ownership. | Fix nested-version and canonical-command examples; route transport conflict. | Retire obsolete prescriptions, not attestation or scope obligations. |
| Invariant | Presence and wrong-subject evidence can pass as proof. | Bind evidence to required reasoning and actual subject. | Repairs existing guarantees rather than introducing another gate family. | GHI996 plus attributed receipt correction; keep lineage coverage disclosure. | Retire refuted audit claims with recorded reasons; retain explicit conditional controls. |
| Escalation | Findings/logs exist but some outcomes overstate coverage or bypass reasoning. | Carry calibration, subject and missing-proof limits into next action. | Supports campaign completion without initiating new OBPIs. | Reconcile freshness semantics and existing airlock calibration obligations. | No evidence that the airlock, handoff or conditional ledger events should be retired. |

## Routing record and residual ownership

- **Repair work orders:** GHI996 for reasoning qualification/binding; GHI997 for live clustering. Both are captured, open and unselected, with no technical blocker invented to explain that status.
- **Attributed observations:** F1, F3–F5, F7–F8 and the rule matrix's secondary stale descriptions are retained in this report and governed insights. Their next action is scoped repair/investigation, not automatic execution.
- **Airlock:** retain the primitive and staged frontier. Follow-up source correction (2026-09-12): the active campaign explicitly routes the disclosed calibration residuals to the already-authored ADR-0.37.0, rather than reopening ADR-0.33.0. That successor remains subject to feature ADR order and operator initiation; this audit does not assert its completion. Read the campaign's Movement B destination before drawing that work.
- **Corpus:** pending07 owns publication. Undrawn08 owns final advisory and `_drift.py`'s stale statement that retirement can only shrink the invariant floor; `retire.py` already handles tombstone revival. The live brief explicitly says its Active status is residue, not a draw. Repair requires operator ownership disposition, and this audit does not supply one.
- **Next-run candidates:** ADR0.32 work-edge integration; ADR0.0.29 transport prerequisite; current lifecycle call-site coverage and automatic-reaper authority context. No sample was widened to them.
- **Additions/removals:** refreshed three proof sets, added bounded trace evidence and two corrective GHIs; corrected obsolete audit conclusions. No control, canon, event type, runtime behavior or OBPI was removed or added.

## Audit limits

Final artifact checks: `git diff --check`, CLI alignment, ledger validation,
and the six-row conflict-matrix evidence validator passed. The disclosed local
Markdown-link check inspected 21 targets and found none missing. Nine findings
or observations were recorded through `gz insights remember` at
2026-09-12T17:42:07–17:42:09Z. Report, trace evidence and refreshed proofs remain
uncommitted; the two corrective GHIs are published. No full-suite or clean-tree
claim is made.

The 98-scope sweep is not the full unit, BDD, lint, typecheck and documentation
suite. This run does not establish active labor per OBPI, a trend in completion
cost, or the effect of a control on elapsed time. The vocabulary census counts
raw event types; source and subject inspection are needed for lifecycle claims.
The literature supplies the four reading lenses; local canon and observed
behavior decide the findings. No new literature claim is offered as evidence
that a gzkit mechanism works.
