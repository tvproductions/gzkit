<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# Design pivot session — requirements, bounded work, releases, and V&V

**Recorded 2026-09-25. Operator: g0. Type: deliberation and provenance record.**
This preserves the breadth and reasoning of the design conversation, including
alternatives that were not selected. The current anchor and all candidate
mechanics live in [design-candidates.md](design-candidates.md); operator wording
and rulings live at [Q-16 and Q-17](OPEN-QUESTIONS.md#q-16-how-do-we-keep-the-fdau-origin-and-separation-hypothesis-under-consideration).
This record is not a second candidate authority or an implementation plan.

**Subsequent ruling, 2026-09-25:** the operator directed an explicit amendment
of Magna Carta §3 and its governing surfaces. The
[adopted ownership relationship and verbatim authorization](../build-to-1.0-campaign-2026-09-20.md#amendments-2026-09-25)
separate independent product requirements from bounded assignments. The remaining
mechanics and alternatives below retain their recorded status; catalog/runtime
migration has not been adopted or implemented by that ruling.

The operator requested this retention check:

> we have a LOT of design pivot candidates here, have you richly captured it? this is a very important design conversation/session

The initial anchor captured the latest synthesis more thoroughly than the
route to it. Its three-row alternatives table lost meaningful distinctions.
This amendment restores the option space, stakes, and source limitations.
It is a substantive account with selected verbatim passages, not a verbatim
transcript of every turn. Earlier alternatives remain visible as deliberation;
they do not supersede the later accepted grounding.

## Why this conversation matters

The operator described an inflection roughly three months earlier: discovering
and repairing bugs or misalignments had come to consume more time than forward
progress. The accumulated investment was approximately six months. These are
the operator's experience and decision context, not measurements establishing
one cause. The operator explicitly declined to blame the ADR design alone.

The decision was consequently larger than terminology: whether to continue
repairing the current organization, postpone structural change until 1.0,
pay for correction now, or acknowledge an unaffordable recovery and abandon
the approach. The recurring fear was making a second plausible design choice
that later becomes another trap. Preserve that concern when proposing an
elegant schema; coherence alone does not answer it.

> I am contemplating the cost of this reorganization, the current approach is untenable.

The operator also challenged an earlier agent assessment that recoverability
at an acceptable cost was not yet known:

> I still need some path forward.

That is a request for a concrete, testable recovery path with decision points.
It is not permission to declare recovery economical without evidence, and it
is not satisfied by repeating uncertainty. The candidate now supplies a bounded
evaluation path while retaining the unmeasured cost and effectiveness questions.

## How the design direction developed

### Initial separation and capability organization

The first proposed destination moved OBPIs out of ADRs and into capabilities,
renamed OBPIs to briefs, and drew on FDAU's requirements/backlog organization.
A brief would assemble requirements, tasks, and V&V into a usable work package.
The operator then accepted the refinement that the brief references authoritative
requirements instead of owning their only definitions:

> yes to this: "a brief can present requirements together with their work and evidence while referencing their authoritative definitions. That would let the bundle be useful without making the requirements disappear into it again."

This separated two questions: where durable product knowledge lives, and how
the working team receives a coherent assignment. A useful bundle does not
require the bundled information to share one lifecycle or owner.

Capabilities were a candidate organizing principle, not a settled answer:

> I do not know if reaching for capabilities organization "buckets" is right either. I mention SEI as one potential anchor. I am trying to fall back on IEEE as a fallback onto authority/standards/principles.

Thus conventional decision ADRs, independently organized briefs, capability
ownership of briefs, and categorized requirements are separate choices. The
first capture incorrectly collapsed the first two with a capability rebuild.
The [expanded inventory](design-candidates.md#decisions-work-ownership-and-names)
now keeps them distinct. Accepting the current mADR role does not prove that
capabilities are wrong or that the existing hierarchy is necessary.

### Narrowing the immediate correction

The operator subsequently focused on separating ADRs, requirements, and release
tracking, possibly through the smallest sufficient adjustment. ADR identity as
release increment, requirements ownership by ADR, and absent independent
release/backlog planning were named as distinct problems.

The parallel investigations have different jobs. The operator explained:

> I reached for ieee to ground on authority/first principles; I reached for the test evaluation because I believe the models have been writing poor tests; I reach for the magna carta because I need some prioritized path forward; I reach for for the effort about requirements/release separation because I know the current approach is flawed.

Later, poor tests were described as technical debt, IEEE comparison as reflective
maintenance, and Magna Carta as release planning. The point was to make these
efforts intelligible together without making every investigation a prerequisite
for all other progress. The final direction explicitly continues all of them.

### The deliberate mADR counterproposal

The operator then tested the opposite explanation: perhaps the tight coupling
was a useful agent-control provision, and a modified ADR could honestly serve
as the decision and plan for one bounded advance. This was a serious competing
hypothesis, not a confession that the current system must be defended at any cost.

Its strongest form included one active ADR, other prospective work pooled,
corrections through GHIs and patch bumps, and no next ADR until current problems
were resolved. Requirements could still leave the ADR for a reusable catalog.
The user asked whether IEEE, SEI, or other authorities supported a deterministic
“clamp” joining decision, assignment, and accountable execution.

Three different relationships emerged: the intent-to-work connection; an
increment deliberately organized around a release; and an ADR identifier
determining package version. The current anchor retains bounded intent and work.
Q-08 rejects deriving package version from ADR identity. The desired strength
of release association and the meaning of “all current problems” are still open.
The first draft's weaker “may target a release” wording was an agent proposal;
it must not erase the stronger operator candidate.

An alternative was to let the ADR name disappear while retaining the bounded
campaign-step function. The decision is functional before it is lexical.
“Brief” describes the assignment; “sortie” expresses a foray. Neither word
ratifies new identifiers or mandates a new artifact type.

### Reuse, learning, and the three identities

The operator embraced three different subjects: `REQ-C2.3` as the product
obligation, `OBPI-0.35.0-14` as the work package, and
`OBPI-0.35.0-14-C2.3` as that package's assignment against the obligation.
The table is retained in the candidate. It resolves a conceptual ambiguity;
the precise syntax is illustrative rather than an implemented or approved parser.

A requirement can participate in several advances as understanding and
capability change. Requirements may be discovered while planning an ADR.
The brief explains its contribution on this attempt: implement part, provide
evidence, revise understanding through approval, or repair a violated obligation.
Completion of the assignment does not imply that every aspect of the whole
requirement is now satisfied in every product configuration.

The operator's military analogy distinguishes continuing product needs from
campaigns, battles, orders, and tasks used to realize them under current
constraints. It is explanatory language, not a proposal to add organizational
levels. The important retained distinction is the durable need versus a bounded
attempt to fulfill it.

### Why one brief and the airlock existed

> In fact, the whole point of one-brief-per-item is that the agent could only handle one serious foray into the system. I conceived of the airlock to help with that.

The [original airlock account](../work-phases-and-airlock.md) makes bounded
context part of the intended design. A proposal that merely abolishes the work
hierarchy would fail to address that purpose. Equally, preserving the hierarchy
does not demonstrate that its context selection or refusal paths work. The
candidate distinguishes selected assignments from all constraints affected by
the change, including obligations from completed or non-parent ADRs.

The assertion about one serious foray is the operator's design rationale,
not a universal empirical capacity limit for every model. The effects of brief
size, context packaging, and model changes remain testable. Existing human
authorization rules still apply while that hypothesis is examined.

### The accepted grounding and its limits

The operator accepted the five roles: requirements catalog; mADR for decision
and rationale for a bounded advance; brief for contribution, boundaries and
evidence; plan/specification/tasks for execution detail; release record for
actual shipped content. Q-17 preserves the role statement verbatim.

They also accepted separating durable obligations from local acceptance criteria
and binding assignments to the requirement state they address. They emphasized
that ADR bodies already hold substantial design intent and requirement material.
Extraction must therefore interpret both ADRs and briefs, preserve provenance,
and split mixed statements without weakening them. A search for REQ tokens or
a bulk move of acceptance lists cannot perform that judgment.

Historical evidence remains about its original requirement state and product
configuration. New understanding may require another assignment. Changed needs
do not by themselves invalidate an honest historical acceptance; invalid old
evidence does not become acceptable by being called historical. Applicability,
supersession, assignment amendment, and evidence reuse need explicit mechanics.

TDD, BDD, and DDD remain strong influences. Deterministic controls can enforce
the conditions they actually check; they cannot make the requirement reflect
the intended need or make a weak test meaningful. The operator accepted this
distinction and requested help realizing it. The resulting control hypothesis
is compatible with continued test evaluation and independent semantic review.

## The attachment's separate contribution

Source: operator-supplied attachment **“I was, uh, one of the recent articles I
wrote with you was about Dex Horthy and…”**, delivered as `Pasted text.txt` in
this task. The text is mixed prior dialogue without explicit speaker labels and
ends mid-sentence before a Claude disclaimer. This section retains its concepts;
it does not elevate prior-assistant assertions into operator rulings or findings.

| Strand introduced in the pasted dialogue | Design question to retain | Limit on its authority |
|---|---|---|
| Familiar vocabulary and model priors | Could established terms reduce translation loss between the operator's intent and successive agents? | Plausible alignment hypothesis; this session has not measured it. Familiar naming does not enforce meaning |
| Capability categories and a feature hierarchy | Could stable product groupings and hierarchical labels improve navigation and requirement reuse? | A category scheme is not proof of architecture or an approved taxonomy |
| Real DDD discipline | Where are the domain models, consistent languages, and explicit relationships between contexts? | The pasted assertion that every capability is a bounded context is not adopted; these boundaries require analysis |
| Parnas and information hiding | Can boundaries isolate changeable decisions and reduce how much surrounding knowledge a foray needs? | Retained conceptual lens from the attachment; no original Parnas text is claimed as freshly inspected here |
| Naur and the operator's theory of the system | How can agents act responsibly when much of the integrated design understanding lives with the operator? | Retained lens, not evidence of an absolute model-comprehension ceiling or proof that repository knowledge cannot help |
| Containment of deterioration | Can the design make change and reconstruction safer locally even if perfect ongoing comprehension is unrealistic? | Intended outcome to evaluate across successive changes, not a demonstrated benefit of capabilities |
| ADR as rationale, brief as work order, release as delivered content | A coherent earlier alternative to the retained mADR synthesis | Part of the history; later accepted roles govern the current anchor |
| Continuity in one conversation | Preserve the connected reasoning rather than repeatedly reconstructing summaries of summaries | The current capture request makes this a concrete documentation responsibility |

The attachment's earlier assistant repeatedly asserted that the ideas were held.
The operator's current request requires inspectable retention instead. This
record preserves those strands without copying the previous assistant's
certainty or treating the later mADR synthesis as the only idea ever discussed.

## Authority and evidence without a borrowed guarantee

The operator sought IEEE and SEI to challenge design from established principles
and align agents, not simply to find prestigious support for a preferred result.
The [candidate source table](design-candidates.md#external-grounding-and-its-limits)
separates each source's support from the claims it cannot establish.

**IEEE/ISO.** Requirements management, traceability, configuration control,
lifecycle processes, and flexible information items provide useful distinctions.
They do not establish that agents require this exact ADR → OBPI hierarchy.
Unconventional terminology can coexist with sound responsibilities, but naming
something an extension does not settle whether its responsibilities conflict.
This remains reflective engineering, not a conformance initiative.

**SEI and SWP/CNS.** The operator explicitly asked about the Software Acquisition
Pathway. SEI's [2025 SWP presentation](https://sei.cmu.edu/documents/6388/20251022_SWA_GoBag_Launch_Webcast.pdf)
describes a government acquisition pathway and separates capability needs,
user value, progress assessment, and release sequencing. Its CNS discussion
concerns high-level needs with room for development tradeoffs. Our inference is
that these responsibilities are useful comparison points for product intent,
requirements, backlog, and release planning. It does not follow that gzkit needs
a new CNS document or that capabilities must own briefs. Any CNS-like role must
first be compared with the existing PRD and Q-02's linkage repair; no replacement
of the PRD or importation of acquisition bureaucracy is approved.

**A useful SEI counterexample.** The [2026 MBSE study](https://www.sei.cmu.edu/blog/native-ai-integration-for-model-based-systems-engineering-three-layers-that-make-it-work/)
reports a model with clean tool checks and a high project-defined pattern score,
yet changed separation requirements and unexecuted verification structures.
This supports retaining source reconciliation and executed evidence alongside
deterministic checks. It is evidence from that benchmark, not an audit result
about gzkit or a comparison of mADRs against independent briefs.

**Anthropic.** The two harness articles in the candidate support examining
bounded assignments, durable progress, explicit contracts, and separate
evaluation. The later article also reports removing some scaffolding as model
capability improved. Both lessons belong in the record: the control function
matters, and its specific structure must remain open to evidence. They do not
establish a permanent law that one particular artifact hierarchy is required.

**FDAU.** The originating comparison is pinned at
`49eec3557145d9825c7026aa4dfee718443d433f`; its
[backlog method](https://github.com/tvproductions/xplane-fdau/blob/49eec3557145d9825c7026aa4dfee718443d433f/docs/project/backlog-method.md)
and [governance retrospective](https://github.com/tvproductions/xplane-fdau/blob/49eec3557145d9825c7026aa4dfee718443d433f/docs/project/backlog-governance-model.md)
are examples, not proof of a standards-derived notation. The prior source review
read its codes in their containing backlog tables as category/family/item labels
for deliverables, not uniformly atomic enduring requirements. A defensible
requirements design can draw on established identity and traceability principles
without claiming FDAU historically derived its particular codes from NASA, IEEE,
SEI, or another authority. That exact provenance was not established.

**Horthy and the dark-factory concern.** The operator invoked successive-change
deterioration as a possible analogy for gzkit. The retained
[Horthy excerpts](raw/dex-horthy-successive-change-2026-09-23.md) and Q-15 already
turn that concern into evaluation questions. External testimony does not prove
gzkit has the same failure mechanism. One impressive implementation or a tidy
record cannot demonstrate durability over subsequent changes.

## Cost and recovery questions

The central alternatives concern both **what model to adopt** and **when/how
to migrate**. They are not one axis. In-place migration, bounded subsystem
replacement, a capability reorganization, deferral, and abandonment have separate
rows in the [recovery inventory](design-candidates.md#recovery-timing-and-extent).
Conventional ADR semantics need not entail rebuilding everything. Retaining
mADRs need not entail retaining ADR-owned requirements.

No estimate in this record establishes days of work, affordable total cost,
or a break-even date. Prior inspection identified reusable acceptance, ledger,
and distribution machinery as reasons to investigate recovery, not proof that
recovery is cheap. The visible risks include all consumers that infer ownership
from existing IDs, sealed history, partial migration, test adequacy, and actual
release configuration under the main-only workflow.

Before making a substantial implementation commitment, the proposed bounded
case should make these questions answerable:

- What is the smallest coherent change that gives requirements independent
  authority while keeping assignment and release claims truthful?
- Which readers, writers, templates, tests, and distributed surfaces must change
  together, and what remains compatible without a second editable authority?
- What operator judgment is required to classify existing material? How are
  ambiguous and unmigrated obligations made visible rather than lost?
- Can the existing acceptance path express revised and repeated assignments
  without rewriting history or reusing another assignment's completion?
- Does the change reduce repeated authority reconstruction and missed constraints
  across successive changes? What new maintenance or ceremony does it create?
- If the candidate fails, can the trial be stopped without corrupting accepted
  evidence, historical identities, or releases?

These are proposed decision questions, not a new gate or an authorized research
campaign. Effort matters to the recovery decision, while lower effort alone
does not justify weaker correctness or human control.

## The Ptolemy/Copernicus challenge

> This might be an epicyclic cope btw.
>
> can I pull this off without it becoming Ptolemy vs. Copernicus?

The concern is whether a modified ADR model removes a mistaken ownership
assumption or merely accumulates exceptions to preserve it. The metaphor is
not evidence for either answer. The later accepted anchor makes the correction
substantive only if requirements actually acquire independent authority,
assignments can recur against identifiable states, and actual releases are
recorded separately from work names and completion.

Proposed signs of failure include continuing to infer requirement ownership
from the parent ADR despite catalog prose, changing old evidence when a current
definition changes, declaring whole requirements satisfied from brief counts,
or adding exceptions whenever the source configuration disagrees with a release
list. The pilot's refusal cases and independent reconstruction address these
risks. Preserving the mADR name is neither sufficient evidence of failure nor
an excuse for them.

The operator's subsequent formulation is retained without softening it:

> Copernicus is the truth that my current model is flawed. Clinging to Ptolemy is the pain of correction and relying on epicycles.

Accepting a correction and retaining useful controls can coexist. Which controls
are useful, which mechanisms need replacement, and what the correction costs
remain engineering questions rather than matters of loyalty to an earlier name.

## What the next reader must carry

Read the accepted [grounding pivot](design-candidates.md#grounding-pivot) first
for direction, this record for why and what else was considered, and the
[candidate inventory](design-candidates.md#alternatives-and-their-disposition)
for current option status. Read `FINDINGS.md` for evidential status; neither
agreement in this conversation nor a design preference promotes a finding.

The five roles and independent requirement references are accepted. Exact
storage, grammar, capability ownership, terminology changes, strong release
coupling, the defect population blocking new work, amendment machinery,
whole-requirement acceptance, migration scope, timing, and affordability remain
open or proposed as labeled. An earlier agent release-first recommendation is
retained alongside the current combined-case proposal; neither is a booked
execution order.

The [test-suite investigation](../../evals/test-suite-integrity-audit-2026-09-24.md),
IEEE/SEI work, and [Magna Carta](../build-to-1.0-campaign-2026-09-20.md) continue.
The test investigation must be read with its own baseline and scope limitations;
it is not evidence that every test is worthless. Existing campaign order,
operator initiation, five gates, and the already-booked airlock successor remain.
This session develops a design; it does not initiate its pilot or implementation.

**Retention review, 2026-09-25:** main-session author plus an independent
conversation-aware reader, `/root/adr_requirements_release`. The audit identified
lost alternatives and distinctions; the candidate inventory and this record
restore them. The review checked retention, not recovery cost or runtime effect.
