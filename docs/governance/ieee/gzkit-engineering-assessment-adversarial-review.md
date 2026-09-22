# GZKit engineering-method assessment: adversarial review

Reviewed 22 September 2026. Persona: main-session.

**Verdict: the report is a useful inventory of friction, but an unreliable basis for structural redesign in its present form.** Its strongest observations concern large context surfaces, weakly exposed evidence, and incomplete enforcement at particular boundaries. Its central causal conclusion—persistent knowledge inside OBPIs explains the engineering burden—is a hypothesis, not an established finding. Several purported absences are contradicted by existing code, historical dispositions, or the supplied standards.

This review attacks the [primary report](/private/tmp/claude-501/report/gzkit-engineering-assessment-phase1.md), rather than repeating its investigation. The report names commit `6a0e5241e`; inspection used `be663409a64a12b501c25bdf9e919606aa0b9937` and checked the intervening diff. That diff contains scanner repairs, continuity records, and removal of two PDF files; the principal counterexamples below already existed at the report's snapshot. Later scanner repairs are not counted as original analytical errors.

Three independent, bounded review tracks checked standards, runtime claims, and causality/history. Their findings were integrated with direct source inspection and a read-only coverage/source-index probe. This is not an exhaustive conformity audit or a fresh census of GitHub. In particular, the report's subjective issue/REQ classifications, complete receipt-retention population, and every historical gate event were not independently reclassified. Unverified figures remain attributed to the report.

No repository content, issues, ADRs, process artifacts, or governance events were authored by this review. Files produced by the review are under `/private/tmp/gzkit-adversarial-review/`. The repository was initially clean; a separately generated, staged session-exit bookmark appeared during inspection and was left untouched. No Phase 2 work was initiated.

## 1. Report reliability summary

**Strongly supported, within narrower scopes:**

- REQ-to-test discovery is a useful, functioning local mechanism. The reported `1,794/2,749` coverage and `713` drift count reproduce exactly. They measure linkage, not passing execution or adequacy.
- Context delivery is large and repetitive. The pipeline skill is substantial, and handoff entry explicitly requests lineage reading. This creates a credible reconstruction burden; the claimed universal 92,000-token entry cost and its dominance over other costs were not measured.
- The inspected pipeline hook does not refuse out-of-allowlist writes, and the airlock CLI declares diagnostic-only HOLD. These are specific enforcement limitations, not proof that all governance boundaries are unenforced.
- Some historical gate records have weak explanatory content; the deprecated `gz gates` Gate-5 stub is a poor guide to current completion behavior.
- Falsifiability witnesses, distinct proof channels, explicit degradation, and repairable historical records are valuable practices. Their value comes from observed behavior and applicable scope, not superiority to a standard.

**Plausible but under-evidenced:**

Durable obligations may be difficult to find across existing surfaces; some requirements may need visibility beyond their originating brief; repeated reconstruction may contribute to repair loops; some reviews and BDD scenarios may be redundant. None of these establishes that a new requirements registry, separate constraint objects, consolidated ledger, or gate removal is the cheapest remedy.

**Incorrect or materially overstated:**

The standard mandates work packages reference requirements they cannot contain; hierarchical REQ IDs cannot survive their OBPI; chore staleness has no reader; the current adversarial completion path lacks substantive checks; historical agent attestations demonstrate a present bypass; the project has no means of retiring defects; receipts are records rather than evidence; the testing standards lack oracle vocabulary; and the PRD has been frozen since January. Each has counterevidence below.

**Major uncertainty:**

There is no causal comparison establishing which proportion of elapsed delivery time or reconstruction failure is attributable to knowledge placement rather than queue waiting, changing rulings, coupled obligations, repeated verification, transport faults, or reviewer scope expansion. The needed persistent subset of today's REQs has not been identified. The report itself postpones that classification to P2-A, after treating its answer as settled in Sections 4, 6, and 8.

The defensible revised thesis is:

> Some enduring obligations are difficult to retrieve and distinguish from historical or work-specific material. Test whether better selection, applicability, and retrieval over existing authoritative sources solves that difficulty before adding persistent objects or moving requirement ownership.

## 2. Findings challenge table

Evidence references E1–E14 and standards references S1–S8 are defined below. “Not applicable” means no standards claim is needed to establish the observation.

