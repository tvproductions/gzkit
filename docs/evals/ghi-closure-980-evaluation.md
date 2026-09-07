# Bounded GHI closure — behavioral evaluation

Date: 2026-09-07. Work order: GHI #980.

## Contract and method

The authorized change seats a bounded closure contract in `ghi-author` 1.5.0
and `ghi-close` 2.8.0. Required behavior is to finish a verified repair, reject
counterexamples and introduced regressions, track independent findings without
automatically executing them, and change method after repeated reopenings.
Investigation authoring must not invent a cause or promise an unlimited repair.

The [scenario packet](ghi-closure-980-scenarios.json) contains the complete
prompts and response contract. A separate Codex subagent, with no inherited
conversation history, read the two candidate canonical skills and the packet.
It returned decisions without executing repository or GitHub actions. The
implementing agent assessed the returned actions against the criteria below.
The initial run covered six scenarios. After the independent review found
the invocation-boundary conflict described below, the same evaluator read the
amendment and answered the new author_unselected case plus the affected
investigation case again: seven distinct cases and eight total responses.
These are not independently sampled models or a before/after experiment.
The evaluator was not given this report or its expected-action table before
responding.

## Expected and observed decisions

| Case | Required decision | Observed decision | Assessment |
|---|---|---|---|
| complete | Close the verified repair; do not require speculative extra rounds | Closure permitted; complete accounting/sync and stop | Pass |
| counterexample | Block closure; extend the matrix for the demonstrated invalid-journal acceptance | Closure refused; add fixture and repair the reader/recovery discrepancy | Pass |
| adjacent | Track the independent defect; close the verified repair without automatically fixing the sibling | Closure permitted; separately track the diagnostic-ordering defect | Pass |
| coupled_regression | Block closure for a consumer broken by the shared-helper change | Closure refused; add library consumer and empty-field preservation to the contract | Pass |
| repeated_reopening | Reassess the contract and validation authority before another patch; do not waive the defect | Closure refused; reassess reader/writer authority and fixture assumptions | Pass |
| investigation | Author a bounded question and evidence deliverable; no presumed subsystem replacement | No closure yet; author the investigation and stop after recording it | Pass |
| author_unselected | Record eligible but unselected work; do not execute it or invent a blocker | Leave issue open, record eligibility and next-work disposition, then return | Pass |

## Response excerpts

These are verbatim next-action fields returned by the evaluating agent.

**complete**

> Close with the verified commit and contract evidence after required citation checks; decline speculative additional fuzzing as a closure prerequisite.

**counterexample**

> Record the counterexample, amend the acceptance matrix, reproduce the reader/recovery disagreement with a failing semantic test, and repair the validation discrepancy.

**adjacent**

> Track the diagnostic-ordering defect separately through ghi-author or gz insights remember, then close the verified parser repair without implementing the sibling fix automatically.

**coupled_regression**

> Record the shared-helper data flow and omitted consumer, expand the contract, add a failing library empty-field test, and repair the introduced regression before closing.

**repeated_reopening**

> Reassess the contract, shared validation authority, reader/writer data flow, and fixture assumptions before choosing another implementation. Add the latest counterexample and repair the demonstrated validation divergence using that reassessment.

**investigation**

> Author an investigation contract asking what produced the duplicate recovery attempts, bounded to the recorded transaction trace, current journal producer, and two retry callers. Require an evidence-backed causal analysis or explicitly bounded inconclusive findings.

The investigation response's stopping point was:

> For this authoring request, stop after the bounded investigation issue is recorded. Its later closure requires the completed evidence deliverable and a verified citable destination; it does not require an unbounded subsystem repair.

## Independent contract review and focused follow-up

A separate reviewer checked four criteria: outcome-derived contract, correct
expansion boundary, preserved checks/operator authority, and agreement between
author/closer/user docs. It found one blocker despite the six passing samples:
the author's unchanged Step 7 still ordered immediate execution of an easy
independent finding. The amendment gives capture-only invocations explicit
precedence, returns before the execution rows, and reports eligible but
unselected work without inventing a technical blocker. The reviewer then
checked that exact correction and reported the blocker resolved; no broader
review was added.

The follow-up evaluator returned this next action for **author_unselected**:

> Leave the evidenced issue open, record its number and disposition as eligible for direct repair but unselected, and return to the parser work order. Do not implement the defect or author an ADR/OBPI destination.

Its repeated **investigation** next action was:

> Author an investigation GHI asking what caused the duplicate recovery attempts in the recorded transaction. Bound the evidence population to that trace, the current journal producer, and its two retry callers. Record its eligibility and next-work disposition, then return without executing the investigation.

## Limits and reuse

These observations support the seven decisions under the supplied hypothetical
facts. They do not prove sustained behavior during a real repair, correctness
of the scenario facts, generalization to Claude or other models, or improvement
over the previous skill versions. No runtime gate was introduced and no
Mechanical score is claimed. A heading-presence test or the existing structural
skill scorer would not establish these decisions.

To repeat the sample, give an isolated evaluator the current canonical skill
versions and scenario packet, request the packet's response format, and retain
its actual decisions before assessing them against the table. Re-evaluate when
guidance changes or a real counterexample invalidates a criterion; passing this
sample does not justify repeated unrequested review of a completed GHI.

GHI #943 remains the separate vendor/model-tuning work order. GHI #978's remaining
ownership mechanisms and the implementation of #979 are not modified by this
guidance repair.
