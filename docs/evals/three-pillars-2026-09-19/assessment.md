# Three pillars: recovered assessment and disposition

Dated 2026-09-19; author: g0 (operator), assessment prepared by the main-session
agent. Code baseline: `5c777c965fe7aa3df6b7859fd3f66c0a0d72aab1`.
This reconstructs the existing conversation and reconciles it with current code;
it is not a newly initiated ADR, OBPI, or retrospective attestation.

## Conclusion

The useful diagnosis is **false closure**: an agent can retrieve enough relevant
material to produce a coherent answer without establishing that it considered
the applicable obligations, consumers, and current authority. Pillar three is
the strongest fit to the operator's experience. Neither the video nor this
assessment establishes sparse attention as the cause of a gzkit failure.

Two bounded repairs are shipped: declared handoff lineage is correctly ordered
and reports real truncation; skill auditing detects unfinished scaffolds and
enforces explicit body-size ceilings. These improve particular mechanisms, not
general comprehension. An independent current-code review found no concrete new
regression in its inspected paths; 84 focused existing tests passed.

The missing instruction comparison is now performed: current and reduced
pipeline text each met all six predeclared decision criteria in one fresh-context
sample. That is **no observed decision regression, no demonstrated improvement**.
Keep the canonical pipeline unchanged. The proposed history lift removes only
1.47% of its primary bytes and adds stored companion text. This result does not
justify presenting it as a remedy for context reliability.

## Recovery and plan actually followed

### Scope reconciliation after operator correction, 2026-09-19

Rechecked at `7b6b48378`. The operator rejected the later substitution of a
general rule audit for this assignment: "are you focused on the work or just
doing random work in gzkit now?" The original conversation was reread, including
the four-step execution proposal and the subsequent authorization to write GHIs
and do the work. That agreement, rather than the resumed overhaul handoff,
defines this work's completion boundary.

| Original commissioned outcome | Pillar and diagnosis | Implementation / disposition | Direct validation and remaining limit |
|---|---|---|---|
| Repair lineage accuracy | 2: ordering relationships; 3: incomplete discovery reported as complete | `5c777c965`, GHIs #870/#1038: ancestry ordering and actual truncation; keep the repair | Shortcut/merge/boundary/cycle tests and CLI/session-start consumers. Only declared lineage is covered; no claim that the agent reads it or discovers undeclared obligations. |
| Complete bounded skill-body auditing | 1: instruction load and unfinished procedures; supporting 3: audit success masking unfinished material | `5c777c965`, GHI #1037: marker detection, fixed body ceilings and actionable output; keep the repair | Scaffold, completed-body, fence and threshold controls. This is a supporting authoring check, not a remedy for semantic dependency discovery. |
| Compare a reduced pipeline against the existing instructions | 1: usable context; 2: retaining decision-critical relationships | Comparison completed at `3dc6f6130`; both conditions passed 6/6; candidate deliberately not adopted | Raw answers and independent scoring retained. One prompted sample per condition establishes no comparative benefit. Neither pipeline shortening nor general comprehension improvement is demonstrated. |
| Observe the already-landed Stage 4 change during a normal run | 1/2: procedural burden and repeated invalidation; relevant to 3 because narrowing depends on discovered inputs | Existing change `6b440453e`; GHI #1028 remains open for production observation, #1029 for the dependency-sensitive currency design | Fresh census: 16,949 ledger rows; zero relevant events after the treatment cutoff. No observed production outcome exists. A synthetic OBPI cannot fulfill this condition. |

Current independent code review found these repaired production paths unchanged
since `5c777c965` and no concrete unmet requirement within the bounded repairs.
The six existing test modules listed in `code-review.md` were rerun together:
**84 tests passed in 2.647s**. This is fresh focused regression evidence, not a
new full-suite run and not a model-behavior result.

The rule-pair audit at `7757851b6`/`7b6b48378` is adjacent instruction-consistency
work. It is not an additional runtime remedy for the three pillars and must not
be used to claim closure of this assignment's discovery question. Further
general audits are not the next action selected by this assessment.

