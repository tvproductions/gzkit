<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Grounding pivot and design candidates — requirements, bounded advances, and releases

**2026-09-25. Status: accepted design grounding, with proposed mechanics below.**
Operator: **g0**. The request to move this conversation into a plausible design
pivot opens this bounded Phase 4 drafting exercise; see
[`OPEN-QUESTIONS.md` Q-17](OPEN-QUESTIONS.md#q-17-move-this-conversation-to-a-plausible-design-pivot).
This file is the candidate home already selected at Q-12. It is subordinate to
[`FINDINGS.md`](FINDINGS.md); design reasoning changes no finding's evidential
status. **The ownership relationship is now adopted doctrine:** the operator
directed an explicit [Magna Carta §3 amendment](../build-to-1.0-campaign-2026-09-20.md#amendments-2026-09-25)
and reconciliation of its governing surfaces. This adopts independent requirement
authority and reference-based work assignments; it does not implement catalog
mechanics. Pilot, adoption of proposed mechanics, migration, ADR booking, and OBPI
execution remain separate decisions. Existing campaign order, operator initiation, five gates,
and Q-08/Q-10 release rulings remain in force.

For the stakes, reasoning sequence, attachment provenance, and alternatives
that led here, read the [dated session record](design-pivot-session-2026-09-25.md).
That record preserves deliberation; this file remains the sole candidate home.
The [option inventory](#alternatives-and-their-disposition) distinguishes
accepted directions from explored alternatives and agent recommendations.

## Grounding pivot

This is the durable starting point for the next design discussion. The operator
accepted the five roles below and directed that this conversation become a
**GROUNDING/ANCHORING pivot**. Preserve these distinctions across investigation,
planning, implementation proposals, and handoffs; changing the direction calls
for an explicit operator decision, not a new agent's reconstruction of it.

1. Product requirements have authority and a change history independent of any
   one attempt to realize them. Planning can discover or refine them.
2. mADRs retain design intent, decisions, rationale, scope, and constraints for
   a bounded advance. Briefs assemble the assignment and evidence by reference
   to authoritative requirements. Their bounded-foray function is intentional.
3. Catalog obligations, local acceptance criteria, design constraints, rationale,
   implementation tasks, and historical evidence have distinct meanings even
   when they appear in one document. Extract from ADR bodies as well as briefs.
4. An assignment and its evidence concern an identifiable requirement state and
   product configuration. Changed needs do not silently rewrite prior acceptance.
5. Brief completion, whole-requirement satisfaction, and actual release content
   are separate claims. Each must have an identifiable basis.
6. Deterministic controls can enforce specified boundaries and transitions.
   Correct requirements and meaningful tests still require engineering judgment.
   TDD, BDD, and DDD remain strong grounding influences.
7. The coupling's effectiveness remains a hypothesis to examine. Preserve its
   intended control function while allowing evidence to challenge its mechanics;
   neither standards vocabulary nor sunk investment proves it effective.
8. **All investigations continue.** IEEE can substantiate and challenge the
   design even where names were appropriated unconventionally. The test work
   addresses a real verification problem. Magna Carta supplies release planning
   logic. These efforts inform the pivot rather than compete to replace it.

These are accepted design directions, not assertions that the code implements
them or that they explain all churn. The remaining sections propose how to
realize and test them. A schema, identifier grammar, migration schedule, new
gate, and capability hierarchy are not adopted by this anchor.

## Recommended pivot

Keep the bounded increment → brief → task operating structure. Give product
requirements an independent, versioned authority. Make each brief's contribution
to those requirements explicit. Record shipped configurations independently of
the work's name or completion.

The correction is to ownership and claims. A work package may discover a
requirement, implement part of it, or supply evidence about it; that does not
make the requirement's continuing existence depend on the package's lifecycle.
Likewise, a completed advance does not erase its design rationale, and a
requirement reference does not prove satisfaction.

The operator accepted these roles:

| Role | Authority and purpose |
|---|---|
| Requirements catalog | What the product must satisfy, why, and how that understanding has changed |
| mADR | The decision and rationale for the next bounded advance, including scope and constraints |
| Brief | The assignment: its contribution to selected requirements, implementation boundaries, and required evidence |
| Plan, specification, and tasks | The detail needed to execute the assignment |
| Release record | What actually shipped, with supporting evidence |

These are information responsibilities, not a mandate for five new document
types. Keep ADR and OBPI names and historical identifiers in the first candidate.
Use “brief” as the understandable name for the existing OBPI work package.
Capability categories may aid navigation; they need not own briefs or require
a new hierarchy. The PRD remains the source of product intent under Q-02.

## Extract meaning from ADRs as well as briefs

The extraction unit is a statement and its governing context, not a file, a
heading, or a token beginning with REQ. Read ADR intent, decision, constraints,
boundary invariants, alternatives, amendments, and related brief criteria
together. Preserve the originating passage and decision provenance.

| Question about the statement | Proposed treatment |
|---|---|
| Must supported product configurations continue to satisfy it after this work ends? | Candidate catalog obligation, with applicability and a means of evaluating it |
| Does it select or constrain a design while that decision remains applicable? | Keep the decision and rationale in the ADR; reference the applicable constraint. Promote a separately testable obligation only where justified |
| Does it say what this particular assignment must deliver or demonstrate? | Local acceptance criterion in the brief, linked to any catalog obligation it advances |
| Does it prescribe a sequence of implementation actions? | Plan or task; do not treat the action's completion as product satisfaction |
| Does it explain why an option was chosen or rejected? | Rationale in the ADR, retained even if the decision is later superseded |
| Does it report what happened, what ran, or who accepted it? | Historical evidence and ledger provenance, not a new requirement |

“Continuing” does not mean eternal, externally visible, or implementation-free.
Security properties, quality attributes, interfaces, internal invariants, and
deliberately chosen design constraints can all be continuing obligations.
Their applicability can later change through an explicit decision. Conversely,
a local criterion can be technically substantive and mandatory without becoming
a standing product obligation.

Split mixed statements without weakening them: retain the continuing property,
the local delivery commitment, and the reason they were joined. An extraction
must not quietly broaden a narrow promise, weaken a broad one, or decide an
ambiguous obligation on the operator's behalf. Unknown disposition remains
explicitly unresolved; it is not an excuse to lose the statement.

The existing **BEHAVIOR / SUPPORT / STRUCTURAL-FENCE** distinction answers
which proof channel applies. It does not answer how long a statement applies or
who owns it. Preserve those channels while evaluating durability separately.

### An illustrative split

Consider an airlock-related statement combining a continuing requirement to
account for affected boundaries, a requirement to expose an entry operation,
and a task to wire that operation into a particular pipeline stage.

- The catalog can carry the continuing boundary-accounting obligation with
  explicit applicability.
- The ADR retains the decision to realize it through an entry/exit airlock and
  the rationale for that choice.
- A brief undertakes the pipeline integration, defines its bounded contribution,
  and states the behavior and evidence needed to accept that integration.
- The implementation plan names the actual wiring tasks.

This is a design illustration, not a claim that existing airlock coverage is
complete. The original [airlock model](../work-phases-and-airlock.md) expressly
seeks to give an agent a bounded working set. Its implementation and calibration
must be judged from their own evidence. ADR-0.37.0 already owns the campaign's
airlock calibration work; this proposal does not reorder or duplicate it.

### Worked classification from the existing airlock package

These are proposed classifications after reading the complete ADR-0.33.0,
OBPI-02, and OBPI-06 artifacts. They are not amendments to their accepted text
and are not assertions about the present runtime.

| Existing material | Proposed disposition and reason |
|---|---|
| [REQ-0.33.0-02-04](../../design/adr/pre-release/ADR-0.33.0-airlock-membrane/obpis/OBPI-0.33.0-02-airlock-in-pipeline-tracer.md): NO-GO explains the seam, provenance, and recovery | Candidate continuing behavior. Its test citation is a proof binding, and its explanation of avoiding an unhelpful refusal is rationale |
| REQ-0.33.0-02-06 in the same brief: invoke the primitive, emit L2, never write L1, with specified helper placement | Mixed. Separate ongoing invocation/accounting constraints from the implementation recipe. Whether helper/executor separation is itself a continuing architectural constraint requires judgment; do not silently demote it to a task |
| [REQ-0.33.0-06-02](../../design/adr/pre-release/ADR-0.33.0-airlock-membrane/obpis/OBPI-0.33.0-06-airlock-doctrine-lawful.md): a seam has both BODY and BOUNDARY, delivered in the SAME promotion | Continuing domain definition plus local sequencing. DDD preserves the definition without requiring every definition to become a numbered product REQ |
| REQ-0.33.0-06-04 in the same brief: check a named campaign box and produce its edit evidence | Local acceptance, task, and historical evidence; a dated checkbox is not a continuing product property |
| REQ-0.33.0-02-03: refuse an omitted edge at a REAL pipeline entry, versus the brief's dated tracer frontier | Unresolved mapping. The July acceptance qualification says production Stage-1 wiring remained diagnostic. Preserve the literal criterion and qualification and obtain an explicit disposition; do not infer full product satisfaction from completed work |

These cases demonstrate why extraction requires statement-level interpretation
with provenance. They do not quantify how much of the overall corpus is durable.

## Requirement, assignment, and evidence identity

The operator's accepted distinction remains the starting point. These codes
are illustrative; this proposal does not make them executable grammar.

| Identity | Example | Meaning |
|---|---|---|
| Catalog requirement | `REQ-C2.3` | Independently maintained obligation |
| Work package | `OBPI-0.35.0-14` | Particular assignment being executed |
| Requirement assignment | `OBPI-0.35.0-14-C2.3` | This brief's responsibility for the obligation |

Recommend a Git-versioned catalog rather than a new service or database.
Initially, the needed information can live in a small authored catalog and an
assignment table in existing briefs. File splitting and field syntax follow
the worked example; they are not reasons to rename historical artifacts.

A catalog entry needs stable identity, the requirement statement, rationale or
source, applicability, and retained revision/approval history. It links upward
to the relevant product need or decision. Its change history distinguishes
proposed wording from approved obligations. A category is navigation metadata;
moving an entry between categories should not force identity changes.

An assignment needs the catalog identity and exact applicable revision, the
contribution promised, local acceptance criteria, applicable design constraints,
and the required proof channels. Its contribution may implement, refine,
verify, repair, or retire an obligation through an authorized change. A brief
may address several requirements; a requirement may have several assignments.
No assignment needs its own new document.

**Amendments are new contract versions.** Before execution, approval fixes the
assignment contract and the requirement states it addresses. An approved change
creates a distinguishable successor contract; existing acceptance records keep
their original subject. A split produces successor assignments with explicit
lineage, not duplicate identities or rewritten proof subjects. The current
acceptance store's immutable contract/roster behavior needs a designed transition
for this; adding a mutable catalog lookup does not supply one.
See [`acceptance_store.py`](../../../src/gzkit/acceptance_store.py), contract
initialization and replay: an existing contract and its roster cannot simply be
replaced under the same recorded subject.

For migration, existing `REQ-X.Y.Z-NN-MM` identities can remain local acceptance
identities and assignment aliases. A reviewed mapping relates them to catalog
entries. A mixed legacy criterion may map to more than one obligation; the
mapping must explain the split rather than promise a one-to-one conversion.
Old test tags and ledger subjects retain their historical meaning. New
reusable catalog codes must not become globally reusable TASK identities.

### What acceptance claims

An acceptance concerns an identifiable requirement revision, assignment
contract, product configuration, execution conditions, and evidence. A retained
Git revision plus the requirement identity can identify the definition; a
digest verifies content but does not replace retrievable content or approval.
“Latest” is not a reproducible requirement reference.

Completing a brief means its assigned contribution was accepted. Establishing
that a product configuration satisfies the whole requirement additionally
needs evidence covering that requirement's applicability and full obligation.
Do not calculate this from a count of completed briefs. Unknown satisfaction
must remain unknown, and a planning status must not stand in for evidence.

**Proposed owner of the full claim:** the operator accepts an explicit
whole-requirement claim against the named requirement revision and product
configuration, supported by integrated proof and the required independent
review. Record it through the existing acceptance/attestation route and L2
provenance; this does not propose a sixth gate. The precise event subject and
schema remain to be designed. Until they can express this claim, an L3 view
must report accepted contributions and unestablished overall satisfaction.
Release approval alone cannot manufacture that claim.

The catalog is L1 authored intent. Approval and acceptance occurrences are L2
events through the governed write path. Current satisfaction reports and
coverage summaries are L3 projections. They must identify the requirement and
configuration about which they make a claim, under existing
[state doctrine](../state-doctrine.md).

## Learning without rewriting history

Planning can discover a requirement. Capture the proposed definition in the
catalog with a reference to the originating ADR; approval uses the existing
human decision process. The approved assignment then references that definition.
No special preliminary requirements phase is required before useful design can
begin, and a discovery does not silently become an approved obligation.

When a requirement changes during execution, identify the semantic change and
its affected assignments, evidence, and intended release. Obtain the required
decision on continuing against the old baseline or revising the assignment.
Changed wording is not an automatic permission to expand the work or an
automatic assertion that old tests remain sufficient.

An older pin is not stale merely because a newer definition exists. It is
inapplicable when the governing approval no longer authorizes that definition
for the assignment or target configuration. Evidence for unaffected assertions
may be reusable after explicit applicability assessment and the required
current checks; the old whole-contract acceptance is not relabeled as new.
Changed proof subjects require new proof. Preserve the original evidence's
actual inputs and conditions even when it contributes to a later claim.

For example, an illustrative requirement might require rejecting acceptance
evidence that does not match its governing contract. A later revision may add
an explicit obligation to bind evidence to the tested product configuration.
The first brief's acceptance remains about the earlier statement and
configuration. A later brief can provide the new binding. An intervening
release must declare which approved requirement baseline applies; it cannot
claim the new obligation is satisfied merely because the old brief completed.

Historical acceptance is not repudiated merely because needs changed. Conversely,
evidence later shown invalid is not rescued by calling it historical. Keep
those cases separate under the existing withdraw/repudiate doctrine.

The [attested-REQ retirement rule](../attested-req-subject-retirement.md)
already distinguishes repairable proof surfaces from literal obligations that
a later ruling retires. The latter require an operator decision. The pivot
needs an explicit supersession/applicability relation for them; it does not
authorize rewriting sealed ADRs or deleting their evidence.

**Conflict rule:** a catalog edit cannot silently override an applicable ADR
constraint. Record the approving decision, the superseded statement, and its
effective applicability. Equally, an old ADR does not veto an explicitly
approved successor decision. If the governing relationship is unresolved,
surface the conflict and withhold the affected claim; neither “catalog always
wins” nor “historical ADR always wins” is the rule.

A concrete pilot case is
[REQ-0.19.0-01-04](../../design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/obpis/OBPI-0.19.0-01-gz-closeout-adr-x-y-z-end-to-end-closeout-pipeline.md):
it literally requires the version bump to derive from ADR semver, while Q-08
rules that derivation must stop. A successor requirement must identify that
supersession and its applicability through operator disposition. Retagging the
old test is not a truthful reconciliation of the two assertions.

## Retain and test the control discipline

Keep one admitted delivery increment and a bounded assignment for each agent
foray as the proposed operating policy. “One active” concerns work admission,
not the number of still-applicable architectural decisions. Finishing an
increment does not switch off all its design constraints. Research, pooled
ideas, and authorized corrective GHIs retain their existing routes.

This is work-admission policy. A catalog category is navigation; a DDD bounded
context is a domain/model boundary. A brief may cross categories and contexts
while accounting for their contracts. These are not interchangeable containers.
“Other work pooled” does not authorize demoting existing work, adding forbidden
runtime-track pool entries, or promoting post-1.0 work.

The airlock's role is to establish the affected boundaries and relevant
obligations at entry, then account for effects at exit. It should make the
selected context sufficient and inspectable, including relevant unselected
obligations that the change could violate. A narrow catalog selection must not
permit the agent to ignore the rest of the product's applicable constraints.

Separate two claims:

1. **Mechanical claim:** a transition refuses missing authorization, missing or
   mismatched requirement references, insufficient required evidence, or
   unaccounted effects where those controls are implemented. Demonstrate each
   refusal and its valid counterpart; a rule's presence is not enforcement.
2. **Engineering claim:** the requirement expresses the intended need; the
   implementation fulfills it; and the tests can detect meaningful violations.
   This needs substantive validation and review, not only well-formed records.

The existing gate names and human authority remain. TDD supplies requirement-
derived assertions and meaningful failing controls; BDD exercises the accepted
user behavior on the heavy lane; DDD keeps the domain language and boundaries
coherent. Independent review checks omissions, incorrect assumptions, and
whether the observed evidence warrants the stated claim. A reviewer agreeing
with the implementer is not an oracle by itself.

**Hypothesis:** bounded assignments with explicit, current obligations and
accountable entry/exit reduce unauthorized scope changes, missed constraints,
and repeated operator corrections across successive changes. The exact
artifact hierarchy, brief size, and context packaging are implementations of
that hypothesis. Their value must be measured under named tasks and models.
Existing human authorization and acceptance requirements do not disappear when
a model improves; changing a control requires a recorded decision.

## Release and backlog implications

An mADR may target a release and organize the work intended for it. Under Q-08,
its identifier does not determine the package version. Under Q-10, the L2
release record identifies approved content. It must bind the actual source or
artifact configuration, version, relevant accepted contributions, requirement
baseline, and evidence. An inventory of selected briefs cannot exclude code
already present in the published artifact.

The main-only workflow has a concrete constraint: if unfinished next-increment
code has landed on main, publishing main as a patch also publishes that code.
The candidate therefore cannot promise patch-only interruption without an
explicit source-selection policy. Retaining main-only implies the late repair
ships with a configuration approved as a whole, or publication waits; choosing
a separate maintenance source would require a deliberate workflow change.
No branch strategy is introduced by this proposal.

The proposed “resolve problems before the next ADR” rule needs a defined
population: failures against accepted obligations cannot vanish through issue
filing, while research questions and proposed enhancements are not automatically
defects. Whether every known defect blocks admission is an operator policy
choice, not something this proposal silently weakens into a readiness score.
Magna Carta continues to prioritize the work; the catalog describes needs and
is not itself a delivery schedule.

## Implementation seam and bounded migration

Inspection at HEAD `5972058826e654db1c06cb33e7f2b57ee7fa4393`, with concurrent
working-tree activity, identifies reusable machinery, not an implementation
estimate. [`acceptance.py`](../../../src/gzkit/acceptance.py) already separates
obligations, executed proofs, and independent judgments. Its module contract
explicitly disclaims inferring semantic adequacy from metadata.
[`acceptance_execution.py`](../../../src/gzkit/acceptance_execution.py) obtains
requirements from the brief and includes the brief and parent ADR in the
contract digest. Catalog definitions and their pinned revisions would have to
enter that authoritative read path and digest.

The coupled consumers include authoring/templates, requirement discovery and
coverage, proof resolution, task allocation, acceptance/completion, and derived
reporting. STRUCTURAL-FENCE resolution and some ownership queries infer the ADR
from today's REQ identity; reusable requirements need explicit assignment
context there. Merely moving Markdown would leave those consumers wrong.
Distribution and documentation must deliver the same behavior to adopters.

Recommended migration shape, subject to the pilot and adoption decision:

1. Classify one representative existing ADR package, including ADR-body material,
   and prepare a reviewed mapping with sources and unresolved cases.
2. Exercise a catalog-backed assignment through the existing acceptance path,
   with an explicit compatibility reader for unchanged legacy briefs. Each
   obligation has one authoritative definition; copied excerpts are labeled
   projections, not a second editable authority.
3. Make requirement revision, assignment amendment, evidence validity, and
   release content work together for that bounded case before expanding.
4. Introduce future work through the proven path and migrate existing durable
   obligations when affected, retaining a visible inventory of unmigrated
   scope. A partial catalog must not claim complete product coverage.

This bounds the first implementation without declaring the rest migrated.
Catalog extraction, release authority, and effective proof cannot be claimed
complete independently if their connecting read paths remain inconsistent.

## Alternatives and their disposition

**Expanded 2026-09-25 after the operator's retention check.** The first rendition
compressed this landscape into three rows. It conflated conventional ADRs with
capability ownership and omitted timing, replacement scope, and an earlier
release-first recommendation. The following inventory repairs that loss without
reopening the accepted five roles or treating an agent's preference as a ruling.
Labels in these tables are discussion handles, not new governance identifiers.

### Recovery timing and extent

| Explored route | Why it was considered | Cost or unresolved challenge | Current standing |
|---|---|---|---|
| Continue with corrections to the current organization | Preserve familiar controls and near-term delivery; use GHIs and patches | Repeated local repairs may leave the ownership conflict producing new defects | Operator's null hypothesis and comparison baseline; leaving requirements embedded conflicts with the later accepted anchor |
| Defer structural change until 1.0 | Avoid combining migration with current work | No demonstrated basis that waiting lowers total cost or makes 1.0 reachable; more material may accumulate under the current relationships | Operator-raised timing option, not selected; adoption of the anchor does not itself schedule migration |
| Incremental migration in place | Preserve ledger history, acceptance machinery, distribution, and bounded work while correcting authority | Compatibility, revision binding, task identity, and release consumers still require coordinated changes | Current agent recommendation for a bounded pilot, not an implementation authorization or cost estimate |
| Replace a bounded subsystem | A catalog/assignment/release subsystem could be cleaner than extending assumptions spread across current consumers | Requires explicit interfaces, a cutover, history preservation, and an honest comparison with in-place change | Earlier research option retained; distinct from a whole-project rewrite and from capability ownership |
| Broad reorganization around capabilities | Reconsider ownership, vocabulary, and work organization together | More simultaneous semantic and migration changes; capability boundaries remain unvalidated | Operator's initial direction, subsequently questioned; not selected, not permanently rejected |
| Abandon or restart | Operator raised the possibility that recovery cost may exceed the project's value | Six months already spent proves neither recoverability nor futility; reusable investments and replacement risks need examination | Strategic concern preserved, not a recommendation or a concluded diagnosis |

The agent recommendation is to obtain bounded recovery evidence now before
committing to a large migration. Neither recoverability at an acceptable cost
nor the superiority of waiting has been established. The
[session record](design-pivot-session-2026-09-25.md#cost-and-recovery-questions)
retains the cost questions; Q-15 supplies the successive-change test.

### Decisions, work ownership, and names

| Candidate | Intended benefit | Unsettled relationship and disposition |
|---|---|---|
| Conventional ADRs with independently organized briefs | ADRs retain decisions and rationale; briefs reference requirements and applicable decisions without needing one ADR as their container | Distinct from capability ownership. Earlier candidate, not the current recommended first implementation; could preserve bounded work through explicit links |
| Capability-owned briefs | Product capabilities provide the stable organizing frame; work contributes to them | Operator-origin candidate. Must show useful boundaries and handle cross-capability work; a catalog category is not automatically a DDD bounded context |
| Retained mADR → brief coupling, independent requirements | Keep bounded intent and assignment control while allowing product obligations to recur across advances | Closest to the accepted anchor. Exact schema, admission policy, and effectiveness remain proposed or unmeasured |
| Strong mADR/release discipline | One admitted effort aims at a release; corrections use GHIs and patches before admitting the next effort | Explicit operator-proposed alternative, not reduced to a naming issue. Release association and the population of blocking problems remain to be specified; cannot silently reverse Q-08/Q-10 |
| Rename the campaign step while preserving its function | Let the overloaded ADR name disappear while keeping decision, rationale, scope, and bounded delivery planning | Operator's alternative to defending an unconventional name. No replacement name selected; a rename alone cannot correct ownership or evidence claims |
| Rename OBPIs to briefs or call them sorties | Make the work assignment understandable and preserve the idea of one serious foray | “Brief” is accepted as the work-package role; executable names, identifier migration, and “sortie” terminology remain open |

Three couplings must be evaluated separately: **intent to assigned work**,
**a planned increment to an intended release**, and **an ADR identifier to the
package version**. The anchor retains the first. The stronger mADR candidate
explores the second. Q-08 rejects the third. Q-10 still requires a record of
actual approved shipped content. Saying an mADR “may target a release” above
is the agent's proposed minimum relationship, not an operator rejection of
the stronger release-effort discipline.

The recommendation to avoid a capability hierarchy in the first pilot means
it is unnecessary to test the immediate separation. It does not mean the
operator has rejected capability organization or conventional ADR semantics.

### Requirement and assurance candidates carried forward

| Design strand | Accepted foundation | Mechanics or question still open |
|---|---|---|
| FDAU-like categorized requirements/backlog | Requirements independent of work, reusable through assignment references | FDAU codes are local precedent, not a sourced standard; category boundaries and executable grammar need design |
| Catalog requirement / work package / assignment identities | The three meanings are accepted, with `REQ-C2.3`, `OBPI-0.35.0-14`, and `OBPI-0.35.0-14-C2.3` as illustrations | Stable identity versus category movement; aliases, composite references, and assignment-local task/proof lookup |
| Extract ADR intent and REQs | Durable obligations and local acceptance are distinct; ADR bodies contain both design and requirement material | Statement-level classification, mixed statements, design constraints, and unresolved mappings; no indiscriminate REQ copying |
| Evolving requirements during planning and successive assignments | Planning may discover needs; historical acceptance retains its original subject | Approval, revisions, supersession, split/amended assignments, applicable baselines, and evidence reuse |
| Brief as an enveloping work package | Selected requirements, contribution, boundaries, work, and evidence are presented together by reference | How much plan/spec/task detail each assignment needs; no mandatory separate file for every information role |
| Deterministic clamp and airlock | Bounded work and accountable transitions retain their intended control purpose | Whether selected context is sufficient, whether refusal paths actually work, and whether controls reduce repeated errors |
| TDD, BDD, DDD, and independent evaluation | All remain strong influences; procedural completion cannot establish correct needs or meaningful tests | Semantic oracles, negative controls, domain boundaries, and the proposed whole-requirement acceptance subject |
| Release/backlog planning | Product obligations, work admission, and shipped content are distinct | Strong release coupling, patch interruption on main, actual-content selection, and readiness criteria |

### Previously examined implementation sequences

| Sequence | Rationale and tradeoff | Status |
|---|---|---|
| Release authority first | Implement Q-08/Q-10 independently of capability ownership, then exercise reusable requirements over successive assignments/releases. Removes an explicit false equivalence early, but leaves requirement ownership to follow | Earlier agent recommendation retained; never an accepted execution order |
| Catalog/assignment seam first | Start with classification and the acceptance reader, then connect revisions, proof, and releases. Exercises the most important identity distinction early, but must not leave release truth disconnected | Order used in the current agent-proposed migration sketch |
| One bounded end-to-end case | Carry requirement, assignment, evidence, and actual release through successive changes before wider migration. Tests the connections, but needs a deliberately limited case | Current recommended evaluation shape; pilot authorization remains separate |

These routes can be staged together, but their order is not silently settled by
their presentation here. The selected control structure must remain correctable
if the pilot contradicts its intended benefit.

## Pilot specification, for separate authorization

Use the existing Q-15 successive-change criterion. First capture a comparable
baseline for a bounded case: applicable obligations, reconstruction correctness,
missed constraints, regressions, recurring operator corrections, and effort
needed to determine authority. Record model, task, context, and configuration.
Effort supplements correctness; reduced effort alone does not justify weaker
control. This small worked classification is not the full M-A population study.

Carry the same artifacts through this sequence rather than resetting examples:

1. An initial assignment addresses part of one requirement and completes before
   release. Whole-requirement satisfaction must remain unclaimed without proof.
2. A second assignment addresses the same requirement. Its completion and proof
   must not be inherited from the first assignment's ID or TASK status.
3. A new requirement revision changes a meaningful behavior and an already
   initialized assignment must be amended or superseded. Preserve the old
   acceptance, identify impacted assignments, and refuse old proof for a changed
   acceptance contract. Demonstrate the paired case where an older approved
   baseline remains applicable and succeeds. Re-run unchanged obligations where
   applicability warrants.
4. Defer or cancel one item and release a concrete configuration. Reconstruct
   included and excluded content, including the main-only patch interruption case.
5. Include an applicable constraint from a completed, non-parent ADR and a
   relevant obligation not selected for implementation. The work must discover
   and preserve them, or record an explicitly approved supersession; selecting
   a short requirement roster is not evidence of complete impact analysis.
6. A reader who did not author the remedy reconstructs requirement history,
   applicable decisions, accepted contributions, and shipped content from retained
   artifacts. No private explanation from the designer counts as evidence.

Challenge the mechanism with missing definitions, inapplicable pinned revisions,
unapproved assignment changes, evidence from another product configuration, a
retired literal constraint, and a test that passes despite a meaningful violation.
State expected valid and invalid outcomes before exercising them. An invalid
test baseline makes the experiment inconclusive; it is not evidence of strength.

**Reject or revise** if the candidate silently rewrites historical claims,
confuses partial contribution with full satisfaction, permits self-selected
scope to omit applicable constraints, misstates shipped content, or needs
duplicated authoritative status. Repeated operator corrections and expanding
exceptions are evidence to investigate, not automatically agent fault.

Holding the brief discipline fixed tests the catalog pivot, not the causal
necessity of the hierarchy. A claim that this exact coupling is essential would
need a separate controlled comparison. Do not infer that from a successful
pilot. Phase 6 remains led by someone other than this design's author.

## External grounding and its limits

| Primary source | What it supports | What it does not establish |
|---|---|---|
| [ISO/IEC/IEEE 29148:2018 official preview](https://www.iso.org/obp/ui?_escaped_fragment_=iso:std:iso-iec-ieee:29148:ed-2:v1:en), definitions of requirements management, traceability, verification and validation | Requirements management through the lifecycle; derivation/allocation relationships; objective evidence distinct from links | This catalog layout or identifier grammar |
| [ISO/IEC/IEEE 12207:2026 scope](https://www.iso.org/standard/90219.html) | Iterative, incremental and recursive application of lifecycle processes without prescribing one lifecycle method | A requirement to use mADR → OBPI, or one active increment |
| [ISO/IEC/IEEE 15289:2019 scope](https://www.iso.org/standard/74909.html) | Information items can be combined or subdivided to suit the project | Five separate files or an additional ceremony for every information role |
| [NASA requirements management](https://www.nasa.gov/reference/6-2-requirements-management/) | Baselines, change control, and maintained traceability between requirements and design | FDAU's particular codes as a standard |
| [SEI, AI Engineering: Twelve Foundational Practices](https://www.sei.cmu.edu/documents/6504/AI-Engineering-12-Foundational-Practices.pdf), 2026-04-22, practices 6–7 and 12 | Versioned context, explicit authority boundaries, automated constraints with human oversight, and measured effectiveness | Empirical validation of gzkit's current mechanisms or decomposition |
| [SEI, Five Essential Questions for Implementing the Software Acquisition Pathway](https://sei.cmu.edu/documents/6388/20251022_SWA_GoBag_Launch_Webcast.pdf), 2025-10-22, slides 5, 12 and 16 | Iterative capability delivery; distinct questions about capability needs, user value, progress, and release sequencing | That this government acquisition pathway prescribes gzkit's hierarchy, requires a new CNS document, or validates mADRs |
| [SEI, Native AI Integration for Model-Based Systems Engineering](https://www.sei.cmu.edu/blog/native-ai-integration-for-model-based-systems-engineering-three-layers-that-make-it-work/), 2026-09-02 | Deterministic validation, curated guidance, and accountable engineering review play different roles; the reported model passed checks while changing requested obligations | That structurally valid, traceable artifacts establish semantic fidelity or executed V&V |
| [Anthropic, Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), 2025-11-26 | One-feature-at-a-time work, durable progress information, and end-to-end checks helped in the reported setting | A universal law about agent capacity or a requirement for ADR ownership |
| [Anthropic, Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps), 2026-03-24 | Explicit contracts and separate evaluation helped; later model changes allowed removal of the sprint construct | A reason to remove gzkit's controls without its own evidence and operator decision |

Exact standards clauses about requirement revision and document references
quoted in [piece 02](02-requirements-vs-release-2026-09-22.md) and the
[series README](README.md#standards-corpus) remain repository-held citations;
this candidate does not claim a fresh inspection of licensed full texts.
FDAU remains an originating example, not a demonstrated implementation of this
catalog. The control hypothesis is our application of these sources.

## Relationship to work already underway

IEEE supplies distinctions and challenges; test evaluation supplies evidence
about oracle quality; Magna Carta supplies priority; TDD, BDD and DDD remain
engineering practices. None needs to become a subsidiary migration project.
The pivot gives their outputs a clearer destination without treating their
existence as proof that the pivot works.

Related prior art includes `ADR-pool.feature-adr-semver-discipline` (Q-09's
promotion restriction stands), `ADR-pool.spec-delta-markers`, and
`ADR-pool.constraint-library`. Their proposals overlap specific concerns;
this candidate neither promotes them nor assumes their dated designs are current.
The earlier `ADR-pool.obpi-req-taxonomy-scope-fence` records supersession into
ADR-0.0.59; it is precedent for preserving proof distinctions, not another
unbuilt taxonomy to add.

## Design review record

**2026-09-25 — full-triad design review.** Main author: `/root`. Adversarial
reader: `/root/adr_requirements_release`, an explorer with prior repository
research and conversation context. Fresh design reader: `/root/pivot_fresh_reader`,
started without conversation history, read the five canonical investigation
records before the candidate, and received the operator's current instructions.
Neither is claimed as a new historical Act 1 or a pilot evaluator.

| Challenge | Disposition in this revision |
|---|---|
| Mutable assignment wording meets an immutable acceptance contract and roster | Added successor-contract/split lineage semantics and a pilot amendment to an already initialized assignment. Concrete transition schema still requires design before execution |
| A hand-selected parent context can hide other applicable ADRs | Added a completed non-parent ADR and an unselected applicable obligation to the pilot. Scope completeness is tested, not inferred from selected links |
| Literal retired doctrine is already present, not hypothetical | Added REQ-0.19.0-01-04 versus Q-08 as an operator-disposition case; no sealed text or test changed |
| An old pin can be an authorized baseline | Defined inapplicability separately from age and added paired valid/invalid cases; preserved actual proof provenance |
| Catalog wording and applicable ADR constraints need a precedence rule | Require explicit approved supersession/applicability, with unresolved conflicts surfaced before an affected claim |
| Whole-requirement satisfaction needs an owner and recorded subject | Proposed operator acceptance through the existing route with integrated evidence; exact L2 subject/schema remains open and L3 cannot substitute contribution counts |
| Categories, DDD contexts, and admission policy can be mistaken for one hierarchy | Explicitly separated all three and retained existing pool restrictions |

Both readers found the direction plausible, with the above precisions and
remaining mechanics visible. This is evidence of design challenge and response,
not proof of effectiveness. The pilot, migration cost, and causal necessity of
the retained hierarchy remain unmeasured.

**2026-09-25 — retention audit after the operator's capture challenge.** The
main author compared the visible conversation and supplied attachment with the
record; `/root/adr_requirements_release` independently checked the retained
design history. Expanded the option inventory and added the dated session
record to restore timing/recovery options, independent conventional ADR and
capability candidates, the release-first route, and stronger mADR coupling.
This is a retention correction, not a new architecture ruling or pilot result.