| Primary finding | Evidence quality | Standards interpretation quality | Counterevidence | Alternative explanation | Verdict |
|---|---|---|---|---|---|
| §1: GHI repair is the primary change channel, roughly 4:1 | Commit-label counts support a descriptive trend, not effort or delivered value | Not applicable | Commits mentioning GHIs and OBPIs are not mutually exclusive work units; one feature may need many repair commits | Deliberate stabilization, batching, and operator-controlled feature sequencing | CONFIRM WITH QUALIFICATION |
| §1/§2: PRD is frozen/inert; product-intent traceability was abandoned | Identifier-use evidence is narrower than claimed semantics | Overreads missing explicit links | PRD contains later glossary/context additions; git shows changes through August 17. It still states a product and north star [E10] | Weak explicit linkage and stale metadata, rather than absent product intent | CONFIRM WITH QUALIFICATION |
| §2/§8: No persistent system model or knowledge home exists | Absence claim not sustained | Conflates full 42010 AD conformity with possession of useful system knowledge | State/trust doctrine, CLI specification, architectural identity, source ontology, and OKF knowledge bundle exist [E7,E9,E10] | Fragmented, partly stale, insufficiently queryable knowledge | REJECT |
| §1/§4/§6: Deleted briefs demonstrate loss of 39% of enduring requirements | Deletion count is real; durability and causal attribution are unclassified | 16326 inference is invalid | 364 of 384 deletion events cluster in two deliberate demotion campaigns, largely unstarted work [E1] | Backlog retirement; a smaller, consequential retention/traceability problem | DOWNGRADE TO HYPOTHESIS |
| §2/§8: Hierarchical IDs cannot outlive work packages | Logical assertion, not observed property of the grammar | Contradicted by 29148's permitted relational identity [S2] | The parser accepts an ID independently; storage lookup and deletion govern discoverability [E6] | Lifecycle/storage policy rather than namespace defect | REJECT |
| §6: OBPI is overloaded and template responsibilities grew | Template growth and mixed content are direct observations | Standards do not prohibit mixed artifacts | Briefs deliberately retain closure rationale; acceptance criteria and plans are not categorically incompatible [E2] | Required ceremony grew; selection could reduce reading without splitting storage | CONFIRM WITH QUALIFICATION |
| §6: Persistent knowledge in OBPI explains long duration | No causal test; created-to-completed mixes queue and execution | Not established by a standard | One >33-day OBPI completed 3.25 hours after its first lock [E2] | Authorization/sequence waiting, scope coupling, churn | DOWNGRADE TO HYPOTHESIS |
| §7/§8: Mandatory entry costs 92k tokens and dominates cost | Composite byte estimate, not measured delivered tokens or time | Not applicable | Uses ADR-0.35.0 size with a median brief; generic status is not required by the inspected pipeline; harness inputs vary [E2] | Overdelivery, lineage policy, or irrelevant retrieval rather than missing objects | CONFIRM WITH QUALIFICATION |
| §1/§8: Jurisdiction/airlock do not prevent inspected out-of-scope writes | Direct caller/hook evidence | Standards analogy unnecessary | Airlock's limitation is explicit; its NC calls `airlock_enter`, not merely `_decide`; existing successor owns calibration [E8] | Unfinished calibration/compulsion and harness coverage | CONFIRM WITH QUALIFICATION |
| §1/§8: Gates record exit codes and decide nothing | Good historical payload concern; false generalization | Confuses a check, a gate condition, and the authorization consuming it | Closeout blocks failures; completion emits human-attestation receipts [E4] | Deprecated interface plus dispersed evidence, not universally absent gating | CONFIRM WITH QUALIFICATION |
| §11: Computed `not-refuted` bypasses real adversarial outcome | Stops before upstream prerequisite | Not applicable | `completion_review` checks proofs, required reviews, and unresolved findings first; refuted rounds can be retained [E4] | Legacy dead code/comment beside newer acceptance model | REJECT |
| §2/§11: Fifteen agent attestations indict current Gate 5 | Historical count is not version-stratified | Not applicable | All fifteen date to March; universal rule cutoff is April 26 [E4] | Pre-doctrine practice; present relay-authentication limitation is separate | REJECT |
| §1/§8: Self-detection works but retirement is missing | Historical audit and backlog sizes do not establish current failure | A baseline is not automatically an undeveloped assurance argument | July NC defects have subsequent repair commits; withdrawal, repudiation and demotion were exercised [E1,E5] | Disposition discoverability or continuing class recurrence | REJECT |
| §2/§11: Insights have no reader or close path | Too absolute | Record/report distinction does not require a new report type | Rubric reads references from content; 36 `defect-resolution` records exist [E3] | No adequate linked current-state reduction, despite useful archival signals | CONFIRM WITH QUALIFICATION |
| §2/§11: `staleness.periodDays` is unread | Contradicted by code and tests | Not applicable | Status calculates due dates; session orientation consumes status; freshness script also reads the field [E3] | No autonomous scheduler, or no operator selection of due work | REJECT |
| §5: Coverage numbers disagree without a coherent basis | Totals verified; semantic explanation omitted | Different proof populations are legitimate | Covers includes feature tags and broader kinds; drift filters non-test obligations and retired work [E6] | Different queries, with insufficiently obvious presentation | CONFIRM WITH QUALIFICATION |
| §4/§5: Only REQ→test trace exists; parent/allocation are absent | Production source allocation is unpopulated; total absence is false | Five-leg guidance does not prescribe a new ontology | `ReqEntity.parent_obpi` exists; source-anchor/coupling implementation exists, with zero current source anchors [E6,E7] | Incomplete population/projection rather than missing modeling capability | CONFIRM WITH QUALIFICATION |
| §2/§4: Risks/research questions have no home; interface spec absent beyond manpages | Nonexistence claims exceed the inventory | A concept need not have its own object | ADR consequences and research records hold such content; canonical CLI specification exists [E9,E10] | No unified current risk view; heterogeneous descriptions | REJECT |
| §3/§8: REQ correspondence and proof-channel distinction are strong assets | Direct implementations and reproducible link counts | Useful analogy to correspondence methods, not full conformance proof | Static tags do not prove execution or semantic coverage | Strength is bounded discoverability and routing of proofs | CONFIRM WITH QUALIFICATION |
| §3/§8: Anti-tautology stack is ahead of 29119; `none` proves inability to fail | Mechanisms useful; superiority and universal inference unsupported | Part 1 explicitly defines oracle and oracle problem [S8] | A passing selected baseline does not establish incapacity to fail on all relevant faults | Local adequacy witness with limited experiment scope | CONFIRM WITH QUALIFICATION |
| §3/§8: BDD gate largely duplicates unit tests; retain only unique REQs | ID/function overlap is insufficient | 1012 note is misapplied to suite architecture [S6] | Same lines/REQs can be exercised under different conditions and assertions | Some redundant tests amid useful boundary/acceptance checks | NEEDS MORE EVIDENCE |
| §8: Independent requirement/constraint identity fixes loss, rationale and impact questions | Proposed causal remedy not demonstrated | Neither 16326 nor 29148 mandates it | New IDs do not supply rationale, allocation, currentness or preservation | Retrieval/applicability improvements may suffice | REJECT |
| §8: One inconsistency list with retirement is the highest-leverage consolidation | Duplication and maintenance savings not measured | 42010 permits recording or referencing; not one physical list [S3] | GHIs, histories and ratchets have different subjects and dispositions | A derived cross-reference may help; merging authoritative stores may hurt | DOWNGRADE TO HYPOTHESIS |
| §8: Risk thresholds should replace operator initiation | No measured safety/cost advantage | Risk tolerance is not a grant of authority | Initiation is an explicit human-sovereignty policy; a violation does not invalidate its purpose | Improve adherence or clarify delegation only if operator chooses | REJECT |
| §9: Avoid wholesale compliance bureaucracy; reuse local mechanisms | Good project-fit judgment | Broadly supported by flexible information-item packaging [S4] | Must apply this same restraint to the report's proposed ontology | Existing sources plus targeted retrieval | CONFIRM |

## 3. Standards-misreading check

The standards are evidence about engineering practice, not authority to alter GZKit's governance. The following corrections materially change the report's reasoning. PDF page numbers below are one-based and refer to the supplied editions.