**The central pillar-three gap remains:** no evaluated mechanism establishes
complete discovery of semantically affected consumers. The six-case exercise
explicitly cues the indirect-consumer problem; it cannot measure unsuspected
dependency discovery. This is a limit of that experiment, not evidence that a
particular unimplemented retrieval mechanism would solve it. The production
scope-discovery residual already belongs to ADR-0.37.0. Proof currency must stay
conservative under #1029 until a ruled design demonstrates its dependency
boundary and fallback. Neither ownership reference is implementation, and neither
authorizes initiating those OBPIs from this assessment.

The defensible outcome is therefore **completed bounded repairs and appraisal,
with general discovery reliability unresolved**, not "the three pillars are
fixed." No additional runtime patch is justified by the current reviewed
counterexamples. New implementation must name the failing obligation and its
specific acceptance evidence before it is selected; another green audit or a
larger instruction set cannot stand in for that evidence.

The initiating request was assessment only. The operator subsequently authorized
GHIs and implementation. Recovery used the original task's recorded exchanges,
the supplied transcript, committed review packet, issues, current producer and
consumer code, and freshly checked primary research pages.

1. Recover the scholarly appraisal and distinguish hypotheses from measurements.
2. Reconcile the original findings with changes since the first inspection.
3. Review the shipped remedies and run the missing comparative decision exercise.
4. Record a disposition for each proposal, retaining evidence and limitations.

The earlier snapshot was `ea5c424d6`; the refreshed pre-repair assessment was
`8169f57c1`, followed by sync `65436e910` and repair `5c777c965`.
Historical growth measurements and earlier instruction sizes are dated context,
not the current state. Recent Stage-4 review-window, focused-follow-up and bounded
exit changes already existed at the refresh and were not implemented again.

Two reasoning corrections matter. First, an isolated lite coverage subgate was
mistaken for the final completion boundary. Tracing the final guard withdrew that
recommendation. Second, issue closure and green tests were mistakenly substituted
for completion of the broader appraisal. The present report closes that analytical
gap; it does not invent OBPI work to justify earlier activity. The operator's
corrections are recorded in the insight stream.

## Appraisal: sharpened pillars

| Pillar | Defensible claim | What does not follow | Appropriate engineering response |
|---|---|---|---|
| 1: usable context | Having tokens available does not establish successful use of their evidence. Retrieval, retention and integration are different operations. | File bytes do not measure comprehension; a larger window or shorter prompt does not guarantee correctness. | Measure decisions against known obligations; preserve authority and conditions when reducing instruction load. |
| 2: relationships | A model can have the right facts and still miss their ordering, conditions or relationships. | Sparse attention has not been identified as the cause in the models used here. | Encode important relationships in shared authority and test their consumers; evaluate conflicting and inherited obligations. |
| 3: discovery and currency | Relevant retrieval is not evidence of complete applicable scope; stale but plausible examples can mislead. | A search result, graph reach, or green local test does not certify all affected consumers were found. | Trace writers through storage/contracts to readers, preserve declared lineage, bind proof to current inputs, and state the limits of discovery. |

The transcript overstates pillar three when it says there is "nothing to search
for" without a direct code reference. Its database example still supplies table
and column identities, SQL, migrations and change history as discovery routes.
The difficult claim is sufficient impact coverage across those representations,
not the impossibility of searching. A passing writer test can coexist with a
wrong report because the two checks concern different meanings of the same
stored field. gzkit has the analogous boundary between canon, skills, runtime,
tests and evidence; declared identifiers help traverse it but cannot certify
that every semantic relationship has been represented.

