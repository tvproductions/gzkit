# Proof currency: decision draft for GHI #1029

Dated 2026-09-19; code baseline `d6bc23d0ebef83a1b3391c521e35931f5f8013b6`.
Persona: main-session — craftsperson, governance-aware, whole-file reasoning,
direct. Parent: [three-pillars implementation plan](three-pillars-implementation-plan-2026-09-19.md),
[GHI #1029](https://github.com/tvproductions/gzkit/issues/1029).
This is a design proposal for review, not a ruled change to acceptance authority.

## Recommendation

Retain the existing broad currency key until a proposed narrower dependency
boundary can be independently enforced. Do not replace it with the brief
allowlist, test imports, or an observed-read list. Each has a concrete omission
case below. First distinguish the proof's dependency boundary from the review's
subject: a test can have narrow inputs while a quality reviewer reads broader
architecture. Reusing that review across changes outside the test inputs would
silently approve material the reviewer never saw.

This does not solve the repeated-work cost in #1029. It identifies why a small
hashing patch would not be an acceptable remedy. A bounded advisory impact view
can assist discovery without becoming the authority for currency. Its usefulness
and its ability to justify excluding inputs are separate questions.

## Current producer and consumer map

| Surface read | Current behavior | Obligation for a replacement |
|---|---|---|
| `acceptance_execution._brief_contract`, `canonical_obligations` | Parse the brief and its unique parent; bind the requirement roster and normative contract. Recognized historical sections are excluded. | Keep contract changes invalidating all affected obligations; unknown sections remain conservative. |
| `acceptance_execution._input_paths`, `_file_roster`, `digest_components` | Read configured source/test roots and the additional named audit population; content-hash the roster, including missing roots and additions/deletions; reject member symlinks. | A narrowed roster must preserve absence and directory-membership dependencies, not just hash existing selected files. |
| `acceptance_execution.prove` | Capture inputs before/after actual proof execution; require equality; separately bind explicitly declared environment keys. | Dependency discovery must itself be stable across execution. Unknown or unsupported reads must not yield narrower credit. |
| `acceptance.proof_aliases`, `_proof_blockers` | Reuse only consecutive valid equivalent claims with equal input, contract, selectors and execution-condition identities; compare each proof with the current broad digest. | Never infer narrower authority or equivalence retrospectively for legacy records. |
| `acceptance._review_proof_scope_errors`, `_record_findings`, `_record_closures`, `assess_readiness` | Bind reviews to exact proof subjects; retain findings and independently verified closures. | Multiple dependency keys cannot simply replace the one review key: explicitly bind each proof plus the review's wider subject, preserving history ordering and closures. |
| `acceptance_context.build_review_context`, `_review_subject` | Capture one stable current subject and refuse superseded proofs or a concurrent change during assembly. | Mixed proof keys must not permit a context assembled from inconsistent snapshots. |
| `acceptance_store._validate_new_review`, `acceptance_status`, `_live_proof_blockers`, `completion_review` | Record valid historical observations without granting current readiness; re-run non-BEHAVIOR resolvers and check declared conditions; completion consumes readiness and review provenance. | Preserve historical recordability, live resolver checks and final refusal. No importer-only fix is sufficient. |
| `adversary_workspace.materialize_adversary_workspace`, `_digest_tree` | Materialize tracked source plus tracked modifications; fingerprint copied files independently of the acceptance key. | Keep replay-source identity distinct from an obligation dependency identity; equality of names would not prove equality of populations. |

Read coverage: the execution module, reducer, reviewer-context module and
acceptance-obligations documentation were read in full; store and workspace
functions above were read at function scope. This is not a complete audit of
all CLI entry points or resolver implementations. The table names the inspected
coupling, rather than claiming an exhaustive dependency graph.

## Alternatives and counterexamples

| Candidate | Concrete failure or cost | Disposition |
|---|---|---|
| Existing broad audit population | An unrelated edit under a configured audit root invalidates all proof. It is conservative within that population, not a proof of every environmental dependency. | Keep as fallback and current behavior. |
| Brief Allowed Paths plus covering tests | An allowed command imports a shared validator outside its editing scope; changing that validator can change the proof. An editing permission is not an execution dependency. | Reject as independent currency authority. |
| Static imports of covering selectors | A test loads a JSON fixture, discovers a plugin dynamically, or checks whether a file exists. An import closure omits those inputs and may not represent deletions or new directory members. | Useful advisory relationship evidence; insufficient alone. |
| Observed reads captured during execution | The execution sees one branch; a new file or changed discovery result can select another branch. Subprocess, native and environment reads need equivalent accounting. A recorder under the implementing agent's control cannot certify its own completeness. | Insufficient unless paired with an independently enforced execution boundary. |
| Hermetic proof runner with declared capabilities | Could refuse or conservatively account for every input outside an independently defined sandbox, including absent-file and directory queries. Current reviewed modules do not establish such an authority. Building it expands runtime, portability and replay scope substantially. | Candidate feature design, not a quick repair. Requires its own bounded threat model and feasibility evidence. |

Removing the broad key for SUPPORT or STRUCTURAL-FENCE merely because their
resolvers re-run is also not established safe. A live resolver can establish
its current boolean result without proving that the earlier review's semantic
judgment still applies after source or rule changes. Resolver implementation and
review dependencies require their own account.

## Required acceptance cases for any narrowed implementation

Use two independently specified obligations A and B in a temporary governed
project, with distinct production functions, tests and fixtures and one shared
validator. Establish executed proofs and actual independent review records,
then mutate one input at a time. These are proposed acceptance cases, not tests
executed by this document.

| Mutation | Required result |
|---|---|
| A production source, A test, A fixture | A proof and approvals become stale. B stays current only if independently established unrelated. |
| Shared validator or shared fixture | Every dependent proof and review becomes stale. |
| A previously absent file appears; a discovered directory member is added/deleted | Discovery-dependent proof becomes stale even though the old list of read files is unchanged. |
| Brief or parent normative contract changes | All governed obligations become stale, retaining mapped findings. |
| Evidence/history append only | Preserve current behavior: no new executable-input invalidation. |
| Dependency declaration edited, recorder disabled, unknown input kind, unsupported subprocess | Fall back to the broad boundary or refuse; never infer currentness from missing information. |
| Quality-review source changes outside A's execution inputs | Invalidate that review when the changed source was part of its judgment subject, even if A's executed proof can remain current. |
| Old broad-key proof imported alongside new-key proof | Keep original version semantics; no synthesized narrower credit or erased findings. |
| Relevant change during capture, proof, or review import | Refuse current credit for mixed or superseded subjects; preserve valid historical review import, and final completion must refuse stale credit. |

A migration must therefore version proof identity and reviewer transport together,
carry the producer's authority provenance, preserve old ledger records unchanged,
and exercise status, context, review import and completion against the same cases.
No automatic schema migration should turn an old digest into new authority.

## Decision still required

The concrete choice is whether the expected reduction in repeated proof and
review warrants designing an independently enforced execution boundary. The
current recommendation is to retain broad currency and develop advisory impact
assistance first; it delivers useful relationship evidence without granting stale
proof credit. #1029 remains open for the operator's design ruling. This draft
does not close it or initiate an OBPI.