| Report's use | What the source supports | Correction |
|---|---|---|
| 16326 §7.3.1.1 mandates OBPI requirements live elsewhere | That clause concerns the PMP **project overview** (PDF 27). Work-package §7.7.3.2 is a nonexclusive **should** list (PDF 30). §7.1 permits incorporation/reference; §7.11 describes additional plans as usually separate | Do not turn project-plan referencing into a prohibition on co-location [S1] |
| Requirement ID structure makes persistence impossible | 29148 §5.2.8.2 permits identification reflecting relationships; IDs remain unchanged and unreused even after deletion (PDF 22) | Retention and retrieval are separate from identifier origin [S2] |
| Missing rationale field leaves assumptions nowhere to go | §5.2.7 allows an attribute **or accompanying document**, and requires assumptions to be validated as well as documented (PDF 22) | Inspect associated content. A missing field proves neither missing reasoning nor compliance [S2] |
| GWT acceptance criteria are not requirements | §5.2.4 recognizes scenario-form requirements (PDF 20) | Assess required property, abstraction, necessity and verifiability, not syntax [S2] |
| Five traceability legs justify this minimum graph | §6.4.3.5 introduces the five relationships with **should** (PDF 48–49) | Required maintenance does not select separate node types or one implementation [S2] |
| No formal AD means no persistent model; one inconsistency list is required | 42010 Clause 4 attaches Clause-6 requirements to an AD conformance claim; §6.1 prescribes no format and allows derived descriptions; §6.9 allows references (PDF 13,27,31–32) | Distinguish useful architecture knowledge, a description, and demonstrated conformity [S3] |
| Every gate claim must explicitly contain property/limit/uncertainty/scope fields | 15026-2 §5.3.3 gives varied claims; §5.3.5 and §5.3.6 allow context/mapping to supply uncertainty (PDF 12–14) | A narrow command-success claim is valid but may not establish required behavior. Review the inference, not a field checklist [S5] |
| A receipt is a record, not evidence | §5.3.2 explicitly includes activity records as evidence artifacts; contextual interpretation can be elsewhere (PDF 12) | Inspect the evidence-to-claim connection. UUID identity is not itself a standards failure [S5,S4] |
| Grandfather lists are undeveloped arguments | That term belongs to a supported-claim structure (§3.1.7, §5.3.5) | A list may instead define exclusions, tolerated debt or scope; determine its function [S5] |
| 1012 says BDD must not duplicate unit testing | §6.3 Note 2 is explanatory and concerns V&V relative to development; adjacent text permits shared facilities and differentiated inputs (PDF 37–38) | Prove equivalent fault detection before removing tests or a gate [S6] |
| Lite/heavy is an integrity model on the wrong axis | Clause 5 considers complexity, criticality, risk, safety, security and other attributes (PDF 33) | Surface-based lanes can govern contract/documentation obligations independently of integrity. No mapping was demonstrated; that is narrower than inherent error [S6] |
| Testing standards lack oracle vocabulary | 29119-1 §3.115–116 defines oracle/oracle problem; §4.1.10 discusses partial oracles (PDF 21–22,27) | The report's Parts 2–4 search omits the concepts volume. No source-code mutation adequacy method was located in the reviewed parts; that narrower observation is not proof of superiority [S8] |

The report correctly rejects the inference that every information item requires its own document. It then recreates that inference at the **object** level: requirements, constraints, architectural obligations, risks and research questions become candidate persistent entities before a distinct maintenance decision is shown. Machine-readable objects carry cost just as documents do.

Other crosswalk claims, including detailed interpretations of 16085, 32675 and 730, were not exhaustively re-audited here. Their presence in the primary report does not independently validate its authority-policy or gate-removal conclusions.

## 4. Ontology stress test

These are review dispositions of the report's proposals, not instructions to implement a replacement model.

| Proposed or implied persistent object | Disposition | Reason and boundary |
|---|---|---|
| Product need / intent | MERGE WITH EXISTING OBJECT | Use existing product/ADR intent and references first. A `NEED` namespace needs evidence that these cannot answer the relevant why-question |
| Requirement | KEEP AS DISTINCT OBJECT | Named obligations are useful where independently verified, changed or traced. Preserve existing REQ identity; do not create a second requirement tier by default |
| Every current acceptance criterion as permanent system requirement | DO NOT ADD | Migration, documentation and one-off execution criteria can be historical after completion; classify semantics first |
| Constraint | REPRESENT AS ATTRIBUTE | Scope/constraint character can qualify an existing obligation. A scope fence and an enduring property differ in applicability, not necessarily entity type |
| Architectural obligation / boundary invariant | MERGE WITH EXISTING OBJECT | Keep existing ADR-qualified invariants and rules with their witnesses; local `BI-04` needs its ADR context, not automatically a global BI allocator |
| Policy / operator doctrine | MERGE WITH EXISTING OBJECT | Existing corpus/rules own policy. Another policy registry adds an authority conflict |
| Assumption | REPRESENT AS ATTRIBUTE | Record material conditions next to the decision/claim they qualify. A separately managed assumption is justified only by independent change/use |
| Risk | REPRESENT AS ATTRIBUTE | Attach uncertainty/consequence/revisit conditions to the existing decision or work item initially. No universal risk-object lifecycle is yet justified |
| Issue / finding / inconsistency | MERGE WITH EXISTING OBJECT | Use GHI or current acceptance finding according to subject. A derived cross-reference can expose unresolved items without another ledger |
| Research question | MERGE WITH EXISTING OBJECT | R&D records already name challenges and dispositions; no new question ID is needed to ask or preserve one [E9] |
| Architecture description / view | DERIVE AUTOMATICALLY | Derive structural views where possible, with selected authored rationale in existing sources. A generated diagram alone cannot supply stakeholder concerns or design intent |
| Component | DERIVE AUTOMATICALLY | Use present code units/interfaces for structural queries. Do not pretend imports alone determine conceptual architecture or dynamic dependencies |
| Verification obligation | MERGE WITH EXISTING OBJECT | Existing proof channels, tests, validator claims and contract criteria already express obligations. Add no universal parallel list |
| Test / check definition | KEEP AS DISTINCT OBJECT | Executable verification has independent identity and maintenance; report selection and conditions |
| Evidence / receipt | KEEP AS DISTINCT OBJECT | Historical execution records need immutable identity and scope. Do not copy their payload into every brief or graph node |
| Decision / ADR | KEEP AS DISTINCT OBJECT | Retain consequential rationale, context and alternatives. Avoid both “everything in ADRs” and arbitrary tiny-decision fragmentation |
| Completed OBPI and retired decisions | KEEP ONLY AS HISTORY for completed work state; preserve any still-applicable obligations | A closed intervention remains historically valuable. Completion does not expire a system property; retirement needs an explicit disposition |
| Current graph/status/ruling selection | DERIVE AUTOMATICALLY | Separate the selected current interpretation from archival records, subject to existing authority rules |

