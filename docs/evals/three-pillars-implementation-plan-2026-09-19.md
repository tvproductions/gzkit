# Three pillars: opportunities and implementation plan

Dated 2026-09-19. Persona: main-session — craftsperson, governance-aware,
whole-file reasoning, direct. Baseline reviewed for this plan:
`d6bc23d0ebef83a1b3391c521e35931f5f8013b6`. Parent work: the operator's
three-pillars assessment and subsequent authorization to implement warranted
repairs. This is an implementation recommendation and dated evidence account,
not new repository doctrine, an ADR, or OBPI initiation.

## Overall completion: INCOMPLETE

Checked against the linked GitHub issues on 2026-09-19. **Two of the five plan
rows are complete; three remain open.** This is a row count, not a percentage
of engineering effort. The assessment and several measurements are complete;
the overall remedy plan is not. Status clarification is recorded under #1053.

| Row | Done? | What proves completion / what is still missing |
|---|---|---|
| 1 — mirror-path repair | **YES** | #1049 closed with shipped commit `08655b31b854e2f016b53bd638e3423e71936c13`, behavioral regression evidence and review. |
| 2 — configured-source repair | **YES** | #1050 closed with the same shipped commit, configured-root regression evidence and review. |
| 3 — proof-currency decision | **NO** | #1029 is open. A reviewed draft exists; its required operator design ruling is not recorded. Retaining broad currency is a recommendation, not a booked decision. |
| 4 — advisory impact remedy | **NO** | #1053 is open. #1052 completed only the measurement. The proposed capability is unbuilt; design disposition, review-cost evidence and any adopted implementation/validation remain outstanding. |
| 5 — Stage-4 production validation | **NO** | #1028 is open. The dated census contains no qualifying post-treatment production run; the required launch/proof/review/round/exit comparison is missing. |

**How to decide whether the whole plan is done:** follow each row's linked GHI
to its actual exit evidence. For a shipped repair, require its commit and
validation; for a design decision, require the recorded operator ruling; for
production validation, require the observed run and comparison. If a GHI closes
by routing an adopted feature to an ADR, follow that destination through its
implementation and validation: issue closure alone does not make the feature
built. An explicit operator decision not to pursue a proposal is a disposition,
not an implementation claim. Until every row has that evidence or an explicit
operator disposition, this overall verdict remains INCOMPLETE.

Passing repository checks validates the changes that exist. It does not prove
that the unbuilt capability exists or that a production outcome was observed.
A plan, design draft, measurement report, filed GHI or clean working tree is not
by itself evidence of whole-plan completion. The detailed tables below preserve
the supporting work and boundaries; this verdict is a dated evidence summary,
not a new gate or a substitute for issue, commit and ledger evidence.

## Decision

Execute the bounded repairs that make existing discovery and validation respect
their established inputs. Then prepare the two distinct feature decisions:
bounded change-impact assistance and dependency-sensitive proof currency.
Neither needs another general prompt experiment. Neither is justified merely
because a model proposed it during an assessment.

The user commissioned opportunities for fixes, repairs and features across all
three pillars. Equal scores for an added tracing instruction reject that
instruction as an adopted remedy; they do not reject runtime improvements.
Conversely, a local validator repair is useful without establishing that general
obligation discovery has been solved.

## Execution status — 2026-09-19 follow-through