Dense attention has quadratic interactions in sequence length, but that is not a
claim that every generated token recomputes the entire prefix: caching changes
inference work. Exact attention can also use more efficient memory execution.
See [KV-cache documentation](https://huggingface.co/docs/transformers/en/cache_explanation)
and [FlashAttention](https://arxiv.org/abs/2205.14135). Architectural labels alone
cannot explain this repository's observed failures.

The video's economic premise is a hypothesis, not a repository diagnosis.
More software may mean more valuable work, low-value output, or displaced work.
Source/test growth does not establish excess, AI causality, or net productivity.
[METR's task-substitution discussion](https://metr.org/blog/2026-05-08-task-substitution-and-uplift/)
helps separate doing the same work faster from choosing different work.
Source video: [Kantan Coding, 2026-09-15](https://www.youtube.com/watch?v=k2qls2LiBRc),
assessed from the operator-supplied transcript.

## 2026 scholarly evidence

These are scoped empirical results, not a consensus that models cannot maintain
software. The three selected papers were rechecked against their primary text.
No paper's experiments were independently replicated in this work.

| Source | Useful evidence | Limits on transfer to gzkit |
|---|---|---|
| [WildTrace, v2, July 23](https://arxiv.org/html/2607.09328v2) | 481 tasks over 214 natural documents evaluate facts and their relationships. Best reported mean rubric credit is 75.3%. Supports separating presence of evidence from relational use. | Mostly English incident/literature documents, direct document input, LLM judging. The percentage is not binary task accuracy; over-window zeros mix capacity with comprehension. |
| [Agent Retrieval Bench, July 27](https://arxiv.org/html/2607.24882v1) | 427 samples over 25 repositories include affected-file retrieval and negative cases. In analyzed trajectories, some tracks never access gold files in 27–35% of samples. Supports measuring discovery separately. | Approximate/incomplete gold, uneven repositories, small pilot portions; context acquisition is not patch correctness or proof that retrieval dominates failure. |
| [When Retrieval Hurts, May 14](https://arxiv.org/html/2605.14478v1) | Controlled current/stale/mixed helper examples across 17 signature changes show obsolete retrieved patterns can persist. Supports freshness and authority checks. | Five selected Python repositories; small models/sample; supplied oracle context and pattern matching, not executed application correctness. No-context performance is also poor. Submitted to Information and Software Technology, not an accepted-publication claim. |

Other recovered 2026 work provides useful checks on overgeneralization:

- [Language Models Can Control Their Own Attention](https://arxiv.org/abs/2609.02737)
  reports adaptive attention modes and measured efficiency/accuracy tradeoffs.
  Sparse or selective attention is not automatically equivalent to unusable context.
- [Beyond Repository Boundaries](https://arxiv.org/abs/2609.09987), accepted to
  Findings of EMNLP 2026, studies repository plus external-dependency graph retrieval.
  It supports testing wider dependency evidence, not assuming any graph is complete.
- [Debt Behind the AI Boom](https://arxiv.org/abs/2603.28592v2) measures static issues
  in attributed AI commits. Static smells and attribution selection do not establish
  causal maintenance burden relative to a matched human baseline.
- [To What Extent Does Agent-generated Code Require Maintenance?](https://arxiv.org/abs/2605.06464v2),
  accepted to EASE 2026, finds less frequent observed maintenance in its sample.
  Less observed maintenance is not necessarily less needed maintenance; task and
  importance differences complicate a simple anti-AI interpretation.

## Serious practitioner triangulation

[Osmani and Orosz](https://newsletter.pragmaticengineer.com/p/how-ai-will-change-software-engineering)
emphasize architectural judgment, review and the remaining hard work; their
“70%” framing is a practitioner heuristic, not a measured universal proportion.
[Böckeler](https://www.martinfowler.com/articles/exploring-gen-ai/i-still-care-about-the-code.html)
adds defect detectability to likelihood and impact, grounded in migration experience.
[Willison's February 2026 cognitive-debt account](https://simonwillison.net/2026/Feb/15/cognitive-debt/)
describes losing a working mental model after accepting code without reading it;
that is useful testimony, not a prevalence estimate.
[Joshi, May 2026](https://www.martinfowler.com/articles/what-is-code.html)
frames code as a domain model expressed through vocabulary and invariants.
Together these support keeping domain meaning and reviewability central.

[Orosz's March 2026 discussion](https://newsletter.pragmaticengineer.com/p/are-ai-agents-actually-slowing-us)
also warns against conflating output with outcomes; only its public portion was
verified. For a stronger causal design, [METR's July 2025 RCT](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)
found a 19% slowdown among 16 experienced maintainers across 246 tasks under its
conditions. [METR's February 2026 update](https://metr.org/blog/2026-02-24-uplift-update/)
explains why later estimates are affected by task selection and measurement changes.
Neither warrants declaring current AI assistance universally faster or slower.

## Current gzkit diagnosis and remedies

| Finding | Current evidence and disposition | What remains unproved |
|---|---|---|
| Declared handoff ancestors could be misordered or falsely reported truncated | **Repaired**, #870/#1038, `5c777c965`. `handoff_api.py` separates bounded breadth-first discovery from ancestry ordering; CLI/session-start consume the result. Shortcut, merge, duplicate, boundary and cycle cases are tested. | Surfacing ancestry does not force reading it or discover undeclared dependencies. |
| Skill bodies lacked the intended unfinished/size audit | **Repaired**, #1037, same commit. `skills_audit.py` checks recognizable markers, lifecycle and fixed ceilings, and renders warnings. Twelve cutover grandfather ceilings are recorded in packaged data. | A mechanical marker check is not semantic completeness. The ceilings do not shrink automatically after every reduction or remove existing large bodies. |
| Apparent lite coverage loophole | **Withdrawn after full consumer trace.** `obpi_complete.py` calls `completion_review` immediately before the transaction; `acceptance_store.py` and `acceptance.py` reject current blockers, including missing or stale proof. The warning-only test mocked that final review. | The three integration tests are not a complete live completion transaction or proof of every possible acceptance property. |
| Repeated command scopes can drift | **Existing mitigation verified.** `canonical_steps.py` feeds quality typechecking and ARB receipt validation. Mutation tests prove consumers follow the authority. | This verifies a named relationship, not discovery of unknown relationships or all commands sharing one implementation. |
| Pipeline text is large | **Evaluated; retain current text.** Six-passage candidate and exact diff remain reviewable. Both conditions passed six decision cases, with no measured quality gain. | No repeated trials, latency/cost measure, long-session evaluation or production outcome comparison. |
| Airlock does not yet establish production impact scope | **Already owned residual**, ADR-0.37.0 / #807. `check_airlock_in_gate` explicitly documents empty leaf-dependent reach and unwired parent invariants; refusals remain diagnostic. | Nonempty or accurate production obligation coverage. Do not initiate the ADR's OBPIs from this assessment. |
| Broad proof currency causes repeated invalidation | **Keep conservative behavior.** #1029 is an operator-ruled design investigation. Enumerated-input hashing is real; undeclared dependencies cannot be assumed absent. | Safe narrow invalidation requires trustworthy dependency evidence plus a broad fallback. Agent allowlists and current airlock reach do not supply it. |
| Recent Stage-4 changes need observation | **Separate production measurement**, #1028. Retained ledger census found zero relevant postchange run events. | Effectiveness in a real operator-initiated run. This does not block completion of this assessment or authorize a synthetic OBPI. |
| Other control-surface coherence audits are stale | **Existing chore work**, not certified by this assessment. The five-audit program remains in the overhaul record. | Repository-wide doctrine consistency; a scoped source review cannot claim it. |

Code references are relative to the baseline: `src/gzkit/handoff_api.py:1098`,
`src/gzkit/skills_audit.py:603`, `src/gzkit/commands/obpi_complete.py:1332`,
`src/gzkit/acceptance_store.py:485`, `src/gzkit/acceptance.py:206`,
`src/gzkit/quality.py:393`, `src/gzkit/arb/validator.py:278`,
`src/gzkit/pipeline_runtime.py:604`, and `src/gzkit/acceptance_execution.py:209`.

Inherited pipeline citation and plan-entry inconsistencies were reported under
[#921](https://github.com/tvproductions/gzkit/issues/921#issuecomment-5742469907).
An unrelated import-cycle defect was captured as #1039. Neither is silently
represented as fixed by this work.

## Validation and trust boundary

The shipped runtime repair passed the full 62-check quality suite, 10,492 tests
(five skips), and coverage at 88.21%. Existing ARB evidence includes
`arb-step-unittest-ed2bdc49ab5542caa7d254ffbdaae4a0`,
`arb-step-coverage-5f1e91fd134142c5b14cd44989c99af9`, and
`arb-step-mkdocs-6755cbf34add4886805820c7fa77e07c`.
These are recorded results for that repair, not measurements of agent cognition.
The later independent bounded review ran 84 existing tests and found no concrete
new regression in the inspected paths. Full-suite success cannot prove absence
of all regressions.

The comparison's predeclared criteria, input digests, raw responses and result
limits are in [protocol.md](protocol.md), [inputs.json](inputs.json),
[response-a.md](response-a.md), [response-b.md](response-b.md), and
[results.md](results.md). The fixture is intentionally tiny and the questions
cue relevant obligations; passing it cannot establish real-world discovery recall.

The bounded appraisal, diagnosis, justified repairs and comparative evaluation
are complete. Production Stage-4 effectiveness, broader coherence chores and
owned feature work remain separately tracked. None is collapsed into a claim
that gzkit now prevents false closure generally.