The persistent/transient binary should therefore be replaced analytically by six roles: **current authoritative obligations; durable rationale/history; derived views; disposable caches; transient execution state; retained run evidence**. A single brief may legitimately contain several roles. Separating the roles in retrieval does not require splitting the file, inventing types, or deleting history.

Requirements formalization is most valuable for external contracts, consequential invariants, non-obvious acceptance behavior, and obligations that survive several changes. A small internal refactor or directly authorized defect repair may be adequately governed by its existing contract and a regression test. Naming an obvious implementation step as a permanent REQ creates little value. When code and requirements disagree, the defect is a decision about intended behavior and applicable authority; automatically rewriting either side to match the other conceals it.

## 5. Traceability minimization

The report's supposedly minimal graph is not internally specified. Its diagram names **seven** nodes, despite claiming six; its labeled relationships do not match the table; the table includes a work-package relationship absent from the diagram and lists “constraint identity” as an edge. The diagram's vertical `verified-by` relationship is also ambiguous. This is not yet an auditable minimum.

Use a smaller **query model over existing identities**, not a new graph engine:

```text
Existing intent/decision --justifies--> selected current obligation
                                      ^                 |
                                      | covers          | applies to, where needed
                                test/check              v
                                      |             code/interface scope
                                      v
                                execution receipt

Existing work item/commit: provenance of the change, not owner of all future truth.
```

| Relationship to retain | Decision it enables | Maintenance and stale-link treatment |
|---|---|---|
| Existing intent/decision → obligation | Why retain this behavior? Is a proposed change allowed? | Author only when the reason is not already clear through parentage; retain references instead of copied rationale; review when intent changes |
| Obligation ← test/check | What demonstrates this property? What loses evidence? | Derive from existing annotations and declared proof channels; unknown IDs and missing targets are mechanically detectable; semantic correctness remains reviewable |
| Test/check → run receipt | Did this verification execute on the relevant revision and conditions? | Generated at execution; applicability is revision/input/condition dependent. An old run remains valid history, not current proof |
| Obligation → code/interface scope, selectively | Which obligations need inspection for this change? | First use existing anchors and test/code relationships; require a maintained manual mapping only where a consequential question remains unanswered |
| Work item → change/review evidence | What introduced or altered this claim? | Existing IDs, commits and receipts already provide provenance; generate reverse lookups |

**Do not maintain** a second REQ→OBPI edge independently of encoded/existing parentage; a second requirements registry with duplicate wording; constraint→requirement→invariant chains expressing the same property; manual component import edges; historical brief→every later fix links; duplicated evidence payloads; or universal NEED/COMPONENT nodes merely to populate a standards diagram. Do not infer semantic allocation from “the test imports this module.”

The current source sensor is material counterevidence to “no implementation exists”: the read-only probe found **0 source anchors, 5,973 coupling edges, and no parse failures**. Unified projection admits only edges with materialized endpoints and excludes coupling edges from its object/link graph [E7]. Thus useful source-path impact answers are missing in the current projection, but building another sensor would duplicate existing capability. Whether populating that capability is worth its annotation burden remains open.

## 6. OBPI alternative-cause analysis and metrics

| Outcome | Strong competing explanation | Existing evidence | What would discriminate |
|---|---|---|---|
| Long OBPI duration | Queue/authorization waiting dominates creation-to-completion | OBPI-0.35.0-01: created July 21; first lock August 24 07:53; completion 11:08 that day. About 33.48 calendar days versus 3.25 hours after lock [E2] | Separate created→authorized/started, active execution, waits and final acceptance; do not call first-lock time pure effort |
| Long OBPI duration | Scope/coupling and repeated QA, not location of requirements | A new CLI verb has seven coupled obligations; scorecard records repeated deterministic failures caused by underdeclared scope [E11] | Compare work of similar scope and consequence; attribute time to rework, verification and missing dependencies |
| Repair loops | Review boundary expands or the oracle changes | Pipeline records five adversarial rounds, 53 minutes compute across 12.5 hours, with later rounds attacking an already accepted residual [E11] | Track each finding's governing claim and whether it changes the agreed boundary; count confirmed repairs separately from new demands |
| Agent re-entry difficulty | Excess historical replay and unclear currentness | Explicit lineage reading, large skill, growing amendments; existing scoped context/knowledge mechanisms [E2,E9] | Cold-entry tasks with measured retrieval and correctness, comparing selected current context against full history |
| Context expansion | Exception accumulation and repeated narrative delivery | Template expansion and amendment-heavy artifacts are documented | Measure actual messages and fetched content, deduplicated by source/revision; distinguish storage volume from delivered context |
| Specification drift | Independently maintained consumers or changing authority | Coverage readers deliberately use different populations; brief example records incompatible byte definitions and coupled amendments [E6,E12] | Separate intentional rulings, implementation drift, stale summaries and contradictory requirements before counting “drift” |
| Persistent-knowledge hypothesis | Enduring obligations cannot be recovered without old briefs/handoffs | Real retained-traceability exception in the Codex demotion; fragmented retrieval | Sample later interventions; identify the missing obligation, wrong action and whether an existing authoritative source already stated it |

The strongest discriminating result already found is the queue-wait example. It does not establish that all OBPIs are fast; it invalidates using created-to-completed duration as evidence of active engineering burden without decomposition.

Metrics should stay few and decision-specific. The following dispositions cover the report's six proposed retained metrics and its rejected counts.