Operator direction: "all of this work needs to be conducted under a GHI".
The remaining advisory-impact design, boundedness validation and implementation
disposition are conducted under [GHI #1053](https://github.com/tvproductions/gzkit/issues/1053).
Proof currency remains under #1029; production validation remains under #1028.
Completed repairs and measurements retain the GHI/commit links below. Each next
work unit names its issue before execution and records decisions and evidence
there; a closed measurement issue does not discharge an unbuilt feature.

| Plan row | Observed status | Evidence / remaining action |
|---|---|---|
| 1: mirror-path equivalence | Shipped and synced; #1049 closed | Commit `08655b31b854e2f016b53bd638e3423e71936c13`; shared repair, behavioral regressions and independent review in [repair evidence](three-pillars-remedies-2026-09-19.md). |
| 2: configured source audit | Shipped and synced; #1050 closed | Same commit; configured-root false-pass reproduction and coupled scope documentation repaired. Gate blocker #1051 also repaired and closed there. |
| 3: proof currency | Design complete; ruling outstanding | [Concrete draft](three-pillars-proof-currency-design-2026-09-19.md). Recommend retaining the broad digest: this measurement adds evidence that import closure cannot safely narrow it. #1029 remains open for its explicit design ruling. |
| 4: bounded impact assistance | Code-derived measurement complete; runtime feature unbuilt | [Report and reproducible artifacts](three-pillars-impact-2026-09-19/report.md), #1052. Import-only output misses live CLI registration; revise the proposal to typed import, registry and test evidence. Human review cost remains unmeasured; successor condition is not yet fully satisfied. |
| 5: Stage-4 production outcome | Waiting for a real run | [Dated ledger census](three-pillars-impact-2026-09-19/production-status.md): zero post-treatment launches/proofs/reviews/OBPI receipts. #1028 remains open. Do not initiate an artificial OBPI to manufacture evidence. |

The shipped repair commit passed all 62 full staged checks, 10,498 unit tests
(four skipped), 432 BDD scenarios and 88.21% coverage. Those are evidence for
that commit, not a prediction about future changes or proof of general discovery.

The next decision is concrete: retain broad proof currency and approve the
revised advisory report design for subsequent governed feature authoring, while
keeping its runtime implementation in campaign order. Approval of a design does
not itself initiate an OBPI. The remaining production observation depends on the
next normal operator-initiated run; no additional prompt experiment is selected.

## Ranked remaining work

The order below ranks this assessment's opportunities by demonstrated failure,
boundedness and expected benefit. It does not reorder the feature campaign.
The first two rows were independently reproduced and routed to GHIs after
ownership checks; their assessment prompts alone were not defect authority.

| Order | Pillar and opportunity | Evidence and expected benefit | Scope and route | Acceptance and next action |
|---|---|---|---|---|
| 1 | 2/3: equivalent mirror paths must produce equivalent refusal | The remedy study identified a shared helper comparing unnormalized Allowed Paths while extraction preserves a leading `./`. A missed identity can let generated-mirror work pass as permissible. | [GHI #1049](https://github.com/tvproductions/gzkit/issues/1049): reproduced bypass; shared correction implemented with RED/GREEN regression evidence and independent review. Keep the repair shared across plan audit, brief validation and promotion. | Existing and CREATE-declared mirror paths, with and without prefix, must receive the same refusal and canonical advice. A prefixed canonical CREATE path must remain valid. Prove the brief-consuming path, not only a string helper. Preserve dotfile roots. |
| 2 | 1/3: source audits must visit the configured source location | The remedy study identified the fixed `src/gzkit` scan location despite a loaded `source_root` configuration. This can report clean while overlooking relocated source. | [GHI #1050](https://github.com/tvproductions/gzkit/issues/1050): reproduced false pass under configured `lib` root; correction implemented after intent/owner/prior-art checks, with RED/GREEN evidence. Source selection is distinct from manifest-based classification of literals. | An unmapped literal under configured-root/gzkit must be reported with its project-relative location and failing command result. A distinguishable stale default-tree violation must not be scanned. Preserve recursive traversal and module-local exemptions. Update scope documentation with the same repair. |
| 3 | 2/3: dependency-sensitive proof currency | [GHI #1029](https://github.com/tvproductions/gzkit/issues/1029), read live for this plan, describes broad invalidation and requires an operator-ruled design. Benefit: preserve genuinely unaffected evidence through a repair without admitting stale evidence. | Design deliverable under #1029, **not direct runtime repair**. Acceptance producers, readiness, reviewer subject binding and final completion are coupled. No implementation route is selected until its authority boundary is ruled. | Specify independent dependency authority, invalidation cases and conservative fallback below. Do not equate an agent allowlist, import closure or observed file list with complete dependencies. |
| 4 | 3, supporting 2: bounded change-impact assistance | Repeated current assessments missed relationships despite finding related code. ADR-0.37.0 explicitly leaves file-coupling discovery unresolved. Benefit: expose affected consumers and uncertain boundaries before a local repair is declared complete. | Feature design, with ADR-0.37.0 § Alternatives Considered item 2 as the existing residual destination rule. First price a bounded advisory result from existing coupling evidence. A successor ADR must answer boundedness; this plan creates none. | Show distinct results for distinct changes, trace each reported relationship to evidence, preserve omitted/unsupported relationship classes, and demonstrate reviewable output on real changes. Do not use the result to authorize closure or narrow proof currency. |
| 5 | 1/2: verify the landed Stage-4 mitigation in production | [GHI #1028](https://github.com/tvproductions/gzkit/issues/1028) remains open when read for this plan. The prior assessment records a landed mitigation and no relevant post-treatment events at its dated census. | Production observation during the next normally initiated OBPI. Do not launch a synthetic OBPI or rewrite the procedure again to discharge the observation. | Record launches, proofs, reviews, rounds, exits and reasons for repeated work against the issue's historical observations. Separate concurrency, model and task effects; a smaller count alone does not prove safer convergence. |

## Follow-through under GHIs #1053 and #1054

The #1053 draft now contains the proposed interface, typed producer/witness
contract, shared source/test resolution, failure/coverage states, display
accounting, semantic acceptance cases and validation protocol. Independent
review corrected the default-depth ambiguity: import depth is separate from the
registry section's complete mapping/invocation chain. This is a concrete reviewed
design, not a runtime implementation or recorded operator approval.

The source-root lead from that design became the reproduced direct repair
[GHI #1054](https://github.com/tvproductions/gzkit/issues/1054). It covers default
source indexing, orphan detection and unified projection, including repeated
nested command use. It is separate from #1050's auditor repair and from #1053's
new relationship types. Its issue owns implementation, regression/review evidence
and closure; an in-flight patch is not yet shipped evidence.

## Concrete design deliverables

Concrete drafts: [proof currency](three-pillars-proof-currency-design-2026-09-19.md)
and [bounded impact assistance](three-pillars-impact-design-2026-09-19.md).
They contain source maps, alternatives and acceptance cases; neither is a ruled
change or an initiated feature.

### Proof currency: decide what can safely remain current

The #1029 design must start from the current proof-generation-to-completion flow,
not from selecting a cheaper hash. Its deliverable is a consumer map, a comparison
of candidate authorities, and an executable acceptance design. Preserve these
invariants in every candidate:

1. A relevant production-source, covering-test, fixture or configuration change
   invalidates the affected proof and reviews that approved that subject.
2. A contract change invalidates all obligations governed by that contract.
3. An actually unrelated change preserves a proof only when independent evidence
   establishes why the excluded input cannot affect its result.
4. Missing, unsupported or uncertain dependencies retain the broad current
   invalidation boundary. A stale or agent-edited dependency record cannot grant
   itself authority.
5. Proof generation, review import, readiness and completion agree on the same
   identity and version rules, including legacy evidence and mixed versions.

Compare at least the existing broad digest, static dependency closure and
execution-observed inputs. Static imports miss runtime data, configuration and
dynamic loading. Observed reads witness a particular execution, not every input
that could alter a future execution; environment, subprocess and absent-file
dependencies also need an account. A per-obligation manifest is a representation,
not a solution to those coverage problems. Combining incomplete sources is not
automatically complete.

The design may conclude that only a limited proof class can be narrowed safely,
or that the conservative digest must remain. That is a decision with specific
benefits and limits, not permission to weaken the closure contract. #1029's live
body explicitly says its exit condition is a ruled design and that nothing is
proposed for landing there. The earlier conversational promise of direct runtime
implementation through that GHI was incorrect.

### Impact assistance: expose relationships without certifying completeness

Draft a design for an advisory result built from existing repository evidence:
the changed surface, direct consumers supported by source evidence, and declared
governance relationships kept separately identifiable. Each relationship needs
its source, direction and freshness basis. Unknown dynamic, data and cross-tool
relationships must remain explicit limitations.

Compare bounded views such as direct consumers grouped by package against deeper
traversal. Report the full result size and any hidden population; a truncated
display must never imply that only displayed files are affected. Assess actual
changes with indirect consumers and changes having no identified consumer. The
acceptance question is whether this reduces concrete omissions at a manageable
review cost, not whether the output contains edges or has a green indicator.

Do not turn this into a new gate, general graph engine, or proof dependency
authority. The existing state-doctrine boundary remains: a derived index is
rebuildable evidence, not canon. Authoring and initiating a feature still follow
the campaign and operator boundary after the design has a ruled destination.

## Existing ownership and completed work

| Pillar | Disposition | Evidence and boundary |
|---|---|---|
| 1: delivery | Done for sampled native paths | [Current delivery measurements](three-pillars-current-2026-09-19/delivery.md): all four ordered instruction chains arrived whole at the named baseline; the reduced-cap negative control truncated. This is native CLI assembly evidence, not all harnesses or comprehension. |
| 1: skill audit | Repair landed | [Recovered assessment](three-pillars-2026-09-19/assessment.md): #1037, `5c777c965`, unfinished-body markers and explicit size ceilings. Mechanical authoring coverage remains narrower than semantic completeness. |
| 1/2: further pipeline reduction | Not adopted | The earlier comparison demonstrated no improvement. Keep current canon; no additional diet is selected by this analysis. |
| 2/3: handoff relationships | Repair landed | #870/#1038, `5c777c965`: declared ancestor ordering and truthful truncation. Undeclared relationships and actual reading remain outside the guarantee. |
| 2: declared-invariant accounting | Existing feature ownership | [ADR-0.37.0](../design/adr/pre-release/ADR-0.37.0-airlock-calibration-and-compulsion/ADR-0.37.0-airlock-calibration-and-compulsion.md) D1/D2 calibrate declared law and its accounting. Its Negative 3 and Alternative 2 expressly defer calibrated file-coupling input. Follow existing campaign sequencing and operator initiation. This plan does not assert a newly measured OBPI completion count. |
| 2/3: contradictory smoke guidance | Repair landed | [Repair evidence](three-pillars-current-2026-09-19/repair.md), #1047: align coupled prose with already-settled adopter opt-in behavior. Runtime behavior unchanged. |
| 3: added tracing instruction | Rejected for adoption | [Remedy comparison](three-pillars-remedy-2026-09-19/results.md), #1048: equal 28/30 totals; 73 versus 57 calls. A bounded negative result, not proof that tracing is never useful. |
| 3: general discovery | Unresolved feature opportunity | Neither the native delivery measurements nor local repairs establish complete semantic impact discovery. Do not label ADR-0.37.0 as its implementation. |

The earlier recovered assessment's statement that the production scope-discovery
residual “already belongs to ADR-0.37.0” was too broad. The ADR owns declared-law
calibration and compulsion. Its file-coupling alternative names a successor
design condition; that is a recorded destination requirement, not an implemented
or currently initiated general discovery feature.

## Execution and completion evidence

For each selected repair: reproduce the failure, confirm existing authority and
ownership, create or reuse its GHI, write a failing behavioral test, repair the
shared cause and coupled consumers, obtain independent review, run required
checks, and close with the landed commit and observed evidence. This plan is
not itself proof that either candidate is repaired. The repair issues and their
commits supply that evidence.

The two concrete design drafts above now exist with source-backed alternatives
and acceptance cases. After the bounded repairs, evaluate and rule their
recommendations; do not repeat the drafting step. Do not stop merely to ask whether to continue
authorized analysis. Do not treat a design proposal as operator initiation of an
OBPI or as permission to change what completion trusts.

This plan uses the committed assessment packets, the live bodies of #1028 and
#1029, and ADR-0.37.0's decision, consequences and alternatives. It is a scoped
reconciliation, not a fresh whole-repository governance audit or new review of
the scholarly sources. Experimental leads outside these rows remain recorded
in the study case files; they are not silently promoted into this implementation
scope.

Repair reproductions, regression witnesses and independent reviews are recorded
in [repair evidence](three-pillars-remedies-2026-09-19.md). Full gates and
landed commit identities belong to the two GHI closure records.

The required full test gate additionally exposed a fresh-interpreter circular
import in advisor-QC/ARB initialization. [GHI #1051](https://github.com/tvproductions/gzkit/issues/1051)
records that separately reproduced blocker and its bounded repair. It does not
change the opportunity ranking or expand the dependency-discovery feature.