| Metric disposition | Information need | Measure | Decision enabled | Metric's own failure mode |
|---|---|---|---|---|
| Retain, refine OBPI duration | Where does delivery wait or rework occur? | Queue interval, start-to-completion elapsed time, observed blocked intervals, separated by comparable work | Change selection/sizing or repair the actual bottleneck | Locks are imperfect work-start proxies; parallel work and missing pause records distort effort |
| Retain, narrow brief-reconcile rate | Was necessary scope knowable before execution? | Distinct interventions with substantive scope repair, classified before/after implementation | Improve discovery or remove duplicated scope representation | Repeated events inflate rate; cosmetic correction and legitimate scope change are different |
| Retain kind-specific coverage | Which current obligation lacks its appropriate proof? | Distinct applicable obligations by declared kind/channel, with unknowns explicit | Select evidence repair | Tags can be gamed; linkage is not passing execution or adequate assertions |
| Retain actual entry cost | What can be omitted without losing correct task understanding? | Delivered/fetched tokens and elapsed retrieval for comparable cold starts, plus missed obligations | Narrow context delivery | Small context can omit crucial facts; cached input cost differs from reasoning burden |
| Retain, qualify RED outcomes | Did a selected witness distinguish the relevant missing behavior? | Outcomes by intervention/base provenance and interpretable experiment | Investigate weak witnesses or inappropriate baselines | Easy mutations improve ratios; error is not assertion; `none` is not universal incapacity |
| Reject fix:feat as a health KPI | Is repair consuming capacity or recurring? | Commit prefixes do not answer this; use sampled attributable repair effort and recurrence when needed | Decide class-level repair after confirming recurrence | Relabeling and commit granularity game the ratio; deliberate stabilization looks unhealthy |
| Reject handoff/validator/REQ counts as goals | Is machinery useful? | Counts can describe inventory, not benefit | No direct optimization target | Splitting, merging or renaming changes the number without changing burden |
| Keep TTL warnings only if actionable | Does a claim risk expiring while work remains active? | Relevant unhandled expiry risk, not repeated session-start emissions | Renew/release or surface a real wait | Counting warning events measures restarts and duplicates |

No new telemetry platform is justified by this table. Existing records can answer initial discriminating questions. Runtime and reading measurements are useful only if they change a specific decision.

## 7. Assurance review

The report collapses four different mechanisms: static native reviewers; executable tests/checks; an adversarial reviewer; and human acceptance. Their independence and cost must be assessed separately.

| Mechanism | What it can add | What it cannot establish |
|---|---|---|
| Native spec/quality review with fresh context | Different reading of scope, contracts and maintainability; useful separation of attention | Dynamic behavior if command execution is unavailable; independent truth merely because two roles agree |
| Tests, validators, RED/mutation probes | Reproducible observations against specified predicates and conditions | That the specification is correct, every relevant fault was considered, or a validator's own assumptions are sound |
| Different-vendor adversarial execution | Potentially different hypotheses and concrete counterexamples; reproduced positive and negative behavior | Statistical independence, no shared blind spots, or completeness of the acceptance claim |
| Acceptance store and completion gate | Current proof/review applicability, explicit approvals and unresolved-finding blocking | Truth of a review's reasoning or authentic human origin of relayed text |
| Human attestation | Authorized acceptance of demonstrated behavior and residuals | A replacement for evidence or proof that all material facts were presented |

**Current enforcement is stronger than the report describes.** Completion calls `completion_review`, which checks blockers before producing the summarized adversarial event. Refuted rounds and findings can be retained. Receipt citation checks are called on the completion path even though the umbrella audit is a no-op. This is not merely a caller choosing `not-refuted` [E4]. The independent runtime track ran 99 relevant tests successfully; those use temporary histories and partly synthetic transport, not end-to-end human authentication.

**False confidence remains a real risk, but identify the right claim.** The pipeline's tier-1 text says a different-vendor model “shares none of this agent's blind spots.” That assertion is unwarranted. Models can share source material, problem framing, flawed requirements, fixtures, and tool limitations. The same skill also demands independent re-derivation, actual output, and positive as well as negative demonstrations—useful safeguards that the review should credit [E11]. Agreement is supporting evidence only to the extent that the reviewers test distinct relevant failure possibilities.

A review can be independent in execution while dependent on the same flawed oracle. Conversely, a native reviewer need not execute tests to find a meaningful design defect. The useful question is **what additional confirmed defect or justified confidence did each stage contribute, at what cost?** The report does not supply that comparison.

The recorded adversary episode shows late boundary clarification causing substantial rework. It does not prove that removing the adversary would be safer or cheaper overall. Earlier agreement on acceptance claims and residuals has stronger local evidence than either adding a reviewer or deleting one.

Finally, “record one observation per gate” is too weak to guarantee assurance and too broad to call cheap. A gate may cover many predicates; a brief success sentence can become another unverified summary. Preserve the actual run, its subject and applicability, then explain only the inference needed for the acceptance decision. Do not add uncertainty fields that agents fill ceremonially.

## 8. Complexity budget

Qualitative costs assume each recommendation becomes maintained practice, not a one-time report. H/M/L indicate high/medium/low; benefits marked uncertain are not established by the report.

| Major recommendation | Engineering benefit | Ongoing maintenance | Agent context | Staleness risk | Automation potential | Disposition |
|---|---|---|---|---|---|---|
| New independent REQ/constraint identity and ownership layer | Uncertain; could aid reuse | H: migration, links, lifecycle, authority | H unless retrieval actually replaces prior inputs | H: parallel specifications | M | Reject blanket adoption; retain current IDs and test retrieval/retention deficit |
| Name gate claims and expose observations | H for misleading consequential claims | M; broader rewrite H | L–M if existing evidence reused | M | H for provenance, L for sufficiency | Keep but scope to live consumers and actual overclaims |
| One known-inconsistency list | M if it improves finding/disposition discovery | H if authoritative duplicate, L–M if derived | L selected, H global | H if copied | H for links, L for semantic equivalence | Prefer an existing-source view; no new authoritative ledger |
| Retire Gate 4 | Possible runtime/maintenance saving; safety benefit unproved | One-time M–H, later possibly lower | May lower ceremony | H risk of lost intent/oracles | M for identifying overlap | Reject now; examine scenario/oracle/fault equivalence |
| Risk object plus replacement escalation policy | Uncertain | H: classification, ownership, calibration | M–H | H: optimistic stale ratings | L for valid consequence judgment | Reject coupling to authority replacement; selective risk attributes only |
| Architecture description/viewpoint structure | M where a concrete question fails | H if hand-maintained, M if mostly derived | M–H unless replacing reconstruction | H for structural copies | H structure, L rationale | Test existing views and references first |
| Entry packet of requirements, constraints, assumptions and blast radius | H if bounded and complete enough | H if manually curated per task | L if replacing context; H if additive | H without source applicability | M | Keep as retrieval hypothesis, not new mandatory packet |
| Full claim/NC reassessment using formal assurance shape | Useful for selected consequential overclaims | H across every claim | H | M–H as claims evolve | M for experiments, L for completeness | Narrow to an evidenced gap; do not restart repaired audits indiscriminately |
| Historical handoff compaction | Potentially H for entry | M; irreversible semantic loss if destructive | L if current retrieval changes | H if summary becomes new authority | M structural, L judgment | Narrow reading/selection first; preserve archival rationale |
| Metrics baseline | M when decisions are specified | L for sampled existing records, H for universal instrumentation | L selected, H dashboard volume | M | H arithmetic, L interpretation | Retain only decision-bound measures from Section 6 |

The report does identify removals, so it is not simply additive. However, its most concrete removal—Gate 4—is under-evidenced, while its foundational additions are asserted before their population and maintenance burden are known. Its own bureaucracy filter should be applied more consistently.

## 9. Remove / simplify candidates

These are candidates for later decisions, not changes authorized or performed by this review.

| Disposition | Strong candidate | Necessary boundary |
|---|---|---|
| DELETE | From the report: false no-reader claims, normative ownership prescription, universal token-cost claim, and no-retirement generalization | Preserve the narrower observed deficits |
| DELETE | Dead legacy adjudication code/comments after caller and compatibility verification | Do not delete active acceptance enforcement because an obsolete function is unused |
| MERGE | Repeated current-state summaries copied into campaign, entry output and handoffs | One source and derived presentation; preserve historical rulings with dates |
| MERGE | Duplicate verification narration already represented by accessible receipts | A closure narrative may explain rationale and residuals absent from raw events; retain that unique information |
| AUTOMATE | Existing linkage, provenance, parser-surface and receipt lookup views | Generation must preserve source and applicability; it must not invent missing semantic edges |
| AUTOMATE | Selection of task-relevant current material from existing sources | Measure missed obligations as well as context reduction; no automatic “retire because old” rule |
| DEMOTE FROM MANDATORY TO OPTIONAL | Universal manual source allocation, universal risk records, and repeated review of unchanged low-consequence proof—if they are proposed | They are not justified as blanket new obligations; existing project rules remain in force |
| KEEP BUT NARROW | ADRs | Preserve contextual consequential decisions; avoid transcript duplication in the default reading path without erasing history |
| KEEP BUT NARROW | OBPI | Bounded intervention plus durable closure/provenance; enduring obligations remain addressable without making every work-log line current instructions |
| KEEP BUT NARROW | Independent review and BDD | Remove only demonstrated duplication, preserving unique assertions and realistic contract conditions |
| KEEP BUT NARROW | Negative controls and proof-channel taxonomy | Match the actual claim; do not multiply controls merely to increase registered-witness counts |

Do not delete history because it is large on disk, merge ledgers because they share a file format, or weaken human initiation because it is inconvenient to automate. Those changes remove distinct properties unless their value is independently disproved.

## 10. Revised top findings

**Five findings confidently retained**

1. Context delivery and historical reconstruction deserve reduction, with measured correctness of the reduced view.
2. Several important claims need tighter correspondence to the precise runtime path and evidence they describe.
3. REQ linkage, proof-channel distinctions, and executable falsifiability checks are useful assets with bounded guarantees.
4. The inspected airlock/jurisdiction surfaces provide less compulsion than some prose implies; the existing successor and disclosed limits matter.
5. Fragmented currentness and repeated summaries can make existing knowledge hard to use; this is stronger than the claim that no durable knowledge exists.

**Five findings requiring more evidence**

1. What subset of requirements remains a current system obligation beyond its originating intervention, and cannot already be recovered reliably.
2. How much delivery/re-entry cost knowledge placement causes after queue waiting, scope coupling and review churn are separated.
3. Which BDD scenarios and review stages provide no material marginal fault detection or decision value.
4. Whether existing-source retrieval and limited applicability metadata outperform a separate persistent model.
5. Whether any material surviving obligations were lost without an intentional disposition, beyond the known demotion exceptions.

**Five recommendations rejected or substantially modified**

1. Do not introduce a new REQ/constraint namespace as the foundation of the remedy.
2. Do not retire Gate 4 from requirement-ID, function or code-coverage overlap alone.
3. Do not replace operator initiation with a risk threshold as a technical consequence of this assessment.
4. Do not create a new authoritative inconsistency/risk/assurance layer when an existing-source view may suffice.
5. Do not convert every gate, receipt and grandfather entry into a uniform assurance object; bind selected consequential claims to adequate evidence and context.

## 11. Human decision points

Only three genuinely discretionary choices remain relevant, and none needs to be demanded before the factual corrections:

1. **Authority:** whether to reconsider delegated initiation at all. The existing operator-initiation ruling remains binding; the assessment does not establish a reason to reopen it. If voluntarily reopened, acceptable delegation and residual risk are human judgments.
2. **Loss/effort tradeoff:** what residual detection and reconstruction risk is acceptable in exchange for fewer reviews, less mandatory reading, or shorter evidence retention. Present measured alternatives first.
3. **Product priority:** whether current investment should prioritize adopter usability, operator productivity, or a specified combination. The repo already states a product; the human need not define it from scratch to compensate for an incomplete report.

The primary report's Q1 is answerable from existing demotion policy; Q3's claim that 67 pool defects are “real and unreachable” needs individual validation and route inspection; Q6 needs retention-versus-entry separation; and Q7 first needs a complete current gate/caller mapping. These are not questions the operator should answer by recollection. Likewise, absence of a `risk` field is not a human decision to create a risk register.

## Evidence notes and sources

**E1 — Deletion policy and cohort.** [Demotion implementation](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/adr_demote.py:1) explicitly cites the May 23 Q1=b ruling; [demotion manpage](/Users/jeff/Documents/Code/gzkit/docs/user/manpages/adr-demote.md:38) describes deletion and re-authoring on re-promotion. `git log --diff-filter=D --name-status -- 'docs/design/adr/**/obpis/*.md'` produced 384 deletion events / 378 unique paths. Commits `993a16c11` and `b15d586da` account for 228 and 136 events. The latter selected unstarted foundations; absence of completion evidence is not itself proof of no code. Two deleted cases had prior completion receipts: OWASP work, with code/tests deliberately removed, and Codex work, with implementation retained and requirement annotations deliberately retired at `15d31d0e6`. The Codex case is real traceability loss, but knowingly accepted—not evidence that ID syntax prevents persistence.

The [current demotion guard](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/adr_demote.py:553) also refuses deletion when live test decorators cite affected REQs unless forced. It protects a narrower consumer than all durable knowledge, but the report's isolated `rmtree` citation omits it. The deleted-path population includes restructuring and repeated deletions, and historical IDs can overlap current IDs; adding historical and current counts does not establish a unique enduring-obligation denominator. Detailed cohort evidence is in the [causality review](/private/tmp/gzkit-adversarial-review/causality-review.md).

**E2 — Work/history/context.** [State doctrine](/Users/jeff/Documents/Code/gzkit/docs/governance/state-doctrine.md:15) treats briefs as durable canon; [pipeline closure narrative](/Users/jeff/Documents/Code/gzkit/.gzkit/skills/gz-obpi-pipeline/SKILL.md:1398) serves later readers. Direct ledger timestamps for OBPI-0.35.0-01 are creation `2026-07-21T23:36:02`, first lock `2026-08-24T07:53:15`, pipeline launch `07:53:29`, completed receipt `11:08:30`. Context census found 553 canonical brief files, median 12,894 bytes, weighted median parent 18,334 bytes; the report uses the 65,593-byte current ADR. This is a different, explicitly scoped population from the report's 556 “live” briefs. [Session entry](/Users/jeff/Documents/Code/gzkit/src/gzkit/session_start.py:165) and [lineage cap](/Users/jeff/Documents/Code/gzkit/src/gzkit/handoff_api.py:1160) establish the real chain-reading burden. Pipeline Stage 1 does not require a generic `gz status` dump.

**E3 — Chores/insights.** [Staleness calculation](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/chores_staleness.py:120), [status caller](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/chores_status_cmd.py:42), and [freshness script](/Users/jeff/Documents/Code/gzkit/scripts/check_proof_freshness.py:94) read the period. Observed `uv run gz chores status --json`, exit 0: `35 overdue, 1 due, 3 unmeasured, 0 paused, 2 current`. [Insight model](/Users/jeff/Documents/Code/gzkit/src/gzkit/insights/model.py:24) includes resolution fields/type; [rubric reader](/Users/jeff/Documents/Code/gzkit/src/gzkit/foundation/rubric.py:172) extracts content references for signals. Direct count: 164 defect and 36 defect-resolution rows. No claim is made that those resolutions are correctly linked to the 164 defects.

**E4 — Actual acceptance.** [Completion prerequisite](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/obpi_complete.py:1025), [review readiness](/Users/jeff/Documents/Code/gzkit/src/gzkit/acceptance_store.py:485), [blocker semantics](/Users/jeff/Documents/Code/gzkit/src/gzkit/acceptance.py:368), [receipt checks](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/obpi_complete.py:1180), [attestation emission](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/obpi_complete.py:1284), and [closeout refusal](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/closeout.py:250). Historical agent-attestor receipts run March 4–28; [waiver cutoff](/Users/jeff/Documents/Code/gzkit/docs/governance/historical-self-close-waivers.md:5) and [receipt-shape enforcement](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/receipt_shape.py:198) distinguish them from current policy. This does not authenticate relayed human words.

**E5 — Retired NC defects.** [July audit](/Users/jeff/Documents/Code/gzkit/docs/governance/enforcement-claim-nc-audit-2026-07-18.md:3) is dated. Repairs include `b6e72cbf5`, `eadcf0963`, `3bff20bbc`, `0f571afb8`, `017863ef7`, `36faf7181`, and `a0f868cd5`. [Current NC entrypoint](/Users/jeff/Documents/Code/gzkit/src/gzkit/governance/trust_audits/_qc_nc_entrypoints.py:27) distinguishes expected failure codes and pins interpreter execution. These refute treating the old population as still unresolved; they do not certify every present control.

**E6 — Requirements and coverage.** [REQ entity](/Users/jeff/Documents/Code/gzkit/src/gzkit/triangle.py:79) has status, parent, description and kinds; [drift scope](/Users/jeff/Documents/Code/gzkit/src/gzkit/triangle.py:376) explains proof-channel and retirement filtering; [coverage computation](/Users/jeff/Documents/Code/gzkit/src/gzkit/traceability.py:628) and [covers caller](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/covers.py:184) show broader linkage scope. Read-only library probe: `1794/2749`, `955` uncovered versus `713` drift-unlinked; 278 appear only in the former, 36 only in the latter, so `955 - 278 + 36 = 713`. Of the 278, 250 are SUPPORT/STRUCTURAL-FENCE; the rest are outside drift's applicable population. The 36 arise from the different test-link inputs. Saved [probe results](/private/tmp/gzkit-adversarial-review/trace-probe.json). `covered` denotes annotation linkage; no test suite was executed to produce these counts. Zero unjustified changes over an empty change set proves nothing about whole-repository justification.

**E7 — Existing source model.** [Source sensor](/Users/jeff/Documents/Code/gzkit/src/gzkit/ontology/source.py:572), [typed relationships](/Users/jeff/Documents/Code/gzkit/src/gzkit/ontology/model.py:51), and [unified projection](/Users/jeff/Documents/Code/gzkit/src/gzkit/ontology/unified.py:211). `build_source_anchor_index(Path('src'), write=False)` produced the figures in Section 5. A working parser with no authored anchors is not a working impact-analysis service; it is also not absence of a parser or model.

**E8 — Airlock/jurisdiction.** [Diagnostic CLI contract](/Users/jeff/Documents/Code/gzkit/src/gzkit/commands/airlock.py:8), [allowlist-scoped hook](/Users/jeff/Documents/Code/gzkit/.claude/hooks/pipeline-gate.py:154), [primitive control](/Users/jeff/Documents/Code/gzkit/src/gzkit/airlock/enter.py:244). The active campaign already identifies ADR-0.37.0 as the calibration/compulsion successor. This review neither initiates it nor treats its design as built enforcement.

**E9 — Knowledge/research homes.** [OKF index](/Users/jeff/Documents/Code/gzkit/.gzkit/governance/knowledge/index.md), [content-boundary declaration](/Users/jeff/Documents/Code/gzkit/.gzkit/governance/knowledge/content-boundary.md), [R&D discipline](/Users/jeff/Documents/Code/gzkit/docs/governance/rnd-discipline.md:78), and [actual research record](/Users/jeff/Documents/Code/gzkit/docs/rnd/ghi-landscape-reorganization.md:1). These establish existing homes and usage, not complete integration or correctness of every statement inside them.

**E10 — Persistent intent/architecture/interface knowledge.** [PRD](/Users/jeff/Documents/Code/gzkit/docs/design/prd/PRD-GZKIT-1.0.0.md:69), [architectural identity](/Users/jeff/Documents/Code/gzkit/docs/design/lodestar/architectural-identity.md), [hexagonal rationale](/Users/jeff/Documents/Code/gzkit/docs/governance/hexagonal-architecture.md), and [canonical CLI specification](/Users/jeff/Documents/Code/gzkit/docs/design/cli-standards-v3.md:13). PRD git history includes August 17, August 2 and May changes. The CLI specification explicitly distinguishes live/met, live/unmet and retired sections. Neither existence nor these self-assessments prove full architectural conformance or complete per-command contract coverage.

**E11 — Scope/review coupling.** [Seven CLI obligations](/Users/jeff/Documents/Code/gzkit/docs/governance/advisory-rules-audit.md:483), [tier claim](/Users/jeff/Documents/Code/gzkit/.gzkit/skills/gz-obpi-pipeline/SKILL.md:1194), [review contract](/Users/jeff/Documents/Code/gzkit/.gzkit/skills/gz-obpi-pipeline/SKILL.md:1296), and [bounded threat-model episode](/Users/jeff/Documents/Code/gzkit/.gzkit/skills/gz-obpi-pipeline/SKILL.md:1348). The episode's durations are a dated repository account, not independently timed by this review.

**E12 — Meaningful brief history.** [OBPI-0.35.0-04 amendments](/Users/jeff/Documents/Code/gzkit/docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-04-section-ownership-and-ratchet.md:93) preserve the attestation naming correction, competing byte definitions and a coupled-surface limitation. This is rationale that raw gate-event duplication would not capture.

**E13 — Binding versus isolation.** [QC descriptor](/Users/jeff/Documents/Code/gzkit/src/gzkit/qc_binding.py:38) calls the field `enforcement_locus`. `Behave = subprocess` describes how the runner enforces the check; it does not claim each scenario launches a fresh CLI process. Primary report §11 row 20 mistakes these levels. Similarly, an explicit validator being outside the default suite does not prove it never runs at a lifecycle chokepoint.

**E14 — Targeted runtime verification.** The independent runtime track observed:

```text
uv run -m unittest tests.commands.test_chores_staleness \
  tests.commands.test_chores_status tests.governance.test_scan_interval_gate \
  tests.test_acceptance tests.test_acceptance_store tests.test_acceptance_integration

Ran 99 tests in 7.251s
OK
```

This is targeted evidence for the challenged code paths, not a complete quality run or certification of reviewer independence. The main read-only probe used `uv run --no-sync python` with a temporary uv cache and bytecode writing disabled; an initial attempt using the default uv cache was denied by the filesystem sandbox, then succeeded with the temporary cache.

Standards consulted for the material corrections:

- **S1:** [16326:2019](</Users/jeff/Library/Mobile Documents/com~apple~CloudDocs/IEEE/16326-2019.pdf>), §§7.1, 7.3.1.1, 7.7.3.2, 7.11.
- **S2:** [29148:2018](</Users/jeff/Library/Mobile Documents/com~apple~CloudDocs/IEEE/29148-2018.pdf>), §§5.2.4–8, 6.4.3.5.
- **S3:** [42010:2022](</Users/jeff/Library/Mobile Documents/com~apple~CloudDocs/IEEE/42010-2022.pdf>), Clauses 4, 6; §§6.1, 6.9.
- **S4:** [15289:2019](</Users/jeff/Library/Mobile Documents/com~apple~CloudDocs/IEEE/15289-2019.pdf>), §§5.1, 6.2, 8.2.
- **S5:** [15026-2:2022](</Users/jeff/Library/Mobile Documents/com~apple~CloudDocs/IEEE/15026-2-2022.pdf>), §§3.1.7, 4.2, 5.3.2–6. Part 1 was not supplied; its composite definition quoted by the primary report was not independently verified from that volume.
- **S6:** [1012:2024](</Users/jeff/Library/Mobile Documents/com~apple~CloudDocs/IEEE/1012-2024.pdf>), Clause 5, §6.3, Annex C.
- **S7:** [29119-4:2021](</Users/jeff/Library/Mobile Documents/com~apple~CloudDocs/IEEE/29119-4-2021.pdf>), §5.2.4. Input syntax mutations are distinct from code-mutation adequacy analysis.
- **S8:** [29119-1:2022](</Users/jeff/Library/Mobile Documents/com~apple~CloudDocs/IEEE/29119-1-2022.pdf>), §§3.115–116, 4.1.10.

## 12. Phase 2 gate

**NOT READY FOR PHASE 2 — MORE INVESTIGATION REQUIRED**

This verdict concerns readiness for **design**, as requested. The primary report itself calls its proposed Phase 2 further investigation, which is more defensible than its earlier recommendations.

Before selecting a replacement engineering model, correct the factual and standards errors; identify the enduring-obligation population and any unintended retention losses; separate queue time from active work; and establish which proposed simplifications preserve useful fault detection and retrieval. Do not make implementation, identifier changes, gate retirement, or authority-policy changes prerequisites for learning those facts.

The evidence supports a smaller investigation into **currentness, retrieval, and claim-to-evidence fit within existing mechanisms**. It does not yet support a new persistent engineering-object layer.
